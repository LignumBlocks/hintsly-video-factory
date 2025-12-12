import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from domain.entities import Asset
from adapters.logger import Logger

class AssetsRepository:
    """
    Repository to access the Assets Catalog (JSON) and resolve physical files.
    """
    def __init__(self, catalog_path: str, files_dir: str):
        self.catalog_path = Path(catalog_path)
        self.files_dir = Path(files_dir)
        self.logger = Logger()
        self._assets_cache: Dict[str, Asset] = {}
        self._loaded = False

    def load_catalog(self):
        """Loads the assets catalog from JSON file into memory."""
        if self._loaded:
            return

        try:
            if not self.catalog_path.exists():
                self.logger.warning(f"Assets catalog not found at {self.catalog_path}")
                return

            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            assets_list = data.get("assets", [])
            for asset_data in assets_list:
                # Handle potential missing optional fields gracefully if needed
                # For now assuming schema matches
                try:
                    asset = Asset(**asset_data)
                    self._assets_cache[asset.asset_id] = asset
                except Exception as e:
                    self.logger.error(f"Failed to parse asset {asset_data.get('asset_id')}: {e}")
            
            self._loaded = True
            self.logger.info(f"Loaded {len(self._assets_cache)} assets from catalog.")

        except Exception as e:
            self.logger.error(f"Failed to load assets catalog: {e}")

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Retrieves an asset by its ID."""
        if not self._loaded:
            self.load_catalog()
        
        return self._assets_cache.get(asset_id)

    def resolve_file_path(self, file_name: str) -> Optional[Path]:
        """
        Resolves the absolute path for an asset file.
        Checks for extensions: .jpeg, .jpg, .png.
        Returns None if file not found.
        """
        # Extensions to try in order
        extensions = [".jpeg", ".jpg", ".png"]
        
        for ext in extensions:
            path = self.files_dir / f"{file_name}{ext}"
            if path.exists():
                return path
        
        return None
