from pydantic import BaseModel, EmailStr, Field

class NombreUpdate(BaseModel):
    nombre: str = Field(max_length=50)

class UsernameUpdate(BaseModel):
    nombre_usuario: str = Field(max_length=50)

class EmailUpdate(BaseModel):
    email: EmailStr