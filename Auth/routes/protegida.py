from fastapi import APIRouter, Depends
from Auth.utils.jwt_utils import get_current_user
from database.models.user_model import Usuario

router = APIRouter()

@router.get("/protegida")
def ruta_protegida(usuario: Usuario = Depends(get_current_user)):
    return {
        "mensaje": "Acceso autorizado ✅",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email
        }
    }
