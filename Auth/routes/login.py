from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.schemas.schemas import UsuarioLogin, UsuarioLoginResponse
from database.db import get_db
from database.models.user_model import Usuario
from Auth.utils.password_utils import verify_password
from Auth.utils.jwt_utils import crear_token
from database.models.encuesta_model import RespuestaEncuestaDB  # 👈 Asegúrate que esto es correcto

router = APIRouter()

@router.post("/login", response_model=UsuarioLoginResponse)
def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if not db_usuario or not verify_password(usuario.password, db_usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = crear_token({"sub": db_usuario.email, "id": db_usuario.id})

    # 👇 Comprobar si respondió la encuesta
    respuesta = db.query(RespuestaEncuestaDB).filter(RespuestaEncuestaDB.usuario_id == db_usuario.id).first()
    encuesta_completada = respuesta is not None

    return UsuarioLoginResponse(
        id=db_usuario.id,
        email=db_usuario.email,
        nombre=db_usuario.nombre,
        usuario=db_usuario.nombre_usuario,
        token=token,
        encuesta_completada=encuesta_completada,
    )
