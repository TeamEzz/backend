# Matriz de Riesgos — Migración Server-Driven Content

**Proyecto:** Ez-APP — Migración de Lecciones a Supabase JSONB  
**Alcance:** Solo Nivel 0 (4 lecciones, 10 tipos de interacción)  
**Creado:** 2026-06-15  
**Revisión:** Pendiente post-implementación  

---

## Escala de evaluación

| Probabilidad | Definición |
|---|---|
| Baja | Requiere una combinación improbable de fallos |
| Media | Podría ocurrir si no se mitiga activamente |
| Alta | Ocurrirá sin acciones preventivas concretas |
| Cierta | Sucede por diseño; el riesgo está en el modo de fallo |

| Impacto | Definición |
|---|---|
| Bajo | Fricción técnica, sin efecto visible al usuario |
| Medio | Degradación de experiencia, no bloquea el flujo principal |
| Alto | Bloquea una o más lecciones o flujos críticos |
| Crítico | App inutilizable o pérdida de datos de usuario |

| Reversibilidad | Definición |
|---|---|
| Alta | Se corrige con un hotfix de datos o config, sin nuevo submit |
| Media | Requiere nuevo deploy de backend (minutos) sin App Store |
| Baja | Requiere nuevo submit al App Store (5-7 días) |
| Ninguna | No se puede deshacer para usuarios que ya actualizaron |

---

## Riesgos Identificados

### R1 — Schema JSON mal diseñado

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Alta |
| **Impacto** | Alto |
| **Reversibilidad** | Baja |
| **Fase de mayor riesgo** | Fase 0 (diseño) |

**Descripción:**  
Si el schema inicial no captura correctamente un tipo de interacción (estructura de campos incorrecta, tipos de datos inadecuados, reglas de validación no expresables en JSON), el error se descubre tarde — potencialmente en Fase 2 (implementación del renderer). Actualizar el schema post-Fase 0 requiere cambios coordinados en backend (nueva Alembic migration, JSON re-seedeado) y en frontend (Codable models actualizados), más un nuevo App Store submit si el cliente ya está publicado.

**Mitigaciones propuestas:**
- [ ] `renderer-prototype-agent`: validar que cada tipo renderiza en SwiftUI antes de escribir contenido real
- [ ] `schema-lint-agent`: validar JSONSchema antes de cualquier seeding
- [ ] Campo `version` en cada lección (permite evolución no breaking con campos opcionales)
- [ ] Review manual del schema contra CADA paso de CADA lección antes de aprobar Fase 0

**Mitigaciones aplicadas:** 🔄 EN CURSO (Fase 1 completada 2026-06-17)
- ✅ Campo `version` implementado en el modelo `Leccion` (Integer, default=1) — evolución no-breaking garantizada
- ✅ Campo `contenido` es JSONB puro: el frontend puede agregar campos opcionales sin romper decodificación existente
- ✅ Schema de los 10 tipos documentado y auditado por schema-review-agent antes del seeding
- ⏳ `schema-lint-agent` y `renderer-prototype-agent` pendientes para Fase 2 (frontend)
- ⚠️ Item pendiente: verificar `drag_drop.accepts_item_id` singular vs. plural al leer SlideMinijuego2.swift

**Advertencia de uso (Fase 1):** El campo `contenido` en la BD es JSONB sin validación de esquema a nivel de PostgreSQL. Si se inserta un JSON malformado (ej. tipo de interacción desconocido), la tabla lo acepta pero el frontend crasheará al decodificar. El seeding-agent + seeding-review-agent son la única barrera de calidad pre-inserción.

**Probabilidad residual:** Media → Baja (schema definido; riesgo residual en seeding quality)  
**Evaluación post-implementación:** Pendiente post-seeding y Fase 2

---

### R2 — Lógica de validación incorrecta en JSON

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Media-Alta |
| **Impacto** | Alto |
| **Reversibilidad** | Media |
| **Fase de mayor riesgo** | Fase 1 (seeding) |

**Descripción:**  
La validación de respuestas correctas está actualmente implícita en código Swift tipado (structs, comparaciones directas). Expresarla como reglas declarativas en JSON y luego interpretarlas correctamente en el motor es la parte más propensa a errores. Un `correct_id` incorrecto hace que respuestas correctas se rechacen (o incorrectas se acepten), rompiendo la experiencia educativa. Reversible vía hotfix del JSON en BD (sin nuevo App Store submit), pero el daño a la UX ya ocurrió para usuarios afectados.

