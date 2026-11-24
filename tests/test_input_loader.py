
"""Automated tests for the Phase 11 interpreter input loader."""

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
        crs="EPSG:32737",
        nodata=NODATA,
        dtype="float32",
        count=1,
    ):
        profile = {
            "driver": "GTiff",
            "height": array.shape[0],
            "width": array.shape[1],
            "count": count,
            "dtype": dtype,
            "crs": crs,
            "transform": transform or self.transform,
        }

        if nodata is not None:
            profile["nodata"] = nodata

        with rasterio.open(path, "w", **profile) as dataset:
            raster_data = array.astype(dtype)

            if count == 1:
                dataset.write(raster_data, 1)
            else:
                multi_band_data = np.stack(
                    [raster_data] * count,
                    axis=0,
                )
                dataset.write(multi_band_data)

            if tags:
                dataset.update_tags(**tags)

    def valid_output_tags(self):
        """Return complete, valid model metadata tags."""

        tags = {
            "model": "MCDA Flood Susceptibility",
            "weighting_method": "AHP",
            "consistency_ratio": f"{self.cr:.10f}",
        }

        for factor in FACTOR_ORDER:
            tags[f"{factor}_weight"] = (
                f"{self.weights[factor]:.10f}"
            )

        return tags

    def reconstructed_array(self):
        """Reconstruct the output using the synthetic factor rasters."""

        reconstructed = np.zeros((2, 2), dtype=np.float64)

        for factor in FACTOR_ORDER:
            reconstructed += (
                self.factor_array.astype(np.float64)
                * self.weights[factor]
            )

        return reconstructed.astype(np.float32)

    def write_valid_dataset(self):
        """Create a complete synthetic dataset accepted by the loader."""

        for path in self.factor_paths.values():
            self.write_raster(path, self.factor_array)

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=self.valid_output_tags(),
        )

    # ---------------------------------------------------------
    # EXISTING BASELINE TESTS
    # ---------------------------------------------------------

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

    def test_missing_susceptibility_output_is_rejected(self):
        """A missing susceptibility output must raise FileNotFoundError."""

        self.output_path.unlink()

        with self.assertRaises(FileNotFoundError):
            input_loader.load_model_inputs()

    def test_unreadable_raster_is_rejected(self):
        """An existing but unreadable raster must raise a clear ValueError."""

        self.factor_paths["slope"].write_bytes(
            b"This is not a valid GeoTIFF file."
        )

        with self.assertRaisesRegex(
            ValueError,
            "Could not read slope factor raster",
        ):
            input_loader.load_model_inputs()

    def test_raster_without_crs_is_rejected(self):
        """A raster without a defined CRS must be rejected."""

        self.write_raster(
            self.factor_paths["elevation"],
            self.factor_array,
            crs=None,
        )

        with self.assertRaisesRegex(
            ValueError,
            "has no defined CRS",
        ):
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

        with self.assertRaisesRegex(
            ValueError,
            "not spatially aligned",
        ):
            input_loader.load_model_inputs()

    def test_factor_values_outside_range_are_rejected(self):
        """Factor values outside 0-1 must be rejected."""

        invalid_array = self.factor_array.copy()
        invalid_array[0, 0] = 1.5

        self.write_raster(
            self.factor_paths["elevation"],
            invalid_array,
        )

        with self.assertRaisesRegex(
            ValueError,
            "outside the expected",
        ):
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

        self.write_raster(
            self.output_path,
            invalid_output,
            tags=self.valid_output_tags(),
        )

        with self.assertRaisesRegex(ValueError, "mask"):
            input_loader.load_model_inputs()

    def test_weight_metadata_mismatch_is_rejected(self):
        """Stored weights must agree with calculated AHP weights."""

        tags = self.valid_output_tags()
        tags["elevation_weight"] = "0.9999999999"

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "weight mismatch",
        ):
            input_loader.load_model_inputs()

    # ---------------------------------------------------------
    # RASTER-STRUCTURE FAILURE TESTS
    # ---------------------------------------------------------

    def test_raster_without_nodata_is_rejected(self):
        """A raster without a NoData value must be rejected."""

        self.write_raster(
            self.factor_paths["elevation"],
            self.factor_array,
            nodata=None,
        )

        with self.assertRaisesRegex(ValueError, "NoData"):
            input_loader.load_model_inputs()

    def test_raster_with_incorrect_nodata_is_rejected(self):
        """A raster using an unexpected NoData value must be rejected."""

        self.write_raster(
            self.factor_paths["elevation"],
            self.factor_array,
            nodata=-9998.0,
        )

        with self.assertRaisesRegex(ValueError, "NoData"):
            input_loader.load_model_inputs()

    def test_multiband_raster_is_rejected(self):
        """A raster with multiple bands must be rejected."""

        self.write_raster(
            self.factor_paths["elevation"],
            self.factor_array,
            count=2,
        )

        with self.assertRaisesRegex(ValueError, "exactly one band"):
            input_loader.load_model_inputs()

    def test_non_float32_raster_is_rejected(self):
        """A raster not stored as float32 must be rejected."""

        self.write_raster(
            self.factor_paths["elevation"],
            self.factor_array,
            dtype="float64",
        )

        with self.assertRaisesRegex(ValueError, "float32"):
            input_loader.load_model_inputs()

    # ---------------------------------------------------------
    # COMMON VALID-DATA MASK FAILURE TESTS
    # ---------------------------------------------------------

    def test_no_common_valid_cells_are_rejected(self):
        """Factor rasters with no overlapping valid cells must be rejected."""

        empty_array = np.full(
            (2, 2),
            NODATA,
            dtype=np.float32,
        )

        for path in self.factor_paths.values():
            self.write_raster(path, empty_array)

        with self.assertRaisesRegex(
            ValueError,
            "no common valid cells",
        ):
            input_loader.load_model_inputs()

    def test_factor_with_empty_valid_selection_is_rejected(self):
        """Factor validation must reject an empty valid-cell selection."""

        valid_mask = np.zeros(
            self.factor_array.shape,
            dtype=bool,
        )

        with self.assertRaisesRegex(
            ValueError,
            "elevation contains no valid cells",
        ):
            input_loader._validate_factor_values(
                "elevation",
                self.factor_array,
                valid_mask,
            )

    def test_factor_with_nonfinite_valid_values_is_rejected(self):
        """Factor validation must reject non-finite selected values."""

        invalid_array = self.factor_array.copy()
        invalid_array[0, 0] = np.nan

        valid_mask = np.zeros(
            invalid_array.shape,
            dtype=bool,
        )
        valid_mask[0, 0] = True

        with self.assertRaisesRegex(
            ValueError,
            "non-finite valid values",
        ):
            input_loader._validate_factor_values(
                "elevation",
                invalid_array,
                valid_mask,
            )

    # ---------------------------------------------------------
    # SUSCEPTIBILITY OUTPUT VALIDATION TESTS
    # ---------------------------------------------------------

    def test_output_values_outside_range_are_rejected(self):
        """Stored susceptibility values outside 0-1 must be rejected."""

        invalid_output = self.reconstructed_array()
        invalid_output[0, 0] = 1.5

        self.write_raster(
            self.output_path,
            invalid_output,
            tags=self.valid_output_tags(),
        )

        # ASCII-only assertion avoids Windows source-encoding problems.
        with self.assertRaisesRegex(
            ValueError,
            "outside",
        ):
            input_loader.load_model_inputs()

    def test_reconstruction_mismatch_is_rejected(self):
        """Stored output must agree with the weighted factor reconstruction."""

        invalid_output = self.reconstructed_array()
        invalid_output[0, 0] += 0.1

        self.write_raster(
            self.output_path,
            invalid_output,
            tags=self.valid_output_tags(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "does not match",
        ):
            input_loader.load_model_inputs()

    # ---------------------------------------------------------
    # MODEL METADATA VALIDATION TESTS
    # ---------------------------------------------------------

    def test_missing_model_metadata_is_rejected(self):
        """The susceptibility raster must identify its model."""

        tags = self.valid_output_tags()
        tags.pop("model")

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "model identifier",
        ):
            input_loader.load_model_inputs()

    def test_incorrect_model_metadata_is_rejected(self):
        """An unexpected model identifier must be rejected."""

        tags = self.valid_output_tags()
        tags["model"] = "Different Model"

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "model identifier",
        ):
            input_loader.load_model_inputs()

    def test_incorrect_weighting_method_is_rejected(self):
        """The stored weighting method must identify AHP."""

        tags = self.valid_output_tags()
        tags["weighting_method"] = "Equal Weighting"

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "weighting method",
        ):
            input_loader.load_model_inputs()

    # ---------------------------------------------------------
    # AHP WEIGHT METADATA VALIDATION TESTS
    # ---------------------------------------------------------

    def test_missing_weight_metadata_is_rejected(self):
        """Every factor must have a stored AHP weight."""

        tags = self.valid_output_tags()
        tags.pop("elevation_weight")

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "elevation_weight",
        ):
            input_loader.load_model_inputs()

    def test_malformed_weight_metadata_is_rejected(self):
        """A non-numeric stored weight must be rejected."""

        tags = self.valid_output_tags()
        tags["elevation_weight"] = "not-a-number"

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid stored weight",
        ):
            input_loader.load_model_inputs()

    # ---------------------------------------------------------
    # CALCULATED AHP WEIGHT VALIDATION TESTS
    # ---------------------------------------------------------

    def test_nonfinite_calculated_weight_is_rejected(self):
        """Calculated AHP weights must all be finite."""

        invalid_weights = self.weights.copy()
        invalid_weights["elevation"] = np.nan

        with patch.object(
            input_loader,
            "calculate_ahp_weights",
            return_value=(invalid_weights, self.cr, None, None),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "non-finite values",
            ):
                input_loader._load_and_validate_weights(
                    self.valid_output_tags()
                )

    def test_negative_calculated_weight_is_rejected(self):
        """Calculated AHP weights cannot be negative."""

        invalid_weights = self.weights.copy()
        invalid_weights["elevation"] = -0.1

        with patch.object(
            input_loader,
            "calculate_ahp_weights",
            return_value=(invalid_weights, self.cr, None, None),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "cannot be negative",
            ):
                input_loader._load_and_validate_weights(
                    self.valid_output_tags()
                )

    def test_calculated_weights_not_summing_to_one_are_rejected(self):
        """Calculated AHP weights must sum to one."""

        invalid_weights = {
            factor: 0.1
            for factor in FACTOR_ORDER
        }

        with patch.object(
            input_loader,
            "calculate_ahp_weights",
            return_value=(invalid_weights, self.cr, None, None),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "do not sum to 1",
            ):
                input_loader._load_and_validate_weights(
                    self.valid_output_tags()
                )

    # ---------------------------------------------------------
    # CALCULATED AHP CONSISTENCY-RATIO VALIDATION TESTS
    # ---------------------------------------------------------

    def test_nonfinite_calculated_consistency_ratio_is_rejected(self):
        """The calculated AHP consistency ratio must be finite."""

        with patch.object(
            input_loader,
            "calculate_ahp_weights",
            return_value=(self.weights, np.nan, None, None),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "consistency ratio is not finite",
            ):
                input_loader._load_and_validate_weights(
                    self.valid_output_tags()
                )

    def test_calculated_consistency_ratio_above_threshold_is_rejected(self):
        """The calculated AHP consistency ratio must meet the threshold."""

        invalid_cr = input_loader.CR_THRESHOLD + 0.01

        with patch.object(
            input_loader,
            "calculate_ahp_weights",
            return_value=(self.weights, invalid_cr, None, None),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "exceeds the accepted threshold",
            ):
                input_loader._load_and_validate_weights(
                    self.valid_output_tags()
                )

    # ---------------------------------------------------------
    # AHP CONSISTENCY-RATIO METADATA VALIDATION TESTS
    # ---------------------------------------------------------

    def test_missing_consistency_ratio_metadata_is_rejected(self):
        """The output must store its AHP consistency ratio."""

        tags = self.valid_output_tags()
        tags.pop("consistency_ratio")

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "consistency_ratio",
        ):
            input_loader.load_model_inputs()

    def test_malformed_consistency_ratio_metadata_is_rejected(self):
        """A non-numeric stored consistency ratio must be rejected."""

        tags = self.valid_output_tags()
        tags["consistency_ratio"] = "not-a-number"

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid stored AHP consistency ratio",
        ):
            input_loader.load_model_inputs()

    def test_consistency_ratio_mismatch_is_rejected(self):
        """Stored and calculated AHP consistency ratios must agree."""

        tags = self.valid_output_tags()
        tags["consistency_ratio"] = f"{self.cr + 0.1:.10f}"

        self.write_raster(
            self.output_path,
            self.reconstructed_array(),
            tags=tags,
        )

        with self.assertRaisesRegex(
            ValueError,
            "consistency ratio mismatch",
        ):
            input_loader.load_model_inputs()


if __name__ == "__main__":
    unittest.main(verbosity=2)
