from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union

from geopandas import GeoDataFrame
from pandas import DataFrame

GeoOrDataFrame = Union[GeoDataFrame, DataFrame]


@dataclass
class TemplateData:
    messages: List[Dict]
    max_tokens: Optional[int] = None


@dataclass
class Output:
    source_code: str
    result: Any
