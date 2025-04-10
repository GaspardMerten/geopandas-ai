# import output dynamically
import importlib.util
import re
import tempfile
from typing import Iterable, List

import pandas as pd
from folium import folium
from geopandas import GeoDataFrame
from litellm import completion
from matplotlib import pyplot as plt

from .config import get_active_lite_llm_config
from .types import GeoOrDataFrame, ResultType

__all__ = ["prompt_with_dataframes"]


def _prompt(messages: List[dict], max_tokens=None, remove_markdown_code_limiter=False) -> str:
    print('\n'.join([f"{m['role']}: {m['content']}" for m in messages]))
    output = completion(**get_active_lite_llm_config(), messages=messages, max_tokens=max_tokens).choices[
        0].message.content
    print("Output:", output)
    print("=" * 50)
    print("\n\n")

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


def prompt_with_dataframes(prompt: str, *dfs: Iterable[
    GeoOrDataFrame]) -> str | plt.Figure | pd.DataFrame | folium.Map | GeoOrDataFrame:
    """
    A function to create a prompt for the GeoDataFrameAI class using litellm.
    It returns a string that starts with TEXT or CHART, followed by the code
    snippet wrapped in <Code> ... </Code>. The snippet must define:

    def execute(*gdf_or_df_in_the_same_order) -> None:
        ...
    """

    result_type = determine_type(prompt)

    result_type_to_string = {
        ResultType.TEXT: "a textual answer",
        ResultType.MAP: "a folium map instance",
        ResultType.PLOT: "a matplotlib plot",
        ResultType.DATAFRAME: "a pandas dataframe",
        ResultType.GEODATAFRAME: "a geopandas dataframe",
    }

    result_type_to_python_type = {
        ResultType.TEXT: "str",
        ResultType.MAP: "folium.Map",
        ResultType.PLOT: "plt.Figure",
        ResultType.DATAFRAME: "pd.DataFrame",
        ResultType.GEODATAFRAME: "gp.GeoDataFrame",
    }

    libraries = ["pandas", "matplotlib.pyplot", "folium", "geopandas"]

    dataset_description = _dfs_to_string(dfs)

    # You can modify system_instructions to guide the model’s output format
    df_args = ', '.join([f'df_{i + 1}' for i in range(len(dfs))])

    system_instructions = (
        "You are a helpful assistant specialized in returning Python code snippets formatted as follow {"
        f"def execute({df_args}) -> {result_type_to_python_type[result_type]}:\n"
        "    ...\n"
    )

    # Here, we pass both system instructions and the user prompt to litellm:
    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": "Here is a prompt: " + prompt},
        {"role": "user", "content": "Here are the libraries I can use: " + ", ".join(libraries)},
        {"role": "user", "content": "Create a code snippet that returns " + result_type_to_string[result_type]},
        {"role": "user", "content": "Here are the dataframes descriptions: " + dataset_description},
        {"role": "user",
         "content": "Only return the python code snippet, without any explanation or additional text. Do not forget to import the libraries you need."},
    ]

    # Call the LLM using litellm
    response = _prompt(messages, max_tokens=2000, remove_markdown_code_limiter=True)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".py",mode="w") as f:
        f.write(response)
        f.flush()

        spec = importlib.util.spec_from_file_location("output", f.name)

        # Create a module object from the spec
        output_module = importlib.util.module_from_spec(spec)

        # Actually execute the module code
        spec.loader.exec_module(output_module)

    # Now output_module should have an execute function
    result = output_module.execute(*dfs)

    if isinstance(result, GeoDataFrame):
        from . import GeoDataFrameAI
        result = GeoDataFrameAI.from_geodataframe(result)

    return result
