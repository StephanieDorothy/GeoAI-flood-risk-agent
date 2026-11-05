
"""Tests for Phase 10.5 — Factor Evidence Extraction."""

import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
from rasterio.crs import CRS
from rasterio.transform import from_origin

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER
from src.interpreter.cell_selector import select_raster_cell
from src.interpreter.factor_evidence import extract_factor_evidence
from src.interpreter.input_loader import ModelInputs


class TestFactorEvidence(unittest.TestCase):

    def setUp(self):
        self.height = 3
        self.width = 4

        factor_values = {
            "elevation": 0.40,
            "slope": 0.50,
            "distance_to_rivers": 0.60,
            "landcover": 0.70,
            "population": 0.80,
        }

        self.factor_arrays = {
            name: np.full(
                (self.height, self.width),
                value,
                dtype=np.float32,
            )
            for name, value in factor_values.items()
        }

        self.susceptibility = np.full(
            (self.height, self.width),
            0.75,
            dtype=np.float32,
        )

        self.valid_mask = np.ones(
            (self.height, self.width),
            dtype=bool,
        )

        self.valid_mask[2, 3] = False
        self.susceptibility[2, 3] = -9999.0

        self.inputs = ModelInputs(
            factor_arrays=self.factor_arrays,
            susceptibility=self.susceptibility,
            valid_mask=self.valid_mask,
            weights={
                "elevation": 0.1868744589,
                "slope": 0.1868744589,
                "distance_to_rivers": 0.4352900433,
                "landcover": 0.1285887446,
                "population": 0.0623722944,
            },
            consistency_ratio=0.02694751171524496,
            crs=CRS.from_epsg(32737),
            transform=from_origin(100, 200, 10, 10),
            width=self.width,
            height=self.height,
            resolution=(10.0, 10.0),
            nodata=-9999.0,
            valid_cell_count=11,
            factor_paths={
                name: Path(f"{name}.tif")
                for name in FACTOR_ORDER
            },
            susceptibility_path=Path("susceptibility.tif"),
            metadata={},
            max_reconstruction_error=0.0,
        )

        self.selection = select_raster_cell(
            self.inputs,
            row=1,
            column=2,
        )

    def test_valid_factor_evidence_extraction(self):
        evidence = extract_factor_evidence(
            self.inputs,
            self.selection,
        )

        self.assertIsNotNone(evidence)

        self.assertAlmostEqual(
            evidence.factor_scores["elevation"],
            0.40,
            places=6,
        )

        self.assertAlmostEqual(
            evidence.factor_scores["slope"],
            0.50,
            places=6,
        )

        self.assertAlmostEqual(
            evidence.factor_scores["distance_to_rivers"],
            0.60,
            places=6,
        )

        self.assertAlmostEqual(
            evidence.factor_scores["landcover"],
            0.70,
            places=6,
        )

        self.assertAlmostEqual(
            evidence.factor_scores["population"],
            0.80,
            places=6,
        )

        self.assertAlmostEqual(
            evidence.susceptibility_score,
            0.75,
            places=6,
        )

    def test_all_five_factors_are_returned(self):
        evidence = extract_factor_evidence(
            self.inputs,
            self.selection,
        )

        self.assertEqual(
            set(evidence.factor_scores.keys()),
            set(FACTOR_ORDER),
        )

    def test_location_information_is_preserved(self):
        evidence = extract_factor_evidence(
            self.inputs,
            self.selection,
        )

        self.assertEqual(evidence.row, self.selection.row)
        self.assertEqual(evidence.column, self.selection.column)
        self.assertEqual(evidence.x, self.selection.x)
        self.assertEqual(evidence.y, self.selection.y)
        self.assertEqual(evidence.crs, self.selection.crs)

    def test_missing_factor_rejected(self):
        incomplete_inputs = replace(
            self.inputs,
            factor_arrays={
                key: value
                for key, value in self.factor_arrays.items()
                if key != "population"
            },
        )

        with self.assertRaisesRegex(ValueError, "population"):
            extract_factor_evidence(
                incomplete_inputs,
                self.selection,
            )

    def test_incompatible_factor_shape_rejected(self):
        incorrect_arrays = self.factor_arrays.copy()

        incorrect_arrays["slope"] = np.ones(
            (2, 2),
            dtype=np.float32,
        )

        incorrect_inputs = replace(
            self.inputs,
            factor_arrays=incorrect_arrays,
        )

        with self.assertRaises(ValueError):
            extract_factor_evidence(
                incorrect_inputs,
                self.selection,
            )

    def test_non_finite_factor_score_rejected(self):
        self.factor_arrays["elevation"][1, 2] = np.nan

        with self.assertRaisesRegex(ValueError, "finite"):
            extract_factor_evidence(
                self.inputs,
                self.selection,
            )

    def test_factor_score_above_one_rejected(self):
        self.factor_arrays["elevation"][1, 2] = 1.2

        with self.assertRaisesRegex(ValueError, "range"):
            extract_factor_evidence(
                self.inputs,
                self.selection,
            )

    def test_negative_factor_score_rejected(self):
        self.factor_arrays["elevation"][1, 2] = -0.1

        with self.assertRaisesRegex(ValueError, "range"):
            extract_factor_evidence(
                self.inputs,
                self.selection,
            )

    def test_invalid_mask_cell_rejected(self):
        invalid_selection = replace(
            self.selection,
            row=2,
            column=3,
            susceptibility_score=-9999.0,
        )

        with self.assertRaisesRegex(ValueError, "valid"):
            extract_factor_evidence(
                self.inputs,
                invalid_selection,
            )

    def test_non_finite_susceptibility_rejected(self):
        self.inputs.susceptibility[1, 2] = np.nan

        with self.assertRaisesRegex(ValueError, "not finite"):
            extract_factor_evidence(
                self.inputs,
                self.selection,
            )

    def test_susceptibility_selection_mismatch_rejected(self):
        mismatched_selection = replace(
            self.selection,
            susceptibility_score=0.60,
        )

        with self.assertRaisesRegex(ValueError, "does not match"):
            extract_factor_evidence(
                self.inputs,
                mismatched_selection,
            )

    def test_input_object_type_rejected(self):
        with self.assertRaises(TypeError):
            extract_factor_evidence(
                object(),
                self.selection,
            )

    def test_selection_object_type_rejected(self):
        with self.assertRaises(TypeError):
            extract_factor_evidence(
                self.inputs,
                object(),
            )


if __name__ == "__main__":
    unittest.main()
