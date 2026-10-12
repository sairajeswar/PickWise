import time
import threading
from typing import Any, Optional, Dict

class SimpleTTLCache:
    def __init__(self, default_ttl_seconds: int = 1800):  # 30 minutes
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            return entry["value"]

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": time.time() + ttl
            }

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

GLOBAL_CACHE = SimpleTTLCache(default_ttl_seconds=1800)
