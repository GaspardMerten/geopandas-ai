import os

from .base import CacheBackend


class FileSystemCacheBackend(CacheBackend):
    def __init__(self, cache_dir: str = "./.geopandasai_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache(self, key: str) -> bytes | None:
        try:
            with open(os.path.join(self.cache_dir, key), "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def set_cache(self, key: str, value: bytes) -> None:
        with open(os.path.join(self.cache_dir, key), "wb") as f:
            f.write(value)

    def clear_cache(self, key: str) -> None:
        try:
            os.remove(os.path.join(self.cache_dir, key))
        except FileNotFoundError:
            pass
