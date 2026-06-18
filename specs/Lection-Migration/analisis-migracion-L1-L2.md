# Análisis de migración: Lección 1 y Lección 2

**Fecha:** 2026-06-17  
**Contexto:** Evaluación de viabilidad para migrar L1 y L2 al sistema Server-Driven Content (SDC).

---

## Qué es SDC (resumen rápido)

El sistema SDC (Server-Driven Content) permite que el contenido de las lecciones viva en Supabase (PostgreSQL JSONB) en lugar de estar codificado en Swift. La app descarga el JSON, y un componente llamado `LeccionEngine` lo renderiza dinámicamente usando un conjunto de vistas genéricas (una por tipo de interacción).

El schema define 10 tipos de interacción: `explanation`, `image_carousel`, `drag_drop`, `card_classification`, `grid_classification`, `icon_grid_selection`, `memory_match`, `multiple_choice`, `motivational_choice`, `achievement`.

El engine genérico ya está implementado en `Bug-Fixes-&-New-design` (commit `07a0fda`).

---

## Estado actual: L3 y L4 migran limpiamente

L3 y L4 no fueron rediseñadas. Sus interacciones (`memory_match`, `multiple_choice`, `motivational_choice`, etc.) mapean 1:1 a los tipos del engine genérico. El seeding JSON ya está listo.

El problema surge con L1 y L2, que fueron rediseñadas con mecánicas custom que el engine genérico no puede reproducir fielmente.

---

## Lección 1 — Dificultades de migración

### Pantalla 2: `L1MercadoView` (El Mercado)

**Mecánica real:**
- 6 productos posicionados por coordenadas relativas (`top`/`left` 0..1) sobre una imagen de fondo de estantería
- Budget tracker en tiempo real: empieza con `$150,000`, se descuenta al arrastrar
- Drag gesture custom (`DragGesture`) — no el sistema `.onDrag` de iOS
- `matchedGeometryEffect`: el producto vuela al carrito con animación fluida
- Si el producto no alcanza (precio > saldo restante), rebota a la estantería con animación `bounce`
- El carrito acumula thumbnails de los productos comprados
- Tap sobre un thumbnail en el carrito devuelve el producto (reembolso)
- No hay respuesta correcta/incorrecta: cualquier selección válida dentro del presupuesto avanza

**Tipo de schema más cercano:** `drag_drop`

**Por qué no funciona:** El schema `drag_drop` actual define items con targets fijos (`accepts_item_id`), cada target acepta exactamente un item, y el feedback es binario (correcto/incorrecto). No tiene noción de presupuesto, carrito acumulativo, precios, rebote por saldo insuficiente, ni posicionamiento relativo por coordenadas. Para migrarlo habría que crear un tipo nuevo `budget_drag_market`.

**Qué se perdería con una implementación genérica:** el presupuesto en tiempo real, las animaciones del carrito, la capacidad de devolver productos, y el posicionamiento de productos sobre la imagen de fondo.

**Estimado de implementación** si se decide migrar: nueva vista `BudgetDragMarketView` en el engine (~8-10 horas) + schema nuevo + seeding.

---

### Pantalla 4: `L1QuincenaView` (La Quincena)

**Mecánica real:**
- 5 facturas listadas verticalmente (Arriendo, Mercado, Salida, Streaming, Transporte)
- El usuario toca para seleccionar; máximo 3 selecciones
- El Toro reacciona en tiempo real según la combinación exacta seleccionada:
  - `["arriendo", "mercado", "transporte"]` → `toro_thumbs_up` (combinación ideal)
  - 3 selecciones con "salida" y "streaming" → `toro_estresado`
  - 3 con al menos 2 esenciales → `toro_satisfecho`
  - Ocio antes que esenciales → `toro_sorprendido`
  - Default → `toro_preocupado`
- No hay una única respuesta correcta; el juego enseña por consecuencia

**Tipo de schema más cercano:** `icon_grid_selection` con `max_selection: 3`

**Por qué no funciona completamente:** `icon_grid_selection` tiene `correct_ids` (una lista de ids correctos) y feedback global. No tiene mecanismo para reacciones dinámicas según combinaciones específicas de selección. Las reacciones del Toro son lógica de aplicación, no datos — no se pueden expresar en JSON sin definir un motor de reglas de combinaciones.

**Qué se perdería:** la retroalimentación visual dinámica del Toro (que es lo que hace pedagógicamente interesante esta pantalla). Se podría simplificar a una selección múltiple estándar, pero pierde el impacto.

