import hashlib
import pickle
from io import BytesIO


def _get_cache_backend():
    from ...config import get_geopandasai_config

    return get_geopandasai_config().cache_backend


def _hash(key: str) -> str:
    """
    Hash the key using a simple hash function.
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def get_from_cache(key: str):
    instance = _get_cache_backend()
    if instance is None:
        return None

    cached_value = instance.get_cache(key)
    return pickle.load(BytesIO(cached_value)) if cached_value is not None else None


def set_to_cache(key: str, value: object):
    instance = _get_cache_backend()
    if instance:
        instance.set_cache(key, pickle.dumps(value))


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
    """
    Reset the entire cache.
    """
    instance = _get_cache_backend()
    instance.reset_cache()
