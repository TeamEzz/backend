# Reglas de Diseño de Lecciones — Ez-APP SDC

**Propósito:** Estas reglas garantizan que cualquier lección nueva o rediseñada pueda reconstruirse completamente en la arquitectura Server-Driven Content (SDC). No es necesario que todo sea schema puro — las animaciones y estilos visuales viven en el código Swift. Lo que no puede perderse es el **contenido** y la **mecánica**.

---

## La distinción fundamental

| Capa | Dónde vive | Ejemplos |
|---|---|---|
| **Contenido** | JSON en Supabase (schema) | Textos, imágenes, opciones, feedback por carta, pares de memoria |
| **Presentación** | SwiftUI views (código) | Animaciones, colores, layout, efectos de partículas, flip 3D |
| **Lógica de negocio** | ❌ No debe existir en lecciones | Reacciones del Toro según combinación específica de selección |

**Regla madre: el contenido y la mecánica deben ser separables del código.** Si alguien puede cambiar los textos, las imágenes o las preguntas editando solo el JSON — sin tocar Swift — la lección cumple.

---

## Reglas de contenido

### R1 — Todo texto visible al usuario debe ser un campo de schema
- Textos principales, subtítulos, labels de botones, feedback, instrucciones → campos en el JSON
- **Prohibido:** texto hardcodeado dentro de un View que no venga de un parámetro de contenido

### R2 — Todo asset visual debe referenciarse por `imagen_key`
- Las imágenes del Toro, íconos de cartas, portadas → strings en el JSON (`"toro_celebrando"`, `"L2_gasto_arriendo"`)
- El View resuelve el key contra el asset catalog de Xcode
- **Prohibido:** `Image("toro_celebrando")` hardcodeado en un View sin venir de un campo de contenido

### R3 — El feedback debe ser por-ítem, no combinatorial
- ✅ Permitido: cada carta tiene `feedback_ok` y `feedback_no`
- ✅ Permitido: cada opción de trivia tiene `feedback_correcto` e `feedback_incorrecto`
- ❌ Prohibido: "si el usuario seleccionó exactamente las opciones A, C y E, mostrar este mensaje específico"
- **Razón:** el feedback combinatorial es lógica ramificada — no se puede expresar como datos sin inventar un lenguaje de reglas

### R4 — Las condiciones de éxito deben ser genéricas
- ✅ "Todas las cartas clasificadas correctamente"
- ✅ "Opción correcta seleccionada"
- ✅ "Todos los pares encontrados"
- ❌ "Exactamente 3 de las 5 opciones seleccionadas, y deben ser estas 3 específicas"
- **Razón:** condiciones de éxito específicas hardcodean lógica en el View que no puede venir del schema

---

## Reglas de interacción

### R5 — Cada minijuego debe mapearse a un tipo de interacción genérico
Los tipos disponibles son:
`explanation` · `image_carousel` · `drag_drop` · `card_classification` · `grid_classification` · `icon_grid_selection` · `memory_match` · `multiple_choice` · `motivational_choice` · `achievement`

Si un minijuego nuevo no encaja en ninguno, se crea un tipo nuevo — pero ese tipo debe poder reutilizarse en al menos 2 lecciones futuras. Si solo sirve para una lección, es una señal de que la mecánica está demasiado acoplada al contenido.

### R6 — No posicionamiento por coordenadas absolutas
- ❌ Prohibido: elementos del juego posicionados con `.position(x: 147, y: 312)` específicos para el contenido
- ✅ Permitido: grillas, stacks, layouts flexibles que se adaptan a cualquier contenido
- **Razón:** el posicionamiento por píxel acopla el diseño visual a datos específicos, imposibilitando la generalización

### R7 — Las reacciones de la mascota son estados, no lógica
- ✅ Permitido: el Toro muestra `imagen_key` distinta según estado genérico (correcto / incorrecto / completado / neutro)
- ✅ Permitido: el JSON especifica qué imagen usar en cada estado (`"feedback_imagen_ok_key": "toro_thumbs_up"`)
- ❌ Prohibido: el Toro reacciona diferente según qué combinación específica de ítems fue seleccionada
- **Razón:** esto convierte una imagen en lógica condicional — no es datos, es código disfrazado de diseño

---

## Reglas de estructura

### R8 — Las pantallas puente son pasos `explanation`
Pantallas de instrucciones, revelaciones, transiciones narrativas, splashes de minijuego → se modelan como pasos `explanation` con sus campos normales. No requieren tipos nuevos.

