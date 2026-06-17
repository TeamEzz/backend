# Plan de Implementación Backend — Fase 1

**Agente:** backend-ez
**Prerequisito:** Step Zero completo, Fase 0 schema aprobado

## Archivos a crear

1. Ampliar database/models/leccion_model.py — agregar clase Leccion con JSONB
2. lecciones/routes/contenido_routes.py — GET /lecciones/{id} y GET /lecciones?nivel=0
3. lecciones/schemas/contenido_schemas.py — LeccionMetadataResponse, LeccionContenidoResponse
4. Modificar main.py — registrar contenido_router con prefix="/lecciones"
5. Alembic migration #7 — tabla lecciones

## Reglas críticas

- NO tocar progreso_routes.py ni ProgresoLeccion model
- id de Leccion es Integer PK sin autoincrement — valores 1-4 para Nivel 0
- FK desde progreso_leccion → lecciones: NULLABLE en esta fase
- Usar JSONB (postgresql.JSONB), no JSON
- Verificar migration localmente antes de push (Render aplica en deploy)

## Seeds

Directorio: /Volumes/SanDisk/EZ/backend/seeds/lecciones/
Archivos: leccion_1.json, leccion_2.json, leccion_3.json, leccion_4.json
Producidos por: seeding-agent (iterar con seeding-review-agent hasta aprobación)

## Orden de dependencias

modelo → migration → rutas+schemas → main.py → seeds → deploy
