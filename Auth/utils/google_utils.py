# Auth/utils/google_utils.py
import logging

from google.oauth2 import id_token
from google.auth.transport.requests import Request
from fastapi import HTTPException
from typing import Mapping, Any

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = "505493283813-5h7io4n2mp3t2rr6b9f0o27a573r1ase.apps.googleusercontent.com"

def verificar_token_google(token: str):
    try:
        # Verifica la firma y la audiencia (aud) con tu client_id
        idinfo: Mapping[str, Any] = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
        
        # Valida issuer (emisor)
        iss = idinfo.get("iss", "")
        if not (iss.endswith("accounts.google.com") or iss.endswith("https://accounts.google.com")):
            raise HTTPException(status_code=403, detail="Issuer del token no válido")

        # (Opcional) chequeo explícito de aud — verify_oauth2_token ya lo hace, pero es útil para logs claros
        if idinfo.get("aud") != GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=403, detail="La audiencia del token no coincide")

        # Devuelve los campos que necesitas
        return {
            "email": idinfo.get("email"),
            "nombre": idinfo.get("name"),  # en Google viene como 'name'
            "sub": idinfo.get("sub"),
        }

    except Exception:
        logger.exception("Error al verificar token de Google")
        raise HTTPException(status_code=403, detail="Token de Google inválido")

 


GOOGLE_CLIENT_ID = "505493283813-5h7io4n2mp3t2rr6b9f0o27a573r1ase.apps.googleusercontent.com"

def verificar_token_google(token: str):
    try:
        # Verifica el token contra el nuevo client_id
        idinfo = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)

        # Validar que el token venga de un emisor confiable
        if not idinfo.get("iss", "").endswith("accounts.google.com"):
            raise HTTPException(status_code=403, detail="Issuer del token no válido")

        return {
            "email": idinfo.get("email"),
            "nombre": idinfo.get("name")  # Asegúrate de que sea 'name' si así llega en el token
        }

    except Exception:
        logger.exception("Error al verificar token de Google")
        raise HTTPException(status_code=403, detail="Token de Google inválido")