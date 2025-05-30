from typing import List, Type

from ._internal import magic_prompt_with_dataframes
from ...shared.types import GeoOrDataFrame


def chat(
    prompt: str,
    *dfs: List[GeoOrDataFrame],
    return_type: Type = None,
    provided_libraries: List[str] = None,
):
    result = magic_prompt_with_dataframes(
        prompt,
        *dfs,
        return_type=return_type,
        provided_libraries=provided_libraries,
    )

    return result.internal
