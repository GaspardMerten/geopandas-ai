import geopandas
import pandas as pd

from .base import Descriptor


class PublicDataDescriptor(Descriptor):
    """
    A descriptor that provides a description of the data which includes
    the shape, columns, statistics, and first 5 rows of the dataframe.

    This means that private data can be shared with the AI.
    """

    def describe(self, dataframe) -> str:
        description = ""
        if isinstance(dataframe, pd.DataFrame):
            description += "Type: DataFrame\n"
        elif isinstance(dataframe, geopandas.GeoDataFrame):
            description += "Type: GeoDataFrame\n"
        if hasattr(dataframe, "crs"):
            description += f"CRS: {dataframe.crs}\n"
        if hasattr(dataframe, "geometry"):
            description += f"Geometry: {dataframe.geometry.name}\n"
        if hasattr(dataframe, "index"):
            description += f"Index: {dataframe.index}\n"
        description += f"Shape: {dataframe.shape}\n"
        description += f"Columns (with types): {' - '.join([f'{col} ({dataframe[col].dtype})' for col in dataframe.columns])}\n"
        description += f"Statistics:\n{dataframe.describe()}\n\n"
        description += f"First 5 rows:\n{dataframe.head()}\n\n"

        return description
