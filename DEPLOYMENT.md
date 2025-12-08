# Hintsly Video Factory - Deployment Guide

## Configuración de Producción

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
# Kie.ai API (para generación de imágenes y videos)
KIE_API_KEY=tu_clave_kie_aqui
KIE_API_BASE=https://api.kie.ai
KIE_NANO_BANANA_MODEL=google/nano-banana
KIE_VEO_MODEL=veo3-1-fast

# URL pública del servidor (IMPORTANTE para Veo)
# Debe ser accesible desde internet para que Kie.ai pueda descargar las imágenes
PUBLIC_BASE_URL=https://tu-dominio.com

# Google API (legacy/fallback - opcional)
GEMINI_API_KEY=tu_clave_google_aqui
```

### 2. Docker Compose

Crea `docker-compose.yml`:

```yaml
version: '3.8'

services:
  hintsly-engine:
    build:
      context: ./engine
      dockerfile: Dockerfile
    restart: always
    environment:
      - KIE_API_KEY=${KIE_API_KEY}
      - KIE_API_BASE=${KIE_API_BASE}
      - KIE_NANO_BANANA_MODEL=${KIE_NANO_BANANA_MODEL}
      - KIE_VEO_MODEL=${KIE_VEO_MODEL}
      - PUBLIC_BASE_URL=${PUBLIC_BASE_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./assets:/app/assets
    ports:
      - "8000:8000"
    command: uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Dockerfile

Crea `engine/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Nginx Reverse Proxy (Recomendado)

Para producción, usa Nginx como reverse proxy:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Proxy to FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (assets)
    location /assets/ {
        proxy_pass http://localhost:8000/assets/;
        proxy_set_header Host $host;
    }

    # Increase timeouts for video generation
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
}
```

### 5. Deployment Steps

1. **Clonar el repositorio:**
   ```bash
   git clone <repo-url>
   cd hintsly-video-factory
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus claves
   ```

3. **Construir y ejecutar:**
   ```bash
   docker-compose up -d --build
   ```

4. **Verificar logs:**
   ```bash
   docker-compose logs -f hintsly-engine
   ```

5. **Probar el endpoint:**
   ```bash
   curl http://localhost:8000/docs
   ```

### 6. Consideraciones Importantes

#### URL Pública
- `PUBLIC_BASE_URL` **debe ser accesible desde internet**
- Kie.ai Veo necesita descargar las imágenes desde esta URL
- En desarrollo local, puedes usar ngrok:
  ```bash
  ngrok http 8000
  # Usar la URL de ngrok como PUBLIC_BASE_URL
  ```

#### Almacenamiento
- Las imágenes y videos se guardan en `./assets/videos/`
- Este directorio está montado como volumen en Docker
- Considera usar almacenamiento en la nube (S3, GCS) para producción

#### Seguridad
- No expongas las claves API en el código
- Usa HTTPS en producción
- Considera agregar autenticación a los endpoints

### 7. Monitoreo

Agregar health check al docker-compose:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 8. Escalabilidad

Para manejar múltiples requests concurrentes:

```yaml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

### 9. Troubleshooting

**Problema:** Veo no puede acceder a las imágenes
- **Solución:** Verifica que PUBLIC_BASE_URL sea accesible desde internet
- Prueba: `curl ${PUBLIC_BASE_URL}/assets/videos/test/...`

**Problema:** Timeouts en generación de video
- **Solución:** Aumenta los timeouts en Nginx y Docker
- Veo puede tomar 2-5 minutos por video

**Problema:** Imágenes no se sirven
- **Solución:** Verifica que el directorio assets esté montado correctamente
- Revisa permisos: `chmod -R 755 assets/`
