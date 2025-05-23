import geopandas as gpd
import pandas as pd

from .base import Descriptor
from ...return_type import type_to_literal


class PublicDataDescriptor(Descriptor):
    """
    A descriptor that provides a description of the data which includes
    the shape, columns, statistics, and first 5 rows of the dataframe.

    This means that private data can be shared with the AI.
    """

    def describe(self, instance) -> str:
        description = ""
        description += f"Type: {type_to_literal(type(instance))}\n"

        if isinstance(instance, gpd.GeoDataFrame):
            if hasattr(instance, "crs"):
                description += f"CRS: {instance.crs}\n"
            if hasattr(instance, "geometry"):
                geometry_type = instance.geometry.geom_type
                description += f"Geometry type (geometry column):{', '.join(geometry_type.unique())}"

        if isinstance(instance, pd.DataFrame):
            if hasattr(instance, "index"):
                description += f"Index: {instance.index}\n"

            description += f"Shape: {instance.shape}\n"
            description += f"Columns (with types): {' - '.join([f'{col} ({instance[col].dtype})' for col in instance.columns])}\n"
            description += f"Statistics:\n{instance.describe()}\n\n"
            description += f"First 5 rows:\n{instance.head()}\n\n"
            description += f"Last 5 rows:\n{instance.tail()}\n\n"
        if hasattr(instance, "ai_description") and instance.ai_description:
            description += f"User provided description: {instance.ai_description}\n\n"

        return description
