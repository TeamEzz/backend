from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UsuarioRegistro(BaseModel):
    nombre: Optional[str] = None
    email: str
    password: str

class UsuarioRegistroSimple(BaseModel):
    email: EmailStr
    password: str
    
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str
    

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: Optional[str] = None
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
        
        
        
class TokenGoogle(BaseModel):
    token: str


class UsuarioConToken(BaseModel):
    id: int
    email: str
    token: str
    nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioLoginResponse(BaseModel):
    id: int
    email: EmailStr
    token: str
    nombre: Optional[str] = None
    usuario: Optional[str] = None
    encuesta_completada: bool = False

    model_config = ConfigDict(from_attributes=True)
