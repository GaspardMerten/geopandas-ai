import os
from contextlib import redirect_stdout, redirect_stderr
from typing import Type, Sequence

from ....shared.types import GeoOrDataFrame


def execute_func(code: str, return_type: Type, *dfs: Sequence[GeoOrDataFrame]):
    from .... import get_geopandasai_config

    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            return get_geopandasai_config().executor.execute(code, return_type, *dfs)
