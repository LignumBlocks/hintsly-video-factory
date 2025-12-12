# Flujo de Aplicación Hintsly Video Factory

Este documento describe el flujo completo de la aplicación desde que se recibe una solicitud hasta que se genera el video final o se reporta un error.

## 1. Entrada (API Request)
**Endpoint**: `POST /shots/process`
**Entrada**: Objeto `Shot`
```json
{
  "video_id": "test_001",
  "bloque": "1",
  "plano": 1,
  "descripcion_visual": "Un coche vintage en La Habana...",
  "movimiento_camara": "Dolly forward"
}
```

## 2. Orquestación (UseCase: ProcessShot)
El caso de uso `ProcessShot` coordina todos los pasos secuenciales.

### Paso 2.1: Generación de Prompts
- **Servicio**: `PromptService`
- **Acción**:
  - Genera prompt de imagen optimizado (estilo cinematográfico).
  - Genera prompt de video (movimiento + descripción).
- **Resultado**: `prompt_imagen`, `prompt_video` en el objeto Shot.

### Paso 2.2: Generación de Imagen (Kie.ai Nano Banana)
- **Adaptador**: `KieNanoBananaClient`
- **Acción**:
  1. Envía solicitud a `POST /api/v1/jobs/createTask` (Modelo: `google/nano-banana`).
  2. Recibe `taskId`.
  3. **Polling**: Consulta estado en `/api/v1/jobs/recordInfo` cada 3s.
  4. Al completar, descarga la imagen desde la URL retornada.
- **Persistencia**: Se guarda en `assets/videos/{video_id}/block_{bloque}/shot_{plano}/image.png`.

### Paso 2.3: Generación de Video (Kie.ai Veo)
- **Adaptador**: `KieVeoClient`
- **Acción**:
  1. Convierte la ruta local de la imagen a URL pública (`PUBLIC_BASE_URL`).
  2. Envía solicitud a `POST /api/v1/veo/generate` (Modelo: `veo3_fast`, image-to-video).
  3. Recibe `taskId`.
  4. **Polling**: Consulta estado en `/api/v1/veo/record-info` cada 10s.
  5. Al completar, descarga el video desde la URL retornada.
- **Persistencia**: Se guarda en `assets/videos/{video_id}/block_{bloque}/shot_{plano}/video.mp4`.

### Paso 2.4: Guardado de Metadatos
- **Adaptador**: `FSAdapter`
- **Acción**: Guarda un JSON con toda la información del shot (prompts, paths, timestamps, estado).
- **Ruta**: `assets/videos/{video_id}/block_{bloque}/shot_{plano}/metadata.json`.

## 3. Salida (Response)
Retorna el objeto `Shot` actualizado.

**Éxito (`estado: COMPLETO`):**
```json
{
  "video_id": "test_001",
  ...
  "image_path": ".../image.png",
  "video_path": ".../video.mp4",
  "estado": "COMPLETO"
}
```

**Error (`estado: ERROR`):**
Cualquier excepción capturada (API caída, timeout, error de validación) actualiza el estado.
```json
{
  "video_id": "test_001",
  ...
  "estado": "ERROR",
  "error_message": "Kie.ai Veo error: Invalid model..."
}
```

## Diagrama de Secuencia Simplificado

1. **Cliente** -> `POST /shots/process`
2. **ProcessShot** -> `PromptService` (Crea prompts)
3. **ProcessShot** -> `KieNanoBananaClient` (Genera Imagen)
   - *Loop Polling...*
   - Guarda `image.png`
4. **ProcessShot** -> `KieVeoClient` (Genera Video)
   - *Upload URL Pública*
   - *Loop Polling...*
   - Guarda `video.mp4`
5. **ProcessShot** -> `FSAdapter` (Guarda `metadata.json`)
6. **API** -> Retorna `Shot` (Completo o Error)
