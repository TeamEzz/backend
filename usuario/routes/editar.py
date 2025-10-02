from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import get_db
from database.models.user_model import Usuario
from Auth.utils.jwt_utils import get_current_user
from usuario.schemas.schemas_editar import NombreUpdate, UsernameUpdate, EmailUpdate

router = APIRouter()

@router.post("/auth/nombre")
def actualizar_nombre(
    payload: NombreUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    usuario.nombre = payload.nombre
    db.commit()
    return {"mensaje": "Nombre actualizado correctamente"}


@router.post("/auth/username")
def actualizar_username(
    payload: UsernameUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Verifica si el username ya existe
    existente = db.query(Usuario).filter(Usuario.nombre_usuario == payload.nombre_usuario).first()
    if existente and existente.id != usuario.id:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")

    usuario.nombre_usuario = payload.nombre_usuario
    db.commit()
    return {"mensaje": "Nombre de usuario actualizado correctamente"}


@router.post("/auth/email")
def actualizar_email(
    payload: EmailUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Verifica si el email ya existe
    existente = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if existente and existente.id != usuario.id:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    usuario.email = payload.email
    db.commit()
    return {"mensaje": "Correo actualizado correctamente"}