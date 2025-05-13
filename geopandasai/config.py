import json
import os

__all__ = [
    "set_active_lite_llm_config",
    "get_active_lite_llm_config",
    "set_libraries",
    "get_libraries",
]

from typing import Union

_active_lite_llm_config: Union[dict, None] = None
_libraries = []


def set_active_lite_llm_config(config: dict) -> None:
    global _active_lite_llm_config
    _active_lite_llm_config = config


def get_active_lite_llm_config() -> dict:
    global _active_lite_llm_config
    if _active_lite_llm_config is None and os.environ.get("LITELLM_CONFIG"):
        _active_lite_llm_config = json.loads(os.environ["LITELLM_CONFIG"])

    assert (
        _active_lite_llm_config is not None
    ), "Active config is not set, please set it first using set_active_lite_llm_config or set the LITELLM_CONFIG environment variable."
    return _active_lite_llm_config


def set_libraries(libraries: list) -> None:
    global _libraries
    _libraries = libraries


def get_libraries() -> list:
    global _libraries
    return _libraries
