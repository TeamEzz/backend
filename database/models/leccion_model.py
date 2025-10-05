from sqlalchemy import Column, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from database.config import Base

__table_args__ = (
    Index('ix_leccion_nivel', 'nivel'),
)

class ProgresoLeccion(Base):
    __tablename__ = "progreso_leccion"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    leccion_id = Column(Integer)  # Este número representa el ID lógico de la lección (ej. 1, 2, 3...)
    completada = Column(Boolean, default=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="progreso_lecciones")