# backend/streaks/streak_utils.py
from datetime import date
from sqlalchemy.orm import Session
from database.models.streak_model import Streak

def update_streak(db: Session, user_id: int, today: date) -> Streak:
    """
    Reglas:
      - Si ya hubo evento HOY: no cambia.
      - Si el último evento fue AYER: current += 1
      - Si fue antes de AYER o no existe: current = 1
      - longest = max(longest, current)
    """
    s = db.query(Streak).filter(Streak.usuario_id == user_id).first()

    if not s:
        s = Streak(
            usuario_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_event_date=today
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        return s

    # Ya contó hoy
    if s.last_event_date == today:
        return s

    # Diferencia en días
    delta = (today - s.last_event_date).days if s.last_event_date else None

    if delta == 1:
        s.current_streak += 1
    else:
        s.current_streak = 1

    if s.current_streak > s.longest_streak:
        s.longest_streak = s.current_streak

    s.last_event_date = today
    db.commit()
    db.refresh(s)
    return s