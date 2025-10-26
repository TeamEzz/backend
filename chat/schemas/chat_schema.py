from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# 🔹 Esquema de mensaje (para entrada/salida)
class MensajeSchema(BaseModel):
    id: Optional[int] = None
    remitente: str
    contenido: str
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True  # permite convertir desde objetos SQLAlchemy

# 🔹 Esquema de conversación
class ConversacionSchema(BaseModel):
    id: Optional[int] = None
    usuario_id: int
    titulo: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_ultima_actualizacion: Optional[datetime] = None
    mensajes: List[MensajeSchema] = []

    class Config:
        orm_mode = True