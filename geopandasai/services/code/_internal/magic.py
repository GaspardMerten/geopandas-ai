from typing import Any, List, Type, Union, Optional, Sequence

import colorama

from .code import build_code
from .determine_type import determine_type
from .execute import execute_func
from .memory import Memory, EntryInput
from ...inject import inject_code
from ....shared.types import GeoOrDataFrame


class MagicReturnCore:
    """
    Core class for generating, executing, and managing AI-generated code from a natural language prompt.
    """

    def __init__(self, memory: Memory, prompt: str):
        """
        :param memory: An instance of Memory that tracks prompts, results, and data context.
        :param prompt: The natural language instruction for which code is generated.
        """
        self.memory = memory
        self._did_execute = False
        self._internal = None

        self.prompt = prompt

        self._code = memory.get_code_for_entry(
            EntryInput(
                prompt=prompt,
                return_type=self.memory.return_type,
                provided_libraries=memory.provided_libraries,
            )
        ) or build_code(
            self.prompt,
            memory.return_type,
            memory.dfs,
            history=memory.get_history_string(),
            user_provided_libraries=memory.provided_libraries,
        )

        self.memory.log(
            EntryInput(
                prompt=prompt,
                return_type=self.memory.return_type,
                provided_libraries=memory.provided_libraries,
            ),
            code=self._code,
        )

    def improve(
        self,
        prompt: str,
        *dfs: Optional[Sequence[GeoOrDataFrame]],
        return_type: Optional[Type] = None,
        provided_libraries: Optional[List[str]] = None,
    ) -> Union["MagicReturn", Any]:
        """
        Re-generates code with an improved or updated prompt and optionally new data or type context.

        :param prompt: Updated natural language instruction.
        :param dfs: Optional list of DataFrames to provide additional context.
        :param return_type: Optional expected return type of the generated code.
        :param provided_libraries: Optional list of extra libraries to use during code generation.
        :return: A new MagicReturn instance or directly the result.
        :rtype: Union[MagicReturn, Any]
        """

        if return_type is not None:
            self.memory.return_type = return_type
        if dfs:
            self.memory.dfs = dfs
        if provided_libraries is not None:
            self.memory.provided_libraries = provided_libraries

        return magic_prompt_with_dataframes(
            prompt,
            *self.memory.dfs,
            return_type=self.memory.return_type,
            provided_libraries=self.memory.provided_libraries,
            memory=self.memory,
        )

    def execute(self) -> Any:
        """
        Executes the generated code if it hasn’t been executed yet.

        :return: Self (with internal result populated).
        """
        self._build()
        return self

    def reset(self) -> "MagicReturnCore":
        """
        Clears the memory state and returns a fresh object.

        :return: Self with memory reset.
        :rtype: MagicReturnCore
        """
        self.memory.reset()
        return self

    @property
    def code(self) -> str:
        """
        :return: The code string generated for the prompt.
        :rtype: str
        """
        return self._code

    @property
    def internal(self) -> Any:
        """
        :return: The result of executing the generated code.
        """
        self._build()
        return self._internal

    def _build(self):
        """Internal method that lazily executes code exactly once."""
        if not self._did_execute:
            self._internal = execute_func(
                self._code,
                self.memory.return_type,
                *self.memory.dfs,
            )
            self._did_execute = True


class MagicReturn(MagicReturnCore):
    """
    Extended class that adds inspectability, print utilities, and rich Python object proxying.
    """

    def inspect(self) -> "MagicReturn":
        """
        Prints the full prompt/code history with syntax coloring.

        :return: Self for chaining.
        :rtype: MagicReturn
        """
        colorama.init(autoreset=True)
        for i, (prompt, code) in enumerate(self.memory.history, start=1):
            print(
                f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT}Prompt {i}:{colorama.Style.RESET_ALL} {prompt}"
            )
            print(
                f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT}Code {i}:{colorama.Style.RESET_ALL}\n"
                f"{colorama.Fore.GREEN}{code}"
            )
            print(f"{colorama.Fore.YELLOW}{'-' * 80}")
        return self

    def inject(
        self,
        function_name: str,
        ai_module: str = "ai",
        ai_module_path: str = "ai",
    ) -> None:
        """
        Injects the generated code into a live module or system under a given function name.

        :param function_name: The name to assign to the injected function.
        :param ai_module: Logical module name where the function should reside.
        :param ai_module_path: Filesystem path or import path to the module.
        """
        inject_code(
            self.code,
            function_name=function_name,
            ai_module=ai_module,
            ai_module_path=ai_module_path,
        )

    # Proxy magic methods to delegate to the internal result
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
    *dfs: GeoOrDataFrame,
    return_type: Optional[Type] = None,
    provided_libraries: Optional[List[str]] = None,
    memory: Optional[Memory] = None,
) -> Union[MagicReturn, Any]:
    """
    Convenience function to generate a `MagicReturn` from a prompt and optional context.

    :param prompt: Natural language instruction to generate code for.
    :param dfs: DataFrames to pass as context into the generated code.
    :param return_type: Expected return type of the result.
    :param provided_libraries: Additional libraries to make available to the code builder.
    :param memory: Optional preconfigured Memory object to use.
    :return: A MagicReturn instance or the computed result.
    :rtype: Union[MagicReturn, Any]
    """
    dfs = list(dfs)

    return_type = return_type or determine_type(prompt)

    memory = memory or Memory(
        dfs=dfs,
        return_type=return_type,
        provided_libraries=provided_libraries or [],
        key=prompt,
    )
    return MagicReturn(memory=memory, prompt=prompt)
