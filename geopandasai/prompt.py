import re

from litellm import completion

from .config import get_active_lite_llm_config
from .types import TemplateData

__all__ = ["prompt_with_template"]


def prompt_with_template(
    template: TemplateData, remove_markdown_code_limiter=False
) -> str:
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
