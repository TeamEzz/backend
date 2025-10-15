# database/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Puedes seguir importando desde tu config si lo prefieres
# from database.config import DATABASE_URL as RAW_DATABASE_URL
RAW_DATABASE_URL = os.getenv("DATABASE_URL", "")

if not RAW_DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definido")

# Normaliza a dialecto SQLAlchemy + psycopg3
# Render a veces entrega 'postgres://', SQLAlchemy espera 'postgresql+psycopg://'
url = RAW_DATABASE_URL
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+psycopg://", 1)
elif url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)

# connect_args según motor
connect_args = {}
if url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif url.startswith("postgresql+psycopg"):
    # Render suele incluir ?sslmode=require en la cadena. Si no, forzamos SSL.
    if "sslmode=" not in url:
        connect_args = {"sslmode": "require"}

# Crea engine con settings seguros para entornos que “duermen”
engine = create_engine(
    url,
    connect_args=connect_args,
    pool_pre_ping=True,   # detecta conexiones muertas
    pool_recycle=1800,    # recicla conexiones (30 min)
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()