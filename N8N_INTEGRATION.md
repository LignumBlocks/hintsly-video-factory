# Hintsly Video Factory - n8n Integration Guide

## API Endpoints

### Base URL
- **Development (with Ngrok)**: `http://localhost:8000`
- **Production**: `http://hintsly-engine:8000`

---

## 1. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify the service is running and properly configured.

**Response**:
```json
{
  "status": "healthy",
  "service": "hintsly-video-factory",
  "version": "1.0.0",
  "public_base_url": "https://engine.srv954959.hstgr.cloud"
}
```

**n8n HTTP Request Node Configuration**:
- Method: `GET`
- URL: `http://hintsly-engine:8000/health`
- Authentication: None

---

## 2. Process Shot

**Endpoint**: `POST /shots/process`

**Purpose**: Generate a complete video shot (image + video) from shot metadata.

### Request Body

```json
{
  "video_id": "csj_B01_P02",
  "block_id": "B01_HOOK",
  "shot_id": "P02",
  "core_flag": true,
  "mv_context": "LAB_TABLE",
  "asset_id": "LAB_CREDITSYSTEM_TABLE",
  "asset_mode": "IMAGE_1F_VIDEO",
  "camera_move": "zoom_in",
  "duracion_seg": 8.0,
  "texto_voz_resumido": "Person A buys a twenty-five-thousand-dollar car with a 650 score...",
  "descripcion_visual": "Isometric view of the central credit system table...",
  "funcion_narrativa": "Introduce the cold system that sees two almost identical people...",
  "prompt_imagen": "Isometric 3D view of a dark institutional financial command table...",
  "prompt_video": "Cinematic slow Zoom In towards the center of the credit system table...",
  "image_path": "",
  "video_path": "",
  "estado": "PENDIENTE",
  "error_message": null
}
```

### Response (Success)

```json
{
  "success": true,
  "shot": {
    "video_id": "csj_B01_P02",
    "block_id": "B01_HOOK",
    "shot_id": "P02",
    "core_flag": true,
    "mv_context": "LAB_TABLE",
    "asset_id": "LAB_CREDITSYSTEM_TABLE",
    "asset_mode": "IMAGE_1F_VIDEO",
    "asset_resolved_file_name": "HL_Core_Lab_CreditSystem_Table_v01",
    "asset_resolved_path": "/app/assets/catalog_files/HL_Core_Lab_CreditSystem_Table_v01.jpeg",
    "asset_mv_context_mismatch": false,
    "camera_move": "zoom_in",
    "duracion_seg": 8.0,
    "texto_voz_resumido": "Person A buys a twenty-five-thousand-dollar car...",
    "descripcion_visual": "Isometric view of the central credit system table...",
    "funcion_narrativa": "Introduce the cold system...",
    "prompt_imagen": "Isometric 3D view of a dark institutional financial command table...",
    "prompt_video": "Cinematic slow Zoom In towards the center...",
    "image_path": "/app/assets/videos/csj_B01_P02/block_B01_HOOK/shot_P02/image.png",
    "video_path": "/app/assets/videos/csj_B01_P02/block_B01_HOOK/shot_P02/video.mp4",
    "estado": "COMPLETADO",
    "error_message": null
  },
  "message": "Shot P02 processed successfully"
}
```

### Response (Error)

```json
{
  "success": false,
  "shot": {
    "video_id": "csj_B01_P02",
    "block_id": "B01_HOOK",
    "shot_id": "P02",
    "estado": "ERROR",
    "error_message": "Image generation failed: API timeout",
    ...
  },
  "message": "Shot processing failed: Image generation failed: API timeout"
}
```

---

## 3. Regenerate Shot

**Endpoint**: `POST /shots/regenerate`

**Purpose**: Retry processing a failed shot or regenerate an existing one.

**Request/Response**: Same format as `/shots/process`

---

## n8n Workflow Example

### Basic Shot Processing Workflow

```
[Webhook/Trigger] 
    ↓
[HTTP Request: POST /shots/process]
    ↓
[IF Node: Check success field]
    ↓
    ├─ TRUE → [Success Handler]
    │           ↓
    │         [Store video_path & image_path]
    │           ↓
    │         [Notify completion]
    │
    └─ FALSE → [Error Handler]
                ↓
              [Log error_message]
                ↓
              [Retry or alert]
```

### n8n HTTP Request Node Configuration

**For /shots/process**:

