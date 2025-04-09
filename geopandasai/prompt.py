import re
from typing import Iterable

from litellm import completion

from .config import get_active_lite_llm_config
from .types import GeoOrDataFrame

__all__ = ["prompt_with_dataframes"]


def prompt_with_dataframes(prompt: str, *dfs: Iterable[GeoOrDataFrame]) -> str:
    """
    A function to create a prompt for the GeoDataFrameAI class using litellm.
    It returns a string that starts with TEXT or CHART, followed by the code
    snippet wrapped in <Code> ... </Code>. The snippet must define:

    def execute(*gdf_or_df_in_the_same_order) -> None:
        ...
    """

    # You can modify system_instructions to guide the model’s output format
    system_instructions = (
        "You are a helpful assistant specialized in returning Python code snippets. "
        "Your job is to produce code that either returns text (str) or a chart (plot), For images, write them as png"
        "to [output_path] (placeholder will automatically be replace with actual file), for text, as UTF-8. The code must be wrapped in <Code> ... </Code> tags. "
        "depending on the user’s request. The output must always begin with either "
        "<Type>TEXT</Type> or <Type>CHART</Type>, followed by the code snippet "
        "<Code>def execute(*gdf_or_df_in_the_same_order) -> None:\n"
        "    ...\n"
        "</Code>\n\n"
    )

    # Here, we pass both system instructions and the user prompt to litellm:
    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": prompt},
        {"role": "user",
         "content": "Example output: ```xml<Type>TEXT</Type><Code>def execute(df1, df2) -> str | plot:... </Code>```"},
        {"role": "user", "content": "Here are the dataframes: " + "\n".join([str(df) for df in dfs])},
    ]

    # Call the LLM using litellm
    response = completion(
        **get_active_lite_llm_config(),
        messages=messages,
    )

    # Check if the response is valid
    regex = r"""<Type>(TEXT|CHART)</Type>.*<Code>(.*)</Code>"""
    message = response.choices[0].message.content

    print(message)
    if not response.choices or not message:
        raise ValueError("Invalid response from the LLM. Please check your prompt.")

    # Check if the response matches the expected format
    match = re.findall(regex, message, re.DOTALL | re.MULTILINE)

    if not match:
        raise ValueError("The response does not match the expected format.")

    # Extract the code snippet from the response
    result_type, code_snippet = match[0]

    return message
