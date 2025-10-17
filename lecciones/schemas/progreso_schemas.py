from pydantic import BaseModel, ConfigDict

class ProgresoLeccionRequest(BaseModel):
    leccion_id: int
    completada: bool

class ProgresoLeccionResponse(BaseModel):
    leccion_id: int
    completada: bool

    model_config = ConfigDict(from_attributes=True)
