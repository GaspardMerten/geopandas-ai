import importlib.util
import importlib.util
import importlib.util
import tempfile
from typing import Iterable

from ...types import GeoOrDataFrame


def execute_func(code: str, *dfs: Iterable[GeoOrDataFrame]):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".py", mode="w") as f:
        f.write(code)
        f.flush()
        spec = importlib.util.spec_from_file_location("output", f.name)
        output_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(output_module)
        result = output_module.execute(*dfs)

        if isinstance(result, GeoOrDataFrame):
            from ... import GeoDataFrameAI

            result = GeoDataFrameAI(result)

        return result
