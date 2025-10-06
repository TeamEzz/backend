from sqlalchemy import Column, Integer, Date, DateTime, String, ForeignKey, func
from database.db import Base

class Streak(Base):
    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True, nullable=False)

    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)

    # Día (en TZ “lógica” del usuario) del último evento que cuenta para la racha
    last_event_date = Column(Date, nullable=True)

    # Opcional (si más adelante guardas la zona horaria del user)
    timezone = Column(String, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())