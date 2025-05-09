from typing import List, Any

from geopandas import GeoDataFrame

from .code import MagicReturn, chat

__all__ = ["GeoDataFrameAI"]


class GeoDataFrameAI(GeoDataFrame):
    """
    A class to represent a GeoDataFrame with AI capabilities. It is a proxy for
    the GeoPandas GeoDataFrame class, allowing for additional functionality
    related to AI and machine learning tasks.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the GeoDataFrameAI class.
        """
        super().__init__(*args, **kwargs)
        self.last_output: MagicReturn | Any = None

    def chat(
        self,
        prompt: str,
        *other_dfs,
        result_type=None,
        user_provided_libraries: List[str] = None,
    ) -> Any | MagicReturn:
        self.last_output = chat(
            prompt,
            *([self] + list(other_dfs)),
            result_type=result_type,
            user_provided_libraries=user_provided_libraries,
        )
        return self.last_output.materialize()

    def improve(self, prompt: str) -> Any:
        if self.last_output is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.last_output.chat(prompt).materialize()

    @property
    def code(self) -> str:
        if self.last_output is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.last_output.source_code

    @staticmethod
    def from_geodataframe(gdf: GeoDataFrame) -> "GeoDataFrameAI":
        """
        Convert a GeoDataFrame or DataFrame to a GeoDataFrameAI.
        """
        if isinstance(gdf, GeoDataFrame):
            return GeoDataFrameAI(gdf)
        else:
            return GeoDataFrameAI(GeoDataFrame(gdf))
