import abc

from ...types import GeoOrDataFrame


class Descriptor(abc.ABC):
    """
    Base class for all descriptors.
    """

    @abc.abstractmethod
    def describe(self, dataframe: GeoOrDataFrame) -> str:
        """
        Describe the object.
        """
        pass
