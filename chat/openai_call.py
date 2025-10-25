# chat/openai_call.py
import os
from openai import OpenAI
from . import prompts

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurada")

client = OpenAI(api_key=OPENAI_API_KEY)

role = prompts.system_message

MODEL = "gpt-5"

history = []
history.append({"role": "system", "content": role})

def obtener_respuesta_ia(user_message):
    
    try:
        agregar_mensaje_usuario(user_message)
        response = client.chat.completions.create(
            model=MODEL,
            messages=history
        )
        agregar_mensaje_IA(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error, algo no salio bien: {str(e)}"

def agregar_mensaje_IA(mensaje:dict):
    mensaje_agregar = {"role": "assistant", "content":mensaje}
    history.append(mensaje_agregar)
    
def agregar_mensaje_usuario(mensaje:dict):
    mensaje_agregar = {"role": "user", "content":mensaje}
    history.append(mensaje_agregar)

def obtener_respuesta_ia(mensaje_usuario: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": mensaje_usuario}
        ]
    )
    return response.choices[0].message.content.strip()