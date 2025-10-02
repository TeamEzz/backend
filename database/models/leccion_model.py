from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base
from database.db import Base, SessionLocal, engine

class ProgresoLeccion(Base):
    __tablename__ = "progreso_leccion"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    leccion_id = Column(Integer)  # Este número representa el ID lógico de la lección (ej. 1, 2, 3...)
    completada = Column(Boolean, default=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="progreso_lecciones")