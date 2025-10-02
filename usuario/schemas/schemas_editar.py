from pydantic import BaseModel, EmailStr

class NombreUpdate(BaseModel):
    nombre: str

class UsernameUpdate(BaseModel):
    nombre_usuario: str

class EmailUpdate(BaseModel):
    email: EmailStr