**Mitigaciones propuestas:**
- [ ] Loop seeding-agent / seeding-review-agent: review-agent compara cada regla de validación contra el código Swift original
- [ ] Campo `validation_notes` en JSON (string no renderizado) para documentar la regla en lenguaje natural
- [ ] Para drag_drop y memory_match: test manual de cada par/target antes de seeding final
- [ ] Los hotfixes de contenido JSON no requieren App Store submit (ventaja clave del server-driven approach)

**Mitigaciones aplicadas:** ⏳ PENDIENTE — se aplica en Fase 1 seeding (próximo paso)
- ✅ Infraestructura lista: `seeds/lecciones/` y `seeds/review/` creados y commiteados
- ✅ Agentes listos: `seeding-agent.md` y `seeding-review-agent.md` configurados con checklist de validación
- ✅ Campo `validation_notes` en el schema del seeding-agent (documenta regla en lenguaje natural)
- ⏳ Loop seeding-agent / seeding-review-agent: ejecutar cuando el seeding comience

**Probabilidad residual:** Media (hasta que el loop seeding/review esté completo)  
**Evaluación post-implementación:** Pendiente post-seeding

---

### R3 — Backend no disponible en momento de uso (Render cold start / caída)

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Alta |
| **Impacto** | Alto |
| **Reversibilidad** | Alta |
| **Fase de mayor riesgo** | Fase 4 (producción) |

**Descripción:**  
`ez-backendd.onrender.com` en tiers básicos de Render tiene cold start de 15-30 segundos tras períodos de inactividad. Post-migración, si el backend está dormido cuando el usuario abre la app, las lecciones no cargan — esto es un regresión directa respecto al estado actual donde las lecciones son instantáneas y offline. También aplica para caídas del servicio.

**Mitigaciones propuestas:**
- [ ] Cache local con TTL (implementar en LeccionContentService antes de eliminar path hardcodeado)
- [ ] Pre-fetch de todas las lecciones en onboarding (cuando hay WiFi)
- [ ] Modo offline básico: servir desde cache cuando API no responde
- [x] ~~Evaluar upgrade a tier de Render con keep-alive~~ — ya tiene instancia de pago, sin cold start
- [ ] Health check en startup: si API no responde en 3 segundos, usar cache sin error visible

**Mitigaciones aplicadas:** ✅ RESUELTO PARCIALMENTE (2026-06-17)
- ✅ **Cold start eliminado**: el backend corre en instancia de pago en Render — no hay sleep ni arranque en frío. El escenario principal de R3 (15-30s de espera) **no aplica**.
- ⏳ Cache local (LeccionContentService): se implementa en Fase 2 frontend — protege contra caídas de red y outages del servicio
- ⏳ Pre-fetch en onboarding: Fase 2 frontend
- ⏳ Modo offline: Fase 2 frontend

**Probabilidad residual:** Baja — solo escenario de outage real del servicio (no cold start)  
**Evaluación post-implementación:** R3 recalificado. Impacto real reducido significativamente por instancia de pago.

---

### R4 — IDs de lecciones desfasados durante seeding

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Media |
| **Impacto** | Crítico |
| **Reversibilidad** | Alta (pre-producción), Baja (post-producción) |
| **Fase de mayor riesgo** | Fase 1 (seeding + migración) |

**Descripción:**  
Los IDs 1-4 (Nivel 0) están hardcodeados en el frontend y en la tabla `progreso_leccion`. Si el script de seeding crea lecciones con IDs distintos, los registros de progreso existentes quedan huérfanos. Usuarios que ya completaron lecciones verían su progreso perdido o duplicado. En pre-producción esto es fácil de corregir (re-seeding + reset de datos de prueba). Post-launch con usuarios reales, requeriría una migración de datos en `progreso_leccion`.

**Mitigaciones propuestas:**
- [ ] El seeding script usa IDs explícitos (1, 2, 3, 4), no auto-generados
- [ ] seeding-review-agent verifica que los IDs en JSON coinciden con los IDs en el código Swift
- [ ] La tabla `lecciones` usa `id SERIAL` con insert explícito, no `GENERATED ALWAYS AS IDENTITY`
- [ ] Verificar conteo de registros `progreso_leccion` antes y después del seeding

