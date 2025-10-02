from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from Auth.utils.jwt_utils import get_current_user
from database.models.user_model import Usuario
from usuario.schemas.schemas_perfil import UsuarioPerfilResponse

router = APIRouter()

@router.get("/perfil", response_model=UsuarioPerfilResponse)
def obtener_perfil(db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_current_user)):
    return {
        "nombre": usuario_actual.nombre,
        "usuario": usuario_actual.nombre_usuario,
        "email": usuario_actual.email,
        "foto_perfil": usuario_actual.foto_perfil
    }
