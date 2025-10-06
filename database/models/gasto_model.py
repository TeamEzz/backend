from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime

__table_args__ = (
    Index('ix_gasto_user_fecha', 'usuario_id', 'fecha'),
    Index('ix_gasto_user_cat', 'usuario_id', 'categoria'),
)

class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria = Column(String, nullable=False)  # Ej: "comida", "entretenimiento", etc.
    monto = Column(Float, nullable=False)
    es_necesario = Column(Boolean, default=False)
    fecha = Column(DateTime, default=datetime)

    usuario = relationship("Usuario", back_populates="gastos")