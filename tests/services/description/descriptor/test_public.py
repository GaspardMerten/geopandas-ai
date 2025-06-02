import unittest

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from geopandasai.services.description.descriptor.public import PublicDataDescriptor


class TestPublicDataDescriptor(unittest.TestCase):
    def setUp(self):
        # Create a sample GeoDataFrame for testing
        self.geometry = [Point(0, 0), Point(1, 1), Point(2, 2)]
        self.data = {
            "name": ["A", "B", "C"],
            "value": [1, 2, 3],
            "category": ["X", "Y", "Z"],
        }
        self.gdf = gpd.GeoDataFrame(self.data, geometry=self.geometry, crs="EPSG:4326")
        self.descriptor = PublicDataDescriptor(sample_rows=2)

    def test_description_immutability(self):
        # Get description twice
        description1 = self.descriptor.describe(self.gdf)
        description2 = self.descriptor.describe(self.gdf)

        # Check that descriptions are identical
        self.assertEqual(description1, description2)

        new_descriptor = PublicDataDescriptor(sample_rows=2)

        new_description = new_descriptor.describe(self.gdf)
        self.assertEqual(new_description, description1)

    def test_description_content(self):
        description = self.descriptor.describe(self.gdf)

        # Check that essential components are present
        self.assertIn("Type: geopandas.geodataframe.GeoDataFrame", description)
        self.assertIn("CRS: EPSG:4326", description)
        self.assertIn("Geometry type (geometry column):Point", description)
        self.assertIn(
            "Shape: (3, 4)", description
        )  # 3 rows, 4 columns (3 data + 1 geometry)

        # Check that column information is present
        self.assertIn("name", description)
        self.assertIn("value", description)
        self.assertIn("category", description)

        # Check that statistics are included
        self.assertIn("Statistics:", description)

    def test_sample_rows_limit(self):
        # Create a larger GeoDataFrame
        n_rows = 100
        geometry = [Point(i, i) for i in range(n_rows)]
        data = {"value": np.random.rand(n_rows), "category": ["X"] * n_rows}
        large_gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")

        # Get description
        sample_rows = 13
        descriptor = PublicDataDescriptor(sample_rows=sample_rows)
        description = descriptor.describe(large_gdf)

        # Check that only sample_rows number of rows are shown
        sample_section = description.split("Randomly sampled rows")[1]
        row_count = sample_section.count("\n") - 3  # Subtract 1 for the headers
        self.assertEqual(row_count, sample_rows)  # Should match sample_rows parameter


if __name__ == "__main__":
    unittest.main()
