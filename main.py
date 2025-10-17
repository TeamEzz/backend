from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from Auth.routes import registro, login, login_google, protegida, nombre
from encuesta.routes import encuesta_routes
from usuario.routes import perfil as perfil_routes
from usuario.routes import editar as editar_routes
from usuario.routes import foto as foto_routes
from chat.routes import chat_routes
from Gastos.routes import gasto
from Gastos.dashboard.routes import resumen_routes as dashboard_routes
from lecciones.routes import progreso_routes

from database.db import engine, Base


app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}


@app.head("/")
def root_head() -> Response:
    return Response(status_code=200)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# CORS (ajusta allow_origins a tus dominios si quieres más seguridad)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # p.ej. ["https://tu-dominio.app", "exp://..."]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(registro.router,      prefix="/auth",     tags=["Auth"])
app.include_router(login.router,         prefix="/auth",     tags=["Auth"])
app.include_router(login_google.router,  prefix="/auth",     tags=["Auth"])
app.include_router(protegida.router,     prefix="/auth",     tags=["Auth"])
app.include_router(nombre.router,        prefix="/auth",     tags=["Auth"])

app.include_router(encuesta_routes.router)                           # ya tiene prefix="/encuesta" adentro
app.include_router(perfil_routes.router, prefix="/usuario", tags=["Usuario"])
app.include_router(editar_routes.router)
app.include_router(foto_routes.router)

app.include_router(chat_routes.router,   prefix="/chat",     tags=["Chat"])
app.include_router(gasto.router,         prefix="/gasto",    tags=["Gastos"])
app.include_router(dashboard_routes.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(progreso_routes.router, prefix="/lecciones", tags=["Lecciones"])

