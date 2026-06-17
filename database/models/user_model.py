from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from database.db import Base  # Asegúrate de que Base se define en database/db.py


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)  # (el índice de la PK es implícito)
    nombre = Column(String, nullable=True)
    nombre_usuario = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    proveedor = Column(String, nullable=True, default="local")
    foto_perfil = Column(String, nullable=True, default="UsuarioDefault")

    # verificación de correo (registro local)
    verificado = Column(Boolean, nullable=False, server_default="false")
    codigo_verificacion = Column(String, nullable=True)        # hash bcrypt del código de 6 dígitos
    codigo_expira_en = Column(DateTime(timezone=True), nullable=True)
    codigo_enviado_en = Column(DateTime(timezone=True), nullable=True)  # para cooldown de reenvío
    codigo_intentos = Column(Integer, nullable=False, server_default="0")

    # borrado de cuenta (soft delete + anonimización irreversible — App Store 5.1.1 / GDPR)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    anonymized = Column(Boolean, nullable=False, server_default="false")

    # timestamps
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actualizado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relaciones
    gastos = relationship("Gasto", back_populates="usuario", cascade="all, delete-orphan")
    progreso_lecciones = relationship("ProgresoLeccion", back_populates="usuario")