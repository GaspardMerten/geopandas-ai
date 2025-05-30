import os
import re
from functools import partial
from typing import Optional

from .regex import inject_code_pattern
from ...shared import constants


def _function_call_builder(
    match: Optional[re.Match], module_name: str, function_name: str
):
    """
    Build the function call string.
    """
    if match:
        args = [match.group(1)]
        if match.group(3):
            args += match.group(3).split(",")
    else:
        args = ["gdf1, gdf2, ..."]

    return f"{module_name}.{function_name}({', '.join(args)})"


def inject_code(code: str, function_name: str, ai_module: str, ai_module_path: str):
    """
    Injects the provided code into a Python module.
    The code must contain the function signature placeholder defined in constants.FUNCTION_SIGNATURE.
    The function will create a new Python file with the function name in the specified module path,
    and it will also update the __init__.py file to include the new function.
    :param code: The code to inject, which must contain the function signature placeholder.
    :param function_name: The name of the function to create in the module.
    :param ai_module: The name of the AI module where the function will be injected.
    :param ai_module_path: The path to the AI module where the function will be created.
    :raises AssertionError: If the code does not contain the function signature placeholder.
    """
    from ... import get_geopandasai_config

    assert (
        constants.FUNCTION_SIGNATURE in code
    ), f"Code must contain {constants.FUNCTION_SIGNATURE}."

    os.makedirs(ai_module_path, exist_ok=True)

    with open(os.path.join(ai_module_path, function_name + ".py"), "w") as f:
        code = code.replace(constants.FUNCTION_SIGNATURE, f"def {function_name}")
        f.write(code)

    with open(os.path.join(ai_module_path, "__init__.py"), "a+") as f:
        f.write(f"from .{function_name} import {function_name}\n")

    injector = get_geopandasai_config().injector
    injector.inject(
        inject_code_pattern,
        partial(
            _function_call_builder, function_name=function_name, module_name=ai_module
        ),
        f"import {ai_module}",
    )
