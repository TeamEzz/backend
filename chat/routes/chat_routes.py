from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database.db import get_db
from chat.openai_call import obtener_respuesta_ia
from chat.schemas.chat_schema import ConversacionSchema, MensajeSchema
from chat.utils.openai_utils import (
    listar_conversaciones_usuario,
    obtener_mensajes_conversacion,
)

load_dotenv()

router = APIRouter()

# ----- Esquemas de entrada/salida -----
class MensajeRequest(BaseModel):
    usuario_id: int
    mensaje: str
    conversacion_id: int | None = None  # None si es una nueva conversación

class MensajeResponse(BaseModel):
    respuesta: str
    conversacion_id: int


# ----- Endpoint principal -----
@router.post("/mensaje", response_model=MensajeResponse)
def enviar_mensaje(payload: MensajeRequest, db: Session = Depends(get_db)):
    """
    Recibe un mensaje del usuario, llama al modelo de OpenAI,
    guarda la conversación y devuelve la respuesta junto con el conversacion_id.
    """
    try:
        # Llamada a la lógica principal del chat (en openai_call.py)
        respuesta_ia, conversacion_id = obtener_respuesta_ia(
            user_message=payload.mensaje,
            db=db,
            usuario_id=payload.usuario_id,
            conversacion_id=payload.conversacion_id,
        )

        return MensajeResponse(respuesta=respuesta_ia, conversacion_id=conversacion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")


# ----- Endpoints de historial -----
class ConversacionResumen(BaseModel):
    id: int
    titulo: str | None = None
    fecha_creacion: str | None = None
    fecha_ultima_actualizacion: str | None = None


@router.get("/conversaciones", response_model=list[ConversacionResumen])
def listar_conversaciones(usuario_id: int, db: Session = Depends(get_db)):
    try:
        convs = listar_conversaciones_usuario(db, usuario_id)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando conversaciones: {str(e)}")


@router.get("/conversaciones/{conversacion_id}/mensajes", response_model=list[MensajeSchema])
def listar_mensajes(conversacion_id: int, db: Session = Depends(get_db)):
    try:
        mensajes = obtener_mensajes_conversacion(db, conversacion_id)
        # Conversión a esquema con orm_mode
        return [
            MensajeSchema(
                id=m.id,
                remitente=m.remitente,
                contenido=m.contenido,
                timestamp=m.timestamp,
            )
            for m in mensajes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando mensajes: {str(e)}")
