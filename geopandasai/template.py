import enum
import json
import re

from .types import TemplateData


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


def insert_text_in_json_middle(
    json_obj: dict, insert_text: str, key: str = None
) -> str:
    # Convert the insert_text to a JSON-safe string
    safe_text = json.dumps(insert_text)[1:-1]  # remove quotes added by json.dumps

    if key:
        if key not in json_obj or not isinstance(json_obj[key], str):
            raise ValueError("Key must exist and its value must be a string")
        original_value = json_obj[key]
        mid = len(original_value) // 2
        modified_value = original_value[:mid] + insert_text + original_value[mid:]
        json_obj[key] = modified_value
    else:
        # Convert full JSON to string and insert in the middle
        json_str = json.dumps(json_obj)
        mid = len(json_str) // 2
        modified_str = json_str[:mid] + safe_text + json_str[mid:]
        return modified_str

    return json.dumps(json_obj)[1:-1]


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
        content = content.replace(
            match[0],
            json.dumps(context[match[1]])[1:-1],  # remove quotes added by json.dumps
        )
    return TemplateData(**json.loads(content))
