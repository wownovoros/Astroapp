import time
from typing import Any, Dict, Optional, Tuple

_CACHE: Dict[str, Tuple[Any, float]] = {}


def get_cache(key: str) -> Optional[Any]:
    item = _CACHE.get(key)
    if not item:
        return None
    value, expires_at = item
    if time.time() > expires_at:
        _CACHE.pop(key, None)
        return None
    return value


def set_cache(key: str, value: Any, ttl: int = 3600) -> None:
    _CACHE[key] = (value, time.time() + ttl)
