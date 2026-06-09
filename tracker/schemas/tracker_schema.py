from pydantic import BaseModel, ConfigDict
from typing import List

from metas.schemas.meta_schema import BudgetResultOut


# ── Entradas ───────────────────────────────────────────────────────────────

class DiaCheckinRequest(BaseModel):
    dia_checkin: int          # 1–28


class CheckInRequest(BaseModel):
    monto_aportado: float


class PlanUpdateRequest(BaseModel):
    ahorro_mensual: float     # nuevo aporte objetivo / mes (deriva el horizonte)
    horizonte_meses: int
    gastos_mensuales: float


# ── Salidas ──────────────────────────────────────────────────────────────────

class CheckInOut(BaseModel):
    id: int
    mes: int
    anio: int
    monto_aportado: float
    objetivo_mes: float

    model_config = ConfigDict(from_attributes=True)


class TrackerDataOut(BaseModel):
    plan: BudgetResultOut
    check_ins: List[CheckInOut]
    total_ahorrado: float
    racha_actual: int
    proyeccion_meses: int
    dia_checkin: int          # 0 = sin configurar
    ya_registro_este_mes: bool
    ingreso_mensual: float    # para recalcular en BudgetDetailView (slider local)
    gastos_mensuales: float
