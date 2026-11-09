"""Tests for deterministic Phase 10.8 explanation generation."""

import unittest

import numpy as np

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER

from src.interpreter.weighted_contributions import (
    FactorContribution,
    WeightedContributions,
)

from src.interpreter.score_verification import (
    ScoreVerification,
)

from src.interpreter.explanation_generator import (
    generate_deterministic_explanation,
)


class TestExplanationGenerator(unittest.TestCase):

    def setUp(self):
        """Create consistent evidence for one raster cell."""

        self.weights = {
            "elevation": 0.1868744589,
            "slope": 0.1868744589,
            "distance_to_rivers": 0.4352900433,
            "landcover": 0.1285887446,
            "population": 0.0623722944,
        }

        self.factor_scores = {
            factor: 0.8
            for factor in FACTOR_ORDER
        }

        self.row = 100
        self.column = 200
        self.x = 36.821
        self.y = -1.286
        self.crs = "EPSG:32737"

        self.contributions = self._build_contributions(
            self.factor_scores,
            stored_score=None,
        )

        self.verification = self._build_verification(
            reconstructed_score=self._reconstructed_score(),
            stored_score=self._reconstructed_score(),
            tolerance=1e-5,
            verification_passed=True,
        )

    def _reconstructed_score(self):
        """Reconstruct the weighted score using Phase 10.7 precision."""

        total = sum(
            self.factor_scores[factor] * self.weights[factor]
            for factor in FACTOR_ORDER
        )

        return float(np.float32(total))

    def _build_contributions(
        self,
        factor_scores,
        stored_score,
    ):
        """Build a WeightedContributions object."""

        factor_contributions = {}

        for factor in FACTOR_ORDER:
            score = factor_scores[factor]
            weight = self.weights[factor]

            factor_contributions[factor] = FactorContribution(
                factor_score=score,
                weight=weight,
                weighted_contribution=score * weight,
            )

        if stored_score is None:
            stored_score = self._reconstructed_score()

        return WeightedContributions(
            row=self.row,
            column=self.column,
            x=self.x,
            y=self.y,
            crs=self.crs,
            susceptibility_score=stored_score,
            factor_contributions=factor_contributions,
        )

    def _build_verification(
        self,
        reconstructed_score,
        stored_score,
        tolerance,
        verification_passed,
    ):
        """Build a ScoreVerification object."""

        return ScoreVerification(
            row=self.row,
            column=self.column,
            x=self.x,
            y=self.y,
            crs=self.crs,
            reconstructed_score=reconstructed_score,
            stored_score=stored_score,
            absolute_difference=abs(
                reconstructed_score - stored_score
            ),
            tolerance=tolerance,
            verification_passed=verification_passed,
        )

    def _generate(self):
        """Generate an explanation using the default valid evidence."""

        return generate_deterministic_explanation(
            self.contributions,
            self.verification,
        )

    # -------------------------------------------------------------
    # Successful explanation tests
    # -------------------------------------------------------------

    def test_generates_structured_explanation(self):
        result = self._generate()

        expected_keys = {
            "location",
            "susceptibility",
            "factor_evidence",
            "contribution_ranking",
            "interpretation",
            "limitations",
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_returns_correct_cell_location(self):
        result = self._generate()

        self.assertEqual(result["location"]["row"], self.row)
        self.assertEqual(result["location"]["column"], self.column)
        self.assertEqual(result["location"]["x"], self.x)
        self.assertEqual(result["location"]["y"], self.y)
        self.assertEqual(result["location"]["crs"], self.crs)

    def test_returns_stored_and_reconstructed_scores(self):
        result = self._generate()

        susceptibility = result["susceptibility"]

        self.assertAlmostEqual(
            susceptibility["stored_score"],
            self._reconstructed_score(),
        )

        self.assertAlmostEqual(
            susceptibility["reconstructed_score"],
            self._reconstructed_score(),
        )

    def test_successful_verification_is_reported_as_pass(self):
        result = self._generate()

        self.assertTrue(
            result["susceptibility"]["verification_passed"]
        )

        self.assertEqual(
            result["susceptibility"]["verification_status"],
            "PASS",
        )

    def test_all_five_factor_evidence_items_are_returned(self):
        result = self._generate()

        self.assertEqual(
            set(result["factor_evidence"]),
            set(FACTOR_ORDER),
        )

        self.assertEqual(
            len(result["factor_evidence"]),
            5,
        )

    def test_factor_evidence_contains_score_weight_and_contribution(self):
        result = self._generate()

        for factor in FACTOR_ORDER:
            evidence = result["factor_evidence"][factor]

            self.assertIn("factor_score", evidence)
            self.assertIn("ahp_weight", evidence)
            self.assertIn("weighted_contribution", evidence)
            self.assertIn("interpretation", evidence)

    def test_contribution_ranking_is_descending(self):
        result = self._generate()

        ranking = result["contribution_ranking"]

        values = [
            item["weighted_contribution"]
            for item in ranking
        ]

        self.assertEqual(
            values,
            sorted(values, reverse=True),
        )

    def test_contribution_ranking_contains_all_five_factors(self):
        result = self._generate()

        ranking = result["contribution_ranking"]

        self.assertEqual(len(ranking), 5)

        ranked_factors = {
            item["factor"]
            for item in ranking
        }

        self.assertEqual(
            ranked_factors,
            set(FACTOR_ORDER),
        )

    def test_equal_contributions_use_factor_order_as_tiebreaker(self):
        # Elevation and slope have equal AHP weights.
        # Equal scores therefore produce equal contributions.
        result = self._generate()

        ranking = result["contribution_ranking"]

        ranked_factors = [
            item["factor"]
            for item in ranking
        ]

        self.assertLess(
            ranked_factors.index("elevation"),
            ranked_factors.index("slope"),
        )

    def test_population_is_identified_as_exposure_related(self):
        result = self._generate()

        population = result["factor_evidence"]["population"]

        self.assertIn(
            "exposure",
            population["interpretation"].lower(),
        )

        population_ranking = next(
            item
            for item in result["contribution_ranking"]
            if item["factor"] == "population"
        )

        self.assertEqual(
            population_ranking["factor_type"],
            "exposure-related",
        )

    def test_physical_factors_are_distinguished_from_population(self):
        result = self._generate()

        ranking = result["contribution_ranking"]

        for item in ranking:
            if item["factor"] == "population":
                self.assertEqual(
                    item["factor_type"],
                    "exposure-related",
                )
            else:
                self.assertEqual(
                    item["factor_type"],
                    "physical-susceptibility indicator",
                )

    def test_landcover_category_is_not_inferred(self):
        result = self._generate()

        landcover = result["factor_evidence"]["landcover"]

        self.assertIn(
            "original land-cover category is not retained",
            landcover["interpretation"],
        )

    def test_limitations_are_included(self):
        result = self._generate()

        limitations = result["limitations"]

        self.assertIsInstance(limitations, list)
        self.assertGreaterEqual(len(limitations), 5)

        combined = " ".join(limitations).lower()

        self.assertIn("probability", combined)
        self.assertIn("predictive accuracy", combined)
        self.assertIn("unosat", combined)

    def test_explanation_generation_is_deterministic(self):
        first_result = self._generate()
        second_result = self._generate()

        self.assertEqual(first_result, second_result)

    # -------------------------------------------------------------
    # Failed verification tests
    # -------------------------------------------------------------

    def test_failed_verification_withholds_contribution_ranking(self):
        reconstructed_score = self._reconstructed_score()
        stored_score = 0.7

        contributions = self._build_contributions(
            self.factor_scores,
            stored_score=stored_score,
        )

        verification = self._build_verification(
            reconstructed_score=reconstructed_score,
            stored_score=stored_score,
            tolerance=1e-5,
            verification_passed=False,
        )

        result = generate_deterministic_explanation(
            contributions,
            verification,
        )

        self.assertFalse(
            result["susceptibility"]["verification_passed"]
        )

        self.assertEqual(
            result["susceptibility"]["verification_status"],
            "FAIL",
        )

        self.assertIsNone(
            result["contribution_ranking"]
        )

        self.assertIsNone(
            result["interpretation"]["dominant_factor"]
        )

        self.assertIn(
            "withheld",
            result["interpretation"]["overall"].lower(),
        )

    # -------------------------------------------------------------
    # Input validation tests
    # -------------------------------------------------------------

    def test_rejects_incorrect_contribution_reconstruction(self):
        incorrect_verification = self._build_verification(
            reconstructed_score=0.9,
            stored_score=0.9,
            tolerance=1e-5,
            verification_passed=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "sum of weighted factor contributions",
        ):
            generate_deterministic_explanation(
                self.contributions,
                incorrect_verification,
            )

    def test_rejects_factor_contribution_not_equal_to_score_times_weight(self):
        factor_contributions = dict(
            self.contributions.factor_contributions
        )

        original = factor_contributions["elevation"]

        factor_contributions["elevation"] = FactorContribution(
            factor_score=original.factor_score,
            weight=original.weight,
            weighted_contribution=original.weighted_contribution + 0.01,
        )

        invalid_contributions = WeightedContributions(
            row=self.row,
            column=self.column,
            x=self.x,
            y=self.y,
            crs=self.crs,
            susceptibility_score=self._reconstructed_score(),
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "does not match",
        ):
            generate_deterministic_explanation(
                invalid_contributions,
                self.verification,
            )

    def test_rejects_incomplete_factor_set(self):
        factor_contributions = dict(
            self.contributions.factor_contributions
        )

        factor_contributions.pop("population")

        invalid_contributions = WeightedContributions(
            row=self.row,
            column=self.column,
            x=self.x,
            y=self.y,
            crs=self.crs,
            susceptibility_score=self._reconstructed_score(),
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "exactly the five model factors",
        ):
            generate_deterministic_explanation(
                invalid_contributions,
                self.verification,
            )

    def test_rejects_weights_that_do_not_sum_to_one(self):
        factor_contributions = dict(
            self.contributions.factor_contributions
        )

        original = factor_contributions["elevation"]

        factor_contributions["elevation"] = FactorContribution(
            factor_score=original.factor_score,
            weight=original.weight + 0.05,
            weighted_contribution=(
                original.factor_score * (original.weight + 0.05)
            ),
        )

        invalid_contributions = WeightedContributions(
            row=self.row,
            column=self.column,
            x=self.x,
            y=self.y,
            crs=self.crs,
            susceptibility_score=self._reconstructed_score(),
            factor_contributions=factor_contributions,
        )

        with self.assertRaisesRegex(
            ValueError,
            "weights must sum to 1.0",
        ):
            generate_deterministic_explanation(
                invalid_contributions,
                self.verification,
            )

    def test_rejects_mismatched_cell_rows(self):
        incorrect_verification = self._build_verification(
            reconstructed_score=self._reconstructed_score(),
            stored_score=self._reconstructed_score(),
            tolerance=1e-5,
            verification_passed=True,
        )

        incorrect_verification = ScoreVerification(
            row=self.row + 1,
            column=self.column,
            x=self.x,
            y=self.y,
            crs=self.crs,
            reconstructed_score=incorrect_verification.reconstructed_score,
            stored_score=incorrect_verification.stored_score,
            absolute_difference=incorrect_verification.absolute_difference,
            tolerance=incorrect_verification.tolerance,
            verification_passed=incorrect_verification.verification_passed,
        )

        with self.assertRaisesRegex(
            ValueError,
            "row mismatch",
        ):
            generate_deterministic_explanation(
                self.contributions,
                incorrect_verification,
            )

    def test_rejects_inconsistent_verification_status(self):
        incorrect_verification = self._build_verification(
            reconstructed_score=self._reconstructed_score(),
            stored_score=self._reconstructed_score(),
            tolerance=1e-5,
            verification_passed=False,
        )

        with self.assertRaisesRegex(
            ValueError,
            "status is inconsistent",
        ):
            generate_deterministic_explanation(
                self.contributions,
                incorrect_verification,
            )

    def test_rejects_wrong_contributions_object_type(self):
        with self.assertRaises(TypeError):
            generate_deterministic_explanation(
                {},
                self.verification,
            )

    def test_rejects_wrong_verification_object_type(self):
        with self.assertRaises(TypeError):
            generate_deterministic_explanation(
                self.contributions,
                {},
            )


if __name__ == "__main__":
    unittest.main()