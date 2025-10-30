# chat/openai_call.py
import os
from openai import OpenAI
from . import prompts
from chat.utils import openai_utils as utils


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurada")

client = OpenAI(api_key=OPENAI_API_KEY)

ROLE = prompts.system_message

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def obtener_respuesta_ia(user_message, db, usuario_id, conversacion_id=None):
    conversacion = utils.obtener_o_crear_conversacion(db, usuario_id, conversacion_id)
    # Si es nueva, sugiere título por el primer mensaje
    if not conversacion.titulo:
        titulo_sugerido = user_message.strip().replace("\n", " ")[:60]
        try:
            conversacion.titulo = titulo_sugerido or "Nueva conversación"
            db.commit()
            db.refresh(conversacion)
        except Exception:
            db.rollback()
    historial = utils.obtener_historial_conversacion(db, conversacion.id)
    if len(historial) == 0:
        historial.append({"role": "system", "content": ROLE})

    historial.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(model=MODEL, messages=historial)
        respuesta_texto = response.choices[0].message.content.strip()

        utils.guardar_mensajes(db, conversacion.id, user_message, respuesta_texto)

        return respuesta_texto, conversacion.id
    except Exception as e:
        # Propaga el error para que lo maneje el router y devuelva 500 controlado
        raise
    

def agregar_mensaje_IA(mensaje, historial: list):
    mensaje_agregar = {"role": "assistant", "content":mensaje}
    historial.append(mensaje_agregar)
    
def agregar_mensaje_usuario(mensaje,historial:list):
    mensaje_agregar = {"role": "user", "content":mensaje}
    historial.append(mensaje_agregar)
