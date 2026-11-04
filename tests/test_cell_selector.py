import unittest
from pathlib import Path

import numpy as np
from rasterio.crs import CRS
from rasterio.transform import from_origin

from src.interpreter.input_loader import ModelInputs
from src.interpreter.cell_selector import select_raster_cell


def create_test_inputs():
    """Create a small synthetic ModelInputs object for testing."""

    susceptibility = np.array(
        [
            [0.60, 0.65, 0.70, 0.75],
            [0.68, 0.72, 0.75, 0.80],
            [0.74, 0.78, 0.82, 0.85],
        ],
        dtype=np.float32,
    )

    valid_mask = np.ones((3, 4), dtype=bool)
    valid_mask[2, 3] = False

    susceptibility[2, 3] = -9999

    factor_arrays = {
        "elevation": np.full((3, 4), 0.5, dtype=np.float32),
        "slope": np.full((3, 4), 0.5, dtype=np.float32),
        "distance_to_rivers": np.full((3, 4), 0.5, dtype=np.float32),
        "landcover": np.full((3, 4), 0.5, dtype=np.float32),
        "population": np.full((3, 4), 0.5, dtype=np.float32),
    }

    return ModelInputs(
        factor_arrays=factor_arrays,
        susceptibility=susceptibility,
        valid_mask=valid_mask,
        weights={
            "elevation": 0.2,
            "slope": 0.2,
            "distance_to_rivers": 0.2,
            "landcover": 0.2,
            "population": 0.2,
        },
        consistency_ratio=0.0,
        crs=CRS.from_epsg(32737),
        transform=from_origin(100, 200, 10, 10),
        width=4,
        height=3,
        resolution=10.0,
        nodata=-9999.0,
        valid_cell_count=11,
        factor_paths={},
        susceptibility_path=Path("synthetic_susceptibility.tif"),
        metadata={},
        max_reconstruction_error=0.0,
    )


class TestCellSelector(unittest.TestCase):

    def setUp(self):
        self.inputs = create_test_inputs()

    def test_valid_cell_selection(self):
        result = select_raster_cell(self.inputs, 1, 2)

        self.assertEqual(result.row, 1)
        self.assertEqual(result.column, 2)
        self.assertAlmostEqual(result.x, 125.0)
        self.assertAlmostEqual(result.y, 185.0)
        self.assertAlmostEqual(result.susceptibility_score, 0.75)

    def test_negative_row_rejected(self):
        with self.assertRaises(ValueError):
            select_raster_cell(self.inputs, -1, 0)

    def test_negative_column_rejected(self):
        with self.assertRaises(ValueError):
            select_raster_cell(self.inputs, 0, -1)

    def test_row_out_of_bounds_rejected(self):
        with self.assertRaises(ValueError):
            select_raster_cell(self.inputs, 3, 0)

    def test_column_out_of_bounds_rejected(self):
        with self.assertRaises(ValueError):
            select_raster_cell(self.inputs, 0, 4)

    def test_non_integer_row_rejected(self):
        with self.assertRaises(TypeError):
            select_raster_cell(self.inputs, 1.5, 0)

    def test_non_integer_column_rejected(self):
        with self.assertRaises(TypeError):
            select_raster_cell(self.inputs, 0, 2.5)

    def test_boolean_index_rejected(self):
        with self.assertRaises(TypeError):
            select_raster_cell(self.inputs, True, 0)

    def test_invalid_mask_cell_rejected(self):
        with self.assertRaises(ValueError):
            select_raster_cell(self.inputs, 2, 3)


if __name__ == "__main__":
    unittest.main()