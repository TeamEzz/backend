from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class GastoBase(BaseModel):
    categoria: str = Field(max_length=50)  # Ej: 'Alimentación'
    monto: float    # Ej: 25000.0
    tipo: str       # Ej: 'necesario', 'impulsivo', etc.

class GastoCreate(GastoBase):
    pass

class GastoOut(GastoBase):
    id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
