# TICKET 204 — Definir caso de uso `RegenerateShot`

## 🎯 Objetivo
Permitir regenerar un plano limpiando estados previos.

## ✔️ Descripción
El caso de uso debe:

- Resetear prompts, paths y errores.
- Invocar nuevamente a `ProcessShot`.

## ✔️ Criterios de aceptación
- Archivo `regenerate_shot.py` implementado.
- Puede ser llamado desde el endpoint o n8n.
