
"""Automated tests for the Phase 10.3 interpreter input loader."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.flood_factors.mcda_flood_susceptibility import (
    FACTOR_ORDER,
    calculate_ahp_weights,
)
from src.interpreter import input_loader


NODATA = -9999.0


class TestInputLoader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.factor_paths = {
            factor: self.root / f"{factor}_score.tif"
            for factor in FACTOR_ORDER
        }
        self.output_path = self.root / "flood_susceptibility.tif"

        self.transform = from_origin(
            239612.24, 9871698.95, 30.8655, 30.8655
        )

        self.weights, self.cr, _, _ = calculate_ahp_weights()

        self.weights = {
            factor: float(self.weights[factor])
            for factor in FACTOR_ORDER
        }

        self.factor_array = np.array(
            [
                [0.2, 0.4],
                [0.6, NODATA],
            ],
            dtype=np.float32,
        )

        self.write_valid_dataset()

        self.patches = [
            patch.object(
                input_loader,
                "FACTOR_FILES",
                self.factor_paths,
            ),
            patch.object(
                input_loader,
                "OUTPUT_FILE",
                self.output_path,
            ),
        ]

        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in self.patches:
            item.stop()

        self.temp_dir.cleanup()

    def write_raster(
        self,
        path,
        array,
        transform=None,
        tags=None,
    ):
        profile = {
            "driver": "GTiff",
            "height": array.shape[0],
            "width": array.shape[1],
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:32737",
            "transform": transform or self.transform,
            "nodata": NODATA,
        }

        with rasterio.open(path, "w", **profile) as dataset:
            dataset.write(array.astype(np.float32), 1)

            if tags:
                dataset.update_tags(**tags)

    def write_valid_dataset(self):
        for path in self.factor_paths.values():
            self.write_raster(path, self.factor_array)

        reconstructed = np.zeros((2, 2), dtype=np.float64)

        for factor in FACTOR_ORDER:
            reconstructed += (
                self.factor_array.astype(np.float64)
                * self.weights[factor]
            )

        reconstructed = reconstructed.astype(np.float32)

        tags = {
            "model": "MCDA Flood Susceptibility",
            "weighting_method": "AHP",
            "consistency_ratio": f"{self.cr:.10f}",
        }

        for factor in FACTOR_ORDER:
            tags[f"{factor}_weight"] = (
                f"{self.weights[factor]:.10f}"
            )

        self.write_raster(
            self.output_path,
            reconstructed,
            tags=tags,
        )

    def test_valid_inputs_load_successfully(self):
        """All valid inputs should be accepted."""

        result = input_loader.load_model_inputs()

        self.assertEqual(result.valid_cell_count, 3)
        self.assertEqual(result.width, 2)
        self.assertEqual(result.height, 2)
        self.assertEqual(result.crs.to_epsg(), 32737)
        self.assertEqual(result.max_reconstruction_error, 0.0)

    def test_missing_factor_is_rejected(self):
        """A missing factor file must raise FileNotFoundError."""

        self.factor_paths["slope"].unlink()

        with self.assertRaises(FileNotFoundError):
            input_loader.load_model_inputs()

    def test_grid_mismatch_is_rejected(self):
        """A factor on a different grid must be rejected."""

        different_transform = from_origin(
            239700, 9871698.95, 30.8655, 30.8655
        )

        self.write_raster(
            self.factor_paths["slope"],
            self.factor_array,
            transform=different_transform,
        )

        with self.assertRaisesRegex(ValueError, "not spatially aligned"):
            input_loader.load_model_inputs()

    def test_factor_values_outside_range_are_rejected(self):
        """Factor values outside 0–1 must be rejected."""

        invalid_array = self.factor_array.copy()
        invalid_array[0, 0] = 1.5

        self.write_raster(
            self.factor_paths["elevation"],
            invalid_array,
        )

        with self.assertRaisesRegex(ValueError, "outside the expected 0–1 range"):
            input_loader.load_model_inputs()

    def test_output_mask_mismatch_is_rejected(self):
        """The output mask must match the common factor mask."""

        invalid_output = np.array(
            [
                [0.2, 0.4],
                [0.6, 0.5],
            ],
            dtype=np.float32,
        )

        tags = {
            "model": "MCDA Flood Susceptibility",
            "weighting_method": "AHP",
            "consistency_ratio": f"{self.cr:.10f}",
        }

        for factor in FACTOR_ORDER:
            tags[f"{factor}_weight"] = (
                f"{self.weights[factor]:.10f}"
            )

        self.write_raster(
            self.output_path,
            invalid_output,
            tags=tags,
        )

        with self.assertRaisesRegex(ValueError, "mask"):
            input_loader.load_model_inputs()

    def test_weight_metadata_mismatch_is_rejected(self):
        """Stored weights must agree with calculated AHP weights."""

        tags = {
            "model": "MCDA Flood Susceptibility",
            "weighting_method": "AHP",
            "consistency_ratio": f"{self.cr:.10f}",
        }

        for factor in FACTOR_ORDER:
            tags[f"{factor}_weight"] = (
                f"{self.weights[factor]:.10f}"
            )

        tags["elevation_weight"] = "0.9999999999"

        reconstructed = np.zeros((2, 2), dtype=np.float32)

        for factor in FACTOR_ORDER:
            reconstructed += (
                self.factor_array * self.weights[factor]
            )

        self.write_raster(
            self.output_path,
            reconstructed,
            tags=tags,
        )

        with self.assertRaisesRegex(ValueError, "weight mismatch"):
            input_loader.load_model_inputs()


if __name__ == "__main__":
    unittest.main(verbosity=2)
