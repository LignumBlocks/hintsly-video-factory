# TICKET 305 — Adapter VeoVideoClient

## Objetivo
Implementar cliente para Veo 3.1 Flow.

## Descripción
- Crear archivo `engine/adapters/veo_client.py`.
- Implementar método `generate_video(image_path, prompt_video)`.
- Manejar jobs async.

## Criterios de aceptación
- Detectar estados del job.
- Retornar URL final del video.
