# Documento Técnico — Historias de Usuario  
## Motor de Generación de Imágenes con NanoBananaPro  
### Proyecto: Clean Score Jump (Clay / Stop-Motion)

---

## Contexto General

El motor que estamos construyendo recibe **registros JSON** que describen **qué imágenes deben generarse** para un storyboard.

Este motor:
- NO genera video.
- SOLO genera **imágenes estáticas (PNG 4K)** usando **NanoBananaPro**.
- Las imágenes generadas serán **insumos obligatorios** para la etapa posterior de video (Veo 3.1).

El JSON de referencia principal para esta etapa es:
- `NanoBananaPro.txt`

---

## Definición clave

### ¿Qué es NanoBananaPro?
NanoBananaPro es un generador de imágenes que:
- Construye una imagen final combinando:
  - **un prompt de texto**
  - **un conjunto de imágenes de referencia (refs)**
- Tiene límites estrictos:
  - Máximo **8 imágenes de referencia por imagen**
  - Devuelve **imágenes estáticas**, no video
- Genera **variantes** (ej. 2 versiones) por cada tarea

---

# HISTORIAS DE USUARIO

---

## HU-01 — Ingestar un registro JSON de imágenes

**Como** motor de generación  
**Quiero** recibir un JSON con definición de tareas de imagen  
**Para** saber exactamente qué imágenes debo generar con NanoBananaPro  

### Detalles
El endpoint del motor recibe un JSON que contiene:

- Metadata del proyecto
- Reglas de producción
- Librería de assets
- Una lista de `image_tasks`

Ejemplo conceptual:
```json
{
  "project": {...},
  "asset_library": {...},
  "image_tasks": [ ... ]
}
```

El motor NO debe inferir nada fuera de lo que está explícito en el JSON.

---

## HU-02 — Interpretar correctamente un image_task

**Como** motor  
**Quiero** procesar cada objeto dentro de `image_tasks[]`  
**Para** generar exactamente una imagen (o varias variantes) por tarea  

Cada `image_task` representa una imagen lógica a generar.

Campos relevantes:

| Campo | Uso |
|------|-----|
| task_id | Identificador único. Clave primaria del pipeline |
| block_id / shot_id | Contexto editorial (no afecta generación) |
| role | start o end (para uso futuro en video) |
| variants | Número de imágenes a generar |
| refs | Lista de imágenes guía (IDs) |
| prompt | Descripción específica del plano |
| negative_prompt | Restricciones explícitas |
| output | Resolución y formato |
| approval | Estado de aprobación |

---

## HU-03 — Resolver referencias (refs) a imágenes reales

**Como** motor  
**Quiero** convertir los IDs de refs en rutas o URLs de imágenes reales  
**Para** pasarlas como imágenes de referencia a NanoBananaPro  

Ejemplo:
```json
"refs": [
  "OVERHEAD_CANON_SCALE_SHEET",
  "STAGE_TABLE_OVERHEAD_NAVY_EMPTY",
  "CUTOUT_SEDAN_HERO_34_SS"
]
```

Proceso esperado:
1. Buscar cada ID dentro de `asset_library`
2. Resolverlo a un archivo (local o URL pública)
3. Validar:
   - Que el archivo exista
   - Que sea una imagen válida
   - Asegurar que el total de refs ≤ 8

---

## HU-04 — Construir el prompt final para NanoBananaPro

**Como** motor  
**Quiero** construir un prompt textual completo  
**Para** enviarlo correctamente al generador de imágenes  

### Regla CRÍTICA
El prompt final **NO** es solo `image_task.prompt`.

Debe ser la concatenación de:
1. `style_presets.global_image_style`
2. Reglas duras del proyecto (ej. stop-motion)
3. El prompt específico del `image_task`

Ejemplo conceptual:
```
[GLOBAL IMAGE STYLE]

[STOP-MOTION HARD RULES]

[IMAGE TASK PROMPT]
```

### Negative prompt
Debe combinar:
- `style_presets.global_negative_append`
- `image_task.negative_prompt` (si existe)

---

## HU-05 — Enviar la solicitud a NanoBananaPro

**Como** motor  
**Quiero** enviar una solicitud estructurada a NanoBananaPro  
**Para** generar las imágenes solicitadas  

Cada llamada incluye:
- Prompt final
- Negative prompt final
- Lista de imágenes de referencia (refs)
- Resolución objetivo (3840×2160)
- Formato (png)
- Número de variantes

⚠️ El motor NO debe mezclar:
- Prompts contradictorios
- Refs irrelevantes
- Más de 8 refs

---

## HU-06 — Generar variantes por image_task

**Como** motor  
**Quiero** generar múltiples variantes por tarea  
**Para** permitir selección humana posterior  

Si:
```json
"variants": 2
```

Entonces el motor debe:
1. Ejecutar la generación 2 veces
2. Guardar cada imagen con un sufijo determinístico (ej. `_v1`, `_v2`)

---

## HU-07 — Guardar resultados y metadatos

**Como** motor  
**Quiero** almacenar cada imagen generada con metadata  
**Para** que el pipeline posterior pueda consumirlas  

Debe registrarse:
- task_id
- variante
- ruta/URL de la imagen
- timestamp
- estado (`PENDING_REVIEW`)

---

## HU-08 — Respetar el Approval Gate

**Como** motor  
**Quiero** detener el flujo si una imagen no está aprobada  
**Para** no permitir que el video se genere con imágenes incorrectas  

Regla:
- Si `approval_gate = true`
- Ninguna imagen pasa a video sin aprobación explícita

---

## HU-09 — NO asumir inteligencia creativa

**Como** motor  
**Quiero** seguir estrictamente el JSON  
**Para** evitar introducir errores creativos  

El motor:
- NO interpreta metáforas
- NO decide composición
- NO agrega objetos
- NO “mejora” prompts

Todo debe venir declarado en el JSON.

---

## Flujo resumido (end-to-end)

1. Recibir JSON por endpoint  
2. Validar estructura  
3. Iterar `image_tasks`  
4. Resolver refs  
5. Construir prompt final  
6. Llamar a NanoBananaPro  
7. Generar variantes  
8. Guardar imágenes + metadata  
9. Esperar aprobación humana  

---

## Resultado esperado

Un conjunto de imágenes:
- 4K
- PNG
- Clay stop-motion
- Consistentes visualmente
- Listas para alimentar Veo 3.1

---

## Nota final

Este motor no es creativo.  
Es determinista, declarativo y repetible.

La creatividad vive en el JSON.  
El motor solo ejecuta fielmente.
