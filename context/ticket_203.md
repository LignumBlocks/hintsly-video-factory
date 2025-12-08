# TICKET 203 — Definir caso de uso `ProcessShot`

## 🎯 Objetivo
Encapsular la lógica de generación completa de un plano.

## ✔️ Descripción
El caso de uso debe:

1. Validar datos del `Shot`.
2. Generar prompts si están vacíos.
3. Llamar al adapter de imagen.
4. Guardar la imagen en `/assets/videos/...`.
5. Llamar al adapter de video.
6. Guardar el clip.
7. Retornar un `Shot` actualizado.

## ✔️ Criterios de aceptación
- Archivo `process_shot.py` implementado.
- Funciona con adapters mock.
