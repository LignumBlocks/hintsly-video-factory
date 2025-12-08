# TICKET 207 — Crear adapter de sistema de archivos

## 🎯 Objetivo
Gestionar creación de carpetas y guardado de assets.

## ✔️ Descripción
El adapter debe:

- Crear rutas `/assets/videos/{video_id}/block_{n}/shot_{m}`
- Guardar imágenes y videos.
- Retornar paths absolutos al Engine.

## ✔️ Criterios de aceptación
- Funciona con URLs mock.
- Almacena archivos dummy correctamente.
