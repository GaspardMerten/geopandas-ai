from typing import Optional

from .base import CacheBackend


class InMemoryCacheBackend(CacheBackend):
    def __init__(self):
        self.cache = {}

    def get_cache(self, key: str) -> Optional[bytes]:
        return self.cache.get(key)

    def set_cache(self, key: str, value: bytes) -> None:
        self.cache[key] = value

    def clear_cache(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]

    def reset_cache(self) -> None:
        self.cache.clear()
