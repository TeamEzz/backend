# migrations/env.py
from __future__ import annotations
import os, sys, pathlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Alembic config ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Añadir el root del proyecto al sys.path ---
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]  # carpeta "backend"
sys.path.append(str(BASE_DIR))

# Importa Base y (MUY IMPORTANTE) registra los modelos para autogenerate
from database.db import Base  # contiene Base = declarative_base()
# importa módulos que definen tablas (no hace falta usarlos, solo importarlos)
from database.models import user_model, encuesta_model  # añade aquí los demás: gasto_model, leccion_model, etc.

target_metadata = Base.metadata

# --- URL desde el entorno ---
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definido")

# Normaliza driver y SSL por si acaso
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
if "sslmode=" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

# Coloca la URL dentro de la config de Alembic
config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_offline() -> None:
    """Modo offline: genera SQL sin conectar."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Modo online: se conecta y aplica/inspecciona."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()