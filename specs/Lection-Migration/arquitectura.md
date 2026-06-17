# Informe de Arquitectura: Migración Server-Driven Content

**Fecha:** 2026-06-15
**Stack:** FastAPI + SQLAlchemy + Alembic + PostgreSQL (Supabase) + SwiftUI
**Alcance:** Solo Nivel 0 (4 lecciones, 10 tipos de interacción)
**Nivel 1:** Descartado — eliminado en Step Zero

## Resumen Ejecutivo

Las lecciones de Nivel 0 migran de código Swift hardcodeado a una columna JSONB en Supabase. El frontend actúa como motor de plantillas que sabe renderizar 10 tipos de interacción genéricos. El backend sirve el JSON de contenido por lesson_id. Los assets (imágenes) permanecen en el bundle de la app en esta fase.

## Decisión: Supabase JSONB (MongoDB descartado)

Ya usamos PostgreSQL en Supabase. JSONB es nativo, Alembic ya funciona con 6 migrations aplicadas, y mantiene transacciones ACID entre contenido y progreso de usuario en el mismo DB.

## Los 10 Tipos de Interacción de Nivel 0

| # | Tipo | Vista Swift origen |
|---|---|---|
| 1 | explanation | SlideExplicacion1/2.swift |
| 2 | image_carousel | SlideIntroduccion.swift |
| 3 | drag_drop | SlideMinijuego2.swift |
| 4 | card_classification | Minijuego1_0.2.swift |
| 5 | grid_classification | Minijuego2_0.2.swift |
| 6 | icon_grid_selection | Minijuego1_0.3.swift |
| 7 | memory_match | Minijuego2_03.swift |
| 8 | multiple_choice | PreguntaTriviaView.swift |
| 9 | motivational_choice | PreguntaMotivacionalSlide.swift |
| 10 | achievement | SlideLogro.swift |

## Schema JSON — Fase 0

### Raíz
```json
{
  "id": 1, "nivel": 0, "orden": 1, "titulo": "...", "descripcion": "...",
  "duracion_minutos": 8, "imagen_portada_key": "...", "version": 1,
  "pasos": [{"paso_id": 1, "tipo": "explanation", "contenido": {...}}]
}
```

### Por tipo

**explanation**: texto_principal (str), subtitulo (str|null), imagen_key (str|null), texto_boton (str)

**image_carousel**: items [{imagen_key (str), caption (str|null)}]

**drag_drop**: instruccion (str), items [{id, label, imagen_key}], targets [{id, label, accepts_item_id}], feedback_correcto (str), feedback_incorrecto (str), validation_notes (str)

**card_classification**: instruccion (str), cards [{id, label, imagen_key}], categories [{id, label, color_key, correct_card_ids[]}]

**grid_classification**: instruccion (str), items [{id, label, imagen_key}], columns [{id, label, correct_item_ids[]}]

**icon_grid_selection**: instruccion (str), opciones [{id, icon_key, label}], correct_ids [], min_selection (int), max_selection (int), feedback_correcto (str), feedback_incorrecto (str)

**memory_match**: instruccion (str), pares [{id, carta_a {label, imagen_key}, carta_b {label, imagen_key}}], validation_notes (str)

**multiple_choice**: pregunta (str), imagen_key (str|null), opciones [{id, texto}], correct_id (str), feedback_correcto (str), feedback_incorrecto (str)

**motivational_choice**: pregunta (str), imagen_key (str|null), opciones [{id, texto, respuesta_personalizada}]

**achievement**: titulo (str), mensaje (str), imagen_key (str|null), texto_boton (str)

## Reglas de Schema

- id: siempre 1, 2, 3 o 4 (Nivel 0) — nunca auto-generado
- version: siempre 1 inicialmente
- paso_id: entero único dentro de la lección
- imagen_key: snake_case sin espacios
- correct_id y similares: deben referenciar un id que exista en el mismo array de opciones/items
- validation_notes: campo no renderizado para tipos complejos (drag_drop, memory_match)
- Último paso de cada lección: tipo "achievement"

## Tabla lecciones (Supabase)

```sql
CREATE TABLE lecciones (
  id INTEGER PRIMARY KEY,
  nivel INTEGER NOT NULL,
  orden INTEGER NOT NULL,
  titulo VARCHAR NOT NULL,
  descripcion TEXT,
  duracion_minutos INTEGER,
  imagen_portada_key VARCHAR,
  activa BOOLEAN DEFAULT TRUE,
  contenido JSONB NOT NULL,
  version INTEGER DEFAULT 1,
  creado_en TIMESTAMPTZ DEFAULT NOW(),
  actualizado_en TIMESTAMPTZ
);
```

FK a progreso_leccion: NULLABLE en esta fase — no romper registros existentes.

## Arquitectura de Agentes

- seeding-agent: produce JSONs de lecciones desde Swift
- seeding-review-agent: revisa JSON vs Swift original (loop hasta aprobación)
- backend-ez: implementa modelo, migration, rutas (Fase 1)
- frontend-ez: implementa LeccionEngine, cache, views (Fase 2)

## Riesgos Principales

R1 (schema mal diseñado) 🔴, R2 (validación incorrecta) 🔴, R3 (cold start) 🟠, R4 (IDs desfasados) 🔴
Ver: /Users/danielrincon/.claude/plans/riesgos-lection-migration.md
