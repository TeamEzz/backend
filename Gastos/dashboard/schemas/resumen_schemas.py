from datetime import date
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class PeriodoEnum(str, Enum):
    diario = "diario"
    semanal = "semanal"
    mensual = "mensual"
    anual = "anual"

class CategoriaItem(BaseModel):
    nombre: str
    monto: float
    pct: float

class GastosResumen(BaseModel):
    periodo: PeriodoEnum
    inicio: date
    fin: date
    total: float
    por_categoria: List[CategoriaItem]
    necesarios_pct: float
    no_necesarios_pct: float

class StreakDTO(BaseModel):
    actual: int
    maxima: int
    hoy_contada: bool

class LeccionesDTO(BaseModel):
    nivel: int
    completadas: int
    total: int

class ResumenResponse(BaseModel):
    streak: StreakDTO
    lecciones: LeccionesDTO
    gastos: GastosResumen
    insights: List[dict] = []