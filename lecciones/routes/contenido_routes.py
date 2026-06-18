# lecciones/routes/contenido_routes.py
# Rutas para consultar el contenido de las lecciones

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from Auth.utils.jwt_utils import get_current_user
from database.db import get_db
from database.models.contenido_leccion_model import Leccion
from database.models.user_model import Usuario
from lecciones.schemas.contenido_schemas import (
    LeccionContenidoResponse,
    LeccionMetadataResponse,
)

router = APIRouter()


@router.get("/{leccion_id}", response_model=LeccionContenidoResponse)
def obtener_leccion(
    leccion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna una lección completa (metadatos + contenido JSONB) por su ID."""
    leccion = (
        db.query(Leccion)
        .filter(Leccion.id == leccion_id, Leccion.activa == True)  # noqa: E712
        .first()
    )
    if not leccion:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    return LeccionContenidoResponse(
        id=leccion.id,
        nivel=leccion.nivel,
        orden=leccion.orden,
        titulo=leccion.titulo,
        descripcion=leccion.descripcion,
        duracion_minutos=leccion.duracion_minutos,
        imagen_portada_key=leccion.imagen_portada_key,
        activa=leccion.activa,
        version=leccion.version,
        pasos=leccion.contenido.get("pasos", []),
    )


@router.get("", response_model=list[LeccionMetadataResponse])
def listar_lecciones_por_nivel(
    nivel: int = Query(..., description="Nivel de las lecciones a consultar"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna la lista de lecciones activas de un nivel (solo metadatos, sin contenido)."""
    lecciones = (
        db.query(Leccion)
        .filter(Leccion.nivel == nivel, Leccion.activa == True)  # noqa: E712
        .order_by(Leccion.orden)
        .all()
    )
    return lecciones
