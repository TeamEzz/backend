from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from database.db import Base


class CheckIn(Base):
    """Aporte mensual registrado por el usuario dentro del Budget Tracker.

    Cada fila es el check-in de un mes/año concreto. Solo puede existir uno por
    (usuario, mes, año) — la restricción única lo garantiza a nivel de DB.
    """
    __tablename__ = "check_ins"
    __table_args__ = (
        UniqueConstraint("usuario_id", "mes", "anio", name="uq_checkin_usuario_mes_anio"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    meta_id = Column(Integer, ForeignKey("metas_usuario.id"), nullable=False, index=True)

    mes = Column(Integer, nullable=False)             # 1–12
    anio = Column(Integer, nullable=False)            # año calendario
    monto_aportado = Column(Float, nullable=False)    # lo que el usuario reporta haber ahorrado
    objetivo_mes = Column(Float, nullable=False)      # ahorro_requerido del plan al momento del check-in

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
    meta = relationship("MetaUsuario")
