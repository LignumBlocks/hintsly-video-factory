# 📘 Resumen Oficial — Cierre de Fase 1 (Google Sheets + n8n)

La **Fase 1** dejó operativa toda la capa de **interfaz de producción** y **orquestación automatizada** de la fábrica Hintsly.  
Tu agente debe asumir que **todos los flujos y validaciones de n8n ya están funcionando**, y que el sistema está listo para recibir un Engine real (Fase 2).

---

## ✅ 1. La hoja de producción `storyboard_master` ya está creada

El Google Sheet oficial contiene todas las columnas definidas en el roadmap:

```
video_id, bloque, plano, descripcion_visual, funcion_narrativa,
movimiento_camara, texto_voz_resumido,
prompt_imagen, prompt_video,
image_path, video_path,
estado, error_message
```

El director usa esta hoja como **único punto de entrada** al pipeline.

---

## ✅ 2. n8n está conectado con Google Sheets (lectura y escritura)

- Las credenciales OAuth ya están configuradas en n8n.  
- Los workflows pueden **leer** y **actualizar** cualquier fila de la hoja.  
- Se usa `video_id` (o row_number interno) para identificar filas a actualizar.

---

## ✅ 3. Workflow principal LISTO → ENGINE funcionando

n8n ejecuta un ciclo automático cada pocos minutos:

1. Lee la hoja  
2. Filtra filas cuyo `estado = "LISTO"`  
3. Construye el JSON del plano  
4. Llama al endpoint del engine:  
   `POST http://hintsly-engine:8000/shots/process`  
5. Recibe la respuesta del engine mock  
6. Actualiza la fila con:
   - `video_path` (ruta retornada)  
   - `prompt_imagen` / `prompt_video` (si aplicara)  
   - `estado = COMPLETADO`  
   - `error_message` vacío

Esto cierra el **pipeline de procesar plano** de punta a punta.

---

## ✅ 4. Workflow REGENERAR implementado

Cuando el director cambia el campo `estado` a:

```
REGENERAR
```

El workflow:

1. Limpia automáticamente:  
   - `prompt_imagen`  
   - `prompt_video`  
   - `image_path`  
   - `video_path`  
   - `error_message`  

2. Cambia `estado = "LISTO"`  

→ El plano reingresa al flujo principal y se procesa **como nuevo**, 100% automático.

---

## ✅ 5. Validaciones obligatorias antes de enviar al Engine

Se implementó un nodo IF que verifica que los campos mínimos estén completos:

- `video_id`  
- `bloque`  
- `plano`  
- `descripcion_visual`  
- `movimiento_camara`

Si falta alguno:

- `estado = "ERROR"`  
- `error_message = "Faltan campos obligatorios"`

Esto evita enviar al engine planos incompletos o rompidos.

---

## ✅ 6. Integración estable con el Engine mock

El engine mock de la Fase 0 (FastAPI) está completamente integrado.  
n8n:

- envía el JSON correctamente,  
- recibe el resultado,  
- actualiza la hoja.

Esto valida el backend de comunicación y deja todo listo para reemplazar el mock con el **Engine real de la Fase 2** sin cambiar n8n.

---

## 🎯 Resultado final de la Fase 1

- La fábrica ya tiene un **circuito de producción autónomo**.  
- El director tiene una interfaz simple (Google Sheets).  
- n8n controla:
  - disparo,
  - validaciones,
  - regeneración,
  - sincronización con el engine.  

Ya existe un **pipeline operativo**, estable y probado, que procesa planos automáticamente.

---

## 🚀 Qué asume la Fase 2

La próxima fase puede asumir:

- La hoja ya funciona como **fuente de verdad del storyboard**.  
- n8n ya está totalmente conectado.  
- Los workflows principales están completos.  
- Solo falta reemplazar el engine mock por un **Hintsly Engine real**, con:
  - generación de prompts,  
  - generación de imágenes,  
  - generación de video,  
  - manejo robusto de errores,  
  - escritura en `/assets/videos/...`.

---

## 🏁 Resumen ultracorto

- Hoja lista  
- n8n conectado  
- LISTO → ENGINE → UPDATE funcionando  
- Validaciones activas  
- REGENERAR operativo  

👉 **La fábrica ya funciona de forma automática. Fase 1 completada.**
