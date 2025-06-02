import importlib.util
import tempfile
from typing import Type, Iterable

from .base import ACodeExecutor
from ....shared.types import GeoOrDataFrame


class TrustedCodeExecutor(ACodeExecutor):
    def execute(self, code: str, return_type: Type, *dfs: Iterable[GeoOrDataFrame]):
        with tempfile.NamedTemporaryFile(delete=True, suffix=".py", mode="w") as f:
            f.write(code)
            f.flush()
            spec = importlib.util.spec_from_file_location("output", f.name)
            output_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(output_module)
            result = output_module.execute(
                **{f"df_{i+1}": df for i, df in enumerate(dfs)}
            )

            if not isinstance(result, return_type):
                raise TypeError(
                    f"Expected return type {return_type}, but got {type(result)}\n\nCode:\n\n{code}\n\n"
                )

            if isinstance(result, GeoOrDataFrame):
                from ....geodataframe_ai import GeoDataFrameAI

                result = GeoDataFrameAI(result)

            return result
