from typing import List, Any, Union

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
        self.state: Union[MagicReturn, Any] = None
        self._memories = set()

    def chat(
        self,
        prompt: str,
        *other_dfs,
        result_type=None,
        user_provided_libraries: List[str] = None,
    ) -> Union[Any, MagicReturn]:
        self.state = chat(
            prompt,
            *([self] + list(other_dfs)),
            result_type=result_type,
            user_provided_libraries=user_provided_libraries,
        )
        self._memories.add(self.state.memory)
        return self.state.materialize()

    def improve(self, prompt: str) -> Any:
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.improve(prompt).materialize()

    @property
    def code(self) -> str:
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.code

    def inspect(self) -> str:
        """
        Inspect the last output.
        """
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.inspect()

    def print_history(self) -> List[str]:
        """
        Print the history of the last output.
        """
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.print_history()

    @staticmethod
    def from_geodataframe(gdf: GeoDataFrame) -> "GeoDataFrameAI":
        """
        Convert a GeoDataFrame or DataFrame to a GeoDataFrameAI.
        """
        if isinstance(gdf, GeoDataFrame):
            return GeoDataFrameAI(gdf)
        else:
            return GeoDataFrameAI(GeoDataFrame(gdf))

    def reset(self):
        """
        Reset the state of the GeoDataFrameAI.
        """
        self.state = None
        for memory in self._memories:
            memory.reset()
