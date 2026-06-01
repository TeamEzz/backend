import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from Auth.utils.jwt_utils import get_current_user
from database.models.user_model import Usuario
from database.models.meta_model import MetaUsuario
from database.models.encuesta_model import RespuestaEncuestaDB
from ..schemas.meta_schema import PlanRequest, BudgetResultOut, ContextoFinancieroOut
from ..utils import meta_calculator as calc

router = APIRouter()

# Personaje de Encuesta2 (Slide114) → (punto medio, rango texto).
# El mapeo de rangos vive en el frontend Slide114.swift; aquí lo duplicamos.
PERSONAJE_INGRESO = {
    "Bula":   (2_000_000,  "1.000.000 – 3.000.000"),
    "Toriel": (5_000_000,  "4.000.000 – 6.000.000"),
    "EZ":     (10_500_000, "6.000.000 – 15.000.000"),
}

# Preg9 (encuesta original, índice 8) → (punto medio, rango texto). E) = sin dato.
_PREG9_TOKENS = [
    ("hasta $3m",   (2_500_000, "Hasta $3.000.000")),
    ("$3m – $6m",   (4_500_000, "$3.000.000 – $6.000.000")),
    ("$3m - $6m",   (4_500_000, "$3.000.000 – $6.000.000")),
    ("$6m – $10m",  (8_000_000, "$6.000.000 – $10.000.000")),
    ("$6m - $10m",  (8_000_000, "$6.000.000 – $10.000.000")),
    ("más de $10m", (12_000_000, "Más de $10.000.000")),
    ("mas de $10m", (12_000_000, "Más de $10.000.000")),
]


@router.post("/plan", response_model=BudgetResultOut)
def crear_plan(
    data: PlanRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    resultado = calc.calcular(
        meta_titulo=data.meta_titulo,
        meta_tag=data.meta_tag,
        es_custom=data.es_custom,
        horizonte_meses=data.horizonte_meses,
        ingreso_mensual=data.ingreso_mensual,
        gastos_mensuales=data.gastos_mensuales,
        costo_meta=data.costo_meta,
    )

    nueva = MetaUsuario(
        usuario_id=usuario.id,
        meta_titulo=resultado["meta_titulo"],
        meta_tag=resultado["meta_tag"],
        es_custom=resultado["es_custom"],
        es_primaria=data.es_primaria,
        horizonte_meses=resultado["horizonte_meses"],
        ingreso_mensual=data.ingreso_mensual,
        gastos_mensuales=data.gastos_mensuales,
        costo_meta=resultado["costo_meta"],
        ahorro_requerido=resultado["ahorro_requerido"],
        pct_ingreso=resultado["pct_ingreso"],
        viabilidad=resultado["viabilidad"],
        instrumento=resultado["instrumento"],
        mensaje_toro=resultado["mensaje_toro"],
        otras_metas_json=json.dumps(data.otras_metas, ensure_ascii=False),
    )
    db.add(nueva)
    db.commit()

    return BudgetResultOut(**resultado)


@router.get("/contexto-financiero", response_model=ContextoFinancieroOut)
def contexto_financiero(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    row = db.query(RespuestaEncuestaDB).filter_by(usuario_id=usuario.id).first()
    if not row or not row.respuestas_json:
        return ContextoFinancieroOut()

    try:
        data = json.loads(row.respuestas_json)
    except (ValueError, TypeError):
        return ContextoFinancieroOut()

    # 1. Personaje financiero (Encuesta2, dict) — fuente primaria.
    if isinstance(data, dict):
        personaje = data.get("personaje")
        if personaje in PERSONAJE_INGRESO:
            mid, rango = PERSONAJE_INGRESO[personaje]
            return ContextoFinancieroOut(
                ingreso_estimado=mid, ingreso_rango=rango, personaje=personaje
            )

    # 2. Fallback: Preg9 (encuesta original, lista índice 8).
    if isinstance(data, list) and len(data) > 8 and isinstance(data[8], str):
        ans = data[8].lower()
        for token, (mid, rango) in _PREG9_TOKENS:
            if token in ans:
                return ContextoFinancieroOut(ingreso_estimado=mid, ingreso_rango=rango)

    # 3. Sin dato → campo en blanco editable.
    return ContextoFinancieroOut()
