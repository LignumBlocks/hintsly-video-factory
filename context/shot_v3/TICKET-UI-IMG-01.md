# 🎫 TICKET-UI-IMG-01 — UI React “NanoBanana Runner”
### JSON → enviar → ver resultado

---

## 🎯 Objetivo

Construir una **interfaz ultra simple en React** que permita:

- Pegar un **JSON completo** (storyboard / `JSON_1_NanoBananaPro`) en un textarea
- Presionar **“Enviar”**
- Enviar el JSON a un endpoint del motor
- Mostrar el resultado **por task**:
  - Link(s) de imagen generada
  - Prompt final usado
  - Assets / refs enviados a NanoBananaPro

> ⚠️ Esta UI es **solo para operación y debug** del pipeline de imágenes (no video).

---

## 📦 Alcance (Scope)

### ✅ Incluye
- Pantalla única
- Textarea grande para JSON
- Botón **“Enviar”**
- Estado de loading
- Render del resultado (lista por `task_id`)
- Manejo de errores:
  - JSON inválido
  - Error HTTP
  - Error del motor

### ❌ No incluye
- Auth / roles
- Historial
- Edición avanzada de tasks
- Aprobar / rechazar imágenes
- Upload de assets  
  _(se asume que el motor resuelve refs)_

---

## 🔌 Suposición mínima de backend (Contrato)

### Request
```http
POST /api/...
Content-Type: application/json
Body: <JSON completo pegado>
```

### Response (sync o async)
```json
{
  "job_id": "job_123",
  "status": "PROCESSING" | "DONE" | "ERROR",
  "results": [
    {
      "task_id": "img__csj__B01__P01__start",
      "variant": 1,
      "image_url": "https://.../img__...__v1.png",
      "final_prompt": "...",
      "final_negative_prompt": "...",
      "assets_sent": [
        {
          "ref_id": "CUTOUT_SEDAN_HERO_34_SS",
          "resolved_url": "https://..."
        },
        {
          "ref_id": "STAGE_STUDIO34_NAVY_CYCLO_SS",
          "resolved_url": "https://..."
        }
      ]
    }
  ],
  "error": null
}
```

### Async (opcional)
Si el motor responde primero con `PROCESSING`:


- Polling hasta `DONE` o `ERROR`
- Intervalo sugerido: **2s**
- Timeout sugerido: **60s**

---

## 📋 Requerimientos funcionales (FR)

### FR-1 Entrada de JSON
- Textarea debe aceptar **texto largo** (JSON completo).
- Debe permitir pegar sin lag.
- No aplicar formateo costoso en cada keystroke.

### FR-2 Validación mínima en cliente
Antes de enviar:
- Intentar `JSON.parse()`
- Si falla:
  - Mostrar error
  - **No enviar** request

### FR-3 Envío al endpoint
- Botón **“Enviar”** dispara request `POST`
- Deshabilitar botón durante envío
- Mostrar estado **“Procesando…”**

### FR-4 Mostrar resultados
Para cada elemento de `results[]`:
- Mostrar `task_id` y `variant`
- Mostrar `image_url` como link clickeable
- Mostrar `final_prompt` en bloque legible (`pre-wrap`)
- Mostrar lista de `assets_sent`:
  - `ref_id`
  - `resolved_url` (link)

### FR-5 Errores
- Error de red/HTTP: mostrar mensaje
- Error del motor (`status: "ERROR"` + `error` string): mostrar detalle
- Respuesta malformada: mostrar **“Unexpected response”**

---

## ⚙️ Requerimientos no funcionales (NFR)
- UI debe ser simple y rápida
- No usar dependencias pesadas
- No suponer backend response perfecto (validar campos)
- Seguridad: no ejecutar nada del JSON, solo parsearlo

---

## 🧩 UX / UI (wireframe)

- Título: **NanoBanana Runner**
- Textarea: 70% alto de pantalla (monospace)
- Botón primario: **Enviar**
- Debajo: panel de resultados

Ejemplo de layout:

```
[NanoBanana Runner]

[ JSON textarea (pegas JSON completo aquí) ]

[ Enviar ]   (loading spinner cuando corre)

Resultados:
- task_id ... variant ...
  image: link
  prompt: ...
  assets:
    - ref_id: ... link
```

---

## ✅ Criterios de aceptación (AC)

- [ ] Se puede pegar un JSON completo y enviarlo
- [ ] Si el JSON no parsea, se muestra error y **no se envía**
- [ ] Al enviar, se llama al endpoint con el JSON completo
- [ ] Se muestra loading hasta recibir respuesta final (`DONE`) o error
- [ ] Se lista cada resultado con:
  - [ ] Link de imagen
  - [ ] Prompt final
  - [ ] Assets/refs enviados (IDs + URLs)
- [ ] Manejo correcto de errores HTTP y errores del motor
- [ ] UI funciona en mobile y desktop (responsive básico)

---

## 📝 Notas para implementación (para el agente)

- Usar `fetch` (preferido) o `axios`
- Textarea en monospace
- Mostrar prompts con `white-space: pre-wrap`
- Si el backend tarda, implementar polling cada 2s con límite (ej. 60s) o hasta `DONE`
- Validar shape de response antes de render (fallback a “Unexpected response”)

