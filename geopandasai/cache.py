import abc
import hashlib
import os
from typing import Iterable

from pandas import DataFrame

__all__ = [
    "get_from_cache_query_and_dfs",
    "set_to_cache_query_and_dfs",
    "set_cache_instance",
    "get_from_cache",
    "set_to_cache",
    "ResultCache",
    "InMemoryResultCache",
    "FileResultCache",
]


class ResultCache(abc.ABC):
    def get_cache(self, key: str) -> str | None:
        """
        Get the cached result for the given key.
        """
        pass

    def set_cache(self, key: str, value: str) -> None:
        """
        Set the cached result for the given key.
        """
        pass

    def clear_cache(self, key: str) -> None:
        """
        Clear the cached result for the given key.
        """
        pass


class InMemoryResultCache(ResultCache):
    def __init__(self):
        self.cache = {}

    def get_cache(self, key: str) -> str | None:
        return self.cache.get(key)

    def set_cache(self, key: str, value: str) -> None:
        self.cache[key] = value

    def clear_cache(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]


class FileResultCache(ResultCache):
    def __init__(self, cache_dir: str = "./.geopandasai_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache(self, key: str) -> str | None:
        try:
            with open(os.path.join(self.cache_dir, key), "r") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def set_cache(self, key: str, value: str) -> None:
        with open(os.path.join(self.cache_dir, key), "w") as f:
            f.write(value)

    def clear_cache(self, key: str) -> None:
        try:
            os.remove(os.path.join(self.cache_dir, key))
        except FileNotFoundError:
            pass


current_cache = None


def _get_cache_instance():
    global current_cache
    return current_cache


def set_cache_instance(cache_instance: ResultCache):
    global current_cache
    current_cache = cache_instance


def get_from_cache(key: str):
    instance = _get_cache_instance()
    if instance is None:
        return None
    return instance.get_cache(key)


def set_to_cache(key: str, value: str):
    instance = _get_cache_instance()
    if instance:
        instance.set_cache(key, value)


def _hash(key: str) -> str:
    """
    Hash the key using a simple hash function.
    """
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def _hash_query_and_dfs(query: str, dfs: Iterable[DataFrame]):
    """
    Hash the query and dataframes to create a unique key.
    """
    key = _hash(
        query
        + "_"
        + "_".join([_hash(str(df)) for df in dfs])
        + "_".join([str(df.dtypes) for df in dfs])
    )
    return key


def get_from_cache_query_and_dfs(
    query: str, dfs: Iterable[DataFrame], result_type: str = ""
):
    """
    Get the cached result for the given query and dataframes.
    """
    return get_from_cache(_hash_query_and_dfs(query + result_type, dfs))


def set_to_cache_query_and_dfs(
    query: str, dfs: Iterable[DataFrame], value: str, result_type: str = ""
):
    """
    Set the cached result for the given query and dataframes.
    """
    set_to_cache(_hash_query_and_dfs(query + result_type, dfs), value)
