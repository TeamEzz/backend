from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from database.db import get_db
from Auth.utils.jwt_utils import get_current_user
from database.models.user_model import Usuario
from database.models.meta_model import MetaUsuario
from database.models.checkin_model import CheckIn
from metas.schemas.meta_schema import BudgetResultOut
from metas.utils import meta_calculator as calc
from ..schemas.tracker_schema import (
    DiaCheckinRequest,
    CheckInRequest,
    PlanUpdateRequest,
    CheckInOut,
    TrackerDataOut,
)
from ..utils import tracker_calculator as tcalc

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _plan_activo(db: Session, usuario_id: int) -> MetaUsuario:
    """Devuelve la meta primaria más reciente del usuario o 404 si no hay plan."""
    meta = (
        db.query(MetaUsuario)
        .filter(MetaUsuario.usuario_id == usuario_id)
        .order_by(MetaUsuario.es_primaria.desc(), MetaUsuario.creado_en.desc())
        .first()
    )
    if meta is None:
        raise HTTPException(status_code=404, detail="No tienes un plan de presupuesto activo")
    return meta


def _result_out(meta: MetaUsuario) -> BudgetResultOut:
    """Reconstruye el BudgetResultOut a partir de la meta persistida.

    `instrumento_desc` no se almacena; se deriva del horizonte (igual que en /metas/plan).
    """
    _, inst_desc = calc.instrumento(meta.horizonte_meses)
    return BudgetResultOut(
        meta_titulo=meta.meta_titulo,
        meta_tag=meta.meta_tag,
        es_custom=meta.es_custom,
        horizonte_meses=meta.horizonte_meses,
        costo_meta=meta.costo_meta,
        ahorro_requerido=meta.ahorro_requerido,
        pct_ingreso=meta.pct_ingreso,
        viabilidad=meta.viabilidad,
        instrumento=meta.instrumento,
        instrumento_desc=inst_desc,
        mensaje_toro=meta.mensaje_toro or "",
    )


def _tracker_data(db: Session, meta: MetaUsuario) -> TrackerDataOut:
    check_ins = (
        db.query(CheckIn)
        .filter(CheckIn.usuario_id == meta.usuario_id)
        .order_by(CheckIn.anio.desc(), CheckIn.mes.desc())
        .all()
    )

    total = tcalc.calcular_total_ahorrado(check_ins)
    racha = tcalc.calcular_racha(check_ins)
    promedio = (total / len(check_ins)) if check_ins else 0.0
    proyeccion = tcalc.calcular_proyeccion(total, meta.costo_meta, promedio)

    now = datetime.now()
    ya_registro = any(ci.mes == now.month and ci.anio == now.year for ci in check_ins)

    return TrackerDataOut(
        plan=_result_out(meta),
        check_ins=[CheckInOut.model_validate(ci) for ci in check_ins],
        total_ahorrado=total,
        racha_actual=racha,
        proyeccion_meses=proyeccion,
        dia_checkin=meta.dia_checkin or 0,
        ya_registro_este_mes=ya_registro,
        ingreso_mensual=meta.ingreso_mensual,
        gastos_mensuales=meta.gastos_mensuales,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("", response_model=TrackerDataOut)
def obtener_tracker(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    meta = _plan_activo(db, usuario.id)
    return _tracker_data(db, meta)


@router.patch("/dia-checkin", response_model=TrackerDataOut)
def configurar_dia_checkin(
    data: DiaCheckinRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if not (1 <= data.dia_checkin <= 28):
        raise HTTPException(status_code=400, detail="El día de check-in debe estar entre 1 y 28")

    meta = _plan_activo(db, usuario.id)
    meta.dia_checkin = data.dia_checkin
    db.commit()
    db.refresh(meta)
    return _tracker_data(db, meta)


@router.post("/checkin", response_model=TrackerDataOut)
def registrar_checkin(
    data: CheckInRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    meta = _plan_activo(db, usuario.id)

    now = datetime.now()
    existente = (
        db.query(CheckIn)
        .filter(
            CheckIn.usuario_id == usuario.id,
            CheckIn.mes == now.month,
            CheckIn.anio == now.year,
        )
        .first()
    )
    if existente is not None:
        raise HTTPException(status_code=409, detail="Ya registraste tu aporte de este mes")

    nuevo = CheckIn(
        usuario_id=usuario.id,
        meta_id=meta.id,
        mes=now.month,
        anio=now.year,
        monto_aportado=float(data.monto_aportado),
        objetivo_mes=meta.ahorro_requerido,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(meta)
    return _tracker_data(db, meta)


@router.patch("/plan", response_model=TrackerDataOut)
def actualizar_plan(
    data: PlanUpdateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    meta = _plan_activo(db, usuario.id)

    # Recalcula con la fuente de verdad. El costo de la meta no cambia: el slider
    # ajusta horizonte/gastos y de ahí se deriva el nuevo ahorro requerido.
    resultado = calc.calcular(
        meta_titulo=meta.meta_titulo,
        meta_tag=meta.meta_tag,
        es_custom=meta.es_custom,
        horizonte_meses=data.horizonte_meses,
        ingreso_mensual=meta.ingreso_mensual,
        gastos_mensuales=data.gastos_mensuales,
        costo_meta=meta.costo_meta,
    )

    meta.horizonte_meses = resultado["horizonte_meses"]
    meta.gastos_mensuales = data.gastos_mensuales
    meta.ahorro_requerido = resultado["ahorro_requerido"]
    meta.pct_ingreso = resultado["pct_ingreso"]
    meta.viabilidad = resultado["viabilidad"]
    meta.instrumento = resultado["instrumento"]
    meta.mensaje_toro = resultado["mensaje_toro"]
    db.commit()
    db.refresh(meta)
    return _tracker_data(db, meta)


@router.delete("/plan", status_code=204)
def eliminar_plan(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Elimina el presupuesto del usuario: TODOS sus planes (metas_usuario) y
    TODOS sus check-ins. Como cada 'Empezar mi plan' inserta una fila nueva, un
    usuario puede acumular varias; borrarlas todas garantiza que tras el DELETE
    `GET /tracker` devuelva 404 y no resucite un plan viejo.
    """
    existe = (
        db.query(MetaUsuario.id)
        .filter(MetaUsuario.usuario_id == usuario.id)
        .first()
    )
    if existe is None:
        raise HTTPException(status_code=404, detail="No tienes un plan de presupuesto activo")

    db.query(CheckIn).filter(CheckIn.usuario_id == usuario.id).delete(synchronize_session=False)
    db.query(MetaUsuario).filter(MetaUsuario.usuario_id == usuario.id).delete(synchronize_session=False)
    db.commit()
    return Response(status_code=204)
