from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.schemas.schemas import UsuarioRegistroSimple, UsuarioConToken
from Auth.utils.password_utils import hash_password
from Auth.utils.jwt_utils import crear_token
from database.models.user_model import Usuario
from database.db import get_db

router = APIRouter()

@router.post("/registro", response_model=UsuarioConToken)
def registrar_usuario(usuario: UsuarioRegistroSimple, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    
    hashed_password = hash_password(usuario.password)

    nuevo_usuario = Usuario(
        nombre=None,  # Se asigna luego
        email=usuario.email,
        hashed_password=hashed_password,
        proveedor="correo"
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    token = crear_token({"sub": nuevo_usuario.email, "id": nuevo_usuario.id})
    
    print("UsuarioConToken ->", {
    "id": nuevo_usuario.id,
    "nombre": nuevo_usuario.nombre,
    "email": nuevo_usuario.email,
    "token": token
})

    return UsuarioConToken(
        id=nuevo_usuario.id,
        nombre=nuevo_usuario.nombre,
        email=nuevo_usuario.email,
        token=token
    )
