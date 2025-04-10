import enum

from geopandas import GeoDataFrame
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
