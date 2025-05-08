import hashlib
import importlib.util
import importlib.util
import tempfile
import traceback
from typing import Iterable, List, Self, Any

import colorama
from geopandas import GeoDataFrame

from . import get_from_cache, set_to_cache
from .config import get_libraries
from .determine_type import determine_type
from .inject.inject import inject_code
from .prompt import prompt_with_template
from .template import Template, parse_template
from .types import GeoOrDataFrame, ResultType, Output


def _dfs_to_string(dfs: List[GeoOrDataFrame]) -> str:
    description = ""

    for i, df in enumerate(dfs):
        description += f"DataFrame {i + 1}, will be sent_as df_{i + 1}:\n"
        if hasattr(df, "crs"):
            description += f"CRS: {df.crs}\n"
        description += f"Shape: {df.shape}\n"
        description += f"Columns (with types): {' - '.join([f'{col} ({df[col].dtype})' for col in df.columns])}\n"
        description += f"Statistics:\n{df.describe()}\n\n"
        description += f"First 5 rows:\n{df.head()}\n\n"

    return description


def execute_func(code: str, *dfs: Iterable[GeoOrDataFrame]):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".py", mode="w") as f:
        f.write(code)
        f.flush()
        spec = importlib.util.spec_from_file_location("output", f.name)
        output_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(output_module)
        return output_module.execute(*dfs)


def build_static_description(dfs, result_type, user_provided_libraries):
    result_type_to_python_type = {
        ResultType.TEXT: "str",
        ResultType.MAP: "folium.Map",
        ResultType.PLOT: "plt.Figure",
        ResultType.DATAFRAME: "pd.DataFrame",
        ResultType.GEODATAFRAME: "gp.GeoDataFrame",
        ResultType.LIST: "list",
        ResultType.DICT: "dict",
        ResultType.INTEGER: "int",
        ResultType.FLOAT: "float",
        ResultType.BOOLEAN: "bool",
    }
    libraries = (
        ["pandas", "matplotlib.pyplot", "folium", "geopandas"]
        + (user_provided_libraries or [])
        + get_libraries()
    )
    libraries_str = ", ".join(libraries)
    dataset_description = _dfs_to_string(dfs)
    df_args = ", ".join([f"df_{i + 1}" for i in range(len(dfs))])
    system_instructions = (
        "You are a helpful assistant specialized in returning Python code snippets formatted as follow {"
        f"def execute({df_args}) -> {result_type_to_python_type[result_type]}:\n"
        "    ...\n"
    )
    return dataset_description, libraries_str, system_instructions


class Memory:
    def __init__(
        self,
        dfs: List[GeoOrDataFrame],
        result_type: ResultType,
        user_provided_libraries: List[str] = None,
    ):
        self.dfs = dfs
        self.result_type = result_type
        self._cache = dict()
        self.user_provided_libraries = user_provided_libraries or []
        self.history = []
        self.memory_cache_key = hashlib.sha256(
            "".join(
                build_static_description(dfs, result_type, user_provided_libraries)
            ).encode()
        ).hexdigest()
        self.restore_cache()

    def restore_cache(self):
        self._cache = get_from_cache(self.memory_cache_key) or {}

    def flush_cache(self):
        set_to_cache(self.memory_cache_key, self._cache)

    def log(self, prompt: str, code: str):
        self.history.append([prompt, code])

    def get_history_string(self):
        return (
            "<History>"
            + "\n".join(
                [
                    f"<Prompt>{item[0]}</Prompt><Output>{item[1]}</Output>"
                    for item in self.history
                ]
            )
            + "</History>"
        )

    def build_key_for_prompt(self, prompt: str) -> str:
        description = build_static_description(
            self.dfs, self.result_type, self.user_provided_libraries
        )
        return hashlib.sha256((prompt + "".join(description)).encode()).hexdigest()

    def get_for_prompt(self, prompt: str):
        key = self.build_key_for_prompt(prompt)
        if key in self._cache:
            return self._cache[key]

        return None

    def set_for_prompt(self, prompt: str, code: str):
        key = self.build_key_for_prompt(prompt)
        self._cache[key] = code
        self.flush_cache()

    def reset(self):
        self.history = []
        self._cache = {}
        self.flush_cache()


