# import output dynamically
import importlib.util
import importlib.util
import re
import tempfile
import traceback
from typing import Iterable, Union
from typing import List

import folium
import matplotlib.pyplot as plt
import pandas as pd
from geopandas import GeoDataFrame
from litellm import completion

from .config import get_active_lite_llm_config
from .types import GeoOrDataFrame, ResultType

__all__ = ["prompt_with_dataframes"]


def _prompt(messages: List[dict], max_tokens=None, remove_markdown_code_limiter=False) -> str:
    output = completion(**get_active_lite_llm_config(), messages=messages, max_tokens=max_tokens).choices[
        0].message.content

    if remove_markdown_code_limiter:
        output = re.sub(r"```[a-zA-Z]*", "", output)

    return output


def determine_type(prompt: str) -> ResultType:
    """
    A function to determine the type of prompt based on its content.
    It returns either "TEXT" or "CHART".
    """

    choices = [
        result_type.value for result_type in ResultType
    ]
    result = _prompt([
        {
            "role": "user", "content": prompt}, {
            "role": "user",
            "content": f"Which of the following type of result should a code answering the prompt return? You must choose between {' - '.join(choices)}, only answer with the type between <Type> and </Type> tags. Example: <Type>{choices[0]}</Type>"
        }, ], max_tokens=30, )

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
        description += f"Shape: {df.shape}\n"
        description += f"Columns (with types): {' - '.join([f'{col} ({df[col].dtype})' for col in df.columns])}\n"
        description += f"Head:\n{df.head()}\n\n"

    return description


def execute_with_result_type(
        prompt: str, result_type: ResultType, *dfs: Iterable[GeoOrDataFrame]
) -> Union[str, plt.Figure, pd.DataFrame, folium.Map, GeoOrDataFrame]:
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

    libraries = ["pandas", "matplotlib.pyplot", "folium", "geopandas"]

    dataset_description = _dfs_to_string(dfs)
    df_args = ', '.join([f'df_{i + 1}' for i in range(len(dfs))])

    system_instructions = (
        "You are a helpful assistant specialized in returning Python code snippets formatted as follow {"
        f"def execute({df_args}) -> {result_type_to_python_type[result_type]}:\n"
        "    ...\n"
    )

    max_attempts = 5
    last_code = None
    last_exception = None

    result = None

    for _ in range(max_attempts):
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": "Here is a prompt: " + prompt},
            {"role": "user", "content": "Here are the libraries I can use: " + ", ".join(libraries)},
            {"role": "user", "content": f"Create a code snippet that returns a {result_type.name.lower()}"},
            {"role": "user", "content": "Here are the dataframes descriptions: " + dataset_description},
            {"role": "user",
             "content": "Only return the python code snippet, without any explanation or additional text. Do not forget to import the libraries you need."},
        ]

        if last_code:
            messages.append({"role": "assistant", "content": last_code})
            messages.append(
                {"role": "user", "content": f"Here is the code you gave previously: {last_code}"}
            )
            messages.append(
                {"role": "user",
                 "content": f"Here is the exception you raised: {last_exception}, please fix it in your next attempt."}
            )

        response = _prompt(messages, max_tokens=2000, remove_markdown_code_limiter=True)

        with tempfile.NamedTemporaryFile(delete=True, suffix=".py", mode="w") as f:
            f.write(response)
            f.flush()

            spec = importlib.util.spec_from_file_location("output", f.name)
            output_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(output_module)
        try:
            result = output_module.execute(*dfs)
            break
        except Exception as e:
            last_code = response
            last_exception = f"{e}, {traceback.format_exc()}"

    if result is None:
        raise ValueError("The code did not return a valid result.")

    if isinstance(result, GeoDataFrame):
        from . import GeoDataFrameAI
        result = GeoDataFrameAI.from_geodataframe(result)

    return result


def prompt_with_dataframes(
        prompt: str, *dfs: Iterable[GeoOrDataFrame], result_type: ResultType = None
) -> Union[str, plt.Figure, pd.DataFrame, folium.Map, GeoOrDataFrame]:
    result_type = result_type or determine_type(prompt)
    return execute_with_result_type(prompt, result_type, *dfs)
