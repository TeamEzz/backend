# database/models/contenido_leccion_model.py
# Modelo para el contenido de las lecciones (tabla `lecciones`)
# NOTA: No confundir con ProgresoLeccion (tabla `progreso_leccion`) en leccion_model.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from database.db import Base


class Leccion(Base):
    __tablename__ = "lecciones"
    __table_args__ = (Index("ix_lecciones_nivel", "nivel"),)

    # id explícito, sin autoincrement — debe coincidir con los IDs hardcoded del frontend (1-4)
    id = Column(Integer, primary_key=True, autoincrement=False)
    nivel = Column(Integer, nullable=False)
    orden = Column(Integer, nullable=False)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    duracion_minutos = Column(Integer, nullable=True)
    imagen_portada_key = Column(String, nullable=True)
    activa = Column(Boolean, default=True)
    contenido = Column(JSONB, nullable=False)
    version = Column(Integer, default=1)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
