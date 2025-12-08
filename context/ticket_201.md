# TICKET 201 — Crear estructura del Hintsly Engine (Hexagonal)

## 🎯 Objetivo
Establecer la estructura base del motor siguiendo arquitectura hexagonal.

## ✔️ Descripción
Crear dentro de `/engine` las carpetas:

```
engine/
├── main.py
├── domain/
│   ├── entities.py
│   └── errors.py
├── usecases/
│   ├── process_shot.py
│   ├── regenerate_shot.py
│   └── utils_prompt.py
├── adapters/
│   ├── fs_adapter.py
│   ├── gemini_client.py
│   ├── veo_client.py
│   └── logger.py
└── infra/
    ├── config.py
    └── paths.py
```

## ✔️ Criterios de aceptación
- La estructura existe y el proyecto corre sin errores de importación.
- Todos los archivos están listos para empezar a implementar lógica.
