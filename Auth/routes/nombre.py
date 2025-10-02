from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import get_db
from database.models.user_model import Usuario
from Auth.utils.jwt_utils import get_current_user
from pydantic import BaseModel

router = APIRouter()

class NombreUsuarioRequest(BaseModel):
    nombre: str
    usuario: str

@router.post("/perfil")
def guardar_nombre_y_usuario(datos: NombreUsuarioRequest, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    # Verificar si el nombre de usuario ya existe y no es el suyo
    usuario_existente = db.query(Usuario).filter(Usuario.nombre_usuario == datos.usuario).first()
    if usuario_existente and usuario_existente.id != usuario_actual.id:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    usuario_actual.nombre = datos.nombre
    usuario_actual.nombre_usuario = datos.usuario
    db.commit()

    return {"mensaje": "Perfil actualizado"}