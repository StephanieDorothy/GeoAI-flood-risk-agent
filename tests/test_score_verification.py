"""
Tests for Phase 10.7 — Susceptibility Score Reconstruction and Verification.
"""

import unittest
from dataclasses import replace

import numpy as np

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER
from src.interpreter.input_loader import RECONSTRUCTION_TOLERANCE
from src.interpreter.weighted_contributions import (
    FactorContribution,
    WeightedContributions,
)
from src.interpreter.score_verification import (
    ScoreVerification,
    verify_susceptibility_score,
)


class TestScoreVerification(unittest.TestCase):

    def setUp(self):
        self.weights = {
            "elevation": 0.20,
            "slope": 0.20,
            "distance_to_rivers": 0.30,
            "landcover": 0.20,
            "population": 0.10,
        }

        self.factor_scores = {
            "elevation": 0.50,
            "slope": 0.60,
            "distance_to_rivers": 0.80,
            "landcover": 0.40,
            "population": 0.70,
        }

        self.factor_contributions = {
            factor: FactorContribution(
                factor_score=self.factor_scores[factor],
                weight=self.weights[factor],
                weighted_contribution=(
                    self.factor_scores[factor] * self.weights[factor]
                ),
            )
            for factor in FACTOR_ORDER
        }

        self.expected_score = sum(
            self.factor_contributions[factor].weighted_contribution
            for factor in FACTOR_ORDER
        )

        self.valid_contributions = WeightedContributions(
            row=100,
            column=200,
            x=36.8215,
            y=-1.2864,
            crs="EPSG:32737",
            susceptibility_score=self.expected_score,
            factor_contributions=self.factor_contributions.copy(),
        )

    def test_successful_reconstruction(self):
        result = verify_susceptibility_score(
            self.valid_contributions
        )

        self.assertIsInstance(result, ScoreVerification)
        self.assertTrue(result.verification_passed)
        self.assertAlmostEqual(
            result.reconstructed_score,
            self.expected_score,
            places=7,
        )

    def test_stored_score_is_preserved(self):
        result = verify_susceptibility_score(
            self.valid_contributions
        )

        self.assertAlmostEqual(
            result.stored_score,
            self.expected_score,
            places=7,
        )

    def test_selected_cell_metadata_is_preserved(self):
        result = verify_susceptibility_score(
            self.valid_contributions
        )

        self.assertEqual(result.row, 100)
        self.assertEqual(result.column, 200)
        self.assertEqual(result.x, 36.8215)
        self.assertEqual(result.y, -1.2864)
        self.assertEqual(result.crs, "EPSG:32737")

    def test_all_five_contributions_are_included(self):
        result = verify_susceptibility_score(
            self.valid_contributions
        )

        expected_sum = sum(
            self.factor_contributions[factor].weighted_contribution
            for factor in FACTOR_ORDER
        )

        self.assertAlmostEqual(
            result.reconstructed_score,
            float(np.float32(expected_sum)),
            places=7,
        )

        self.assertEqual(
            set(self.valid_contributions.factor_contributions),
            set(FACTOR_ORDER),
        )

    def test_reconstruction_uses_shared_tolerance(self):
        result = verify_susceptibility_score(
            self.valid_contributions
        )

        self.assertEqual(
            result.tolerance,
            RECONSTRUCTION_TOLERANCE,
        )

    def test_difference_within_tolerance_passes(self):
        stored_score = (
            self.expected_score + RECONSTRUCTION_TOLERANCE / 2
        )

        contributions = replace(
            self.valid_contributions,
            susceptibility_score=stored_score,
        )

        result = verify_susceptibility_score(contributions)

        self.assertTrue(result.verification_passed)
        self.assertLessEqual(
            result.absolute_difference,
            RECONSTRUCTION_TOLERANCE,
        )

    def test_difference_beyond_tolerance_fails_without_raising(self):
        stored_score = (
            self.expected_score + RECONSTRUCTION_TOLERANCE * 2
        )

        contributions = replace(
            self.valid_contributions,
            susceptibility_score=stored_score,
        )

        result = verify_susceptibility_score(contributions)

        self.assertFalse(result.verification_passed)
        self.assertGreater(
            result.absolute_difference,
            RECONSTRUCTION_TOLERANCE,
        )

    def test_missing_factor_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()
        factor_contributions.pop("population")

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Missing factor contributions",
        ):
            verify_susceptibility_score(contributions)

    def test_unexpected_factor_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["unexpected_factor"] = (
            FactorContribution(
                factor_score=0.5,
                weight=0.1,
                weighted_contribution=0.05,
            )
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unexpected factor contributions",
        ):
            verify_susceptibility_score(contributions)

    def test_invalid_factor_contribution_type_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()
        factor_contributions["elevation"] = 0.1

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaises(TypeError):
            verify_susceptibility_score(contributions)

    def test_non_finite_factor_score_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["elevation"] = replace(
            factor_contributions["elevation"],
            factor_score=np.nan,
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "factor score is not finite",
        ):
            verify_susceptibility_score(contributions)

    def test_factor_score_outside_range_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["elevation"] = replace(
            factor_contributions["elevation"],
            factor_score=1.5,
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "factor score is outside",
        ):
            verify_susceptibility_score(contributions)

    def test_non_finite_weight_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["slope"] = replace(
            factor_contributions["slope"],
            weight=np.inf,
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "AHP weight is not finite",
        ):
            verify_susceptibility_score(contributions)

    def test_weight_outside_range_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["slope"] = replace(
            factor_contributions["slope"],
            weight=1.2,
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "AHP weight is outside",
        ):
            verify_susceptibility_score(contributions)

    def test_non_finite_weighted_contribution_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["landcover"] = replace(
            factor_contributions["landcover"],
            weighted_contribution=np.nan,
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "weighted contribution is not finite",
        ):
            verify_susceptibility_score(contributions)

    def test_weighted_contribution_outside_range_is_rejected(self):
        factor_contributions = self.factor_contributions.copy()

        factor_contributions["landcover"] = replace(
            factor_contributions["landcover"],
            weighted_contribution=1.5,
        )

        contributions = replace(
            self.valid_contributions,
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "weighted contribution is outside",
        ):
            verify_susceptibility_score(contributions)

    def test_non_finite_stored_score_is_rejected(self):
        contributions = replace(
            self.valid_contributions,
            susceptibility_score=np.nan,
        )

        with self.assertRaisesRegex(
            ValueError,
            "stored susceptibility score is not finite",
        ):
            verify_susceptibility_score(contributions)

    def test_stored_score_outside_range_is_rejected(self):
        contributions = replace(
            self.valid_contributions,
            susceptibility_score=1.5,
        )

        with self.assertRaisesRegex(
            ValueError,
            "stored susceptibility score is outside",
        ):
            verify_susceptibility_score(contributions)

    def test_wrong_top_level_object_type_is_rejected(self):
        with self.assertRaises(TypeError):
            verify_susceptibility_score({"susceptibility_score": 0.5})


if __name__ == "__main__":
    unittest.main()