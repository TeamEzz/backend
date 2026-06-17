"""Instancia compartida de rate limiting (slowapi).

Se define aquí, fuera de `main.py`, para que tanto la app como los routers puedan
importar `limiter` sin crear un ciclo de imports (`main → router → main`).

Key por defecto: IP del cliente (`get_remote_address`). Las rutas autenticadas
(p. ej. chat) pasan un `key_func` propio que aísla el conteo por usuario.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
