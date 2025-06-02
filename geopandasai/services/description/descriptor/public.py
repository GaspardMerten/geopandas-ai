import geopandas as gpd
import pandas as pd

from .base import ADescriptor
from ....shared.return_type import type_to_literal


class PublicDataDescriptor(ADescriptor):
    """
    A descriptor that provides a description of the data which includes
    the shape, columns, statistics, and first 5 rows of the dataframe.

    This means that potentially private data could be shared with a distant AI service, use with caution.
    """

    def __init__(self, sample_rows: int = 20):
        """
        Initialize the PublicDataDescriptor.

        :param sample_rows: Number of rows to sample from the dataframe for description.
        """
        super().__init__()
        self.sample_rows = sample_rows

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

            numbers_of_rows_to_sample = min(len(instance), self.sample_rows)
            rows = instance.sample(numbers_of_rows_to_sample, random_state=42)
            description += (
                f"Randomly sampled rows ({numbers_of_rows_to_sample} rows):\n"
            )
            description += rows.to_string(index=False, max_colwidth=100) + "\n\n"
        if hasattr(instance, "ai_description") and instance.ai_description:
            description += f"User provided description: {instance.ai_description}\n\n"

        return description
