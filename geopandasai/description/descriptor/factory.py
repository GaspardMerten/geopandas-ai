from .base import Descriptor
from .public import PublicDataDescriptor


def descriptor_factory(
    descriptor_type: type[Descriptor] = PublicDataDescriptor,
) -> Descriptor:
    return descriptor_type()
