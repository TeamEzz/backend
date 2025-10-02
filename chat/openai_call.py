import requests as r
from openai import OpenAI
from database.config import OPENAI_API_KEY
from . import prompts

URL = "https://api.openai.com"

client = OpenAI(api_key=OPENAI_API_KEY)

system_message = prompts.system_message

def obtener_respuesta_ia(mensaje_usuario: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": mensaje_usuario}
        ]
    )
    return response.choices[0].message.content.strip()