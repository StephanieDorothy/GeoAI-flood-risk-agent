
"""Tests for Phase 10.6 — Weighted Factor Contributions."""

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
from src.interpreter.weighted_contributions import (
    calculate_weighted_contributions,
)


class TestWeightedContributions(unittest.TestCase):

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

        self.weights = {
            "elevation": 0.1868744589,
            "slope": 0.1868744589,
            "distance_to_rivers": 0.4352900433,
            "landcover": 0.1285887446,
            "population": 0.0623722944,
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
            weights=self.weights.copy(),
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

        self.evidence = extract_factor_evidence(
            self.inputs,
            self.selection,
        )

    def test_valid_weighted_contributions(self):
        result = calculate_weighted_contributions(
            self.inputs,
            self.evidence,
        )

        for factor in FACTOR_ORDER:
            expected = (
                self.evidence.factor_scores[factor]
                * self.inputs.weights[factor]
            )

            actual = result.factor_contributions[
                factor
            ].weighted_contribution

            self.assertAlmostEqual(
                actual,
                expected,
                places=12,
            )

    def test_all_five_factors_are_returned(self):
        result = calculate_weighted_contributions(
            self.inputs,
            self.evidence,
        )

        self.assertEqual(
            set(result.factor_contributions.keys()),
            set(FACTOR_ORDER),
        )

    def test_factor_scores_and_weights_are_preserved(self):
        result = calculate_weighted_contributions(
            self.inputs,
            self.evidence,
        )

        for factor in FACTOR_ORDER:
            item = result.factor_contributions[factor]

            self.assertAlmostEqual(
                item.factor_score,
                self.evidence.factor_scores[factor],
                places=12,
            )

            self.assertAlmostEqual(
                item.weight,
                self.inputs.weights[factor],
                places=12,
            )

    def test_authoritative_model_weights_are_used(self):
        result = calculate_weighted_contributions(
            self.inputs,
            self.evidence,
        )

        expected = (
            self.evidence.factor_scores["elevation"]
            * self.inputs.weights["elevation"]
        )

        self.assertAlmostEqual(
            result.factor_contributions[
                "elevation"
            ].weighted_contribution,
            expected,
            places=12,
        )

    def test_cell_information_is_preserved(self):
        result = calculate_weighted_contributions(
            self.inputs,
            self.evidence,
        )

        self.assertEqual(result.row, self.evidence.row)
        self.assertEqual(result.column, self.evidence.column)
        self.assertEqual(result.x, self.evidence.x)
        self.assertEqual(result.y, self.evidence.y)
        self.assertEqual(result.crs, self.evidence.crs)
        self.assertEqual(
            result.susceptibility_score,
            self.evidence.susceptibility_score,
        )

    def test_missing_factor_score_rejected(self):
        incomplete_evidence = replace(
            self.evidence,
            factor_scores={
                key: value
                for key, value in self.evidence.factor_scores.items()
                if key != "population"
            },
        )

        with self.assertRaisesRegex(ValueError, "population"):
            calculate_weighted_contributions(
                self.inputs,
                incomplete_evidence,
            )

    def test_unexpected_factor_score_rejected(self):
        incorrect_scores = self.evidence.factor_scores.copy()
        incorrect_scores["unexpected_factor"] = 0.5

        incorrect_evidence = replace(
            self.evidence,
            factor_scores=incorrect_scores,
        )

        with self.assertRaisesRegex(ValueError, "unexpected_factor"):
            calculate_weighted_contributions(
                self.inputs,
                incorrect_evidence,
            )

    def test_missing_weight_rejected(self):
        incomplete_inputs = replace(
            self.inputs,
            weights={
                key: value
                for key, value in self.weights.items()
                if key != "population"
            },
        )

        with self.assertRaisesRegex(ValueError, "population"):
            calculate_weighted_contributions(
                incomplete_inputs,
                self.evidence,
            )

    def test_unexpected_weight_rejected(self):
        incorrect_weights = self.weights.copy()
        incorrect_weights["unexpected_factor"] = 0.1

        incorrect_inputs = replace(
            self.inputs,
            weights=incorrect_weights,
        )

        with self.assertRaisesRegex(ValueError, "unexpected_factor"):
            calculate_weighted_contributions(
                incorrect_inputs,
                self.evidence,
            )

    def test_non_finite_weight_rejected(self):
        incorrect_weights = self.weights.copy()
        incorrect_weights["elevation"] = np.nan

        incorrect_inputs = replace(
            self.inputs,
            weights=incorrect_weights,
        )

        with self.assertRaisesRegex(ValueError, "not finite"):
            calculate_weighted_contributions(
                incorrect_inputs,
                self.evidence,
            )

    def test_negative_weight_rejected(self):
        incorrect_weights = self.weights.copy()
        incorrect_weights["elevation"] = -0.1

        incorrect_inputs = replace(
            self.inputs,
            weights=incorrect_weights,
        )

        with self.assertRaisesRegex(ValueError, "outside"):
            calculate_weighted_contributions(
                incorrect_inputs,
                self.evidence,
            )

    def test_weight_above_one_rejected(self):
        incorrect_weights = self.weights.copy()
        incorrect_weights["elevation"] = 1.2

        incorrect_inputs = replace(
            self.inputs,
            weights=incorrect_weights,
        )

        with self.assertRaisesRegex(ValueError, "outside"):
            calculate_weighted_contributions(
                incorrect_inputs,
                self.evidence,
            )

    def test_weights_not_summing_to_one_rejected(self):
        incorrect_weights = self.weights.copy()
        incorrect_weights["elevation"] += 0.05

        incorrect_inputs = replace(
            self.inputs,
            weights=incorrect_weights,
        )

        with self.assertRaisesRegex(ValueError, "sum"):
            calculate_weighted_contributions(
                incorrect_inputs,
                self.evidence,
            )

    def test_factor_score_outside_range_rejected(self):
        incorrect_scores = self.evidence.factor_scores.copy()
        incorrect_scores["slope"] = 1.5

        incorrect_evidence = replace(
            self.evidence,
            factor_scores=incorrect_scores,
        )

        with self.assertRaisesRegex(ValueError, "outside"):
            calculate_weighted_contributions(
                self.inputs,
                incorrect_evidence,
            )

    def test_non_finite_factor_score_rejected(self):
        incorrect_scores = self.evidence.factor_scores.copy()
        incorrect_scores["slope"] = np.nan

        incorrect_evidence = replace(
            self.evidence,
            factor_scores=incorrect_scores,
        )

        with self.assertRaisesRegex(ValueError, "not finite"):
            calculate_weighted_contributions(
                self.inputs,
                incorrect_evidence,
            )

    def test_invalid_model_inputs_type_rejected(self):
        with self.assertRaises(TypeError):
            calculate_weighted_contributions(
                object(),
                self.evidence,
            )

    def test_invalid_evidence_type_rejected(self):
        with self.assertRaises(TypeError):
            calculate_weighted_contributions(
                self.inputs,
                object(),
            )


if __name__ == "__main__":
    unittest.main()