### R9 — Las pantallas de resultado son estado interno del View
Los scores, cronómetros, contador de intentos → estado `@State` en el View, no campos del schema. El schema define si el tipo de interacción "tiene score" de forma implícita (todos los `memory_match` tienen score, todos los `card_classification` no).

### R10 — Una lección = un array de pasos ordenados, sin bifurcaciones
- ✅ Permitido: pasos secuenciales (paso 1 → paso 2 → ... → paso N)
- ❌ Prohibido: "si el usuario falló el minijuego, ir al paso 4b; si pasó, ir al paso 5"
- **Razón:** las bifurcaciones requieren un motor de flujo, no un renderer lineal. Si se necesita ramificación en el futuro, es un cambio de arquitectura mayor.

---

## Lista de verificación antes de diseñar una lección

Antes de commitsear el rediseño de una lección, confirmar:

- [ ] ¿Todos los textos visibles vienen de campos JSON?
- [ ] ¿Todas las imágenes son `imagen_key` strings, no hardcodeadas?
- [ ] ¿El feedback es por-ítem (no por combinación)?
- [ ] ¿La condición de éxito es genérica (no específica a este contenido)?
- [ ] ¿El minijuego mapea a un tipo existente, o el tipo nuevo sirve para ≥2 lecciones futuras?
- [ ] ¿No hay coordenadas absolutas acopladas al contenido?
- [ ] ¿Las reacciones del Toro son estados genéricos (correcto/incorrecto), no lógica combinatorial?
- [ ] ¿Las pantallas de transición son pasos `explanation`?
- [ ] ¿El flujo es lineal (sin bifurcaciones)?

---

## Reglas para el desarrollador frontend

Estas aplican al escribir el código Swift hardcodeado de una lección nueva. Seguirlas hace que la migración posterior a SDC sea casi un copy-paste.

### F1 — Textos en el modelo, no en el View (9/10)
`Text(card.label)` no `Text("Arriendo")`. Ningún string visible al usuario debe estar hardcodeado dentro de un View.

### F2 — Imágenes como `imagen_key` string en el modelo (9/10)
`Image(card.imagenKey)` no `Image("toro_leyendo")`. Esto es lo que permite que el JSON reemplace el asset después sin tocar el View.

### F3 — `correctId` como dato del modelo, no del View (8/10)
La lógica "¿es correcto?" debe comparar contra un campo del modelo (`opcion.id == pregunta.correctId`), no contra un string hardcodeado en el View.

### F4 — Feedback de imágenes como campos opcionales del modelo (8/10)
Si una interacción muestra una imagen distinta según correcto/incorrecto (ej: Toro en trivia), agregar `feedbackImagenOk: String?` y `feedbackImagenNo: String?` a la struct correspondiente. Así el schema puede poblarlos después.

### F5 — Score y cronómetro como `@State` puro (5/10)
Estado de runtime (`@State var intentos: Int`, `@State var segundos: Int`) nunca debe contaminar el modelo de datos. El modelo es contenido; el estado es runtime.

**Principio:** `L{N}Models.swift` es la única fuente de verdad para el contenido. Los Views solo renderizan lo que reciben. El swap hardcoded → JSON es cambiar quién llena el modelo, no reescribir los Views.

---

## Caso de referencia: por qué L1 no cumple

`L1QuincenaView` viola **R3**, **R4** y **R7**:
- El Toro reacciona con combinaciones específicas según cuáles 3 de las 5 opciones se seleccionaron → lógica combinatorial
- La condición de éxito es "exactamente estas 3 específicas" → no genérico
- La `L1MercadoView` viola **R6**: productos posicionados por coordenadas exactas acopladas al diseño visual de esa lección específica

**Decisión:** L1 se queda hardcodeada permanentemente. Es el único caso hasta la fecha.

---

## Caso de referencia: cómo L2 y L3 cumplen

**L2** (`card_classification` con `modo: "one_at_a_time"`):
- Contenido: textos y feedback por carta en JSON ✅
- Mecánica: el tipo `card_classification` se extendió con un campo `modo` — reutilizable ✅
- Animaciones (drag, bounce): implementadas en `CardClassificationView.swift` ✅

**L3** (`memory_match` rediseñado):
- Contenido: pares palabra↔definición en JSON ✅
- Animación flip 3D: implementada en `MemoryMatchView.swift`, no en schema ✅
- Score/cronómetro: estado `@State` en el View ✅
- Pantalla de resultado: estado interno del View ✅
- Pantallas puente (instrucciones, revelación): pasos `explanation` en el JSON ✅
