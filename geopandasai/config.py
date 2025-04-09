import json
import os


def get_active_lite_llm_config() -> dict:
    return {
        "model": "vertex_ai/gemini-2.0-flash",
        "vertex_credentials": json.dumps(
            json.load(open(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "google-credentials.json"), "r")))
    }
