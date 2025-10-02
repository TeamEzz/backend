from pydantic import BaseModel
from typing import Optional

class UsuarioPerfilResponse(BaseModel):
    nombre: Optional[str]
    usuario: str
    email: str
    foto_perfil: Optional[str] = None