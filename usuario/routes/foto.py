from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.utils.jwt_utils import get_current_user
from database.config import get_db
from database.models.user_model import Usuario
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "static/perfiles"

@router.post("/usuario/foto")
def subir_foto_perfil(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Crear carpeta si no existe
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # Validar extensión
    extension = archivo.filename.split(".")[-1]
    if extension.lower() not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Formato no permitido")

    # Generar nombre único
    nombre_archivo = f"{uuid.uuid4()}.{extension}"
    ruta_completa = os.path.join(UPLOAD_DIR, nombre_archivo)

    # Guardar archivo
    with open(ruta_completa, "wb") as f:
        f.write(archivo.file.read())

    # Actualizar en la base de datos
    usuario.foto_perfil = f"static/perfiles/{nombre_archivo}"
    db.commit()

    return {"mensaje": "Foto actualizada", "foto_perfil": usuario.foto_perfil}