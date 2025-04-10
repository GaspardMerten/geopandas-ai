import enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

import folium
import pandas as pd
from geopandas import GeoDataFrame
from matplotlib import pyplot as plt
from pandas import DataFrame

GeoOrDataFrame = GeoDataFrame | DataFrame


class ResultType(enum.Enum):
    """
    Enum to represent the type of result returned by the AI.
    """

    DATAFRAME = "dataframe"
    GEODATAFRAME = "geodataframe"
    TEXT = "text"
    PLOT = "plot"
    MAP = "map"
    LIST = "list"
    DICT = "dict"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


Output = (
    pd.DataFrame
    | GeoDataFrame
    | str
    | list
    | dict
    | folium.Map
    | plt.Figure
    | int
    | float
    | bool
)


@dataclass
class TemplateData:
    messages: List[Dict]
    max_tokens: Optional[int] = None


@dataclass
class Output:
    source_code: str
    result: Any
