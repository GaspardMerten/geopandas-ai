import json
import os

__all__ = ["set_active_lite_llm_config", "get_active_lite_llm_config"]

_active_lite_llm_config: dict | None = None


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
