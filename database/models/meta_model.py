from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from database.db import Base


class MetaUsuario(Base):
    __tablename__ = "metas_usuario"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)

    # Meta
    meta_titulo = Column(String, nullable=False)
    meta_tag = Column(String, nullable=True)          # hogar, viaje, ahorro, movilidad, educacion, futuro
    es_custom = Column(Boolean, default=False, nullable=False)
    es_primaria = Column(Boolean, default=True, nullable=False)
    horizonte_meses = Column(Integer, nullable=False)

    # Datos financieros del plan
    ingreso_mensual = Column(Float, nullable=False)
    gastos_mensuales = Column(Float, nullable=False)
    costo_meta = Column(Float, nullable=False)

    # Resultado calculado
    ahorro_requerido = Column(Float, nullable=False)
    pct_ingreso = Column(Float, nullable=False)
    viabilidad = Column(String, nullable=False)        # "verde" | "amarillo" | "rojo"
    instrumento = Column(String, nullable=False)
    mensaje_toro = Column(Text, nullable=True)

    # Otros sueños no priorizados (JSON: lista de títulos)
    otras_metas_json = Column(Text, nullable=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