1. **Method**: `POST`
2. **URL**: `http://hintsly-engine:8000/shots/process`
3. **Authentication**: None (or configure if you add auth)
4. **Body Content Type**: `JSON`
5. **Body**:
   ```json
   {
     "video_id": "{{ $json.video_id }}",
     "block_id": "{{ $json.block_id }}",
     "shot_id": "{{ $json.shot_id }}",
     "core_flag": {{ $json.core_flag }},
     "mv_context": "{{ $json.mv_context }}",
     "asset_id": "{{ $json.asset_id }}",
     "asset_mode": "{{ $json.asset_mode }}",
     "camera_move": "{{ $json.camera_move }}",
     "duracion_seg": {{ $json.duracion_seg }},
     "texto_voz_resumido": "{{ $json.texto_voz_resumido }}",
     "descripcion_visual": "{{ $json.descripcion_visual }}",
     "funcion_narrativa": "{{ $json.funcion_narrativa }}",
     "prompt_imagen": "{{ $json.prompt_imagen }}",
     "prompt_video": "{{ $json.prompt_video }}",
     "image_path": "",
     "video_path": "",
     "estado": "PENDIENTE",
     "error_message": null
   }
   ```

6. **Options**:
   - Timeout: `600000` (10 minutes - video generation can take time)
   - Response Format: `JSON`

---

## Field Descriptions

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `video_id` | string | Unique video identifier | `"csj_B01_P02"` |
| `block_id` | string | Block/section identifier | `"B01_HOOK"` |
| `shot_id` | string | Shot identifier within block | `"P02"` |
| `mv_context` | string | Visual context/setting | `"LAB_TABLE"` |
| `asset_mode` | enum | Generation mode | `"IMAGE_1F_VIDEO"` |
| `camera_move` | string | Camera movement description | `"zoom_in"` |
| `duracion_seg` | float | Duration in seconds | `8.0` |
| `texto_voz_resumido` | string | Voice-over text | `"Person A buys..."` |
| `descripcion_visual` | string | Visual description | `"Isometric view..."` |
| `funcion_narrativa` | string | Narrative function | `"Introduce the system..."` |

### Optional Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `asset_id` | string | Asset catalog ID | `null` |
| `core_flag` | boolean | Is core shot | `false` |
| `prompt_imagen` | string | Custom image prompt | Auto-generated |
| `prompt_video` | string | Custom video prompt | Auto-generated |

### Asset Modes

- `STILL_ONLY`: Generate only a static image (no video)
- `IMAGE_1F_VIDEO`: Generate image + video from that image
- `IMAGE_2F_VIDEO`: Generate 2 images + video (future)

---

## Error Handling in n8n

### Check for Success

Use an **IF Node** after the HTTP Request:

**Condition**: `{{ $json.success }} === true`

- **TRUE branch**: Process successful result
- **FALSE branch**: Handle error (retry, log, alert)

### Extract Error Details

In the FALSE branch, you can access:
- `{{ $json.message }}` - Human-readable error message
- `{{ $json.shot.error_message }}` - Detailed error from the pipeline
- `{{ $json.shot.estado }}` - Will be `"ERROR"`

---

## Testing the API

### Using curl

```bash
# Health check
curl http://hintsly-engine:8000/health

# Process shot
curl -X POST http://hintsly-engine:8000/shots/process \
  -H "Content-Type: application/json" \
  -d @shot_example.json
```

### Using Python

```python
import requests

# Health check
response = requests.get("http://hintsly-engine:8000/health")
print(response.json())

# Process shot
shot_data = {
    "video_id": "test_001",
    "block_id": "B01",
    "shot_id": "S01",
    # ... other fields
}

response = requests.post(
    "http://hintsly-engine:8000/shots/process",
    json=shot_data
)

result = response.json()
if result["success"]:
    print(f"✅ Video: {result['shot']['video_path']}")
else:
    print(f"❌ Error: {result['message']}")
```

---

## Production Deployment Notes

1. **CORS**: Update `allow_origins` in `main.py` to restrict to your n8n domain
2. **Authentication**: Consider adding API key authentication
3. **Rate Limiting**: Add rate limiting middleware to prevent abuse
4. **Monitoring**: Use the `/health` endpoint for uptime monitoring
5. **Timeouts**: Ensure n8n timeout is at least 10 minutes (video generation is slow)

---

## Troubleshooting

### Common Issues

1. **Timeout errors**:
   - Increase n8n HTTP Request timeout to 600000ms (10 min)
   - Video generation with Veo can take 1-2 minutes

2. **"Image generation failed"**:
   - Check KIE_API_KEY is configured
   - Verify Kie.ai API quota/limits

3. **"Asset not found"**:
   - Verify `asset_id` exists in assets catalog
   - Check ASSETS_CATALOG_PATH configuration

4. **"File not accessible by Veo"**:
   - Ensure PUBLIC_BASE_URL is correctly configured
   - Verify `/assets` directory is publicly accessible
   - Check Nginx/web server configuration

---

## Support

For issues or questions, check the logs:
```bash
docker logs hintsly-engine
```
