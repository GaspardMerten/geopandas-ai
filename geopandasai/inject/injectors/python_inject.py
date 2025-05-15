import inspect
import re
from typing import Callable, Optional

from .base import ACodeInjector


class PythonCodeInjector(ACodeInjector):
    def inject(
        self,
        pattern: re.Pattern,
        function_call_builder: Callable[[Optional[re.Match]], str],
        import_statement: str,
    ):
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back.f_back
        filename = caller_frame.f_code.co_filename
        with open(filename, "r") as f:
            code = f.read()
        # Find one or more matches
        match = pattern.search(code)

        if not match:
            raise ValueError(
                "No match found for the pattern in the code. Please check your code."
            )

        if import_statement not in code:
            code = f"{import_statement}\n{code}"

        # replace the first match with the new function name and arguments
        with open(filename, "w") as f:
            args = [match.group(1)]
            if match.group(3):
                args += match.group(3).split(",")
            f.write(
                code.replace(
                    match.group(0),
                    function_call_builder(match),
                )
            )
