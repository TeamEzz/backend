from sqlalchemy import Column, Integer, String
from database.db import Base  # asegúrate que Base esté definido en config.py
from sqlalchemy.orm import relationship


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=True)
    nombre_usuario = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    proveedor = Column(String)
    foto_perfil = Column(String, nullable=True, default="UsuarioDefault")
    gastos = relationship("Gasto", back_populates="usuario", cascade="all, delete-orphan")
    progreso_lecciones = relationship("ProgresoLeccion", back_populates="usuario")