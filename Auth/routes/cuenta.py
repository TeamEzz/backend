import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from jose import jwt, JWTError
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from Auth.utils.jwt_utils import get_current_user, SECRET_KEY, ALGORITHM
from database.db import get_db
from database.models.user_model import Usuario
from limiter import limiter

router = APIRouter()


def _key_por_usuario(request: Request) -> str:
    """Key del rate limiter por usuario autenticado (no por IP).

    Extrae el `id` del JWT del header Authorization. Fallback a la IP si no hay
    token válido (defensa en profundidad; en la práctica Depends(get_current_user)
    ya rechaza con 401 antes de evaluar la key).
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            uid = payload.get("id")
            if uid is not None:
                return f"user:{uid}"
        except JWTError:
            pass
    return get_remote_address(request)


@router.delete("/cuenta")
@limiter.limit("3/hour", key_func=_key_por_usuario)  # evita borrados accidentales repetidos
def eliminar_cuenta(
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Soft delete con anonimización irreversible del PII (App Store 5.1.1 / GDPR).

    NO borra el registro (preserva las foreign keys) ni los datos financieros, que ya
    no son identificables tras la anonimización. NO revoca el JWT: el cliente descarta
    el token y el TTL de 7 días lo expira de forma natural.
    """
    if usuario_actual.deleted_at is not None:
        raise HTTPException(status_code=400, detail="La cuenta ya fue eliminada")

    token = uuid.uuid4().hex
    # email y nombre_usuario tienen unique=True → el UUID aleatorio evita colisiones
    usuario_actual.email = f"deleted_{token}@deleted.ez"
    usuario_actual.nombre = "Usuario eliminado"
    usuario_actual.nombre_usuario = f"deleted_{token}"
    usuario_actual.foto_perfil = None
    usuario_actual.deleted_at = datetime.utcnow()
    usuario_actual.anonymized = True
    db.commit()

    return {"message": "Cuenta eliminada correctamente"}


@router.post("/logout")
def logout(usuario_actual: Usuario = Depends(get_current_user)):
    """El JWT es stateless: no hay blacklist. El cliente descarta el token al recibir 200.

    # FUTURO: implementar blacklist de tokens (Redis) cuando el TTL de 7 días sea un
    # riesgo operacional real.
    """
    return {"message": "Sesión cerrada"}
