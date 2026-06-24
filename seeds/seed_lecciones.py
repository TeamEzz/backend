"""
seed_lecciones.py — Inserta o actualiza L2, L3 y L4 en la tabla `lecciones`.

Uso:
    DATABASE_URL=<tu_url> python seeds/seed_lecciones.py

Requiere DATABASE_URL en el entorno (igual que el backend en producción).
Hace UPSERT: si la lección ya existe se actualiza; si no, se crea.
"""

import json
import os
import sys
from pathlib import Path

# Permite importar database.config desde la raíz del backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from database.config import DATABASE_URL

SEEDS_DIR = Path(__file__).parent / "lecciones"
LECCION_IDS = [2, 3, 4]   # L1 permanece hardcodeado


def load_seed(leccion_id: int) -> dict:
    path = SEEDS_DIR / f"leccion_{leccion_id}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


UPSERT_SQL = text("""
    INSERT INTO lecciones
        (id, nivel, orden, titulo, descripcion, duracion_minutos,
         imagen_portada_key, activa, version, contenido)
    VALUES
        (:id, :nivel, :orden, :titulo, :descripcion, :duracion_minutos,
         :imagen_portada_key, :activa, :version, :contenido::jsonb)
    ON CONFLICT (id) DO UPDATE SET
        nivel              = EXCLUDED.nivel,
        orden              = EXCLUDED.orden,
        titulo             = EXCLUDED.titulo,
        descripcion        = EXCLUDED.descripcion,
        duracion_minutos   = EXCLUDED.duracion_minutos,
        imagen_portada_key = EXCLUDED.imagen_portada_key,
        activa             = EXCLUDED.activa,
        version            = EXCLUDED.version,
        contenido          = EXCLUDED.contenido,
        actualizado_en     = now()
""")


def main():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        for leccion_id in LECCION_IDS:
            data = load_seed(leccion_id)
            conn.execute(UPSERT_SQL, {
                "id":                data["id"],
                "nivel":             data["nivel"],
                "orden":             data["orden"],
                "titulo":            data["titulo"],
                "descripcion":       data.get("descripcion"),
                "duracion_minutos":  data.get("duracion_minutos"),
                "imagen_portada_key": data.get("imagen_portada_key"),
                "activa":            True,
                "version":           data.get("version", 1),
                "contenido":         json.dumps({"pasos": data["pasos"]}),
            })
            print(f"  ✓ leccion_{leccion_id} insertada/actualizada ({len(data['pasos'])} pasos)")

    print("\nSeed completo.")


if __name__ == "__main__":
    main()
