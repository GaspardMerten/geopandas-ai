import abc

from ....shared.types import GeoOrDataFrame


class ADescriptor(abc.ABC):
    """
    Base class for all descriptors.
    """

    @abc.abstractmethod
    def describe(self, dataframe: GeoOrDataFrame) -> str:
        """
        Describe the object.
        """
        pass
