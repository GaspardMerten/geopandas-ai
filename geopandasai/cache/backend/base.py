import abc


class CacheBackend(abc.ABC):
    def get_cache(self, key: str) -> bytes | None:
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
