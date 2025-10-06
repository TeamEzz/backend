# streaks/routes/streak_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from Auth.utils.jwt_utils import get_current_user
from database.models.streak_model import Streak
from database.models.user_model import Usuario  

router = APIRouter()

@router.get("/streak/actual")
def get_streak_actual(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)  
):
    s = db.query(Streak).filter_by(usuario_id=usuario.id).first()
    if not s:
        return {"current": 0, "longest": 0, "last_date": None}
    return {
        "current": s.current_streak,
        "longest": s.longest_streak,
        "last_date": s.last_event_date,
    }