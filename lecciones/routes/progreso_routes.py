from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.utils.jwt_utils import get_current_user
from database.db import get_db
from database.models.leccion_model import ProgresoLeccion
from lecciones.schemas.progreso_schemas import ProgresoLeccionRequest, ProgresoLeccionResponse

router = APIRouter()

@router.post("/progreso/marcar", response_model=ProgresoLeccionResponse)
def marcar_leccion_progreso(
    progreso_data: ProgresoLeccionRequest,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    progreso = db.query(ProgresoLeccion).filter_by(
        usuario_id=usuario.user_id,
        leccion_id=progreso_data.leccion_id
    ).first()

    if progreso:
        progreso.completada = progreso_data.completada
    else:
        progreso = ProgresoLeccion(
            usuario_id=usuario.user_id,
            leccion_id=progreso_data.leccion_id,
            completada=progreso_data.completada
        )
        db.add(progreso)

    db.commit()
    db.refresh(progreso)
    return progreso


@router.get("/lecciones/progreso")
def obtener_progreso_usuario(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    progreso = db.query(ProgresoLeccion).filter(ProgresoLeccion.usuario_id == usuario.user_id).all()

    return [
        {
            "leccion_id": p.leccion_id,
            "completada": p.completada,
            "fecha_completado": p.fecha_completado
        }
        for p in progreso
    ]