**Estimado si se decide migrar:** nuevo tipo `multi_tap_select` con soporte para reglas de Toro hardcodeadas (no serían data-driven de todos modos) — ~6-8 horas.

---

## Lección 2 — Situación diferente

### `L2DragGameView` (Minijuegos 1 y 2)

**Mecánica real:**
- Una carta visible a la vez (centrada en pantalla)
- El usuario arrastra la carta a una de las columnas (categorías)
- Correcto → `matchedGeometryEffect`: la carta vuela a la columna y se apila como thumbnail
- Incorrecto → shake de la zona + texto de error + Toro sorprendido + la carta rebota para reintentar
- Cada carta tiene feedback individual (`fbOk` y `fbNo`)
- Contador de aciertos a la primera (score)
- Pantalla de resultado al terminar (con opción de reintentar)
- Reutilizable: mismo componente, datos distintos para MG1 (nec/des/imp, 8 cartas) y MG2 (fijo/var, 6 cartas)

**Tipo de schema más cercano:** `card_classification`

**Diferencia clave:** el `CardClassificationView` del engine actual muestra **todas las cartas a la vez** en un scroll horizontal y usa el sistema `.onDrop` de iOS (menos fluido). `L2DragGameView` muestra una carta a la vez con `DragGesture` custom y per-card feedback.

**¿Se puede migrar L2?** Sí, con menos pérdida que L1. El contenido (cartas, categorías, feedbacks) es puramente datos que ya existen en `L2Models.swift` y mapean directamente a un schema. Lo que requeriría:

1. Extender el schema `card_classification` con:
   - `"modo": "one_at_a_time"` — nueva propiedad opcional
   - `feedback_ok` y `feedback_no` por carta (en lugar de solo feedback global)
2. Actualizar `CardClassificationView` para soportar el modo carta-a-carta

**Estimado:** ~4-6 horas de trabajo frontend + actualización del schema + seeding.

**Degradación si no se migra:** ninguna — L2 sigue igual con su implementación custom.

---

## Trade-offs comparados

| | L1 (Mercado) | L1 (Quincena) | L2 (DragGame) |
|---|---|---|---|
| ¿Migrable? | Sí, con nuevo tipo | Parcialmente | Sí, extendiendo tipo existente |
| Tipos nuevos en schema | `budget_drag_market` | `multi_tap_select` | Ninguno (extensión) |
| Trabajo frontend | ~8-10h | ~6-8h | ~4-6h |
| Pérdida de experiencia | Alta (budget, animaciones carrito) | Media-Alta (reacciones Toro) | Baja (cambio de layout, misma lógica) |
| Reutilizabilidad del tipo | Baja (muy específico de L1) | Baja (muy específico de L1) | Alta (`card_classification` mejorado aplica a otras lecciones futuras) |
| Recomendación | Hardcoded | Hardcoded | Evaluar según timeline |

---

## Recomendación final

**L1: mantener hardcoded permanentemente.**  
Los dos minijuegos de L1 son experiencias de marca — su valor pedagógico depende precisamente de la animación del carrito, el budget tracker en tiempo real, y las reacciones dinámicas del Toro. Reproducirlas genéricamente requeriría tanto trabajo que se pierde la ventaja de tener un engine flexible. El código hardcodeado existente es estable y no se tocará.

**L2: candidato para migración en V2 del engine.**  
La mecánica es generalizable y el contenido (cartas + feedbacks por carta) es puramente datos. El esfuerzo es razonable (~5h). Sin embargo, dado el timeline de lanzamiento, no es prioritario para esta fase. Se puede migrar después de validar el pipeline con L3/L4.

**L3 y L4: scope de la migración actual.** Todo el trabajo de SDC para el lanzamiento apunta aquí.

---

## Implicaciones para el código

`Nivel0View.swift` en `Bug-Fixes-&-New-design` tiene actualmente:

```swift
if Config.useServerDrivenContent && leccionId >= 1 && leccionId <= 4 {
    LeccionEngineView(leccionId: leccionId)
}
```

Debe cambiarse a:

```swift
if Config.useServerDrivenContent && leccionId >= 3 && leccionId <= 4 {
    LeccionEngineView(leccionId: leccionId)
}
```

L1 y L2 siempre caen al path `else` (hardcoded), independientemente del valor del feature flag.
