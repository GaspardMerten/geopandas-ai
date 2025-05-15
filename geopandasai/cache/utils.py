import hashlib
import pickle
from io import BytesIO

from ..cache.backend.base import CacheBackend
from ..cache.backend.file_system import FileSystemCacheBackend

current_cache: CacheBackend = FileSystemCacheBackend()


def _get_cache_instance():
    global current_cache
    return current_cache


def set_cache_instance(cache_instance: CacheBackend):
    global current_cache
    current_cache = cache_instance


def get_from_cache(key: str):
    instance = _get_cache_instance()
    if instance is None:
        return None

    cached_value = instance.get_cache(key)
    return pickle.load(BytesIO(cached_value)) if cached_value is not None else None


def set_to_cache(key: str, value: object):
    instance = _get_cache_instance()
    if instance:
        instance.set_cache(key, pickle.dumps(value))


def _hash(key: str) -> str:
    """
    Hash the key using a simple hash function.
    """
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def cache(func):
    def wrapped(*args, **kwargs):
        cache_key = _hash(str(args) + str(kwargs))
        result = get_from_cache(cache_key)
        if not result:
            result = func(*args, **kwargs)
            set_to_cache(cache_key, result)
        return result

    return wrapped


def reset_cache():
    instance = _get_cache_instance()
    if instance:
        instance.reset_cache()
