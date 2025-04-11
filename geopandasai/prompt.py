# import output dynamically
import importlib.util
import importlib.util
import re
import tempfile
import traceback
from typing import Iterable, List

from geopandas import GeoDataFrame
from litellm import completion

from .cache import get_from_cache_query_and_dfs, set_to_cache_query_and_dfs
from .config import get_active_lite_llm_config, get_libraries
from .template import Template, parse_template
from .types import GeoOrDataFrame, ResultType, TemplateData, Output

__all__ = ["prompt_with_dataframes"]


def _prompt(template: TemplateData, remove_markdown_code_limiter=False) -> str:
    output = (
        completion(
            **get_active_lite_llm_config(),
            messages=template.messages,
            max_tokens=template.max_tokens,
        )
        .choices[0]
        .message.content
    )

    if remove_markdown_code_limiter:
        output = re.sub(r"```[a-zA-Z]*", "", output)

    return output


def determine_type(prompt: str) -> ResultType:
    """
    A function to determine the type of prompt based on its content.
    It returns either "TEXT" or "CHART".
    """

    choices = [result_type.value for result_type in ResultType]
    result = get_from_cache_query_and_dfs(prompt, []) or _prompt(
        parse_template(Template.TYPE, prompt=prompt, choices=", ".join(choices))
    )

    set_to_cache_query_and_dfs(prompt, [], result)

    regex = f"<Type>({'|'.join(choices)})</Type>"

    if not result:
        raise ValueError("Invalid response from the LLM. Please check your prompt.")

    # Check if the response matches the expected format
    match = re.findall(regex, result, re.DOTALL | re.MULTILINE)

    if not match:
        raise ValueError("The response does not match the expected format.")

    # Extract the code snippet from the response
    result_type = match[0]

    return ResultType(result_type)


def _dfs_to_string(dfs: Iterable[GeoOrDataFrame]) -> str:
    description = ""

    for i, df in enumerate(dfs):
        description += f"DataFrame {i + 1}, will be sent_as df_{i + 1}:\n"
        if hasattr(df, "crs"):
            description += f"CRS: {df.crs}\n"
        description += f"Shape: {df.shape}\n"
        description += f"Columns (with types): {' - '.join([f'{col} ({df[col].dtype})' for col in df.columns])}\n"
        description += f"Head:\n{df.head()}\n\n"

    return description


def execute_with_result_type(
    prompt: str,
    result_type: ResultType,
    *dfs: Iterable[GeoOrDataFrame],
    user_provided_libraries: List[str] = None,
) -> Output:
    result_type_to_python_type = {
        ResultType.TEXT: "str",
        ResultType.MAP: "folium.Map",
        ResultType.PLOT: "plt.Figure",
        ResultType.DATAFRAME: "pd.DataFrame",
        ResultType.GEODATAFRAME: "gp.GeoDataFrame",
        ResultType.LIST: "list",
        ResultType.DICT: "dict",
        ResultType.INTEGER: "int",
        ResultType.FLOAT: "float",
        ResultType.BOOLEAN: "bool",
    }

    libraries = (
        ["pandas", "matplotlib.pyplot", "folium", "geopandas"]
        + (user_provided_libraries or [])
        + get_libraries()
    )
    libraries_str = ", ".join(libraries)

    dataset_description = _dfs_to_string(dfs)
    df_args = ", ".join([f"df_{i + 1}" for i in range(len(dfs))])

    system_instructions = (
        "You are a helpful assistant specialized in returning Python code snippets formatted as follow {"
        f"def execute({df_args}) -> {result_type_to_python_type[result_type]}:\n"
        "    ...\n"
    )

    max_attempts = 5
    last_code = None
    last_exception = None
    response = None
    result = None

    for _ in range(max_attempts):
        if last_code:
            template = parse_template(
                Template.CODE_PREVIOUSLY_ERROR,
                system_instructions=system_instructions,
                last_code=last_code,
                last_exception=last_exception,
                libraries=libraries_str,
                prompt=prompt,
                result_type=result_type.name.lower(),
                dataset_description=dataset_description,
            )
            response = _prompt(template, remove_markdown_code_limiter=True)
        else:
            template = parse_template(
                Template.CODE,
                system_instructions=system_instructions,
                last_code=last_code,
                last_exception=last_exception,
                libraries=libraries_str,
                prompt=prompt,
                result_type=result_type.name.lower(),
                dataset_description=dataset_description,
            )

            response = get_from_cache_query_and_dfs(
                prompt, dfs, result_type.value
            ) or _prompt(template, remove_markdown_code_limiter=True)

        with tempfile.NamedTemporaryFile(delete=True, suffix=".py", mode="w") as f:
            f.write(response)
            f.flush()

            try:
                spec = importlib.util.spec_from_file_location("output", f.name)
                output_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(output_module)
                result = output_module.execute(*dfs)
                break
            except Exception as e:
                last_code = response
                last_exception = f"{e}, {traceback.format_exc()}"

    if result is None:
        raise ValueError("The code did not return a valid result.")

    set_to_cache_query_and_dfs(prompt, dfs, response, result_type=result_type.value)

    if isinstance(result, GeoDataFrame):
        from . import GeoDataFrameAI

        result = GeoDataFrameAI.from_geodataframe(result)

    return Output(
        source_code=response,
        result=result,
    )


def prompt_with_dataframes(
    prompt: str,
    *dfs: Iterable[GeoOrDataFrame],
    result_type: ResultType = None,
    user_provided_libraries: List[str] = None,
) -> Output:
    result_type = result_type or determine_type(prompt)
    return execute_with_result_type(
        prompt, result_type, *dfs, user_provided_libraries=user_provided_libraries
    )
