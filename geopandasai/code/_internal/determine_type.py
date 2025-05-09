import re
from typing import Type

from ...cache import cache
from ...result_type import get_available_result_types, result_type_from_literal
from ...template import parse_template, Template, prompt_with_template


@cache
def determine_type(prompt: str) -> Type:
    """
    A function to determine the type of prompt based on its content.
    It returns either "TEXT" or "CHART".
    """

    choices = get_available_result_types()
    result = prompt_with_template(
        parse_template(Template.TYPE, prompt=prompt, choices=", ".join(choices))
    )

    regex = f"<Type>({'|'.join(choices)})</Type>"

    if not result:
        raise ValueError("Invalid response from the LLM. Please check your prompt.")

    # Check if the response matches the expected format
    match = re.findall(regex, result, re.DOTALL | re.MULTILINE)

    if not match:
        raise ValueError("The response does not match the expected format.")

    # Extract the code snippet from the response
    result_type = match[0]

    return result_type_from_literal(result_type)
