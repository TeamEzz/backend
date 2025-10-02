from pydantic import BaseModel, EmailStr
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

    class Config:
        from_attributes = True  # Para Pydantic v2
        
        
        
class TokenGoogle(BaseModel):
    token: str


class UsuarioConToken(BaseModel):
    id: int
    email: str
    token: str
    nombre: Optional[str] = None
    
    
    
    
