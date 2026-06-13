"""Envío de correos transaccionales para la verificación de cuenta.

Usa la API HTTP de Resend mediante la dependencia `requests` ya presente en el proyecto
(no requiere paquetes adicionales). Para cambiar de proveedor (SendGrid, Postmark, …) basta
con reescribir `enviar_codigo`.

Variables de entorno requeridas:
    RESEND_API_KEY   API key de Resend.
    EMAIL_FROM       Remitente verificado, p.ej. "onboarding@ezapp.tech".
"""
import os
import secrets
from datetime import datetime, timedelta, timezone

import requests

# --- Parámetros del código de verificación ---
CODIGO_EXPIRA_MINUTOS = 10      # vigencia del código
CODIGO_MAX_INTENTOS = 5         # intentos fallidos permitidos antes de bloquear
REENVIO_COOLDOWN_SEGUNDOS = 60  # tiempo mínimo entre reenvíos

RESEND_API_URL = "https://api.resend.com/emails"


def generar_codigo() -> str:
    """Devuelve un código numérico de 6 dígitos (100000–999999)."""
    return str(secrets.randbelow(900000) + 100000)


def expiracion_codigo() -> datetime:
    """Instante de expiración para un código recién generado (UTC)."""
    return datetime.now(timezone.utc) + timedelta(minutes=CODIGO_EXPIRA_MINUTOS)


def _cuerpo_html(codigo: str) -> str:
    return (
        f"<div style=\"font-family:-apple-system,Segoe UI,Roboto,sans-serif;\">"
        f"<h2>Verifica tu cuenta de EZ</h2>"
        f"<p>Tu código de verificación es:</p>"
        f"<p style=\"font-size:32px;font-weight:800;letter-spacing:6px;\">{codigo}</p>"
        f"<p>Caduca en {CODIGO_EXPIRA_MINUTOS} minutos. Si no creaste esta cuenta, ignora este correo.</p>"
        f"</div>"
    )


def _cuerpo_recuperacion(codigo: str) -> str:
    return (
        f"<div style=\"font-family:-apple-system,Segoe UI,Roboto,sans-serif;\">"
        f"<h2>Recupera tu contraseña de EZ</h2>"
        f"<p>Recibimos una solicitud para restablecer tu contraseña. Tu código es:</p>"
        f"<p style=\"font-size:32px;font-weight:800;letter-spacing:6px;\">{codigo}</p>"
        f"<p>Caduca en {CODIGO_EXPIRA_MINUTOS} minutos. Si no solicitaste esto, ignora este correo.</p>"
        f"</div>"
    )


def enviar_codigo(email: str, codigo: str, tipo: str) -> None:
    """Envía un código de 6 dígitos al correo indicado.

    `tipo` selecciona el asunto y el cuerpo:
        "verificacion" → verificación de cuenta (registro).
        "recuperacion" → restablecimiento de contraseña.

    Lanza RuntimeError si falta configuración o si el proveedor responde con error,
    para que la ruta que llama pueda devolver un 502 limpio.
    """
    api_key = os.getenv("RESEND_API_KEY")
    remitente = os.getenv("EMAIL_FROM")
    if not api_key or not remitente:
        raise RuntimeError("Faltan RESEND_API_KEY o EMAIL_FROM en el entorno")

    if tipo == "recuperacion":
        subject = "Recupera tu contraseña de EZ"
        html = _cuerpo_recuperacion(codigo)
    else:
        subject = "Tu código de verificación de EZ"
        html = _cuerpo_html(codigo)

    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": remitente,
                "to": [email],
                "subject": subject,
                "html": html,
            },
            timeout=10,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"No se pudo contactar al proveedor de correo: {exc}") from exc

    if resp.status_code >= 400:
        raise RuntimeError(f"El proveedor de correo respondió {resp.status_code}: {resp.text}")
