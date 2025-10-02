from fastapi import APIRouter
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from chat.openai_call import obtener_respuesta_ia

# carga las variables del .env
load_dotenv()

router = APIRouter()

class MensajeRequest(BaseModel):
    mensaje: str

class MensajeResponse(BaseModel):
    respuesta: str

@router.post("/", response_model=MensajeResponse)
def chat(mensaje: MensajeRequest):
    print(f"📥 Usuario: {mensaje.mensaje}")
    respuesta_ia = obtener_respuesta_ia(mensaje.mensaje)
    print(f"🤖 IA: {respuesta_ia}")
    return MensajeResponse(respuesta=respuesta_ia)