import re
from typing import Type

from ....external.cache import cache
from ....shared.return_type import (
    get_available_return_types,
    return_type_from_literal,
)
from ....services.code.template import (
    parse_template,
    Template,
    prompt_with_template,
)


@cache
def determine_type(prompt: str, attempt: int = 0) -> Type:
    """
    A function to determine the type of prompt based on its content.
    It returns either "TEXT" or "CHART".
    """
    choices = get_available_return_types()
    regex = f"({'|'.join(choices)})"

    result = prompt_with_template(
        parse_template(
            Template.TYPE, prompt=prompt, choices=", ".join(choices), regex=regex
        )
    )

    if not result:
        raise ValueError("Invalid response from the LLM. Please check your prompt.")

    # Check if the response matches the expected format
    match = re.findall(regex, result, re.DOTALL | re.MULTILINE)

    if not match:
        if attempt < 3:
            # Retry with a different prompt
            return determine_type(
                prompt,
                attempt=attempt + 1,
            )
        else:
            raise ValueError(
                f"Invalid response from the LLM. Please check your prompt. Response: {result}"
            )

    # Extract the code snippet from the response
    return_type = match[0]
    return return_type_from_literal(return_type)
