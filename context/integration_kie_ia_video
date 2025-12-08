
# 📘 Fase 3 — Integración con KIE.ai para generación de video  
## Requisitos + Cambios necesarios en el Engine + Instrucciones para servir imágenes públicamente

Este documento explica **qué debe modificarse** en el Hintsly Engine para usar **KIE.ai** como proveedor de video, cumpliendo el requisito de que **la imagen debe ser accesible públicamente**, incluso dentro del entorno actual basado en Docker + Traefik.

---

# 1️⃣ Requisito clave de KIE.ai

KIE.ai exige que la imagen usada para generar video esté accesible mediante una **URL pública**.

❌ No funciona pasar un path local como:  
`/assets/videos/.../image.png`

✔ Debe ser una URL accesible desde Internet, ejemplo:  
`https://factory.hintsly.io/assets/videos/.../image.png`

---

# 2️⃣ Servir imágenes públicamente desde FastAPI

Modifica `main.py` para montar `/assets` como static files:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Sirve todos los archivos dentro de /assets
app.mount("/assets", StaticFiles(directory="/assets"), name="assets")
```

Esto hace que cualquier archivo en `/assets/videos/...` sea accesible vía:

```
https://{TU_DOMINIO}/assets/videos/{video_id}/block_{bloque}/shot_{plano}/image.png
```

---

# 3️⃣ Configuración de dominio con Traefik

En `docker-compose.yml`, asegúrate de exponer el engine:

```yaml
labels:
  - "traefik.http.routers.hintsly-engine.rule=Host(`factory.hintsly.io`)"
```

Con esto, tu engine es accesible públicamente como:

```
https://factory.hintsly.io
```

➡️ Ya podrás compartir imágenes con KIE.ai.

---

# 4️⃣ Cambios necesarios en FSAdapter

Agregar soporte para:

- `local_path` (ruta interna en Docker)
- `public_url` (URL pública que usará KIE.ai)

Ejemplo:

```python
def save_image(self, shot, image_bytes):
    local_dir = f"{self.base_path}/{shot.video_id}/block_{shot.bloque}/shot_{shot.plano}"
    os.makedirs(local_dir, exist_ok=True)

    local_path = os.path.join(local_dir, "image.png")

    with open(local_path, "wb") as f:
        f.write(image_bytes)

    public_url = f"{self.base_url}/{shot.video_id}/block_{shot.bloque}/shot_{shot.plano}/image.png"

    return local_path, public_url
```

Variables de entorno necesarias:

```
ASSETS_BASE_PATH=/assets/videos
ASSETS_BASE_URL=https://factory.hintsly.io/assets/videos
```

---

# 5️⃣ Modificación del modelo Shot

Agregar un campo nuevo:

```python
image_url: Optional[str]
```

### Ahora el Shot tiene:

- `image_path` → ruta local  
- `image_url` → URL pública  

---

# 6️⃣ Cliente KIE.ai (antes VeoClient)

KIE.ai requiere un POST con un JSON que incluya `image_url` y `prompt`.

Ejemplo:

```python
class KieVeoClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate(self, image_url, prompt_video):
        url = f"{self.base_url}/api/v1/veo/generate"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "image_url": image_url,
            "prompt": prompt_video
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()

        return resp.json()["video_url"]
```

Variables de entorno:

```
VEO_BASE_URL=https://api.kie.ai
VEO_API_KEY=TU_API_KEY_DE_KIE_AI
```

---

# 7️⃣ Cambios en ProcessShot

Después de generar la imagen:

```python
shot.image_path, shot.image_url = fs.save_image(...)
```

Y el cliente:

```python
video_url = kie_client.generate(
    image_url=shot.image_url,
    prompt_video=shot.prompt_video
)
```

👉 **Nunca enviar `image_path` a KIE.ai. Solo `image_url`.**

---

# 8️⃣ Resumen final para el agente

1. Montar `/assets` como static files en FastAPI.  
2. Confirmar que Traefik expone el dominio del engine.  
3. Actualizar FSAdapter para devolver `image_path` + `image_url`.  
4. Añadir `image_url` al modelo Shot.  
5. Crear `KieVeoClient` que envía JSON `{ image_url, prompt }`.  
6. Usar variables de entorno:
   ```
   ASSETS_BASE_PATH=/assets/videos
   ASSETS_BASE_URL=https://factory.hintsly.io/assets/videos
   VEO_BASE_URL=https://api.kie.ai
   VEO_API_KEY=<tu_key>
   ```
7. Procesar video siempre con `image_url`.

---

# ✅ Con esto tu agente puede integrar KIE.ai sin bloquear el flujo actual del Engine.
