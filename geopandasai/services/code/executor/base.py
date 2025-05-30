import abc
from typing import Iterable, Type

from ....shared.types import GeoOrDataFrame


class ACodeExecutor(abc.ABC):
    @abc.abstractmethod
    def execute(self, code: str, return_type: Type, *dfs: Iterable[GeoOrDataFrame]):
        pass
