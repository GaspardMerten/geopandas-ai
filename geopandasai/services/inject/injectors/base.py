import abc
import re
from typing import Callable


class ACodeInjector(abc.ABC):
    @abc.abstractmethod
    def inject(
        self,
        pattern: re.Pattern,
        function_call_builder: Callable[[re.Match], str],
        import_statement: str,
    ):
        """
        Freeze the code and save it to a file.
        """
        pass
