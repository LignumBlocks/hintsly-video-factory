from typing import Optional, Dict
from domain.nanobanana_models import NanoBananaRequest

class NanoBananaRepository:
    def __init__(self):
        self._store: Dict[str, NanoBananaRequest] = {}
        self._current_project_id: Optional[str] = None

    def save(self, data: NanoBananaRequest) -> str:
        project_id = data.project.project_id
        self._store[project_id] = data
        self._current_project_id = project_id
        return project_id

    def get(self, project_id: str) -> Optional[NanoBananaRequest]:
        return self._store.get(project_id)
    
    def get_current(self) -> Optional[NanoBananaRequest]:
        if self._current_project_id:
            return self._store.get(self._current_project_id)
        return None
