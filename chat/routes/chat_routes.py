import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from jose import jwt, JWTError
from slowapi.util import get_remote_address

from Auth.utils.jwt_utils import get_current_user, SECRET_KEY, ALGORITHM
from database.db import get_db
from database.models.user_model import Usuario
from chat.models.chat_model import Conversacion
from chat.openai_call import obtener_respuesta_ia
from chat.schemas.chat_schema import MensajeSchema
from chat.utils.openai_utils import (
    listar_conversaciones_usuario,
    obtener_mensajes_conversacion,
)
from limiter import limiter

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()


def _key_por_usuario(request: Request) -> str:
    """Key del rate limiter por usuario autenticado (no por IP).

    Extrae el `id` del JWT del header Authorization. El conteo del límite diario
    queda aislado por usuario. Fallback a la IP si no hay token válido (defensa en
    profundidad; en la práctica Depends(get_current_user) ya rechaza con 401 antes).

    FUTURO (es_pro): cuando exista usuario.es_pro, reemplazar el "15/day" estático del
    decorador por un límite dinámico que inspeccione el tier del usuario — el
    aislamiento por id de esta key_func ya queda listo para soportarlo.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            uid = payload.get("id")
            if uid is not None:
                return f"user:{uid}"
        except JWTError:
            pass
    return get_remote_address(request)


# ----- Esquemas de entrada/salida -----
class MensajeRequest(BaseModel):
    usuario_id: int | None = None
    mensaje: str = Field(max_length=1000)
    conversacion_id: int | None = None  # None si es una nueva conversación

class MensajeResponse(BaseModel):
    respuesta: str
    conversacion_id: int


# ----- Endpoint principal -----
@router.post("/mensaje", response_model=MensajeResponse)
@limiter.limit("15/day", key_func=_key_por_usuario)  # 15 mensajes/día por usuario autenticado
async def enviar_mensaje(
    request: Request,
    payload: MensajeRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """
    Recibe un mensaje del usuario, llama al modelo de OpenAI,
    guarda la conversación y devuelve la respuesta junto con el conversacion_id.
    """
    try:
        if payload.usuario_id not in (None, 0) and payload.usuario_id != usuario_actual.id:
            raise HTTPException(status_code=403, detail="usuario_id no coincide con el token")
        if payload.conversacion_id is not None:
            conv = (
                db.query(Conversacion)
                .filter_by(id=payload.conversacion_id, usuario_id=usuario_actual.id)
                .first()
            )
            if not conv:
                raise HTTPException(status_code=404, detail="Conversación no encontrada")
        # Llamada a la lógica principal del chat (en openai_call.py)
        respuesta_ia, conversacion_id = await obtener_respuesta_ia(
            user_message=payload.mensaje,
            db=db,
            usuario_id=usuario_actual.id,
            conversacion_id=payload.conversacion_id,
        )

        return MensajeResponse(respuesta=respuesta_ia, conversacion_id=conversacion_id)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error procesando chat")
        raise HTTPException(status_code=500, detail="Error interno")


# ----- Endpoints de historial -----
class ConversacionResumen(BaseModel):
    id: int
    titulo: str | None = None
    fecha_creacion: str | None = None
    fecha_ultima_actualizacion: str | None = None


@router.get("/conversaciones", response_model=list[ConversacionResumen])
def listar_conversaciones(
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    try:
        if usuario_id not in (None, 0) and usuario_id != usuario_actual.id:
            raise HTTPException(status_code=403, detail="usuario_id no coincide con el token")
        convs = listar_conversaciones_usuario(db, usuario_actual.id)
        return [
            ConversacionResumen(
                id=c.id,
                titulo=c.titulo,
                fecha_creacion=c.fecha_creacion.isoformat() if c.fecha_creacion else None,
                fecha_ultima_actualizacion=(
                    c.fecha_ultima_actualizacion.isoformat() if c.fecha_ultima_actualizacion else None
                ),
            )
            for c in convs
        ]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error listando conversaciones")
        raise HTTPException(status_code=500, detail="Error interno")


@router.get("/conversaciones/{conversacion_id}/mensajes", response_model=list[MensajeSchema])
def listar_mensajes(
    conversacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    try:
        conv = (
            db.query(Conversacion)
            .filter_by(id=conversacion_id, usuario_id=usuario_actual.id)
            .first()
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        mensajes = obtener_mensajes_conversacion(db, conversacion_id)
        # Conversión a esquema desde objetos SQLAlchemy
        return [
            MensajeSchema(
                id=m.id,
                remitente=m.remitente,
                contenido=m.contenido,
                timestamp=m.timestamp,
            )
            for m in mensajes
        ]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error listando mensajes")
        raise HTTPException(status_code=500, detail="Error interno")
