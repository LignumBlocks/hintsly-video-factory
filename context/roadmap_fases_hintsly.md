# Roadmap por Fases – Hintsly Video Factory (MVP v0.1)

Este documento describe las **fases de implementación** del sistema y el **backlog de tickets** asociados a cada fase.
Las fases son: **Fase 0, Fase 1, Fase 2, Fase 3, Fase 4 y Fase 5**.

---

## 🧱 FASE 0 — Setup de Infraestructura

Objetivo: tener la base técnica lista (repos, Docker, estructura de carpetas, configuración básica).

### TICKET-001 — Crear repositorio del proyecto (GitHub)
- Crear un repo con carpetas iniciales:
  - `/engine`
  - `/n8n`
  - `/docs`
  - `/assets`

### TICKET-002 — Crear archivo `.env.example`
Variables de entorno base:
- `GEMINI_API_KEY`
- `VEO_API_KEY`
- `ASSETS_PATH`
- `ENGINE_PORT`
- `LOG_LEVEL`

### TICKET-003 — Configurar Docker para Hintsly Engine
- Dockerfile para Python 3.11.
- Instalar FastAPI + Uvicorn.
- Instalar `requests` y librerías auxiliares.

### TICKET-004 — Crear estructura de carpetas en el VPS
Rutas recomendadas:
- `/assets/videos`
- `/assets/tmp`
- `/engine`
- `/n8n`

### TICKET-005 — Montar volumen compartido para assets
- Definir volumen en Docker/Docker Compose.
- Asegurar que el Engine puede leer/escribir `/assets`.

### TICKET-006 — Configurar servicio systemd o Docker Compose
- Levantar `n8n` y `hintsly-engine` desde el mismo stack.
- Asegurar reinicio automático.

### TICKET-007 — Configurar logs rotativos del servidor
- `logrotate` o solución equivalente.
- Política básica de rotación y retención.

---

## 🟦 FASE 1 — Google Sheets + n8n

Objetivo: tener la interfaz de producción y la orquestación base funcionando.

### TICKET-101 — Crear plantilla Google Sheet `storyboard_master`
- Hoja con una fila por plano.
- Columnas:
  - `video_id, bloque, plano, descripcion_visual, funcion_narrativa, movimiento_camara, texto_voz_resumido, prompt_imagen, prompt_video, image_path, video_path, estado, error_message`.

### TICKET-102 — Conectar Google Sheets con n8n
- Configurar credenciales `google_sheets_hintsly`.
- Probar lectura básica de la hoja.

### TICKET-103 — Crear workflow n8n “Detectar planos LISTOS”
- Trigger recurrente (cada 2–5 min).
- Leer `storyboard_master`.
- Filtrar filas con `estado == "LISTO"`.
- Construir JSON de plano y llamar a `POST /shots/process` del Engine (mock al inicio).

### TICKET-104 — Crear workflow n8n “Actualizar fila después del Engine”
- Recibir respuesta del Engine.
- Actualizar la fila con:
  - `prompt_imagen`
  - `prompt_video`
  - `image_path`
  - `video_path`
  - `estado`
  - `error_message` (si aplica).

### TICKET-105 — Workflow n8n “Regenerar plano”
- Detectar `estado == "REGENERAR"`.
- Resetear campos de prompts y paths.
- Limpiar `error_message`.
- Poner estado en `LISTO` para que entre de nuevo al flujo principal.

### TICKET-106 — Validaciones básicas antes de enviar al Engine
- Validar que:
  - `video_id`, `bloque`, `plano`, `descripcion_visual`, `movimiento_camara` no estén vacíos.
- Si falta algo:
  - `estado = "ERROR"`
  - `error_message = "Faltan campos obligatorios"`.

---

## 🟩 FASE 2 — Hintsly Engine (Python) – Núcleo

Objetivo: implementar el motor de lógica de negocio que habla con n8n y controla la generación.

### TICKET-201 — Crear estructura del Hintsly Engine (Hexagonal)
- Carpetas:
  - `/domain`
  - `/usecases`
  - `/adapters`
  - `/infra`
  - `main.py` (punto de entrada).

### TICKET-202 — Definir entidad `Shot` (domain)
- Atributos:
  - `video_id, bloque, plano, descripcion_visual, movimiento_camara, prompt_imagen, prompt_video, image_path, video_path, estado, error_message`.

### TICKET-203 — Definir caso de uso `ProcessShot`
- Encapsular la lógica:
  - Validar datos.
  - Generar prompts si están vacíos.
  - Llamar a IA (imagen + video).
  - Devolver resultado estructurado.

### TICKET-204 — Definir caso de uso `RegenerateShot`
- Reutilizar `ProcessShot` con reglas de regeneración.
- Forzar limpieza de estados previos.

### TICKET-205 — Crear endpoint API `POST /shots/process`
- Recibir JSON de plano.
- Mapear a entidad `Shot`.
- Llamar al caso de uso.
- Devolver JSON con campos actualizados.

