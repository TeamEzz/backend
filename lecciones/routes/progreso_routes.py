# lecciones/routes/progreso_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from datetime import datetime, timezone


from Auth.utils.jwt_utils import get_current_user
from database.config import get_db
from database.models.leccion_model import ProgresoLeccion
from database.models.user_model import Usuario
from lecciones.schemas.progreso_schemas import (
    ProgresoLeccionRequest,
    ProgresoLeccionResponse,
)
from streaks.utils.streak_utils import update_streak

router = APIRouter()

@router.get("/progreso", response_model=list[ProgresoLeccionResponse])
def obtener_progreso_usuario(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # Asegúrate que ProgresoLeccionResponse tiene model_config = ConfigDict(from_attributes=True)
    return (
        db.query(ProgresoLeccion)
          .filter(ProgresoLeccion.usuario_id == usuario.id)
          .all()
    )

@router.post("/{leccion_id}/completar", response_model=ProgresoLeccionResponse)
def marcar_como_completada(
    leccion_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    today = now.date()

    try:
        progreso = (
            db.query(ProgresoLeccion)
              .filter_by(usuario_id=usuario.id, leccion_id=leccion_id)
              .first()
        )

        if progreso:
            progreso.completada = True
            if hasattr(progreso, "fecha_completado"):
                progreso.fecha_completado = now
        else:
            progreso = ProgresoLeccion(
                usuario_id=usuario.id,
                leccion_id=leccion_id,
                completada=True,
                # fecha_completado=now,  # descomenta si tu modelo lo tiene
            )
            db.add(progreso)

        db.commit()
        db.refresh(progreso)

        # Actualiza racha (seguro si se llama 2 veces el mismo día)
        update_streak(db, usuario.id, today)

        return progreso

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar lección: {e}")

@router.post("/progreso/marcar", response_model=ProgresoLeccionResponse)
def marcar_leccion_progreso(
    progreso_data: ProgresoLeccionRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    today = now.date()

    try:
        progreso = (
            db.query(ProgresoLeccion)
              .filter_by(usuario_id=usuario.id, leccion_id=progreso_data.leccion_id)
              .first()
        )

        if progreso:
            progreso.completada = progreso_data.completada
            if hasattr(progreso, "fecha_completado"):
                progreso.fecha_completado = now if progreso_data.completada else None
        else:
            progreso = ProgresoLeccion(
                usuario_id=usuario.id,
                leccion_id=progreso_data.leccion_id,
                completada=progreso_data.completada,
                # fecha_completado = now if progreso_data.completada else None
            )
            db.add(progreso)

        db.commit()
        db.refresh(progreso)

        if progreso.completada:
            update_streak(db, usuario.id, today)

        return progreso

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al marcar progreso: {e}")