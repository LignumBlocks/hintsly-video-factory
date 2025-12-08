
# Resumen Oficial — Cierre de Fase 0 (Infraestructura lista para Fase 1)

La **Fase 0** dejó lista toda la base técnica necesaria para que la fábrica de video Hintsly pueda operar.  
Tu agente debe asumir que **todo lo siguiente ya existe y funciona**, y que puede usarlo sin volver a configurarlo.

---

## 1. Estructura del proyecto lista en GitHub
Repositorio:  
`https://github.com/LignumBlocks/hintsly-video-factory`

Dentro del repo ya existe:

- `/engine` → servicio FastAPI que procesa planos.
- `.env.example` → plantilla de variables de entorno.
- Estructura preparada para crecer por fases.

---

## 2. Código desplegado en el VPS
El repo se clonó en:

```
/root/hintsly-video-factory
```

Para actualizarlo:

```bash
cd /root/hintsly-video-factory
git pull
```

---

## 3. hintsly-engine funcionando en contenedor Docker

El servicio **hintsly-engine** ya está operativo:

- Construido desde `/root/hintsly-video-factory/engine`
- Respondiente en: `http://hintsly-engine:8000/health`
- Endpoint disponible: `POST /shots/process` (modo mock)

---

## 4. Volúmenes y assets configurados

**Host:**
```
/root/hintsly-video-factory/assets/videos
```

**Contenedor:**
```
/assets/videos
```

---

## 5. docker-compose operativo y stack estable

Incluye:

- Traefik
- n8n
- hintsly-engine

Todos con `restart: always`.

---

## 6. Logs y mantenimiento
Logs actualmente en stdout del contenedor. Logrotate opcional.

---

## Qué asume Fase 1

El agente puede:

- Usar HTTP Node en n8n → `http://hintsly-engine:8000/shots/process`
- Registrar paths en Google Sheets
- Ejecutar el pipeline con el engine mock

---

## Resumen ultracorto

- Repo listo  
- Engine en Docker  
- n8n funcionando  
- Comunicación interna OK  
- Sistema de assets OK  

👉 **Objetivo de Fase 1:** conectar Google Sheets con n8n y automatizar el envío/registro de planos.
