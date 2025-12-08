# TICKET 304 — Descargar y guardar imagen

## Objetivo
Guardar la imagen generada por Gemini.

## Descripción
- Implementar `FSAdapter.save_image`.
- Crear carpetas según estructura:
```
/assets/videos/{video_id}/block_{bloque}/shot_{plano}/image.png
```

## Criterios de aceptación
- Archivo descargado y accesible.
