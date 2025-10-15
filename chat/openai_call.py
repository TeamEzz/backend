# chat/openai_call.py
import os
from openai import OpenAI
from . import prompts

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurada")

client = OpenAI(api_key=OPENAI_API_KEY)

system_message = prompts.system_message

def obtener_respuesta_ia(mensaje_usuario: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": mensaje_usuario},
        ],
    )
    return (resp.choices[0].message.content or "").strip()