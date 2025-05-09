from typing import Set, Any, List

import folium
from geopandas import GeoDataFrame
from matplotlib.figure import Figure
from pandas import DataFrame


class ResultTypeRegistry:
    """
    Registry for result types.
    """

    def __init__(self):
        self._registry: Set[Any] = {
            DataFrame,
            GeoDataFrame,
            str,
            folium.Map,
            Figure,
            int,
            float,
            bool,
        }

    def register(self, result_type):
        """
        Register a new result type.
        """
        if not isinstance(result_type, type):
            raise TypeError("Result type must be a class.")
        self._registry.add(result_type)

    def unregister(self, result_type):
        """
        Unregister a result type.
        """
        if not isinstance(result_type, type):
            raise TypeError("Result type must be a class.")
        self._registry.discard(result_type)

    def __iter__(self):
        """
        Iterate over the registered result types.
        """
        return iter(self._registry)


result_type_registry = ResultTypeRegistry()


def type_to_literal(result_type):
    if result_type.__module__ == "builtins":
        return result_type.__name__
    else:
        return f"{result_type.__module__}.{result_type.__name__}"


def get_available_result_types() -> List[str]:
    """
    Get a list of available result types.
    """
    return [type_to_literal(rt) for rt in result_type_registry]


def result_type_from_literal(literal: str) -> Any:
    """
    Get a result type from its literal representation.
    """
    for rt in result_type_registry:
        if type_to_literal(rt) == literal:
            return rt
    raise ValueError(f"Result type '{literal}' not found in registry.")
