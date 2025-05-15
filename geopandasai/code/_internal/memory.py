import hashlib
from typing import List, Type

from .code import dfs_to_string
from ...cache import get_from_cache, set_to_cache
from ...return_type import type_to_literal
from ...types import GeoOrDataFrame


def build_key_for_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


class Memory:
    def __init__(
        self,
        dfs: List[GeoOrDataFrame],
        return_type: Type,
        key: str,
        user_provided_libraries: List[str] = None,
    ):
        self.dfs = dfs
        self.return_type = return_type
        self._cache = dict()
        self.user_provided_libraries = user_provided_libraries or []
        self.history = []
        self.memory_cache_key = hashlib.sha256(
            (dfs_to_string(dfs) + key + type_to_literal(return_type)).encode()
        ).hexdigest()
        self.restore_cache()

    def restore_cache(self):
        self._cache = get_from_cache(self.memory_cache_key) or {}

    def flush_cache(self):
        set_to_cache(self.memory_cache_key, self._cache)

    def log(self, prompt: str, code: str):
        self.history.append([prompt, code])
        self._cache[build_key_for_prompt(prompt)] = code
        self.flush_cache()

    def get_history_string(self):
        if not self.history:
            return ""
        return (
            "<History>"
            + "\n".join(
                [
                    f"<Prompt>{item[0]}</Prompt><Output>{item[1]}</Output>"
                    for item in self.history
                ]
            )
            + "</History>"
        )

    def get_for_prompt(self, prompt: str):
        key = build_key_for_prompt(prompt)
        if key in self._cache:
            return self._cache[key]

        return None

    def reset(self):
        self.history = []
        self._cache = {}
        self.flush_cache()
