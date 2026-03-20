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
└── migrations/          # Alembic versions
```

## Tablas de base de datos

| Tabla | Descripción | Columnas clave |
|-------|-------------|----------------|
| `usuarios` | Usuarios del sistema | id, nombre, nombre_usuario (unique), email (unique), hashed_password, proveedor, foto_perfil |
| `gastos` | Gastos registrados | id, usuario_id, categoria, monto, es_necesario, fecha |
| `progreso_leccion` | Progreso por lección | id, usuario_id, leccion_id, completada |
| `respuestas_encuesta` | Respuestas onboarding | id, usuario_id (unique), respuestas_json |
| `conversaciones` | Conversaciones de chat | id, usuario_id, titulo, fechas |
| `mensajes` | Mensajes de chat | id, conversacion_id, rol, contenido |
| `streaks` | Racha diaria | usuario_id, última actividad, contador |

## Todos los endpoints

### Auth (`/auth`)
| Método | Path | Body / Params | Respuesta |
|--------|------|---------------|-----------|
| POST | `/auth/registro` | `{nombre, email, password}` | `{id, nombre, email, token}` |
| POST | `/auth/login` | `{email, password}` | `{id, nombre, email, token, encuesta_completada}` |
| POST | `/auth/login-google` | `{token: google_id_token}` | `{id, nombre, email, usuario, encuesta_completada, token}` |
| POST | `/auth/perfil` | `{nombre?, nombre_usuario?}` | confirmación |
| GET | `/auth/protegida` | — | ejemplo de ruta protegida |

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
