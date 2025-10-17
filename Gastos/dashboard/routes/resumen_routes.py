from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Auth.utils.jwt_utils import get_current_user
from database.db import get_db
from database.models.user_model import Usuario
from Gastos.dashboard.schemas.resumen_schemas import ResumenResponse, PeriodoEnum
from Gastos.dashboard.utils.resumen_service import rango_periodo, build_streak, build_gastos, build_lecciones

router = APIRouter()

@router.get("/resumen", response_model=ResumenResponse)
def resumen_dashboard(
    periodo: PeriodoEnum = Query("semanal"),
    nivel: int = Query(0),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    inicio, fin = rango_periodo(periodo.value, now)

    streak = build_streak(db, usuario.id)
    gastos = build_gastos(db, usuario.id, inicio, fin, periodo.value)
    lecciones = build_lecciones(db, usuario.id, nivel)

    # puedes generar insights simples aquí
    insights = []

    return {"streak": streak, "gastos": gastos, "lecciones": lecciones, "insights": insights}
