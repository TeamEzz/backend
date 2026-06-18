# lecciones/schemas/contenido_schemas.py
# Esquemas Pydantic para el contenido de lecciones

from pydantic import BaseModel, ConfigDict
from typing import Optional, Any


class LeccionMetadataResponse(BaseModel):
    """Metadatos de una lección, sin incluir el campo contenido (JSONB pesado)."""

    id: int
    nivel: int
    orden: int
    titulo: str
    descripcion: Optional[str] = None
    duracion_minutos: Optional[int] = None
    imagen_portada_key: Optional[str] = None
    activa: bool
    version: int

    model_config = ConfigDict(from_attributes=True)


class LeccionContenidoResponse(LeccionMetadataResponse):
    """Lección completa con pasos extraídos del JSONB."""

    pasos: list  # Extraído de contenido["pasos"] — coincide con el modelo iOS LeccionContenido
