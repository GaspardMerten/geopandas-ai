from typing import List

from geopandas import GeoDataFrame

from .prompt import prompt_with_dataframes
from .types import GeoOrDataFrame

__all__ = ["GeoDataFrameAI"]


class GeoDataFrameAI(GeoDataFrame):
    """
    A class to represent a GeoDataFrame with AI capabilities. It is a proxy for
    the GeoPandas GeoDataFrame class, allowing for additional functionality
    related to AI and machine learning tasks.
    """

    def chat(self, prompt: str, *other_dfs: List[GeoOrDataFrame]):
        return prompt_with_dataframes(prompt, self, *other_dfs)

    @staticmethod
    def from_geodataframe(gdf: GeoDataFrame) -> "GeoDataFrameAI":
        """
        Convert a GeoDataFrame or DataFrame to a GeoDataFrameAI.
        """
        if isinstance(gdf, GeoDataFrame):
            return GeoDataFrameAI(gdf)
        else:
            return GeoDataFrameAI(GeoDataFrame(gdf))
