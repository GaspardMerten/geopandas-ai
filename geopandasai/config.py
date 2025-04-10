import json
import os

active_config: dict | None = None


def set_active_lite_llm_config(config: dict) -> None:
    global active_config
    active_config = config


def get_active_lite_llm_config() -> dict:
    global active_config
    if active_config is None and os.environ.get("LITELLM_CONFIG"):
        active_config = json.loads(os.environ["LITELLM_CONFIG"])

    assert active_config is not None, "Active config is not set, please set it first using set_active_lite_llm_config or set the LITELLM_CONFIG environment variable."
    return active_config
