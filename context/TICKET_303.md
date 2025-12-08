# TICKET 303 — Llamar a Gemini y obtener URL

## Objetivo
Integrar Gemini para obtener la URL de imagen.

## Descripción
- Usar GeminiImageClient.
- Enviar prompt generado.
- Obtener la URL.

## Criterios de aceptación
- Manejo de timeouts.
- Reintentos automáticos.
- Si falla → error IMAGE_ERROR.
