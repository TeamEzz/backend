from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from Auth.schemas.schemas import (
    RecuperacionRequest,
    VerificarRecuperacionRequest,
    UsuarioConToken,
)
from Auth.utils.password_utils import hash_password, verify_password
from Auth.utils.jwt_utils import crear_token
from Auth.utils.email_utils import (
    generar_codigo,
    expiracion_codigo,
    enviar_codigo,
    CODIGO_MAX_INTENTOS,
    REENVIO_COOLDOWN_SEGUNDOS,
)
from database.models.user_model import Usuario
from database.db import get_db
from limiter import limiter

router = APIRouter()


def _as_utc(dt: datetime) -> datetime:
    """Normaliza a UTC consciente de zona (algunos backends devuelven naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.post("/solicitar-recuperacion")
@limiter.limit("5/15minutes")  # anti-abuso por IP
async def solicitar_recuperacion(request: Request, datos: RecuperacionRequest, db: Session = Depends(get_db)):
    mensaje_generico = {
        "mensaje": "Si la cuenta existe, te enviamos un código para restablecer tu contraseña."
    }

    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    # Solo cuentas locales verificadas. No revelamos existencia/proveedor (anti-enumeración).
    if not usuario or not usuario.verificado or usuario.proveedor == "google":
        return mensaje_generico

    # Cooldown entre envíos (mismo que verificación).
    if usuario.codigo_enviado_en:
        transcurrido = (datetime.now(timezone.utc) - _as_utc(usuario.codigo_enviado_en)).total_seconds()
        if transcurrido < REENVIO_COOLDOWN_SEGUNDOS:
            espera = int(REENVIO_COOLDOWN_SEGUNDOS - transcurrido)
            raise HTTPException(status_code=429, detail=f"Espera {espera}s antes de pedir otro código")

    codigo = generar_codigo()
    usuario.codigo_verificacion = hash_password(codigo)
    usuario.codigo_expira_en = expiracion_codigo()
    usuario.codigo_enviado_en = datetime.now(timezone.utc)
    usuario.codigo_intentos = 0
    db.commit()

    try:
        await enviar_codigo(usuario.email, codigo, tipo="recuperacion")
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo enviar el correo de recuperación: {exc}")

    return mensaje_generico


@router.post("/verificar-recuperacion", response_model=UsuarioConToken)
@limiter.limit("10/15minutes")  # límite por IP (además del throttle interno por intentos)
def verificar_recuperacion(request: Request, datos: VerificarRecuperacionRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.codigo_verificacion or not usuario.codigo_expira_en:
        raise HTTPException(status_code=400, detail="No hay un código pendiente. Solicita uno nuevo.")

    if usuario.codigo_intentos >= CODIGO_MAX_INTENTOS:
        raise HTTPException(status_code=400, detail="demasiados intentos")

    if datetime.now(timezone.utc) > _as_utc(usuario.codigo_expira_en):
        raise HTTPException(status_code=400, detail="código expirado")

    if not verify_password(datos.codigo, usuario.codigo_verificacion):
        usuario.codigo_intentos += 1
        db.commit()
        raise HTTPException(status_code=400, detail="código incorrecto")

    # Éxito: actualiza la contraseña, limpia el código y emite la sesión.
    usuario.hashed_password = hash_password(datos.nueva_contrasena)
    usuario.codigo_verificacion = None
    usuario.codigo_expira_en = None
    usuario.codigo_enviado_en = None
    usuario.codigo_intentos = 0
    db.commit()
    db.refresh(usuario)

    token = crear_token({"sub": usuario.email, "id": usuario.id})
    return UsuarioConToken(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        token=token,
    )
