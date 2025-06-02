from typing import Any, List


def type_to_literal(return_type):
    if return_type.__module__ == "builtins":
        return return_type.__name__
    else:
        return f"{return_type.__module__}.{return_type.__name__}"


def get_available_return_types() -> List[str]:
    """
    Get a list of available result types.
    """
    from ..config import get_geopandasai_config

    types = [type_to_literal(rt) for rt in get_geopandasai_config().return_types]
    return sorted(types)


def return_type_from_literal(literal: str) -> Any:
    """
    Get a result type from its literal representation.
    """
    from ..config import get_geopandasai_config

    for rt in get_geopandasai_config().return_types:
        if type_to_literal(rt) == literal:
            return rt
    raise ValueError(f"Unknown return type literal: {literal}")
