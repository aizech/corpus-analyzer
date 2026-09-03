"""Simple disk cache for FetchResult objects."""

import hashlib
import json
import time
from pathlib import Path

from web_fetch_lib.schemas import FetchResult


class DiskCache:
    """JSON-on-disk cache with TTL support."""

    def __init__(self, cache_dir: Path, default_ttl: int = 3600) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _key(self, **kwargs) -> str:
        """Build a deterministic cache key from the input arguments."""
        canonical = json.dumps(kwargs, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, **kwargs) -> FetchResult | None:
        """Return a cached FetchResult if present and not expired."""
        key = self._key(**kwargs)
        path = self._path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("expires", float("inf")) < time.time():
                path.unlink(missing_ok=True)
                return None
            result = FetchResult.model_validate(data["result"])
            result.cached = True
            return result
        except Exception:
            path.unlink(missing_ok=True)
            return None

    def set(self, result: FetchResult, ttl: int | None = None, **kwargs) -> None:
        """Store a FetchResult in the cache."""
        key = self._key(**kwargs)
        path = self._path(key)
        payload = {
            "expires": time.time() + (ttl or self.default_ttl),
            "result": result.model_dump(),
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def clear(self) -> None:
        """Remove all cached entries."""
        for path in self.cache_dir.glob("*.json"):
            path.unlink(missing_ok=True)
