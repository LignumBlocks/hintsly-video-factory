# 🚀 Plan Detallado — Fase 2: Construcción del Hintsly Engine (Python)

La **Fase 2** tiene como objetivo transformar el engine mock actual en un **motor real**, modular, extensible y totalmente integrado con n8n y el pipeline de producción.

Este documento define **qué hacer, en qué orden, y qué archivos crear** para implementar los TICKETS 201–210 del roadmap oficial.

---

# 🎯 Objetivo de la Fase 2

Construir un motor capaz de:

- Gestionar entidades del dominio (Shot)
- Generar prompts (versión mock realista en esta fase)
- Descargar/almacenar assets en `/assets/videos/...`
- Integrarse con FastAPI mediante endpoints sólidos
- Manejar errores y reintentos
- Registrar logs estructurados

El engine quedará listo para conectar IA real en la Fase 3.

---

# 🧱 PARTE 1 — Arquitectura Base (Tickets 201–202)

## ✅ 1. Crear estructura de carpetas  
**TICKET 201**

Dentro de `/engine`:

```
engine/
│
├── main.py               # FastAPI entrypoint
├── domain/
│   ├── entities.py       # Modelo Shot
│   └── errors.py         # Excepciones personalizadas
│
├── usecases/
│   ├── process_shot.py
│   ├── regenerate_shot.py
│   └── utils_prompt.py   # Generación de prompts mock
│
├── adapters/
│   ├── fs_adapter.py     # Manejo de archivos y rutas
│   ├── gemini_client.py  # IA imagen (Fase 3)
│   ├── veo_client.py     # IA video (Fase 3)
│   └── logger.py         # Logging estructurado
│
└── infra/
    ├── config.py         # Variables de entorno
    └── paths.py          # Construcción de rutas
```

---

## ✅ 2. Crear la entidad `Shot`  
**TICKET 202**

Archivo: `engine/domain/entities.py`

```python
from pydantic import BaseModel
from typing import Optional

class Shot(BaseModel):
    video_id: str
    bloque: str
    plano: int
    descripcion_visual: str
    movimiento_camara: str
    prompt_imagen: Optional[str] = None
    prompt_video: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    estado: Optional[str] = None
    error_message: Optional[str] = None
```

---

# ⚙️ PARTE 2 — Casos de Uso (Tickets 203–204)

## ✅ 3. Crear `ProcessShot`  
**TICKET 203**

Responsabilidades:

1. Validar datos del Shot  
2. Generar prompts (mock/plantilla)  
3. Llamar al servicio de imagen  
4. Guardar imagen  
5. Llamar al servicio de video  
6. Guardar video  
7. Retornar el Shot actualizado para n8n  


## Ejemplo:

```python
class ProcessShot:

    def __init__(self, fs, prompt_service, image_client, video_client):
        self.fs = fs
        self.prompt_service = prompt_service
        self.image_client = image_client
        self.video_client = video_client

    def execute(self, shot: Shot) -> Shot:

        # 1. Generación de prompts
        if not shot.prompt_imagen:
            shot.prompt_imagen = self.prompt_service.generate_image_prompt(shot)

        if not shot.prompt_video:
            shot.prompt_video = self.prompt_service.generate_video_prompt(shot)

        # 2. Generar imagen
        img_url = self.image_client.generate(shot.prompt_imagen)
        shot.image_path = self.fs.save_image(shot, img_url)

        # 3. Generar video
        vid_url = self.video_client.generate(shot.image_path, shot.prompt_video)
        shot.video_path = self.fs.save_video(shot, vid_url)

        shot.estado = "COMPLETADO"
        return shot
```

---

## ✅ 4. Crear `RegenerateShot`  
**TICKET 204**

```python
class RegenerateShot:
    def __init__(self, process_shot):
        self.process_shot = process_shot

    def execute(self, shot: Shot) -> Shot:
        shot.prompt_imagen = None
        shot.prompt_video = None
        shot.image_path = None
        shot.video_path = None
        return self.process_shot.execute(shot)
```

---

# 🌐 PARTE 3 — Endpoints API (Tickets 205–206)

## ✅ 5. Crear endpoints reales

### `/shots/process`
### `/shots/regenerate`

Ejemplo en `main.py`:

```python
@app.post("/shots/process")
def process_shot(req: ShotRequest):
    shot = Shot(**req.dict())
    result = process_shot_usecase.execute(shot)
    return result.dict()
```

Estos endpoints serán consumidos directamente por n8n.

---

# 📁 PARTE 4 — Adapters (Tickets 207–210)

## ✅ 6. Sistema de archivos  
**TICKET 207**

Responsable de:

- Crear carpetas por video/bloque/plano  
- Guardar imagen y video descargados  
- Mantener estructura limpia:

```
/assets/videos/{video_id}/block_{n}/shot_{m}/image.png
```

---

## ✅ 7. Logging estructurado  
**TICKET 208**

`adapters/logger.py`:

```python
import logging
logger = logging.getLogger("hintsly")
```

---

## ✅ 8. Clases de error estándar  
**TICKET 209**

```python
class PromptError(Exception): pass
class ImageGenerationError(Exception): pass
class VideoGenerationError(Exception): pass
class NetworkError(Exception): pass
```

---

## ✅ 9. Reintentos  
**TICKET 210**

```python
for attempt in range(3):
    try:
        return call_api()
    except Exception:
        if attempt == 2:
            raise
        time.sleep(2)
```

---

# 🧪 PARTE 5 — Pruebas funcionales

### 🔹 **Test 1 — Proceso normal desde n8n**
- Enviar plano  
- Ver prompts generados  
- Ver assets guardados  
- Ver retorno correcto a n8n  
- Ver fila actualizada

### 🔹 **Test 2 — Regeneración**
- Cambiar estado a `REGENERAR`  
- Validar que se limpia todo  
- Validar que se genera nuevamente

---

# 🏁 Resultado esperado de la Fase 2

Al completar este plan tendrás:

- Un Engine real, modular y preparado para IA  
- Un pipeline estable listo para producción  
- Un backend que cumple las reglas de diseño (hexagonal)  
- La base para implementar IA en la **Fase 3**

---

# ✔️ ¿Qué sigue después?

Fase 3: Integraciones reales  
- Gemini (imagen)  
- Veo 3.1 Flow (video)  
- Metadata  
- Manejo avanzado de errores  

Este plan deja el engine totalmente listo para recibir estas integraciones.

