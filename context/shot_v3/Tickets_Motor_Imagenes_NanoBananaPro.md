# 🎫 TICKETS — Motor de Imágenes NanoBananaPro

---

## 🎫 TICKET-IMG-01  
### Ingesta de JSON para generación de imágenes (NanoBananaPro)

#### Historia de Usuario  
**HU-01 — Ingestar un registro JSON de imágenes**

**Objetivo**  
Implementar un endpoint que reciba un JSON de definición de imágenes y lo cargue en memoria como entrada válida del motor.

**Descripción técnica**  
El motor debe exponer un endpoint (HTTP o interno) que:

- Reciba un JSON estructurado conforme a `NanoBananaPro.txt`
- Valide que contiene, como mínimo:
  - `project`
  - `asset_library`
  - `image_tasks[]`

No debe ejecutar ninguna generación en este ticket, solo validar e ingerir.

**Reglas**
- No inferir campos faltantes  
- No modificar el JSON recibido  
- Rechazar si falta alguna sección obligatoria  

**Criterios de aceptación**
- El endpoint acepta un JSON válido  
- El endpoint rechaza JSON incompleto  
- El JSON queda disponible para procesamiento posterior  

---

## 🎫 TICKET-IMG-02  
### Interpretación de `image_tasks[]`

#### Historia de Usuario  
**HU-02 — Interpretar correctamente un image_task**

**Objetivo**  
Procesar cada objeto dentro de `image_tasks[]` como una unidad de trabajo independiente.

**Descripción técnica**  
Para cada elemento de `image_tasks[]`, el motor debe leer y almacenar:

- `task_id`
- `block_id`
- `shot_id`
- `role`
- `variants`
- `refs`
- `prompt`
- `negative_prompt` (si existe)
- `output`
- `approval.status`

**Reglas**
- `task_id` es clave primaria (no puede repetirse)
- No generar imágenes todavía

**Criterios de aceptación**
- El motor puede iterar todos los `image_tasks`
- Cada task queda representado internamente como una estructura clara
- IDs duplicados generan error

---

## 🎫 TICKET-IMG-03  
### Resolución de referencias (refs) a imágenes reales

#### Historia de Usuario  
**HU-03 — Resolver referencias (refs) a imágenes reales**

**Objetivo**  
Convertir los IDs declarados en `refs` a rutas o URLs reales de imágenes.

**Descripción técnica**  
Para cada `image_task.refs[]`:

- Buscar el ID dentro de `asset_library`
- Resolverlo a una ruta local o URL pública
- Verificar:
  - Que el archivo existe
  - Que es una imagen válida
- Contar el total de refs

**Reglas**
- Máximo permitido: `nanobanana_max_reference_images` (8)
- Si un ref no existe → error

**Criterios de aceptación**
- Todas las refs se resuelven correctamente
- Se bloquean tasks con más de 8 refs
- Error claro si un asset no existe

---

## 🎫 TICKET-IMG-04  
### Construcción del prompt final (texto)

#### Historia de Usuario  
**HU-04 — Construir el prompt final para NanoBananaPro**

**Objetivo**  
Construir el prompt textual completo que se enviará a NanoBananaPro.

**Descripción técnica**  
El prompt final debe ser la concatenación ordenada de:

1. `style_presets.global_image_style`
2. Reglas duras del proyecto (ej. stop-motion)
3. `image_task.prompt`

El **negative prompt** debe combinar:

- `style_presets.global_negative_append`
- `image_task.negative_prompt` (si existe)

**Reglas**
- No eliminar información
- No reescribir semántica
- El orden importa

**Criterios de aceptación**
- El prompt final contiene estilo + reglas + prompt específico
- El negative prompt contiene todas las restricciones
- Ningún campo se pierde

---

## 🎫 TICKET-IMG-05  
### Envío de solicitud a NanoBananaPro

#### Historia de Usuario  
**HU-05 — Enviar la solicitud a NanoBananaPro**

**Objetivo**  
Realizar la llamada efectiva al generador de imágenes NanoBananaPro.

**Descripción técnica**  
El motor debe enviar:

- Prompt final
- Negative prompt final
- Lista de refs (imágenes)
- Resolución (`3840x2160`)
- Formato (`png`)
- Número de variantes

**Reglas**
- No mezclar inputs incompatibles
- No exceder refs máximas
- No modificar prompt antes del envío

**Criterios de aceptación**
- NanoBananaPro recibe payload válido
- La respuesta contiene imágenes
- Errores se capturan y reportan

---

## 🎫 TICKET-IMG-06  
### Generación de variantes por imagen

#### Historia de Usuario  
**HU-06 — Generar variantes por image_task**

**Objetivo**  
Generar múltiples versiones de una misma imagen cuando `variants > 1`.

**Descripción técnica**  
Si un `image_task` tiene:

```json
"variants": 2
```

El motor debe:

- Ejecutar 2 generaciones
- Guardarlas como outputs independientes
- Nombrarlas de forma determinística (`_v1`, `_v2`)

**Criterios de aceptación**
- Se generan exactamente N variantes
- Cada variante tiene ID único
- No se sobreescriben archivos

---

## 🎫 TICKET-IMG-07  
### Persistencia de imágenes y metadatos

#### Historia de Usuario  
**HU-07 — Guardar resultados y metadatos**

**Objetivo**  
Guardar imágenes generadas y su metadata asociada.

**Descripción técnica**  
Por cada imagen generada, almacenar:

- `task_id`
- `variant`
- `ruta/URL`
- `timestamp`
- `estado` (`PENDING_REVIEW`)

**Criterios de aceptación**
- Todas las imágenes quedan persistidas
- Metadata asociada correctamente
- Se puede consultar por `task_id`

---

## 🎫 TICKET-IMG-08  
### Enforcement del Approval Gate

#### Historia de Usuario  
**HU-08 — Respetar el Approval Gate**

**Objetivo**  
Bloquear el avance del pipeline si una imagen no está aprobada.

**Descripción técnica**  
Si `approval_gate = true`:

- El motor no debe exponer imágenes para video
- Hasta que `approval.status == APPROVED`

**Criterios de aceptación**
- Imágenes no aprobadas no avanzan
- Estado de aprobación es verificable
- El pipeline se detiene correctamente

---

## 🎫 TICKET-IMG-09  
### Ejecución estrictamente declarativa (no creativa)

#### Historia de Usuario  
**HU-09 — NO asumir inteligencia creativa**

**Objetivo**  
Garantizar que el motor no toma decisiones creativas.

**Descripción técnica**  
El motor:

- NO agrega objetos
- NO cambia composición
- NO corrige prompts
- NO interpreta metáforas

Solo ejecuta lo que el JSON declara.

**Criterios de aceptación**
- No hay inferencias automáticas
- Todo lo generado está explícitamente definido
- El motor es determinista

---

## 🧠 Nota final para el agente IA

Este motor **no es un modelo creativo**.  
Es un ejecutor declarativo de **prompts + refs**.

👉 **Si algo no está en el JSON, no existe.**
