# TICKET 210 — Implementar sistema de reintentos

## 🎯 Objetivo
Dar resiliencia a integraciones externas (IA, red).

## ✔️ Descripción
- Aplicar reintentos en:
  - adapter de imagen
  - adapter de video
- Usar backoff simple.

## ✔️ Criterios de aceptación
- Fallos intermitentes no rompen workflow.
- Logs registran intentos.
