from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException

GOOGLE_CLIENT_ID = "505493283813-5h7io4n2mp3t2rr6b9f0o27a573r1ase.apps.googleusercontent.com"

def verificar_token_google(token: str):
    try:
        # Verifica el token contra el nuevo client_id
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Validar que el token venga de un emisor confiable
        if not idinfo.get("iss", "").endswith("accounts.google.com"):
            raise HTTPException(status_code=403, detail="Issuer del token no válido")

        print("✅ Token verificado correctamente")
        print("📩 Payload decodificado:", idinfo)

        return {
            "email": idinfo.get("email"),
            "nombre": idinfo.get("name")  # Asegúrate de que sea 'name' si así llega en el token
        }

    except Exception as e:
        print("❌ Error al verificar token:", str(e))
        raise HTTPException(status_code=403, detail=f"Token de Google inválido: {str(e)}")