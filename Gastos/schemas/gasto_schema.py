from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class GastoBase(BaseModel):
    categoria: str  # Ej: 'Alimentación'
    monto: float    # Ej: 25000.0
    tipo: str       # Ej: 'necesario', 'impulsivo', etc.

class GastoCreate(GastoBase):
    pass

class GastoOut(GastoBase):
    id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
