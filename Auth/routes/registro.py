from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.schemas.schemas import UsuarioRegistroSimple, RegistroPendienteResponse
from Auth.utils.password_utils import hash_password
from Auth.utils.email_utils import (
    generar_codigo,
    expiracion_codigo,
    enviar_codigo_verificacion,
)
from database.models.user_model import Usuario
from database.db import get_db

router = APIRouter()


@router.post("/registro", response_model=RegistroPendienteResponse, status_code=201)
def registrar_usuario(usuario: UsuarioRegistroSimple, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    # Genera y envía el código ANTES de persistir el token: el usuario queda sin verificar
    # y no recibe sesión hasta confirmar el código (block-until-verified).
    codigo = generar_codigo()

    nuevo_usuario = Usuario(
        nombre=None,  # Se asigna luego
        email=usuario.email,
        hashed_password=hash_password(usuario.password),
        proveedor="correo",
        verificado=False,
        codigo_verificacion=hash_password(codigo),
        codigo_expira_en=expiracion_codigo(),
        codigo_enviado_en=datetime.now(timezone.utc),  # marca de envío para el cooldown
        codigo_intentos=0,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    try:
        enviar_codigo_verificacion(nuevo_usuario.email, codigo)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo enviar el correo de verificación: {exc}")

    return RegistroPendienteResponse(
        email=nuevo_usuario.email,
        requiere_verificacion=True,
        mensaje="Te enviamos un código de 6 dígitos a tu correo para verificar tu cuenta.",
    )