**Mitigaciones aplicadas:** ✅ COMPLETADO (Fase 1, 2026-06-17)
- ✅ `id = Column(Integer, primary_key=True, autoincrement=False)` — no SERIAL, no IDENTITY
- ✅ Migración #7 (`b2e7f1d4c9a0`) escrita manualmente con `autoincrement=False` — ningún ORM puede auto-generar IDs
- ✅ Los JSON que producirá el seeding-agent tienen IDs explícitos 1-4 (hardcoded en el seeding-agent prompt)
- ✅ `INSERT ... ON CONFLICT (id) DO UPDATE` en el script de seeding → idempotente
- ⏳ Verificar conteo post-seeding: pendiente cuando se ejecute el seeding

**Probabilidad residual:** Baja — la arquitectura hace imposible un ID auto-generado  
**Evaluación post-implementación:** ✅ Controlado. Riesgo residual solo en error humano al editar los JSON manualmente.

---

### R5 — Regresión en streak / progreso durante cambio de arquitectura

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Baja |
| **Impacto** | Alto |
| **Reversibilidad** | Media |
| **Fase de mayor riesgo** | Fase 1-2 (transición) |

**Descripción:**  
`POST /lecciones/{id}/completar` llama a `update_streak()` y es el punto de integración entre el sistema de lecciones y el de streaks/gamificación. Si durante la migración se modifica este endpoint o se agrega una FK obligatoria a la nueva tabla `lecciones`, la inserción en `progreso_leccion` puede fallar, silenciando la actualización de streak. El usuario completa la lección pero no ve su racha crecer.

**Mitigaciones propuestas:**
- [ ] NO modificar `progreso_routes.py` ni `ProgresoLeccion` model durante Fase 1
- [ ] La FK de progreso_leccion → lecciones es NULLABLE en esta fase (no obligatoria)
- [ ] Test de integration: completar una lección vía API y verificar que streak se actualiza

**Mitigaciones aplicadas:** ✅ COMPLETADO (Fase 1, 2026-06-17)
- ✅ `progreso_routes.py` y `ProgresoLeccion` intactos — no se tocaron en ningún commit
- ✅ No se añadió FK entre `lecciones` y `progreso_leccion` en la migración #7 — leccion_id en progreso_leccion sigue siendo Integer libre
- ✅ La nueva tabla `lecciones` es completamente independiente de la lógica de streaks
- ⏳ Test de integration: pendiente post-deploy

**Probabilidad residual:** Muy Baja — la arquitectura mantiene separación total entre contenido y progreso  
**Evaluación post-implementación:** ✅ Controlado en esta fase.

---

### R6 — App Store review delay con versión incongruente

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Media |
| **Impacto** | Medio |
| **Reversibilidad** | Ninguna (durante la ventana) |
| **Fase de mayor riesgo** | Fase 4 (App Store submit) |

**Descripción:**  
**ATENUADO** por el hecho de que la app aún no está publicada. El primer submit incluirá tanto el backend-driven code como el feature flag. No hay usuarios con versión vieja que deban ser soportados. Sin embargo: si durante los 5-7 días de review de Apple se descubre un bug crítico en el renderer, la corrección requiere re-submit (otros 5-7 días). El feature flag actúa como killswitch en este caso.

**Mitigaciones propuestas:**
- [ ] Feature flag implementado antes del submit (permite disabling remoto)
- [ ] Testing exhaustivo en Fase 3 antes de submit — no hay segunda oportunidad sin delay
- [ ] Mantener el path hardcodeado compilable hasta después de la primera aprobación de App Store

**Mitigaciones aplicadas:** ✅ COMPLETADO (Fase 2, 2026-06-17)
- ✅ `Config.useServerDrivenContent` implementado — `false` por defecto, activa LeccionEngine cuando `true`
- ✅ Path hardcodeado (`Leccion*Nivel0()`) preservado íntegro en el `else` branch de `destinoLeccion()`
- ✅ El feature flag es un killswitch real: en cualquier momento se puede flipear a `false` sin re-submit
- ⏳ Testing exhaustivo (Fase 3) pendiente antes de activar el flag y hacer submit

