# TICKET 301 — Adapter GeminiImageClient

## Objetivo
Implementar el cliente para la generación de imágenes con Gemini/NanoBanana.

## Descripción
- Crear archivo `engine/adapters/gemini_client.py`.
- Implementar autenticación mediante API key.
- Crear método `generate_image(prompt: str) -> str`.
- Manejar timeouts, errores y reintentos.

## Responsabilidades
- Construir payload.
- Enviar prompt.
- Recibir imagen (URL/base64).
- Validar y retornar la URL.

## Criterios de aceptación
- Si la llamada es exitosa → retorna URL válida.
- Si falla → lanza `ImageGenerationError`.
