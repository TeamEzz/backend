from fastapi import APIRouter, HTTPException, Depends
from Auth.utils.google_utils import verificar_token_google
from Auth.utils.jwt_utils import crear_token  # ✅ Importar la función para generar el token
from database.models.user_model import Usuario
from database.db import get_db
from sqlalchemy.orm import Session
from Auth.schemas.schemas import TokenGoogle, UsuarioLoginResponse
from database.models.encuesta_model import RespuestaEncuestaDB

router = APIRouter()

@router.post("/login-google", response_model=UsuarioLoginResponse)
def login_google(data: TokenGoogle, db: Session = Depends(get_db)):
    payload = verificar_token_google(data.token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token de Google inválido")

    email = payload.get("email")
    nombre = payload.get("nombre")  

    if not email:
        raise HTTPException(status_code=422, detail="No se pudo obtener el email del token.")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        usuario = Usuario(
            nombre=nombre,
            email=email,
            hashed_password="",  # No hay contraseña
            proveedor="google"
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    # ✅ Consultar si ya completó la encuesta
    ya_tiene_encuesta = db.query(RespuestaEncuestaDB).filter_by(usuario_id=usuario.id).first() is not None

    # ✅ Crear token JWT como en el login tradicional
    token = crear_token({"sub": email, "id": usuario.id})

    return UsuarioLoginResponse(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        usuario=usuario.nombre_usuario,
        token=token,
        encuesta_completada=ya_tiene_encuesta,
    )
