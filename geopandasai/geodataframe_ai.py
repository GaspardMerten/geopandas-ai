from typing import List, Any, Union, Type

from geopandas import GeoDataFrame

from .code import MagicReturn, chat
from .types import GeoOrDataFrame

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
        # User provided description through the describe method
        self.ai_description = None

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
        self.ai_description = description
        return self

    def chat(
        self,
        prompt: str,
        *other_dfs: List[GeoOrDataFrame],
        return_type: Type = None,
        user_provided_libraries: List[str] = None,
    ) -> Union[Any, MagicReturn]:
        self.state = chat(
            prompt,
            *([self] + list(other_dfs)),
            return_type=return_type,
            user_provided_libraries=user_provided_libraries,
        )
        self._memories.add(self.state.memory)
        return self.state.materialize()

    def improve(self, prompt: str) -> Any:
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        self.state = self.state.improve(prompt)
        return self.state.materialize()

    @property
    def code(self) -> str:
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.code

    def inspect(self) -> str:
        """
        Print the history of the last output.
        """
        if self.state is None:
            raise ValueError("No code has been generated yet. Please run a chat first.")
        return self.state.print_history()

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
