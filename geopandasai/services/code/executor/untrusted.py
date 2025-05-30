import re
from typing import Type, Iterable

from colorama import Fore, Style

from .trusted import TrustedCodeExecutor
from ....shared.types import GeoOrDataFrame


def _highlight_code(code: str) -> str:
    # Very basic highlighting for keywords and strings
    keywords = r"\b(def|return|if|else|elif|import|from|as|with|class|raise|try|except|for|in|is|not|and|or|pass|None|True|False)\b"
    code = re.sub(keywords, lambda m: Fore.BLUE + m.group(0) + Style.RESET_ALL, code)
    code = re.sub(
        r"(\".*?\"|\'.*?\')",
        lambda m: Fore.GREEN + m.group(0) + Style.RESET_ALL,
        code,
    )
    code = re.sub(
        r"#.*", lambda m: Fore.LIGHTBLACK_EX + m.group(0) + Style.RESET_ALL, code
    )
    return code


class UntrustedCodeExecutor(TrustedCodeExecutor):
    def execute(self, code: str, return_type: Type, *dfs: Iterable[GeoOrDataFrame]):
        print("\n" + "-" * 30 + " Code Preview " + "-" * 30)
        print(_highlight_code(code))
        print("-" * 75 + "\n")

        confirmation = (
            input("⚠️  Do you want to execute this code? [y/N]: ").strip().lower()
        )
        if confirmation != "y":
            print("🚫 Execution aborted.")
            raise ValueError(
                "Code execution aborted by user because unsafe or untrusted code was signaled."
            )

        return super().execute(code, return_type, *dfs)
