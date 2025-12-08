# TICKET 202 — Definir entidad `Shot` (domain)

## 🎯 Objetivo
Crear la entidad principal del sistema, que representará cada plano.

## ✔️ Descripción
Implementar `Shot` con los atributos:

- video_id  
- bloque  
- plano  
- descripcion_visual  
- movimiento_camara  
- prompt_imagen  
- prompt_video  
- image_path  
- video_path  
- estado  
- error_message  

## ✔️ Criterios de aceptación
- Archivo `entities.py` contiene la clase `Shot`.
- Usar Pydantic para validación interna.
