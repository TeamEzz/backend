# chat/openai_call.py
import os
from openai import OpenAI
from . import prompts
from chat.utils import openai_utils as utils


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurada")

client = OpenAI(api_key=OPENAI_API_KEY)

role = prompts.system_message

MODEL = "gpt-5"

def obtener_respuesta_ia(user_message, db, usuario_id, conversacion_id=None):
    conversacion = utils.obtener_o_crear_conversacion(db, usuario_id,conversacion_id)
    historial = utils.obtener_historial_conversacion(db, conversacion.id)# que le pongo en db session
    if len(historial) == 0:
        historial.append({"role": "system", "content": role})
    
    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=historial
        )
        respuesta_texto = response.choices[0].message.content.strip()

        utils.guardar_mensajes(db, conversacion.id, user_message, respuesta_texto)
        
        return respuesta_texto

    except Exception as e:
        return f"Error, algo no salio bien: {str(e)}"
    

def agregar_mensaje_IA(mensaje, historial: list):
    mensaje_agregar = {"role": "assistant", "content":mensaje}
    historial.append(mensaje_agregar)
    
def agregar_mensaje_usuario(mensaje,historial:list):
    mensaje_agregar = {"role": "user", "content":mensaje}
    historial.append(mensaje_agregar)
