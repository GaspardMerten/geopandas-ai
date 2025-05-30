from typing import Optional

from .descriptor import ADescriptor
from ...shared.types import GeoOrDataFrame


def describe_dataframe(
    dataframe: GeoOrDataFrame, descriptor: Optional[ADescriptor] = None
) -> str:
    """
    Describe the dataframe using the provided descriptor.
    """

    if descriptor is None:
        from ...config import get_geopandasai_config

        descriptor = get_geopandasai_config().descriptor

    return descriptor.describe(dataframe)