class WithPrompt:
    def __init__(self, obj_callable, memory: Memory, prompt: str):
        self.__obj = None
        self.memory = memory
        self._obj_callable = obj_callable

        self.prompt = f"{memory.get_history_string()}\n\n Now while taking into account previous prompts and result, answer this prompt: <Prompt>{prompt}</Prompt>"
        self.code = None
        code = memory.get_for_prompt(self.prompt)

        if not code:
            obj = self._obj
            code = obj.source_code
            memory.set_for_prompt(self.prompt, obj.source_code)
        self.code = code
        memory.log(prompt, code)

    @property
    def _obj(self):
        if self.__obj is None and not self.code:
            self.__obj = self._obj_callable(
                self.prompt,
                result_type=self.memory.result_type,
                dfs=self.memory.dfs,
                user_provided_libraries=self.memory.user_provided_libraries,
            )
        else:
            self.__obj = execute_func(
                self.code,
                *self.memory.dfs,
            )
        return self.__obj

    def chat(self, prompt: str) -> Any | Self:
        return execute_with_result_type(
            prompt,
            result_type=self.memory.result_type,
            dfs=self.memory.dfs,
            user_provided_libraries=get_libraries(),
            memory=self.memory,
        )

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

    def print_code(self):
        print(self.code)
        return self

    def inject(
        self, function_name: str, ai_module: str = "ai", ai_module_path: str = "ai"
    ):
        inject_code(
            self.code,
            function_name=function_name,
            ai_module=ai_module,
            ai_module_path=ai_module_path,
        )

    def reset(self):
        self.__obj = None
        self.memory.reset()
        return self

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def __repr__(self):
        return repr(self._obj)


def memory_function_wrapper(func):
    def wrapper(
        prompt: str,
        result_type: ResultType,
        dfs: List[GeoOrDataFrame],
        user_provided_libraries: List[str] = None,
        memory: Memory = None,
    ):
        memory = memory or Memory(
            dfs=dfs,
            result_type=result_type,
            user_provided_libraries=user_provided_libraries,
        )
        return WithPrompt(func, memory, prompt)

    return wrapper


@memory_function_wrapper
def execute_with_result_type(
    prompt: str,
    result_type: ResultType,
    dfs: List[GeoOrDataFrame],
    user_provided_libraries: List[str] = None,
) -> Output:
    dataset_description, libraries_str, system_instructions = build_static_description(
        dfs, result_type, user_provided_libraries
    )

    max_attempts = 5
    last_code = None
    last_exception = None
    response = None
    result = None

    for _ in range(max_attempts):
        print(last_code)
        print(last_exception)
        if last_code:
            template = parse_template(
                Template.CODE_PREVIOUSLY_ERROR,
                system_instructions=system_instructions,
                last_code=last_code,
                last_exception=last_exception,
                libraries=libraries_str,
                prompt=prompt,
                result_type=result_type.name.lower(),
                dataset_description=dataset_description,
            )
            response = prompt_with_template(template, remove_markdown_code_limiter=True)
        else:
            template = parse_template(
                Template.CODE,
                system_instructions=system_instructions,
                last_code=last_code,
                last_exception=last_exception,
                libraries=libraries_str,
                prompt=prompt,
                result_type=result_type.name.lower(),
                dataset_description=dataset_description,
            )

            response = prompt_with_template(template, remove_markdown_code_limiter=True)

            try:
                result = execute_func(response, *dfs)
                break
            except Exception as e:
                last_code = response
                last_exception = f"{e}, {traceback.format_exc()}"

    if result is None:
        raise ValueError("The code did not return a valid result.")

    if isinstance(result, GeoDataFrame):
        from . import GeoDataFrameAI

        result = GeoDataFrameAI.from_geodataframe(result)

    return Output(
        source_code=response,
        result=result,
    )


def prompt_with_dataframes(
    prompt: str,
    dfs: List[GeoOrDataFrame] = None,
    result_type: ResultType = None,
    user_provided_libraries: List[str] = None,
) -> Output:
    dfs = dfs or []
    result_type = result_type or determine_type(prompt)
    return execute_with_result_type(
        prompt, result_type, dfs, user_provided_libraries=user_provided_libraries
    )


def geopandas_ai_prompt(
    prompt: str,
    dfs: List[GeoOrDataFrame] = None,
    result_type: ResultType = None,
    user_provided_libraries: List[str] = None,
):
    return prompt_with_dataframes(
        prompt,
        dfs=dfs,
        result_type=result_type,
        user_provided_libraries=user_provided_libraries,
    )
