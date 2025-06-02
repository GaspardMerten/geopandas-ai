import traceback
from typing import List, Type, Union

from .execute import execute_func
from .samples import SAMPLES
from ..template import (
    prompt_with_template,
    parse_template,
    Template,
)
from ...description import describe_dataframe
from ....shared.constants import FUNCTION_SIGNATURE
from ....shared.return_type import type_to_literal
from ....shared.types import GeoOrDataFrame


def dfs_to_string(dfs: List[GeoOrDataFrame]) -> str:
    description = ""

    for i, df in enumerate(dfs):
        description += f"DataFrame {i + 1}, will be sent_as df_{i + 1}:\n"
        description += describe_dataframe(df)
    return description


def build_static_description(dfs, user_provided_libraries):
    from ....config import get_geopandasai_config

    libraries = list(
        set((user_provided_libraries or []) + get_geopandasai_config().libraries)
    )
    # To maintain consistency, we sort the libraries alphabetically
    libraries.sort()

    libraries_str = ", ".join(libraries)
    dataset_description = dfs_to_string(dfs)
    df_args = ", ".join([f"df_{i + 1}" for i in range(len(dfs))])
    return dataset_description, libraries_str, df_args


def build_code(
    prompt: str,
    return_type: Type,
    dfs: List[GeoOrDataFrame],
    history: str = None,
    user_provided_libraries: List[str] = None,
) -> Union[str, None]:
    dataset_description, libraries_str, system_instructions = build_static_description(
        dfs, user_provided_libraries
    )
    dfs_string = ", ".join([f"df_{i + 1}" for i in range(len(dfs))])

    history = history or "N/A"

    max_attempts = 5
    last_code = None
    last_exception = None
    response = None

    for _ in range(max_attempts):
        if last_code:
            template = parse_template(
                Template.CODE_PREVIOUSLY_ERROR,
                system_instructions=system_instructions,
                last_code=last_code,
                last_exception=last_exception,
                libraries=libraries_str,
                prompt=prompt,
                history=history,
                return_type=type_to_literal(return_type),
                dfs=dfs_string,
                dataset_description=dataset_description,
                tips=SAMPLES,
                function_signature=FUNCTION_SIGNATURE,
            )
            last_code = prompt_with_template(
                template, remove_markdown_code_limiter=True
            )
        else:
            template = parse_template(
                Template.CODE,
                system_instructions=system_instructions,
                last_code=last_code,
                last_exception=last_exception,
                libraries=libraries_str,
                history=history,
                prompt=prompt,
                dfs=dfs_string,
                return_type=type_to_literal(return_type),
                dataset_description=dataset_description,
                tips=SAMPLES,
                function_signature=FUNCTION_SIGNATURE,
            )

            last_code = prompt_with_template(
                template, remove_markdown_code_limiter=True
            )
        try:
            execute_func(last_code, return_type, *dfs)
            response = last_code
            break
        except Exception as e:
            last_exception = traceback.format_exc()

    if not response:
        raise ValueError(
            "No valid code snippet. Here is the last code snippet that was generated:\n"
            f"{last_code}\n\nAnd the last exception that was raised:\n{last_exception}"
        )

    return response
