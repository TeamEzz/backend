from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from Auth.utils.jwt_utils import get_current_user
from database.db import get_db
from database.models.user_model import Usuario
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("static/perfiles")

MAX_FOTO_BYTES = 5 * 1024 * 1024  # 5 MB
CONTENT_TYPES_PERMITIDOS = {"image/jpeg", "image/png"}
# Firmas (magic bytes) de imagen real, independientes de la extensión declarada.
MAGIC_JPEG = b"\xff\xd8\xff"
MAGIC_PNG = b"\x89PNG\r\n\x1a\n"

@router.post("/usuario/foto")
def subir_foto_perfil(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Crear carpeta si no existe
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Rechazar archivos grandes ANTES de leerlos a memoria (si el cliente reporta tamaño).
    if archivo.size is not None and archivo.size > MAX_FOTO_BYTES:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")

    # Validar extensión
    filename = archivo.filename or ""
    if "." not in filename:
        raise HTTPException(status_code=400, detail="Archivo sin extensión válida")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Formato no permitido")

    # Validar content-type declarado.
    if archivo.content_type not in CONTENT_TYPES_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Tipo de contenido no permitido")

    # Validar magic bytes: confirma que el contenido es realmente JPEG/PNG.
    # Se ejecuta siempre, sea cual sea el valor de archivo.size (incluido None).
    header = archivo.file.read(8)
    archivo.file.seek(0)
    if not (header.startswith(MAGIC_JPEG) or header.startswith(MAGIC_PNG)):
        raise HTTPException(status_code=400, detail="Archivo no es una imagen válida")

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
