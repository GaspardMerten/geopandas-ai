from typing import Type

from ..types import GeoOrDataFrame
from .descriptor import Descriptor, descriptor_factory
from .descriptor.public import PublicDataDescriptor


def describe_dataframe(
    dataframe: GeoOrDataFrame, descriptor: Type[Descriptor] = PublicDataDescriptor
) -> str:
    """
    Describe the dataframe using the provided descriptor.
    """

    return descriptor_factory(descriptor).describe(dataframe)
