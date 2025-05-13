import traceback
from typing import List, Type, Union

from .execute import execute_func
from ...config import get_libraries
from ...description import describe_dataframe
from ...result_type import type_to_literal
from ...template import prompt_with_template, parse_template, Template
from ...types import GeoOrDataFrame


def dfs_to_string(dfs: List[GeoOrDataFrame]) -> str:
    description = ""

    for i, df in enumerate(dfs):
        description += f"DataFrame {i + 1}, will be sent_as df_{i + 1}:\n"
        description += describe_dataframe(df)
    return description


def build_static_description(dfs, user_provided_libraries):
    libraries = (
        ["pandas", "matplotlib.pyplot", "folium", "geopandas", "contextily"]
        + (user_provided_libraries or [])
        + get_libraries()
    )
    libraries_str = ", ".join(libraries)
    dataset_description = dfs_to_string(dfs)
    df_args = ", ".join([f"df_{i + 1}" for i in range(len(dfs))])
    return dataset_description, libraries_str, df_args


def build_code(
    prompt: str,
    result_type: Type,
    dfs: List[GeoOrDataFrame],
    user_provided_libraries: List[str] = None,
) -> Union[str, None]:
    dataset_description, libraries_str, system_instructions = build_static_description(
        dfs, user_provided_libraries
    )
    dfs_string = ", ".join([f"df_{i + 1}" for i in range(len(dfs))])

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
                return_type=type_to_literal(result_type),
                dfs=dfs_string,
                dataset_description=dataset_description,
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
                prompt=prompt,
                dfs=dfs_string,
                return_type=type_to_literal(result_type),
                dataset_description=dataset_description,
            )

            last_code = prompt_with_template(
                template, remove_markdown_code_limiter=True
            )
        try:
            execute_func(last_code, *dfs)
            response = last_code
            break
        except Exception as e:
            last_exception = f"{e}, {traceback.format_exc()}"

    if not response:
        raise ValueError(
            "No valid code snippet. Here is the last code snippet that was generated:\n"
            f"{last_code}\n\nAnd the last exception that was raised:\n{last_exception}"
        )

    return response
