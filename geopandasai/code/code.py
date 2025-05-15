from typing import List, Type

from ._internal import magic_prompt_with_dataframes
from ..types import GeoOrDataFrame


def chat(
    prompt: str,
    *dfs: List[GeoOrDataFrame],
    return_type: Type = None,
    user_provided_libraries: List[str] = None,
):
    return magic_prompt_with_dataframes(
        prompt,
        *dfs,
        return_type=return_type,
        user_provided_libraries=user_provided_libraries,
    )
