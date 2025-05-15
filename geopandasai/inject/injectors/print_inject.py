import re
from typing import Callable, Optional

import colorama

from .base import ACodeInjector

colorama.init(autoreset=True)


class PrintCodeInjector(ACodeInjector):
    def inject(
        self,
        pattern: re.Pattern,
        function_call: Callable[[Optional[re.Match]], str],
        import_statement: str,
    ):
        print(
            f"{colorama.Fore.YELLOW}Manual injection procedure...{colorama.Style.RESET_ALL}"
        )
        print("First add, if not already present, the following import statement:")
        print(
            f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT}import {import_statement}{colorama.Style.RESET_ALL}"
        )
        print(
            f"{colorama.Fore.YELLOW}Then replace the following code with the function call:{colorama.Style.RESET_ALL}"
        )
        print(
            f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT}{function_call(None
            )}{colorama.Style.RESET_ALL}"
        )
