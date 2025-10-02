from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base
from datetime import datetime
from database.db import Base, SessionLocal, engine

class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria = Column(String, nullable=False)  # Ej: "comida", "entretenimiento", etc.
    monto = Column(Float, nullable=False)
    es_necesario = Column(Boolean, default=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="gastos")