# Integración Nano Banana Pro (Kie.ai)
Guía conceptual para agentes IA (Python)

## Visión general
Nano Banana Pro funciona **de forma asíncrona** mediante un sistema de *jobs* en cola.

Flujo general:
1. Crear una tarea (`createTask`)
2. La tarea entra en cola (`waiting`)
3. Un worker la procesa
4. Se consulta el estado (`recordInfo`) hasta `success` o `fail`

⚠️ **Nunca es síncrono**: no se obtiene la imagen en la primera llamada.

---

## 1. Crear la tarea (createTask)

### Endpoint
POST `/api/v1/jobs/createTask`

### Qué se envía
- `model`: `nano-banana-pro`
- `prompt`: texto descriptivo
- `image_input`: **lista de URLs** (aunque solo sea una imagen)
- Parámetros opcionales:
  - `aspect_ratio`
  - `resolution`
  - `output_format`

### Ejemplo conceptual
```json
{
  "model": "nano-banana-pro",
  "input": {
    "prompt": "Usa la imagen como referencia y conviértela en ilustración cartoon",
    "image_input": [
      "https://engine.srv954959.hstgr.cloud/assets/imagen.jpg"
    ],
    "aspect_ratio": "1:1",
    "resolution": "2K"
  }
}
```

### Respuesta
```json
{
  "code": 200,
  "data": {
    "taskId": "abc123..."
  }
}
```

El `taskId` es el identificador único del job.

---

## 2. Consultar estado de la tarea (recordInfo)

### Endpoint
GET `/api/v1/jobs/recordInfo?taskId=...`

### Estados posibles
| state     | Significado                        | Acción |
|----------|------------------------------------|-------|
| waiting  | En cola                            | Seguir esperando |
| running  | Procesándose                       | Seguir esperando |
| success  | Completada correctamente           | Leer resultado |
| fail     | Error                              | Manejar error |

---

## 3. El estado `waiting` NO es error
`waiting` significa **simplemente que aún no hay un worker disponible**.

Puede durar:
- segundos
- o más de 1 minuto según carga

❌ No implica:
- URL inválida
- prompt incorrecto
- error de imagen

✅ Implica:
- hay que hacer *polling*

---

## 4. Resultado exitoso (`success`)

Ejemplo de respuesta:
```json
{
  "state": "success",
  "resultJson": "{\"resultUrls\":[\"https://tempfile.aiquickdraw.com/h/resultado.png\"]}"
}
```

Notas importantes:
- `resultJson` es un **string JSON**, debe parsearse
- Dentro viene `resultUrls` (lista de imágenes generadas)
- Las URLs suelen ser **temporales**

---

## 5. Error típico: `fail 422`

```json
{
  "state": "fail",
  "failCode": "422",
  "failMsg": "Your media file is unavailable, please replace it."
}
```

Significado real:
- El worker **no pudo descargar la imagen**
- No es error del prompt

Causas comunes:
- URL privada
- URL expirada
- Firewall / WAF
- Bloqueo a IPs de datacenter

---

## 6. URLs de imágenes: buenas prácticas

### URLs que funcionan bien
- URLs públicas accesibles (`200 OK`)
- `tempfile.redpandaai.co/...`
- `kieai.redpandaai.co/files/...`

### Riesgos
- URLs temporales pueden expirar
- URLs externas pueden bloquear datacenters

### Solución robusta
1. Backend descarga la imagen
2. Backend la re-subе a un storage confiable
3. Usar esa URL en `image_input`

---

## 7. Flujo recomendado (resumen)

```text
createTask → taskId
loop:
  recordInfo(taskId)
  if waiting/running → sleep
  if success → parse resultJson → usar resultUrls
  if fail → manejar error
```

---

## Regla de oro
**Nunca trates `waiting` como error.**

Nano Banana Pro es un sistema de colas.

---

Documento preparado para implementación en Python.
