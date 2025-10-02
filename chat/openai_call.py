import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from . import prompts
import requests as r

URL = "https://api.openai.com"

load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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