**Probabilidad residual:** Baja — el feature flag garantiza que cualquier bug crítico en el renderer no bloquea a los usuarios  
**Evaluación post-implementación:** ✅ Killswitch implementado. Riesgo real reducido a "delay de re-submit si el flag mismo falla" (extremadamente improbable).

---

### R7 — Assets de imágenes siguen atados al bundle de la app

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Cierta (por diseño del MVP) |
| **Impacto** | Bajo (para MVP) |
| **Reversibilidad** | Alta |
| **Fase de mayor riesgo** | Fase 5+ (futuras actualizaciones de contenido) |

**Descripción:**  
Las imágenes de lecciones (ej: `"Leccion 0.1"`, `"Intro 0.2"`) viven en `Assets.xcassets`. Para el MVP, los campos `imagen_key` en JSON mapean a asset names locales — funciona. Pero el objetivo final del server-driven content (modificar lecciones sin recompilar) se cumple solo para texto/lógica, no para assets. Si se quiere cambiar una imagen en una lección, sigue requiriendo un App Store submit. Mover assets a Supabase Storage es trabajo separado.

**Mitigaciones propuestas:**
- [ ] El schema usa `imagen_key` (string), no URLs absolutas — esto hace la migración futura a Supabase Storage trivial (solo cambiar el resolver en el frontend)
- [ ] Documentar esta limitación explícitamente en el spec frontend
- [ ] Planear Supabase Storage migration como Fase 6

**Mitigaciones aplicadas:** *(completar durante implementación)*  
**Probabilidad residual:** —  
**Evaluación post-implementación:** —

---

### R8 — Lógica de desbloqueo de niveles con count hardcodeado

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Baja (para MVP) |
| **Impacto** | Medio |
| **Reversibilidad** | Media |
| **Fase de mayor riesgo** | Futura expansión de contenido |

**Descripción:**  
`estaNivelDesbloqueado(nivel:leccionesPorNivel:8)` asume 8 lecciones por nivel. Actualmente Nivel 0 solo tiene 4 lecciones (IDs 1-4) — pero el frontend espera 8 para desbloquear. Este desajuste podría existir ya hoy. Post-migración, si se agregan lecciones vía backend sin actualizar el cliente, el contador de desbloqueo queda mal. No bloquea el MVP pero es deuda técnica a resolver.

**Mitigaciones propuestas:**
- [ ] Verificar el comportamiento actual de desbloqueo con solo 4 lecciones en Nivel 0
- [ ] Incluir `total_lecciones` como campo de metadata en el endpoint `GET /lecciones?nivel=0`
- [ ] Actualizar ProgresoLeccionesViewModel para usar el count del API en lugar del hardcoded

**Mitigaciones aplicadas:** *(completar durante implementación)*  
**Probabilidad residual:** —  
**Evaluación post-implementación:** —

---

### R9 — Complejidad del renderer genérico (crashes por decodificación JSON)

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Media |
| **Impacto** | Alto |
| **Reversibilidad** | Media |
| **Fase de mayor riesgo** | Fase 2 (implementación frontend) |

**Descripción:**  
Las vistas hardcodeadas en Swift son imposibles de crashear por datos incorrectos (el compilador garantiza que los datos existen). Un renderer que decodifica JSON en runtime puede crashear si un campo requerido llega nulo, un tipo es incorrecto, o un `tipo` desconocido no está manejado. Estos crashes son silenciosos en producción (Crashlytics, no visible al usuario hasta que la pantalla se congela o cierra).

**Mitigaciones propuestas:**
- [x] Todos los Codable models usan campos opcionales donde aplica, con valores default seguros
- [x] El switch sobre `paso.tipo` siempre tiene un `default:` case que muestra una pantalla de error (no crash)
- [ ] Integrar Crashlytics/logging para detectar decodificación fallida antes del launch
- [ ] `schema-lint-agent` valida que cada JSON puede ser decodificado por los Codable models antes del seeding

**Mitigaciones aplicadas:** ✅ COMPLETADO (Fase 2, 2026-06-17)
- ✅ `PasoData` enum con `case unknown(String)` — cualquier tipo desconocido va a `ErrorPasoView`, jamás crash
- ✅ Todos los campos opcionales son `String?`, `Int?` con nil-coalescing seguro en las vistas
- ✅ Zero force-unwraps en todo el stack LeccionModels → LeccionContentService → LeccionEngineView
- ✅ `ErrorPasoView` siempre compilado — no dead code, es el fallback del engine
- ⏳ Crashlytics/logging — pendiente antes del launch
- ⏳ `schema-lint-agent` — pendiente antes del seeding

