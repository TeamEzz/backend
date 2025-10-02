from pydantic import BaseModel

class ProgresoLeccionRequest(BaseModel):
    leccion_id: int
    completada: bool

class ProgresoLeccionResponse(BaseModel):
    leccion_id: int
    completada: bool

    class Config:
        orm_mode = True