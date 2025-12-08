# TICKET 205 — Crear endpoint API `POST /shots/process`

## 🎯 Objetivo
Permitir que n8n envíe un plano para procesarlo.

## ✔️ Descripción
- Crear endpoint FastAPI.
- Recibir JSON → mapear a Shot.
- Llamar al caso de uso `ProcessShot`.
- Retornar JSON actualizado.

## ✔️ Criterios de aceptación
- Endpoint funcionando vía Docker.
- Valida correctamente input y errores.
