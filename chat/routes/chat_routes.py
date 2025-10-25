from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from chat.openai_call import obtener_respuesta_ia
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import get_db
from chat.openai_call import obtener_respuesta_ia

# carga las variables del .env
load_dotenv()

router = APIRouter()

class MensajeRequest(BaseModel):
    usuario_id: int
    mensaje: str
    conversacion_id: int | None = None

class MensajeResponse(BaseModel):
    respuesta: str
    conversacion_id: int


@router.post("/mensaje", response_model=MensajeResponse)
def enviar_mensaje(payload: MensajeRequest, db: Session = Depends(get_db)):
    """
    Recibe un mensaje del usuario, llama al modelo de OpenAI,
    guarda la conversación y devuelve la respuesta junto con el conversacion_id.
    """
    try:
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