import os
from typing import Optional

from .base import CacheBackend


class FileSystemCacheBackend(CacheBackend):
    def __init__(self, cache_dir: str = "./.geopandasai_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache(self, key: str) -> Optional[bytes]:
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

    def reset_cache(self) -> None:
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
