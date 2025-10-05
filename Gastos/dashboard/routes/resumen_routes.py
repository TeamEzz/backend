from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from Auth.utils.jwt_utils import get_current_user
from database.config import get_db
from Gastos.dashboard.schemas.resumen_schemas import ResumenResponse, PeriodoEnum
from Gastos.dashboard.utils.resumen_service import rango_periodo, build_streak, build_gastos, build_lecciones

router = APIRouter()

@router.get("/resumen", response_model=ResumenResponse)
def resumen_dashboard(
    periodo: PeriodoEnum = Query("semanal"),
    nivel: int = Query(0),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    now = __import__("datetime").datetime.now()
    inicio, fin = rango_periodo(periodo.value, now)

    streak = build_streak(db, usuario.user_id)
    gastos = build_gastos(db, usuario.user_id, inicio, fin, periodo.value)
    lecciones = build_lecciones(db, usuario.user_id, nivel)

    # puedes generar insights simples aquí
    insights = []

    return {"streak": streak, "gastos": gastos, "lecciones": lecciones, "insights": insights}