# TICKET 206 — Crear endpoint API `POST /shots/regenerate`

## 🎯 Objetivo
Permitir regenerar un plano completo desde n8n.

## ✔️ Descripción
- Recibir JSON.
- Construir entidad Shot.
- Ejecutar caso de uso `RegenerateShot`.
- Retornar Shot actualizado.

## ✔️ Criterios de aceptación
- Endpoint activo en FastAPI.
- Regeneración completa funcional.
