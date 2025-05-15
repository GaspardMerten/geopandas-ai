import os
import re
from functools import partial
from typing import Optional

from .. import constants
from .injectors.factory import code_inject_factory
from .regex import inject_code_pattern


def function_call_builder(
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
    Freeze the code and save it to a file.
    """

    assert (
        constants.FUNCTION_SIGNATURE in code
    ), f"Code must contain {constants.FUNCTION_SIGNATURE}."

    os.makedirs(ai_module_path, exist_ok=True)

    with open(os.path.join(ai_module_path, function_name + ".py"), "w") as f:
        code = code.replace(constants.FUNCTION_SIGNATURE, f"def {function_name}")
        f.write(code)

    with open(os.path.join(ai_module_path, "__init__.py"), "a+") as f:
        f.write(f"from .{function_name} import {function_name}\n")

    injector = code_inject_factory()
    injector.inject(
        inject_code_pattern,
        partial(
            function_call_builder, function_name=function_name, module_name=ai_module
        ),
        f"import {ai_module}",
    )
