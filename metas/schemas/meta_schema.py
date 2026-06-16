from pydantic import BaseModel, Field
from typing import Optional, List


class PlanRequest(BaseModel):
    meta_titulo: str = Field(max_length=100)
    meta_tag: Optional[str] = None
    es_custom: bool = False
    horizonte_meses: int
    ingreso_mensual: float
    gastos_mensuales: float
    costo_meta: float = 0
    es_primaria: bool = True
    otras_metas: List[str] = []


class BudgetResultOut(BaseModel):
    meta_titulo: str
    meta_tag: Optional[str] = None
    es_custom: bool
    horizonte_meses: int
    costo_meta: float
    ahorro_requerido: float
    pct_ingreso: float          # 0–1
    viabilidad: str             # "verde" | "amarillo" | "rojo"
    instrumento: str
    instrumento_desc: str
    mensaje_toro: str


class ContextoFinancieroOut(BaseModel):
    ingreso_estimado: Optional[int] = None
    ingreso_rango: Optional[str] = None
    personaje: Optional[str] = None
