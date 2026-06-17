# Auth/utils/jwt_utils.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from database.db import get_db
from database.models.user_model import Usuario
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está configurada en el entorno")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080 

def crear_token(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT con exp en UTC."""
    to_encode = datos.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str) -> dict:
    """Decodifica y valida el JWT. Lanza excepciones específicas si expira o es inválido."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        # exp vencida
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError as e:
        # firma inválida / token mal formado
        logger.error("Error al verificar token: %s", e)
        raise HTTPException(status_code=401, detail="Token inválido")

def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> Usuario:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Encabezado inválido. Usa 'Bearer <token>'")

    token = authorization.split(" ", 1)[1]
    datos = verificar_token(token)  # puede lanzar 401

    if "sub" not in datos or "id" not in datos:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = datos["id"]
    user_email = datos["sub"]

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.email != user_email:
        logger.info(
            "El email almacenado (%s***) no coincide con el presente en el token (%s***)",
            user.email[:3],
            user_email[:3],
        )

    return user
