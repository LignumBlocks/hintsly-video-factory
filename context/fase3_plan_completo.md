# 📘 Plan Detallado — Fase 3: Integraciones IA (Imagen + Vídeo)
**Hintsly Video Factory — MVP v0.1**

Esta fase conecta el Hintsly Engine construido en la Fase 2 con **Gemini/NanoBanana Pro** (para imágenes) y **Veo 3.1 / Flow** (para vídeo), siguiendo los tickets 301–310 del roadmap.

---

# 🎯 1. Objetivo General

Implementar integraciones reales con proveedores IA que permitan:

- Generar prompts reales (imagen y vídeo).
- Llamar a Gemini/NanoBanana → obtener imagen.
- Llamar a Veo 3.1 (Flow) → obtener clip animado.
- Descargar y guardar archivos en `/assets/videos/{video_id}/block_x/shot_y/`.
- Crear metadata por plano.
- Manejar errores de forma robusta.
- Devolver datos finales a n8n para actualizar Google Sheets.

---

# 🧩 2. Tickets incluidos en esta fase

### Adaptadores IA  
- **TICKET-301** — Adapter `GeminiImageClient`  
- **TICKET-305** — Adapter `VeoVideoClient`

### Prompting  
- **TICKET-302** — Generación del `prompt_imagen`  
- **TICKET-306** — Generación del `prompt_video`

### Flujo IA  
- **TICKET-303** — Llamar a Gemini (imagen)  
- **TICKET-307** — Llamar a Veo 3.1 (video)

### Descarga y almacenamiento  
- **TICKET-304** — Guardar imagen  
- **TICKET-308** — Guardar video

### Metadata & errores  
- **TICKET-309** — Crear `metadata.json`  
- **TICKET-310** — Manejo profesional de errores

---

# 🧱 3. Prerrequisitos (Fase 2 completada)

La Fase 2 dejó:

- Arquitectura hexagonal real.
- Endpoints `/shots/process` listos.
- FSAdapter operativo.
- Casos de uso `ProcessShot` y `RegenerateShot`.
- Logging y entidades del dominio.

---

# ⚙️ 4. Plan Detallado Paso a Paso

## 🟦 Paso 1 — Implementar `GeminiImageClient`
Archivo: `engine/adapters/gemini_client.py`

### Responsabilidades
- Autenticación.
- Enviar prompt.
- Recibir imagen (URL/base64).
- Normalizar respuesta.

### Interfaz
```python
class GeminiImageClient:
    def generate_image(self, prompt: str) -> str:
        ...
```

---

## 🟦 Paso 2 — Lógica de `prompt_imagen`
Archivo: `usecases/utils_prompt.py`

Basado en descripción visual + estilo cinematográfico del laboratorio.

---

## 🟦 Paso 3 — Guardar imagen
Ruta final:
```
/assets/videos/{video_id}/block_{bloque}/shot_{plano}/image.png
```

---

## 🟦 Paso 4 — Implementar `VeoVideoClient`
Archivo: `engine/adapters/veo_client.py`

### Función
```python
generate_video(image_path, prompt_video) -> url
```

---

## 🟦 Paso 5 — Lógica de `prompt_video`
Basado en:
- movimiento_camara  
- estilo cinematográfico  

Ej.: “Smooth dolly-in…”, “Parallax camera movement…”

---

## 🟦 Paso 6 — Descargar clip
Guardar como:
```
clip.mp4
```

---

## 🟦 Paso 7 — metadata.json
Ejemplo:
```json
{
  "video_id": "",
  "bloque": "",
  "plano": "",
  "prompt_imagen": "",
  "prompt_video": "",
  "image_path": "",
  "video_path": "",
  "provider_image": "Gemini",
  "provider_video": "Veo 3.1",
  "generated_at": "timestamp"
}
```

---

## 🟦 Paso 8 — Integración en `ProcessShot`
Flujo final:

1. Generar prompts  
2. Generar imagen  
3. Guardarla  
4. Generar vídeo  
5. Guardarlo  
6. Crear metadata  
7. Retornar Shot actualizado  

---

## 🟦 Paso 9 — Manejo de errores IA
Reglas:

- Si falla imagen: `ERROR` + mensaje  
- Si falla video: `ERROR` + mensaje  
- El engine siempre devuelve JSON válido  

---

## 🟦 Paso 10 — Pruebas E2E

### Camino feliz  
Imagen + vídeo generados, metadata creada.

### Error en imagen  
No se intenta video.

### Error en video  
Imagen guardada, error en video.

### Regeneración  
Limpia campos → generar todo de nuevo.

---

# 🏁 5. Resultado Final Esperado

- Engine conectado a IA real.  
- Imágenes y vídeos generados automáticamente.  
- Metadata detallada por plano.  
- Assets organizados para edición.  

---

# ✔ La Fábrica queda totalmente operativa

A partir de esta fase, la fábrica produce **vídeos completos y reales** plano por plano.
