# Deployment Instructions for Production Server

## Resumen
Este documento explica cómo desplegar Hintsly Engine en el servidor de producción con Traefik y acceso público para Kie.ai.

## Pre-requisitos

1. Servidor con Docker y Docker Compose instalados
2. Dominio configurado (ej: `engine.tu-dominio.com`)
3. Traefik ya configurado (según tu docker-compose actual)
4. API Key de Kie.ai

## Pasos de Deployment

### 1. Preparar el Servidor

```bash
# Conectar al servidor
ssh usuario@tu-servidor

# Navegar al directorio del proyecto
cd /opt/hintsly-video-factory

# Hacer pull de los últimos cambios
git pull origin main
```

### 2. Configurar Variables de Entorno

```bash
# Copiar el ejemplo
cp .env.production.example .env

# Editar con tus valores reales
nano .env
```

Configurar:
```env
# Traefik / SSL
SSL_EMAIL=tu_email@ejemplo.com
DOMAIN_NAME=tu-dominio.com
SUBDOMAIN=n8n
ENGINE_SUBDOMAIN=engine  # El engine estará en engine.tu-dominio.com
GENERIC_TIMEZONE=America/New_York

# Kie.ai API
KIE_API_KEY=tu_clave_kie_real

# Google API (opcional)
GEMINI_API_KEY=tu_clave_google
VEO_API_KEY=tu_clave_veo
```

### 3. Verificar el Dockerfile

Asegúrate de que `engine/Dockerfile` existe:

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

### 4. Construir y Desplegar

```bash
# Detener el contenedor anterior (si existe)
docker-compose stop hintsly-engine

# Reconstruir la imagen
docker-compose build hintsly-engine

# Iniciar el contenedor
docker-compose up -d hintsly-engine

# Verificar logs
docker-compose logs -f hintsly-engine
```

### 5. Verificar el Deployment

```bash
# Verificar que el contenedor está corriendo
docker-compose ps

# Verificar logs
docker-compose logs hintsly-engine | tail -50

# Probar el endpoint de docs
curl https://engine.tu-dominio.com/docs

# Probar acceso a assets
curl https://engine.tu-dominio.com/assets/
```

### 6. Probar la Generación End-to-End

Desde tu máquina local, puedes hacer una petición al servidor:

```bash
curl -X POST "https://engine.tu-dominio.com/shots/process" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "test_001",
    "bloque": "1",
    "plano": 1,
    "descripcion_visual": "A vintage car in Havana",
    "movimiento_camara": "Dolly forward"
  }'
```

## Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs hintsly-engine

# Verificar que el Dockerfile existe
ls -la /opt/hintsly-video-factory/engine/Dockerfile

# Verificar permisos
sudo chown -R $USER:$USER /opt/hintsly-video-factory
```

### Problema: Traefik no rutea al engine

```bash
# Verificar labels de Traefik
docker inspect hintsly-video-factory-hintsly-engine-1 | grep traefik

# Verificar que el dominio apunta al servidor
nslookup engine.tu-dominio.com

# Verificar logs de Traefik
docker-compose logs traefik | grep hintsly
```

### Problema: Assets no son accesibles

```bash
# Verificar que el directorio existe
ls -la /opt/hintsly-video-factory/assets

# Crear si no existe
mkdir -p /opt/hintsly-video-factory/assets/videos

# Verificar permisos
chmod -R 755 /opt/hintsly-video-factory/assets

# Probar acceso directo
curl https://engine.tu-dominio.com/assets/
```

### Problema: Kie.ai no puede acceder a las imágenes

```bash
# Verificar que PUBLIC_BASE_URL está configurado
docker-compose exec hintsly-engine env | grep PUBLIC_BASE_URL

# Debe mostrar: PUBLIC_BASE_URL=https://engine.tu-dominio.com

# Probar acceso externo a una imagen de prueba
# (crear una imagen de prueba primero)
curl https://engine.tu-dominio.com/assets/test.jpg
```

### Problema: "Invalid model" en Veo

Verificar que el modelo es correcto:
- Modelos válidos: `veo3`, `veo3-fast`
- NO válidos: `veo3-1-fast`, `veo3.1`

```bash
# Verificar variable
docker-compose exec hintsly-engine env | grep KIE_VEO_MODEL

# Debe mostrar: KIE_VEO_MODEL=veo3-fast
```

## Monitoreo

### Ver logs en tiempo real

```bash
docker-compose logs -f hintsly-engine
```

### Verificar uso de recursos

```bash
docker stats hintsly-video-factory-hintsly-engine-1
```

### Verificar espacio en disco (assets)

```bash
du -sh /opt/hintsly-video-factory/assets/
```

## Mantenimiento

### Actualizar el código

```bash
cd /opt/hintsly-video-factory
git pull origin main
docker-compose build hintsly-engine
docker-compose up -d hintsly-engine
```

### Limpiar assets antiguos

```bash
# Eliminar videos de más de 7 días
find /opt/hintsly-video-factory/assets/videos -type f -mtime +7 -delete
```

### Backup de assets

```bash
# Crear backup
tar -czf assets-backup-$(date +%Y%m%d).tar.gz /opt/hintsly-video-factory/assets/

# Mover a ubicación segura
mv assets-backup-*.tar.gz /backup/
```

## Configuración Importante

### PUBLIC_BASE_URL

Esta variable es **CRÍTICA** para que Kie.ai Veo pueda acceder a las imágenes:

- ✅ Correcto: `https://engine.tu-dominio.com`
- ❌ Incorrecto: `http://localhost:8000`
- ❌ Incorrecto: `http://127.0.0.1:8000`

La URL debe ser:
1. Accesible desde internet
2. Con HTTPS (Traefik maneja esto)
3. Sin trailing slash

### Modelos de Kie.ai

- **Imagen**: `google/nano-banana` (Gemini 2.5 Flash)
- **Video**: `veo3-fast` (Veo 3 Fast) o `veo3` (Veo 3 Quality)

## Próximos Pasos

Una vez desplegado y verificado:

1. Integrar con n8n para automatización
2. Configurar webhooks para notificaciones
3. Implementar sistema de colas para múltiples videos
4. Agregar monitoreo con Prometheus/Grafana
