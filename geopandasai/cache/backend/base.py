import abc
from typing import Optional


class CacheBackend(abc.ABC):
    def get_cache(self, key: str) -> Optional[bytes]:
        """
        Get the cached result for the given key.
        """
        pass

    def set_cache(self, key: str, value: bytes) -> None:
        """
        Set the cached result for the given key.
        """
        pass

    def clear_cache(self, key: str) -> None:
        """
        Clear the cached result for the given key.
        """
        pass

    def reset_cache(self) -> None:
        """
        Reset the cache.
        """
        pass
