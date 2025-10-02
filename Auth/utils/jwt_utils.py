# backend/Auth/utils/jwt_utils.py

from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database.db import get_db
from database.models.user_model import Usuario
import os

# Clave secreta para firmar el token (debería venir del .env)
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_super_segura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Crear el token JWT
def crear_token(datos: dict):
    to_encode = datos.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Verificar el token y retornar los datos si es válido
def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print("❌ Error al verificar token:", e)
        return None

# Dependencia para proteger rutas y obtener el usuario actual
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> Usuario:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Encabezado inválido. Usa 'Bearer <token>'")

    token = authorization.split(" ")[1]
    datos = verificar_token(token)

    if datos is None or "sub" not in datos or "id" not in datos:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user_id = datos["id"]
    user_email = datos["sub"]
    print("🧾 ID del token:", user_id)
    print("📧 Email del token:", user_email)

    user = db.query(Usuario).filter(Usuario.id == user_id, Usuario.email == user_email).first()

    if user is None:
        print("❌ Usuario no encontrado en base de datos")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    print("✅ Usuario autenticado:", user)
    return user
