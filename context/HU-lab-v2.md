# HU – Migración de Shot Schema v1 → v2 (Hintsly Lab Canon) + Soporte de asset_mode/mv_context

## ID

HU-F3-UPGRADE-SHOT-SCHEMA-V2

## Título

Como motor de la fábrica, quiero procesar **shots en el esquema v2 (Hintsly Lab Canon)** para generar prompts/imagen/video según `mv_context` y `asset_mode`, y devolver/guardar el shot con rutas y estado correctos.

---

## Contexto / Problema

Hoy el motor recibe un `Shot` “v1” con campos como `bloque`, `plano`, `movimiento_camara` y estado `LISTO`, y ejecuta un flujo fijo:
PromptService → Imagen (Kie Nano Banana) → Video (Kie Veo) → metadata.json.

Necesitamos subir a una versión superior que reciba un `Shot` con **schema v2 canónico**, incluyendo:

* Identificadores: `video_id`, `block_id`, `shot_id`
* Control de escena: `mv_context`
* Control de generación: `asset_mode` (STILL_ONLY, IMAGE_1F_VIDEO, IMAGE_2F_VIDEO)
* Movimiento: `camera_move` (ENUM/normalizado)
* Campos semánticos: `duracion_seg`, `texto_voz_resumido`, `funcion_narrativa`
* Prompts: `prompt_imagen`, `prompt_video`
* Estado: `PENDIENTE | EN_PROCESO | COMPLETADO | ERROR`

---

## Objetivo

1. Aceptar y validar `Shot v2` como entrada.
2. Ajustar el orquestador para ejecutar el pipeline **condicional** por `asset_mode`.
3. Normalizar/mapeo de campos (incluyendo cámara y estados) y mantener consistencia.
4. Guardar outputs y metadata en rutas Hintsly Lab canon:
   `assets/videos/{video_id}/block_{block_id}/shot_{shot_id}/...`
5. Retornar el `Shot v2` actualizado con `prompt_*`, `image_path`, `video_path`, `estado`, `error_message`.

---

## Definición de “Shot v2” (resumen)

Ejemplo de entrada (representativo):

```json
{
  "video_id": "csj_B01_P01",
  "block_id": "B01_HOOK",
  "shot_id": "P01",
  "core_flag": false,
  "mv_context": "REAL_CHAOS",
  "asset_id": null,
  "asset_mode": "IMAGE_1F_VIDEO",
  "camera_move": "Handheld",
  "duracion_seg": 8.0,
  "texto_voz_resumido": "...",
  "descripcion_visual": "...",
  "funcion_narrativa": "...",
  "prompt_imagen": "",
  "prompt_video": "",
  "image_path": "",
  "video_path": "",
  "estado": "PENDIENTE",
  "error_message": null
}
```

---

## Alcance

### Incluye

* Modelo de dominio / DTO `ShotV2` y validaciones.
* Ajuste del endpoint `POST /shots/process` para aceptar v2 (y opcionalmente compatibilidad v1).
* Cambios en `ProcessShot` para:

  * procesar por `asset_mode`
  * setear `estado` con la máquina de estados
  * persistir rutas canon y `metadata.json`
* Normalización de `camera_move` a un set cerrado (o mapping robusto).
* Actualización de `PromptService` para usar campos v2 (`mv_context`, `funcion_narrativa`, `texto_voz_resumido`, `duracion_seg`).

### No incluye (por ahora)

* Lectura/escritura directa a Google Sheets.
* Soporte completo de `IMAGE_2F_VIDEO` si se decide entregarlo en iteración 2.

---

## Reglas de Negocio

1. **La tabla/origen manda**: el motor no inventa campos “humanos”.
2. **Rutas canon**:

   * Imagen: `assets/videos/{video_id}/block_{block_id}/shot_{shot_id}/image.png`
   * Video: `assets/videos/{video_id}/block_{block_id}/shot_{shot_id}/video.mp4`
   * Metadata: `assets/videos/{video_id}/block_{block_id}/shot_{shot_id}/metadata.json`
3. **Máquina de estados**:

   * `PENDIENTE` → `EN_PROCESO` → `COMPLETADO`
   * Error → `ERROR` + `error_message`
4. **asset_mode**:

   * `STILL_ONLY`: solo imagen.
   * `IMAGE_1F_VIDEO`: imagen + video.
   * `IMAGE_2F_VIDEO`: imagen inicio/fin + video (si aplica).
5. **Prompts**:

   * Si vienen vacíos, se generan.
   * Si vienen llenos, no se sobreescriben.

---

## Criterios de Aceptación (AC)

### AC1 – Validación

* Requests válidos v2 se procesan.
* Requests incompletos retornan 400.

### AC2 – Persistencia

* Se crean archivos esperados y rutas canon.
* `image_path` y `video_path` correctos.

### AC3 – asset_mode

* `STILL_ONLY` no llama a Veo.
* `IMAGE_1F_VIDEO` genera imagen + video.

### AC4 – Estados

* Estados transicionan correctamente.
* En error se guarda metadata.

### AC5 – Prompts

* Se generan usando campos semánticos v2.

---

## Casos de Prueba

1. Shot `IMAGE_1F_VIDEO` completo.
2. Shot `STILL_ONLY`.
3. Error forzado en Veo.
4. Normalización de `camera_move`.
5. Idempotencia básica.

---

## Definition of Done (DoD)

* Todos los AC pasan.
* Pruebas unitarias básicas.
* Prueba end-to-end con Kie.ai.
* Documentación del endpoint actualizada.
