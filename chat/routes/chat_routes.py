from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database.db import get_db
from chat.openai_call import obtener_respuesta_ia

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
            conversacion_id=payload.conversacion_id
        )

        return MensajeResponse(
            respuesta=respuesta_ia,
            conversacion_id=conversacion_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")