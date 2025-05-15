from typing import Any, List, Type, Union

import colorama

from .code import build_code
from .determine_type import determine_type
from .execute import execute_func
from .memory import Memory
from ...inject import inject_code
from ...types import GeoOrDataFrame


class MagicReturnCore:
    def __init__(self, memory: Memory, prompt: str):
        self._internal = None
        self._did_execute = False
        self.memory = memory

        self.prompt = f"{memory.get_history_string()}\n\n Now while taking into account previous prompts and result, answer this prompt: <Prompt>{prompt}</Prompt>"

        self._code = memory.get_for_prompt(prompt)
        if not self._code:
            self._code = build_code(
                self.prompt,
                memory.return_type,
                memory.dfs,
                user_provided_libraries=memory.user_provided_libraries,
            )

        self.memory.log(prompt, self._code)

    def improve(self, prompt: str) -> Union["MagicReturn", Any]:
        return magic_prompt_with_dataframes(
            prompt,
            *self.memory.dfs,
            return_type=self.memory.return_type,
            user_provided_libraries=self.memory.user_provided_libraries,
            memory=self.memory,
        )

    def materialize(self) -> Any:
        self._build()
        return self

    def reset(self):
        self.memory.reset()
        return self

    @property
    def code(self):
        return self._code

    @property
    def internal(self):
        self._build()
        return self._internal

    def _build(self):
        if not self._did_execute:
            self._did_execute = True
            super().__setattr__(
                "_internal",
                execute_func(
                    self._code,
                    *self.memory.dfs,
                ),
            )
            super().__setattr__("_did_execute", True)


class MagicReturn(MagicReturnCore):
    def print_history(self):
        colorama.init(autoreset=True)

        # Print full history of the code and associated prompts
        for i, item in enumerate(self.memory.history):
            print(
                f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT}Prompt {i + 1}:{colorama.Style.RESET_ALL} {item[0]}"
            )
            print(
                f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT}Code {i + 1}:{colorama.Style.RESET_ALL}\n{colorama.Fore.GREEN}{item[1]}"
            )
            print(f"{colorama.Fore.YELLOW}{'-' * 80}")
        return self

    def inspect(self):
        return list(self.memory.history)

    def inject(
        self, function_name: str, ai_module: str = "ai", ai_module_path: str = "ai"
    ):
        inject_code(
            self.code,
            function_name=function_name,
            ai_module=ai_module,
            ai_module_path=ai_module_path,
        )

    def __getattr__(self, name):
        return getattr(self.internal, name)

    def __repr__(self):
        return repr(self.internal)

    def __delattr__(self, name):
        delattr(self.internal, name)

    def __len__(self):
        return len(self.internal)

    def __contains__(self, item):
        return item in self.internal

    def __str__(self):
        return str(self.internal)

    def __getitem__(self, key):
        return self.internal[key]

    def __setitem__(self, key, value):
        self.internal[key] = value

    def __delitem__(self, key):
        del self.internal[key]

    def __iter__(self):
        return iter(self.internal)

    def __next__(self):
        return next(iter(self.internal))


def magic_prompt_with_dataframes(
    prompt: str,
    *dfs: List[GeoOrDataFrame],
    return_type: Type = None,
    user_provided_libraries: List[str] = None,
    memory: Memory = None,
) -> Union[MagicReturn, Any]:
    dfs = dfs or []
    return_type = return_type or determine_type(prompt)
    return MagicReturn(
        memory=memory
        or Memory(
            dfs=dfs,
            return_type=return_type,
            user_provided_libraries=user_provided_libraries,
            key=prompt,
        ),
        prompt=prompt,
    )
