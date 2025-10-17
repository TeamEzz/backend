from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.utils.jwt_utils import get_current_user
from database.db import get_db
from database.models.user_model import Usuario
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("static/perfiles")

@router.post("/usuario/foto")
def subir_foto_perfil(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Crear carpeta si no existe
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Validar extensión
    filename = archivo.filename or ""
    if "." not in filename:
        raise HTTPException(status_code=400, detail="Archivo sin extensión válida")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Formato no permitido")

    # Generar nombre único
    nombre_archivo = f"{uuid.uuid4()}.{extension}"
    ruta_completa = UPLOAD_DIR / nombre_archivo

    # Guardar archivo
    with open(ruta_completa, "wb") as f:
        f.write(archivo.file.read())

    # Actualizar en la base de datos
    foto_url = f"/static/perfiles/{nombre_archivo}"
    usuario.foto_perfil = foto_url
    db.commit()

    return {"mensaje": "Foto actualizada", "foto_perfil": foto_url}
