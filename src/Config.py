
import os
import json
from typing import Any, Optional

class Config(dict):
    def __init__(self, path: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path
        if path:
            if not os.path.exists(self._path):
                with open(self._path, "w") as f:
                    f.write("{}")
            
            self._load()

    def _load(self) -> None:
        """Load data from the JSON file, if it exists."""
        try:
            with open(self._path, "r", encoding="utf-8") as file:
                data = json.load(file)
                super().update(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading configuration: {e}")
            # Start with an empty dictionary if loading fails

    def _save(self) -> None:
        """Save the current dictionary data to the JSON file."""
        if self._path:
            with open(self._path, "w", encoding="utf-8") as file:
                json.dump(self, file, indent=4)

    #def __getitem__(self, key: Any) -> Any:
    #    self._load()
    #    return super().__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key: Any) -> None:
        super().__delitem__(key)
        self._save()

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self._save()

    def clear(self) -> None:
        super().clear()
        self._save()

    def pop(self, key: Any, default: Any = None) -> Any:
        result = super().pop(key, default)
        self._save()
        return result

    def popitem(self) -> tuple:
        result = super().popitem()
        self._save()
        return result