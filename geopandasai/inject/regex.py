import re

inject_code_pattern = re.compile(
    r"(\w+)\s*\.\s*chat\s*\(\s*(['\"]{1,3})[^'\"]*?\2(?:,\s*((?:\w+\s*,\s*)*\w+))?(?:,\s*return_type\s*=\s*ResultType\.\w+)?\s*\)(?:\s*\.\s*chat\s*\(\s*(['\"]{1,3})[^'\"]*?\4(?:,\s*return_type\s*=\s*ResultType\.\w+)?\s*\))*\s*\.\s*inject\s*\(\s*(['\"]{1,3})[^'\"]*?\5(?:,\s*ai_module\s*=\s*(['\"]{1,3})[^'\"]*?\6)?(?:,\s*ai_module_path\s*=\s*(['\"]{1,3})[^'\"]*?\7)?\s*\)",
    re.DOTALL | re.MULTILINE,
)
