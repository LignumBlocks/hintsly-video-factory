# Ticket Técnico – Backend Orchestrator ProcessShot v2

## ID

TICKET-F3-BACKEND-PROCESSSHOT-V2

## Objetivo

Actualizar el caso de uso `ProcessShot` para soportar el **Shot Schema v2 (Hintsly Lab Canon)**, ejecutando el pipeline de generación de assets de forma condicional según `asset_mode` y gestionando correctamente estados, rutas y errores.

---

## Alcance Técnico

* Modificar el endpoint `POST /shots/process` para aceptar `ShotV2`.
* Actualizar el flujo del orquestador para:

  * manejar `PENDIENTE → EN_PROCESO → COMPLETADO / ERROR`.
  * ramificar la ejecución según `asset_mode`.
* Garantizar persistencia de `metadata.json` en todos los casos.

---

## Tareas

1. Adaptar controlador / router para recibir `ShotV2`.
2. En `ProcessShot`:

   * Validar estado inicial (`PENDIENTE`).
   * Setear `EN_PROCESO` al iniciar.
   * Llamar a servicios de prompt, imagen y video según `asset_mode`.
   * Setear `COMPLETADO` al finalizar con éxito.
   * Capturar excepciones y setear `ERROR` + `error_message`.
3. Construir rutas canon:
   `assets/videos/{video_id}/block_{block_id}/shot_{shot_id}/`.
4. Escribir siempre `metadata.json`.

---

## Criterios de Aceptación

* Shots `STILL_ONLY` no llaman a Veo.
* Shots `IMAGE_1F_VIDEO` generan imagen + video.
* Estados y rutas se actualizan correctamente.
* En error, el shot retorna `ERROR` y metadata existe.

---

## Dependencias

* Modelo `ShotV2` (Dominio).
* Adapters KieNanoBananaClient y KieVeoClient.

---

## Definition of Done

* Flujo v2 funcionando end-to-end.
* Logs con `video_id/block_id/shot_id`.
* Prueba manual exitosa con un shot real.
