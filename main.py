import logging
import os

import sentry_sdk
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from slowapi.errors import RateLimitExceeded

from limiter import limiter

from Auth.routes import registro, login, login_google, protegida, nombre, verificar, recuperacion, cuenta
from encuesta.routes import encuesta_routes
from usuario.routes import perfil as perfil_routes
from usuario.routes import editar as editar_routes
from usuario.routes import foto as foto_routes
from chat.routes import chat_routes
from Gastos.routes import gasto
from Gastos.dashboard.routes import resumen_routes as dashboard_routes
from lecciones.routes import progreso_routes
from lecciones.routes import contenido_routes
from metas.routes import metas_routes
from tracker.routes import tracker_routes

from sqlalchemy import text

from database.db import engine, Base, SessionLocal


# Logging estructurado en JSON (una línea por evento) para ingestión/búsqueda en producción.
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

logger = logging.getLogger("ezapp")

# Error tracking (Sentry). DSN vacío → desactivado silenciosamente (no rompe arranque local).
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development"),
    send_default_pii=False,
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
docs_url = None if ENVIRONMENT == "production" else "/docs"
redoc_url = None if ENVIRONMENT == "production" else "/redoc"
openapi_url = None if ENVIRONMENT == "production" else "/openapi.json"
app = FastAPI(docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url)

# Rate limiting (slowapi): la instancia vive en limiter.py para evitar imports circulares.
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    # Handler único: mensaje custom para el límite diario de chat; genérico para el resto.
    # Debe registrarse explícitamente o el handler de Exception devolvería 500 en vez de 429.
    if request.url.path.endswith("/chat/mensaje"):
        detail = "Alcanzaste tu límite de mensajes por hoy. Vuelve mañana o actualiza a EZ Pro."
    else:
        detail = "Demasiadas solicitudes. Intenta más tarde."
    return JSONResponse(status_code=429, content={"detail": detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # El handler intercepta la excepción; sin esto la integración automática de Sentry no la vería.
    sentry_sdk.capture_exception(exc)
    logger.exception("Error no manejado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "perfiles").mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"status": "ok"}


@app.head("/")
def root_head() -> Response:
    return Response(status_code=200)


@app.get("/healthz")
def healthz():
    # Sesión independiente (no Depends(get_db)) para no interferir con el pool de requests.
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        logger.exception("Health check: la DB no respondió")
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "db": "error", "detail": "Database unavailable"},
        )
    finally:
        db.close()


# CORS restringido a los dominios de producción.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ezapp.tech", "https://www.ezapp.tech"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routers
app.include_router(registro.router,      prefix="/auth",     tags=["Auth"])
app.include_router(verificar.router,     prefix="/auth",     tags=["Auth"])
app.include_router(recuperacion.router,  prefix="/auth",     tags=["Auth"])
app.include_router(login.router,         prefix="/auth",     tags=["Auth"])
app.include_router(login_google.router,  prefix="/auth",     tags=["Auth"])
app.include_router(protegida.router,     prefix="/auth",     tags=["Auth"])
app.include_router(nombre.router,        prefix="/auth",     tags=["Auth"])
app.include_router(cuenta.router,        prefix="/auth",     tags=["Auth"])

app.include_router(encuesta_routes.router)                           # ya tiene prefix="/encuesta" adentro
app.include_router(perfil_routes.router, prefix="/usuario", tags=["Usuario"])
app.include_router(editar_routes.router)
app.include_router(foto_routes.router)

app.include_router(chat_routes.router,   prefix="/chat",     tags=["Chat"])
app.include_router(gasto.router,         prefix="/gasto",    tags=["Gastos"])
app.include_router(dashboard_routes.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(progreso_routes.router, prefix="/lecciones", tags=["Lecciones"])
app.include_router(contenido_routes.router, prefix="/lecciones", tags=["Lecciones"])
app.include_router(metas_routes.router,  prefix="/metas",     tags=["Metas"])
app.include_router(tracker_routes.router, prefix="/tracker",   tags=["Tracker"])
