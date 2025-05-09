import enum
import json
import re

from litellm import completion

from .config import get_active_lite_llm_config
from .types import TemplateData

__all__ = ["prompt_with_template", "parse_template", "Template", "sanitize_text"]


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


class Template(enum.Enum):
    CODE_PREVIOUSLY_ERROR = "code_previously_error"
    TYPE = "determine_type"
    CODE = "code"


# Check that all templates are in the templates directory
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _check():
    for template in Template:
        template_file = TEMPLATES_DIR / f"{template.value}.json"
        if not template_file.exists():
            raise FileNotFoundError(f"Template file {template_file} does not exist.")

    _check()


def sanitize_text(data) -> str:
    return json.dumps(data)[1:-1]


def parse_template(template: Template, **context) -> TemplateData:
    """
    Parse the template file and return the content.
    """
    template_file = TEMPLATES_DIR / f"{template.value}.json"
    with open(template_file, "r") as f:
        content = f.read()

    for match in re.findall(r"(\{\{\s*(\w+)\s*}})", content):
        if match[1] not in context:
            raise ValueError(
                f"Missing context variable '{match[1]}' in template {template.value}.json"
            )
        content = content.replace(match[0], sanitize_text(context[match[1]]))
    return TemplateData(**json.loads(content))
