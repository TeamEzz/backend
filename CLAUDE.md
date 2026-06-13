# EZ-APP Backend

FastAPI + PostgreSQL. Desplegado en Render. Ver `../CLAUDE.md` para la integración con el frontend.

## Stack

- **Framework**: FastAPI
- **DB**: PostgreSQL con SQLAlchemy (psycopg3) + Alembic
- **Auth**: JWT HS256 vía `python-jose` + bcrypt para contraseñas
- **IA**: OpenAI API (módulo `chat/`)
- **Google Auth**: `google-auth` para verificar tokens de Google
- **Servidor**: Uvicorn
- **Deploy**: Render (`render.yaml`)

## Variables de entorno requeridas

```
DATABASE_URL=postgresql+psycopg://...
SECRET_KEY=...
OPENAI_API_KEY=...
RESEND_API_KEY=...                 # API key de Resend (envío de códigos de verificación)
EMAIL_FROM=onboarding@ezapp.tech   # remitente verificado en Resend
```

`DATABASE_URL` se auto-normaliza de `postgres://` a `postgresql+psycopg://` en `database/config.py`.

## Comandos

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr servidor local
uvicorn main:app --reload

# Migraciones
alembic upgrade head
alembic revision --autogenerate -m "descripcion"
alembic downgrade -1
```

## Estructura de módulos

```
EZ-APP/
├── main.py              # Entry point: registra todos los routers
├── database/
│   ├── db.py            # Engine SQLAlchemy + get_db() dependency
│   ├── config.py        # DATABASE_URL normalization
│   └── models/          # Tablas SQLAlchemy (un archivo por tabla)
├── Auth/                # Registro, login, Google OAuth, JWT utils
├── usuario/             # Perfil, editar, foto
├── Gastos/              # Registro de gastos + dashboard resumen
├── lecciones/           # Progreso de lecciones
├── encuesta/            # Onboarding survey
├── chat/                # Chat con OpenAI
├── streaks/             # Tracking de racha diaria
├── metas/               # Plan de presupuesto (cálculo + persistencia de metas)
└── migrations/          # Alembic versions
```

## Tablas de base de datos

| Tabla | Descripción | Columnas clave |
|-------|-------------|----------------|
| `usuarios` | Usuarios del sistema | id, nombre, nombre_usuario (unique), email (unique), hashed_password, proveedor, foto_perfil, verificado, codigo_verificacion (hash), codigo_expira_en, codigo_enviado_en, codigo_intentos |
| `gastos` | Gastos registrados | id, usuario_id, categoria, monto, es_necesario, fecha |
| `progreso_leccion` | Progreso por lección | id, usuario_id, leccion_id, completada |
| `respuestas_encuesta` | Respuestas onboarding | id, usuario_id (unique), respuestas_json |
| `conversaciones` | Conversaciones de chat | id, usuario_id, titulo, fechas |
| `mensajes` | Mensajes de chat | id, conversacion_id, rol, contenido |
| `streaks` | Racha diaria | usuario_id, última actividad, contador |
| `metas_usuario` | Plan de presupuesto guardado | id, usuario_id, meta_titulo, meta_tag, es_custom, es_primaria, horizonte_meses, ingreso_mensual, gastos_mensuales, costo_meta, ahorro_requerido, pct_ingreso, viabilidad, instrumento, mensaje_toro, otras_metas_json, creado_en |

## Todos los endpoints

### Auth (`/auth`)
| Método | Path | Body / Params | Respuesta |
|--------|------|---------------|-----------|
| POST | `/auth/registro` | `{email, password}` | `{email, requiere_verificacion, mensaje}` (201, **sin token**) |
| POST | `/auth/verificar` | `{email, codigo}` | `{id, nombre, email, token}` (emite la sesión) |
| POST | `/auth/reenviar-codigo` | `{email}` | mensaje genérico (anti-enumeración) |
| POST | `/auth/login` | `{email, password}` | `{id, nombre, email, token, encuesta_completada}` — **403 `correo_no_verificado`** si la cuenta local no ha verificado |
| POST | `/auth/login-google` | `{token: google_id_token}` | `{id, nombre, email, usuario, encuesta_completada, token}` |
| POST | `/auth/perfil` | `{nombre?, nombre_usuario?}` | confirmación |
| GET | `/auth/protegida` | — | ejemplo de ruta protegida |

**Verificación de correo (registro local):** `/registro` ya **no** devuelve token; crea el
usuario con `verificado=false`, genera un código de 6 dígitos (hash bcrypt + expiración 10 min,
máx. 5 intentos, cooldown de reenvío 60 s) y lo envía con `Auth/utils/email_utils.py` (API de
Resend). El token se emite en `/verificar`. Las cuentas Google nacen `verificado=true`. ⚠️ Esto
cambia el contrato con el frontend (antes recibía token en `/registro`): el cliente Swift debe
consumir la pantalla de verificación y el 403 de login en una tarea coordinada aparte.

### Usuario (`/usuario`)
| Método | Path | Body | Respuesta |
|--------|------|------|-----------|
| GET | `/usuario/perfil` | — | `{id, nombre, email, usuario, foto_perfil, encuesta_completada}` |
| POST | `/usuario/editar` | campos editables | confirmación |
| POST | `/usuario/foto` | multipart/form-data (file) | URL de la foto |

### Gastos (`/gasto`)
| Método | Path | Body / Params | Respuesta |
|--------|------|---------------|-----------|
| POST | `/gasto/registrar` | `{categoria, monto, es_necesario, fecha?}` | gasto creado |
| GET | `/gasto/resumen` | — | lista de gastos del usuario |

### Dashboard (`/dashboard`)
| Método | Path | Params | Respuesta |
|--------|------|--------|-----------|
| GET | `/dashboard/resumen` | `periodo` (semanal/mensual), `nivel` (int) | resumen con streak, gastos, lecciones |

### Lecciones (`/lecciones`)
| Método | Path | Body | Respuesta |
|--------|------|------|-----------|
| GET | `/lecciones/progreso` | — | lista de `{leccion_id, completada}` |
| POST | `/lecciones/{leccion_id}/completar` | — | confirmación |
| POST | `/lecciones/progreso/marcar` | `{leccion_id, completada}` | confirmación |

### Encuesta (`/encuesta`)
| Método | Path | Body | Respuesta |
|--------|------|------|-----------|
| POST | `/encuesta/responder` | `{respuestas: {...}}` | confirmación |

### Chat (`/chat`)
| Método | Path | Body / Params | Respuesta |
|--------|------|---------------|-----------|
| POST | `/chat/mensaje` | `{contenido, conversacion_id?}` | `{respuesta, conversacion_id}` |
| GET | `/chat/conversaciones` | — | lista de conversaciones |
| GET | `/chat/conversaciones/{id}/mensajes` | — | lista de mensajes |

### Metas (`/metas`)
| Método | Path | Body / Params | Respuesta |
|--------|------|---------------|-----------|
| GET | `/metas/contexto-financiero` | — | `{ingreso_estimado?, ingreso_rango?, personaje?}` derivado de la encuesta |
| POST | `/metas/plan` | `{meta_titulo, meta_tag?, es_custom, horizonte_meses, ingreso_mensual, gastos_mensuales, costo_meta, es_primaria, otras_metas[]}` | `BudgetResultOut` (viabilidad, instrumento, ahorro_requerido, pct_ingreso, mensaje_toro, …) |

El cálculo vive en `metas/utils/meta_calculator.py` (**fuente de verdad**; debe coincidir con el
frontend `BudgetCalculator.swift`). El `mensaje_toro` son plantillas estáticas por viabilidad, **sin
OpenAI**. `/metas/contexto-financiero` prioriza el `personaje` de Encuesta2 (Bula/Toriel/EZ → punto
medio del rango de ingreso) con fallback a Preg9 (encuesta original, lista índice 8).

### Health
| Método | Path |
|--------|------|
| GET/HEAD | `/` |
| GET | `/healthz` |

## Autenticación interna

La dependencia `get_current_user` en `Auth/utils/jwt_utils.py` se inyecta en cada endpoint protegido:
```python
current_user: Usuario = Depends(get_current_user)
```
Verifica el Bearer token y devuelve el objeto `Usuario` de la DB.

## Convenciones

- Cada módulo tiene su propio `routes/`, `schemas/` y opcionalmente `utils/` y `models/`
- Los schemas Pydantic están separados de los modelos SQLAlchemy
- Los modelos SQLAlchemy viven en `database/models/`, no dentro de cada módulo
- Nombres en español para tablas, columnas y rutas (excepto términos técnicos)

## Qué no tocar sin coordinación con el frontend

- Formato de fechas en respuestas (el frontend tiene parser multi-formato en `GastoViewModel`)
- El campo `encuesta_completada` en las respuestas de auth/perfil (controla el flujo de onboarding)
- La estructura de `{token, id, nombre, email}` en respuestas de login
- Los IDs de lecciones (enteros secuenciales acordados con el frontend)
- El path `/static/perfiles/` para fotos de perfil
