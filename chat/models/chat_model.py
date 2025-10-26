
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database.db import Base
 # o como tengas tu declarative_base()

class Conversacion(Base):
    __tablename__ = "conversaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow)

    mensajes = relationship("Mensaje", back_populates="conversacion", cascade="all, delete-orphan")


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    conversacion_id = Column(Integer, ForeignKey("conversaciones.id"))
    remitente = Column(String)  # "usuario" o "IA"
    contenido = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversacion = relationship("Conversacion", back_populates="mensajes")
