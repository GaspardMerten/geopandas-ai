from typing import Iterable, Type, Sequence

from ....shared.types import GeoOrDataFrame


def execute_func(code: str, return_type: Type, *dfs: Sequence[GeoOrDataFrame]):
    from .... import get_geopandasai_config

    return get_geopandasai_config().executor.execute(code, return_type, *dfs)