### TICKET-206 — Crear endpoint API `POST /shots/regenerate`
- Endpoint opcional/futuro.
- Permite flujos de regeneración directos.

### TICKET-207 — Crear adapter de sistema de archivos
- Funciones para:
  - Crear carpetas por video/bloque/plano.
  - Guardar imagen/video.
  - Guardar `metadata.json`.

### TICKET-208 — Crear adapter de logging estructurado
- JSON logs por plano y video.
- Niveles de log configurables.

### TICKET-209 — Definir y manejar clases de error estándar
- `PromptError, ImageGenerationError, VideoGenerationError, NetworkError`.
- Mapearlos a mensajes para n8n.

### TICKET-210 — Implementar sistema de reintentos
- Backoff simple (ej. 3 reintentos).
- Aplicable a llamadas IA y red.

---

## 🟥 FASE 3 — Integraciones IA (Imagen + Vídeo)

Objetivo: conectar el Engine con Gemini/NanoBanana y Veo 3.1 (Flow).

### TICKET-301 — Adapter `GeminiImageClient`
- Configurar endpoint y auth.
- Función `generate_image(prompt: str) -> url`.

### TICKET-302 — Lógica de generación de `prompt_imagen`
- A partir de `descripcion_visual` y parámetros del laboratorio.
- Usar LLM (si aplica) o plantillas.

### TICKET-303 — Llamar a Gemini y obtener URL de imagen
- Gestión de timeouts y errores.

### TICKET-304 — Descargar imagen y guardarla
- Guardar como:
  - `/assets/videos/{video_id}/block_{n}/shot_{m}/image.png`.

### TICKET-305 — Adapter `VeoVideoClient`
- Configurar Flow / Veo frame-to-video.
- Función `generate_video(image_path, prompt_video) -> url`.

### TICKET-306 — Lógica de generación de `prompt_video`
- A partir de `movimiento_camara` + contexto del plano.

### TICKET-307 — Llamar a Veo y obtener URL de clip
- Gestión de estados de job.

### TICKET-308 — Descargar clip y guardarlo
- Guardar como:
  - `/assets/videos/{video_id}/block_{n}/shot_{m}/clip.mp4`.

### TICKET-309 — Crear `metadata.json` por plano
- Incluir:
  - prompts usados, tiempos, tamaño de archivos, proveedor, versión de modelo.

### TICKET-310 — Manejo de errores en IA
- Mapear errores de Gemini/Veo a mensajes claros para `error_message`.

---

## 🟨 FASE 4 — Entregables para edición

Objetivo: facilitar el trabajo del editor humano (Premiere/DaVinci).

### TICKET-401 — Script para empaquetar un video en ZIP
- Recorrer `/assets/videos/{video_id}`.
- Crear ZIP con toda la estructura de bloques/planos.

### TICKET-402 — Endpoint `/videos/export/{video_id}`
- Devolver enlace o ruta del ZIP.
- Usado por n8n o manualmente.

### TICKET-403 — Añadir campo `export_path` en el Sheet
- Guardar la ruta del ZIP para cada `video_id`.

### TICKET-404 — Exportar JSON/CSV de timeline
- Listado ordenado por:
  - `bloque`, `plano`, `video_path`.

### TICKET-405 — (Opcional) Generar timeline OTIO/XML
- Formato compatible con Premiere/DaVinci.
- Automatizar el rough cut.

---

## 🟫 FASE 5 — Observabilidad y operación

Objetivo: poder operar y mejorar la fábrica como un sistema profesional.

### TICKET-501 — Dashboard simple en el Sheet
- Usar fórmulas/pivot para mostrar:
  - nº de planos por estado.
  - nº de vídeos listos.

### TICKET-502 — Indicador “vídeo listo para edición”
- Regla:
  - Si todos los planos de un `video_id` están en `COMPLETADO`, marcar el `video_id` como `LISTO_PARA_EDICION`.

### TICKET-503 — Exportar métricas básicas
- Desde logs o Sheet:
  - Tiempo medio por plano.
  - % de errores por proveedor.

### TICKET-504 — Log viewer básico
- CLI simple o endpoint del Engine para leer últimos N logs.

### TICKET-505 — Endpoint `/health` para el Engine
- Devuelve:
  - estado de la app.
  - conexión a servicios clave (IA, FS, etc.).

---

## ✅ Resumen total

- **Fase 0**: Infraestructura base (7 tickets).
- **Fase 1**: Google Sheets + n8n (6 tickets).
- **Fase 2**: Engine core en Python (10 tickets).
- **Fase 3**: Integraciones IA imagen/vídeo (10 tickets).
- **Fase 4**: Entregables para edición (5 tickets).
- **Fase 5**: Observabilidad y operación (5 tickets).

Total aproximado: **43 tickets** para un MVP potente y escalable.