**Probabilidad residual:** Muy Baja — la única forma de crash sería un bug en el propio `init(from:)` del PasoData, no en datos del backend  
**Evaluación post-implementación:** ✅ La arquitectura de decodificación es crash-safe por diseño. El `unknown` case cierra el último vector de crash.

---

### R10 — Step Zero incompleto: referencias a Nivel 1 en VistaEducacion no eliminadas

| Campo | Valor |
|---|---|
| **Probabilidad inicial** | Media |
| **Impacto** | Alto (error de compilación) |
| **Reversibilidad** | Alta |
| **Fase de mayor riesgo** | Step Zero |

**Descripción:**  
El análisis de dependencias confirmó CERO referencias de tipo desde archivos externos hacia Nivel 1. Sin embargo, `VistaEducacion.swift` muy probablemente instancia `Nivel1View()` en su navigation routing — esta referencia no aparece en una búsqueda de tipos si usa pattern matching sobre enteros o string. Si se elimina la carpeta Nivel 1 antes de limpiar VistaEducacion, el proyecto no compila.

**Mitigaciones propuestas:**
- [ ] Leer manualmente VistaEducacion.swift antes de borrar Nivel 1
- [ ] Build limpio en Xcode después de modificar VistaEducacion y ANTES de borrar carpeta
- [ ] Git commit de los cambios a VistaEducacion antes del rm -rf de la carpeta

**Mitigaciones aplicadas:** ✅ COMPLETADO (2026-06-17)
- VistaEducacion.swift auditado antes de borrar: ya tenía referencia a Nivel1View y 7 niveles — se corrigió
- Carpeta `Nivel 1/` eliminada completa: Nivel1View, Nivel1Leccion1, 10 slides, EmojiPricing, EmojiAnnualEstimator
- EmojiPricing/EmojiAnnualEstimator: no requirieron migración (encuesta2 ya había sido eliminada por el developer)
- VistaEducacion.swift: corrupción de encoding UTF-8 detectada y corregida (11 chars: ó, á, ú, é, í)
- Proyecto usa PBXFileSystemSynchronizedRootGroup (Xcode 16): no requirió editar .pbxproj
- Commit: `eb5adfe` en branch `Bug-Fixes-&-New-design`

**Advertencia de uso post-Step Zero:** Si SourceKit muestra errores en `Encuesta2ViewModel.swift` para `calcularRango`, `URLS`, o `TokenManager` — son **falsos positivos pre-existentes**. Resuelven en compilación completa (Cmd+B). No tocar.

**Probabilidad residual:** Ninguna — Step Zero completado y verificado  
**Evaluación post-implementación:** ✅ Sin issues. Nivel 1 eliminado limpiamente. Encoding corregido.

---

## Resumen de Riesgos

| ID | Descripción breve | Prob | Impacto | Reversibilidad | Prioridad de mitigación |
|---|---|---|---|---|---|
| R1 | Schema JSON mal diseñado | Alta | Alto | Baja | 🔴 Crítica |
| R2 | Validación incorrecta en JSON | Media-Alta | Alto | Media | 🔴 Crítica |
| R3 | Backend no disponible (cold start) | Alta | Alto | Alta | 🟠 Alta |
| R4 | IDs de lecciones desfasados | Media | Crítico | Variable | 🔴 Crítica |
| R5 | Regresión en streaks | Baja | Alto | Media | 🟡 Media |
| R6 | App Store review delay | Media | Medio | Ninguna | 🟠 Alta |
| R7 | Assets atados al bundle | Cierta | Bajo | Alta | 🟢 Baja (por diseño) |
| R8 | Count de desbloqueo hardcodeado | Baja | Medio | Media | 🟡 Media |
| R9 | Crashes por decodificación JSON | Media | Alto | Media | 🟠 Alta |
| R10 | Nivel 1 refs no eliminadas en VistaEducacion | Media | Alto (build) | Alta | 🔴 Crítica (Step Zero) |

---

*Este documento se actualiza al completar cada fase. La columna "Mitigaciones aplicadas" y "Probabilidad residual" se llenan durante la implementación para trazar el historial de decisiones de mitigación.*
