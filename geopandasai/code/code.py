from typing import List, Type

from ._internal import magic_prompt_with_dataframes
from ..types import GeoOrDataFrame


def chat(
    prompt: str,
    *dfs: List[GeoOrDataFrame],
    result_type: Type = None,
    user_provided_libraries: List[str] = None,
):
    return magic_prompt_with_dataframes(
        prompt,
        *dfs,
        result_type=result_type,
        user_provided_libraries=user_provided_libraries,
    )
