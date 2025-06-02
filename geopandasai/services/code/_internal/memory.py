import hashlib
from dataclasses import dataclass
from typing import List, Type, Optional

from .code import dfs_to_string
from ....external.cache import get_from_cache, set_to_cache
from ....shared.return_type import type_to_literal
from ....shared.types import GeoOrDataFrame


def build_key_for_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


@dataclass
class EntryInput:
    prompt: str
    return_type: Type
    provided_libraries: List[str]

    def as_string(self) -> str:
        return f"{self.prompt} | {type_to_literal(self.return_type)} | {', '.join(sorted(self.provided_libraries))}"


class Memory:
    def __init__(
        self,
        dfs: List[GeoOrDataFrame],
        return_type: Type,
        key: str,
        provided_libraries: List[str] = None,
    ):
        self.dfs = dfs
        self.return_type = return_type
        self._cache = dict()
        self.provided_libraries = provided_libraries or []
        self.history: List[EntryInput] = []
        self.memory_cache_key = hashlib.sha256(
            (dfs_to_string(dfs) + key + type_to_literal(return_type)).encode()
        ).hexdigest()
        self.restore_cache()

    def restore_cache(self):
        self._cache = get_from_cache(self.memory_cache_key) or {}

    def flush_cache(self):
        set_to_cache(self.memory_cache_key, self._cache)

    def log(self, entry: EntryInput, code: str) -> None:
        self.history.append(entry)
        self._cache[self.build_current_history_key()] = code
        self.flush_cache()

    def build_current_history_key(self, new_entry: Optional[EntryInput] = None) -> str:
        return build_key_for_prompt(
            "".join(
                [
                    p.as_string()
                    for p in ([*self.history, new_entry] if new_entry else self.history)
                ]
            )
        )

    def get_history_string(self):
        if not self.history:
            return ""
        return (
            "<History>"
            + "\n".join(
                [
                    f"<Prompt>{item.prompt}</Prompt><Output>{item.return_type}</Output>"
                    for item in self.history
                ]
            )
            + "</History>"
        )

    def get_code_for_entry(self, entry: EntryInput) -> Optional[str]:
        key = self.build_current_history_key(entry)
        return self._cache.get(key)

    def reset(self):
        self.history = []
        self._cache = {}
        self.flush_cache()
