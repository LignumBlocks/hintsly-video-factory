# Ticket Técnico – Resolver y aplicar `asset_id` (assets.json) como referencia visual para consistencia

## ID
TICKET-F3-ASSETS-RESOLVER-APPLY

## Objetivo
Implementar soporte de **assets canónicos** para que cada `ShotV2` que incluya `asset_id` use el asset correspondiente (definido en `assets.json`) como **contexto/referencia visual** al generar la imagen (y por extensión el video), garantizando consistencia entre planos.

---

## Contexto
- Existe un catálogo `assets.json` con objetos `asset` que describen elementos visuales reutilizables (p.ej. backgrounds del lab).
- Cada fila/shot del storyboard trae `asset_id`.
- El archivo físico del asset (p.ej. `HL_Core_Lab_Isometric_Main_v01.jpeg`) vive en una carpeta de assets (Drive/FS) y debe usarse como referencia al construir la imagen.

---

## Alcance
### Incluye
- Lectura y parsing de `assets.json`.
- Resolver `asset_id` → `asset` (metadata + ruta del archivo).
- Validar coherencia `shot.mv_context` vs `asset.mv_context_default` (warning o error configurable).
- Integración en el flujo de generación de imagen para usar el asset como referencia (image-to-image / conditioning / “base image” según soporte del proveedor).
- Persistencia en `metadata.json` de:
  - `asset_id`
  - `asset_file_name`
  - `asset_path` (local o absoluto)
  - `asset_mv_context_default`

### No incluye (por ahora)
- Sincronización automática desde Google Drive (si actualmente es manual).
- UI/administración de assets (solo motor).

---

## Reglas de Negocio
1. Si `shot.asset_id` viene **vacío o null**, el motor funciona como hasta ahora (generación “from text”).
2. Si `shot.asset_id` viene definido:
   - El motor debe **resolverlo** en `assets.json`.
   - Debe **encontrar el archivo** del asset en la ruta configurada.
   - Debe pasar ese asset como **referencia** en la generación de imagen (según el método del provider).
3. Si `asset_id` no existe en el catálogo → `estado = ERROR` + `error_message` claro.
4. Si el archivo del asset no existe → `estado = ERROR` + `error_message` claro.
5. Consistencia de contexto:
   - Si `shot.mv_context != asset.mv_context_default`, registrar warning en logs y opcionalmente en metadata.
   - (Modo estricto opcional) fallar si no coincide.

---

## Cambios Técnicos Requeridos

### 1) Configuración
Agregar variables (o config file) para ubicar assets:
- `ASSETS_CATALOG_PATH=/path/to/assets.json`
- `ASSETS_FILES_DIR=/path/to/assets/files`  
  (donde vive `HL_Core_Lab_Isometric_Main_v01.jpeg`)

### 2) Nuevo componente: `AssetsRepository` (o `AssetsService`)
Responsabilidades:
- Cargar `assets.json` (una vez, con cache).
- `get_asset(asset_id) -> Asset`
- `resolve_asset_file(asset.file_name) -> absolute_path`
- Validar existencia del archivo.

### 3) Dominio
- Crear `Asset` model (DTO) con campos:
  - `asset_id`, `file_name`, `tipo_asset`, `mv_context_default`,
  - `descripcion_visual`, `uso_sugerido`, `notas`

### 4) Integración con PromptService (opcional, recomendado)
- Si hay `asset_id`, inyectar en prompt un “anchor” breve:
  - Ej: `Use visual anchor: {asset_id} ({asset.descripcion_visual}).`
- No debe duplicar texto; solo reforzar.

### 5) Integración con generación de imagen (Kie Nano Banana)
Modificar `KieNanoBananaClient` (o wrapper) para soportar:
- **Modo con referencia**: enviar la imagen base (asset) como input si el API lo permite.
- Si el API no soporta image-to-image directo, alternativa mínima:
  - Incluir el asset como “context” en prompt y mantener el asset como “soft constraint” (menos ideal).
> La implementación debe elegir el mejor método soportado por Kie.ai para “referenced image”.

### 6) Persistencia metadata
En `metadata.json` guardar:
- `asset_id`
- `asset_file_name`
- `asset_resolved_path`
- `asset_tipo_asset`
- `asset_mv_context_default`
- `mv_context_mismatch` (bool) si aplica

---

## Criterios de Aceptación (AC)

### AC1 – Resolución correcta
- Dado un shot con `asset_id` válido, el sistema encuentra el asset en `assets.json` y resuelve el archivo físico.

### AC2 – Error handling
- Si `asset_id` no existe en el catálogo:
  - `estado = ERROR`
  - `error_message` contiene `asset_id` y causa.
- Si el archivo no existe:
  - `estado = ERROR`
  - `error_message` contiene `file_name` y path esperado.

### AC3 – Aplicación en generación de imagen
- Para shots con `asset_id`, la llamada a Nano Banana utiliza el asset como referencia (parámetro de imagen / base image / reference image) **cuando el provider lo soporte**.
- La imagen final se guarda en la ruta canon del shot.

### AC4 – Metadata
- `metadata.json` incluye los campos de asset (id, file_name, resolved_path, etc.).

### AC5 – Compatibilidad
- Shots sin `asset_id` siguen funcionando exactamente igual que antes.

---

## Pruebas (Checklist)
1. Shot con `asset_id=LAB_ISOMETRIC_MAIN` y archivo presente → genera imagen/video OK.
2. Shot con `asset_id` inexistente → ERROR controlado.
3. Shot con `asset_id` válido pero archivo faltante → ERROR controlado.
4. Shot con mismatch de `mv_context` vs `mv_context_default` → warning en logs y metadata.

---

## Definition of Done
- AssetsRepository implementado y testeado.
- Integración con ProcessShot + KieNanoBananaClient funcionando.
- Logs y metadata completos.
- Prueba manual end-to-end con un shot real del lab usando `LAB_ISOMETRIC_MAIN`.
