from typing import List, Any, Union, Type, Sequence

from geopandas import GeoDataFrame
from pandas import DataFrame

from .services import MagicReturn
from .services.code._internal import magic_prompt_with_dataframes
from .shared.types import GeoOrDataFrame

__all__ = ["GeoDataFrameAI"]


class GeoDataFrameAI(GeoDataFrame):
    """
    A class to represent a GeoDataFrame with AI capabilities. It is a proxy for
    the GeoPandas GeoDataFrame class, allowing for additional functionality
    related to AI and machine learning tasks.
    """

    def __init__(self, *args, description: str = None, **kwargs):
        """
        Initialize the GeoDataFrameAI class.
        """
        super().__init__(*args, **kwargs)
        # User provided description through the describe method
        self.description = description or ""

        # The state of the conversation, calling chat initializes this
        # while calling improve will update the state.
        self.state: Union[MagicReturn, Any] = None

        # A helper storing previous conversation to ensure the reset
        # method delete entire conversation history, even if multiple
        # '.chat' were called.
        self._memories = set()

    def set_description(self, description: str):
        """
        Describe the GeoDataFrameAI. This is a user-provided description that
        can be used to provide context for the AI.
        """
        assert (
            self.state is None
        ), "You cannot set a description after running a chat or improve method. Please reset the state first."
        self.description = description
        return self

    def chat(
        self,
        prompt: str,
        *other_dfs: Sequence[GeoOrDataFrame | "GeoDataFrameAI"],
        return_type: Type = None,
        provided_libraries: List[str] = None,
    ) -> Union[Any, MagicReturn]:
        """
        This method is used to start a conversation with the AI.
        It takes a prompt and any number of other GeoDataFrames as input.
        The prompt is a string that describes the task or question to be answered.
        The other_dfs are additional GeoDataFrames that can be used to provide
        context for the AI.

        :param prompt: The prompt to start the conversation.
        :param other_dfs: Additional GeoDataFrames to provide context.
        :param return_type: The type of the return value. If None, it will be inferred.
        :param provided_libraries: A list of libraries that are provided by the user.
        :return: The result of the conversation, which can be any type or a MagicReturn object.
        """

        # Reset the state if it was previously set, and initialize a new memory
        self.state = magic_prompt_with_dataframes(
            prompt,
            *([self] + list(other_dfs)),
            return_type=return_type,
            provided_libraries=provided_libraries,
        )
        # Only for caching purposes, we store the memory of the conversation to be able to clean it up later.
        self._memories.add(self.state.memory)

        return self.return_value()

    def return_value(self):
        if (
            self.state.memory.return_type == GeoDataFrame
            or self.state.memory.return_type == DataFrame
        ):
            return self.state.internal
        return self.state.execute()

    def improve(
        self,
        prompt: str,
        *other_dfs: List[GeoOrDataFrame | "GeoDataFrameAI"],
        return_type: Type = None,
        provided_libraries: List[str] = None,
    ) -> Union[Any, MagicReturn]:
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")

        self.state = self.state.improve(
            prompt,
            *(self.state.memory.dfs if not other_dfs else ([self] + list(other_dfs))),
            return_type=return_type,
            provided_libraries=provided_libraries,
        )

        return self.return_value()

    @property
    def code(self) -> str:
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.code

    def inspect(self) -> "MagicReturn":
        """
        Print the history of the last output.
        """
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.inspect()

    def reset(self):
        """
        Reset the state of the GeoDataFrameAI.
        """
        self.state = None
        for memory in self._memories:
            memory.reset()

    def inject(self, function_name: str, ai_module="ai", ai_module_path="ai"):
        """
        Inject the state of the GeoDataFrameAI into the current context.
        """
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.inject(function_name, ai_module, ai_module_path)
