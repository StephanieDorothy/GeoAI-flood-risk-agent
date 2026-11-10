
"""End-to-end integration tests for the Phase 10 interpreter."""

import unittest
from pathlib import Path

import numpy as np
from rasterio.crs import CRS
from rasterio.transform import from_origin

from src.flood_factors.mcda_flood_susceptibility import (
    FACTOR_ORDER,
    calculate_ahp_weights,
)

from src.interpreter.input_loader import ModelInputs
from src.interpreter.cell_selector import select_raster_cell
from src.interpreter.factor_evidence import extract_factor_evidence
from src.interpreter.weighted_contributions import (
    calculate_weighted_contributions,
)
from src.interpreter.score_verification import (
    verify_susceptibility_score,
)
from src.interpreter.explanation_generator import (
    generate_deterministic_explanation,
)


class TestInterpreterIntegration(unittest.TestCase):
    """Test the complete deterministic interpretation workflow."""

    def setUp(self):
        self.height = 3
        self.width = 4

        weights, consistency_ratio, _, _ = calculate_ahp_weights()

        self.weights = {
            factor: float(weights[factor])
            for factor in FACTOR_ORDER
        }

        self.consistency_ratio = float(consistency_ratio)

    def create_model_inputs(self, stored_score=None):
        """Create synthetic, internally controlled model inputs."""

        factor_values = {
            factor: 0.8
            for factor in FACTOR_ORDER
        }

        factor_arrays = {
            factor: np.full(
                (self.height, self.width),
                factor_values[factor],
                dtype=np.float32,
            )
            for factor in FACTOR_ORDER
        }

        reconstructed_score = sum(
            float(factor_arrays[factor][0, 0])
            * self.weights[factor]
            for factor in FACTOR_ORDER
        )

        reconstructed_score = float(
            np.float32(reconstructed_score)
        )

        if stored_score is None:
            stored_score = reconstructed_score

        susceptibility = np.full(
            (self.height, self.width),
            stored_score,
            dtype=np.float32,
        )

        valid_mask = np.ones(
            (self.height, self.width),
            dtype=bool,
        )

        return ModelInputs(
            factor_arrays=factor_arrays,
            susceptibility=susceptibility,
            valid_mask=valid_mask,
            weights=self.weights.copy(),
            consistency_ratio=self.consistency_ratio,
            crs=CRS.from_epsg(32737),
            transform=from_origin(100, 200, 10, 10),
            width=self.width,
            height=self.height,
            resolution=(10.0, 10.0),
            nodata=-9999.0,
            valid_cell_count=self.height * self.width,
            factor_paths={
                factor: Path(f"{factor}.tif")
                for factor in FACTOR_ORDER
            },
            susceptibility_path=Path(
                "synthetic_susceptibility.tif"
            ),
            metadata={},
            max_reconstruction_error=0.0,
        )

    def run_interpreter_workflow(
        self,
        model_inputs,
        row=1,
        column=2,
    ):
        """Execute all six Phase 10 interpreter components."""

        selection = select_raster_cell(
            model_inputs,
            row,
            column,
        )

        evidence = extract_factor_evidence(
            model_inputs,
            selection,
        )

        contributions = calculate_weighted_contributions(
            model_inputs,
            evidence,
        )

        verification = verify_susceptibility_score(
            contributions,
        )

        explanation = generate_deterministic_explanation(
            contributions,
            verification,
        )

        return {
            "selection": selection,
            "evidence": evidence,
            "contributions": contributions,
            "verification": verification,
            "explanation": explanation,
        }

    def test_complete_workflow_passes(self):
        """All six components should work together successfully."""

        inputs = self.create_model_inputs()

        result = self.run_interpreter_workflow(inputs)

        self.assertTrue(
            result["verification"].verification_passed
        )

        self.assertEqual(
            result["verification"].row,
            1,
        )

        self.assertEqual(
            result["verification"].column,
            2,
        )

        self.assertEqual(
            result["evidence"].crs,
            inputs.crs,
        )

        self.assertEqual(
            set(result["evidence"].factor_scores),
            set(FACTOR_ORDER),
        )

        explanation = result["explanation"]

        self.assertEqual(
            explanation["susceptibility"]["verification_status"],
            "PASS",
        )

        self.assertEqual(
            len(explanation["factor_evidence"]),
            5,
        )

        self.assertEqual(
            len(explanation["contribution_ranking"]),
            5,
        )

    def test_weighted_contributions_reconstruct_stored_score(self):
        """The five weighted contributions should reconstruct the score."""

        inputs = self.create_model_inputs()

        result = self.run_interpreter_workflow(inputs)

        contribution_sum = sum(
            result["contributions"]
            .factor_contributions[factor]
            .weighted_contribution
            for factor in FACTOR_ORDER
        )

        expected_score = float(
            np.float32(contribution_sum)
        )

        self.assertAlmostEqual(
            expected_score,
            result["contributions"].susceptibility_score,
            delta=1e-5,
        )

    def test_invalid_cell_stops_workflow(self):
        """An invalid raster cell must be rejected at selection."""

        inputs = self.create_model_inputs()

        with self.assertRaises(ValueError):
            self.run_interpreter_workflow(
                inputs,
                row=self.height,
                column=0,
            )

    def test_failed_verification_withholds_ranking(self):
        """An inconsistent stored score must not produce a ranking."""

        inputs = self.create_model_inputs(
            stored_score=0.70,
        )

        result = self.run_interpreter_workflow(inputs)

        self.assertFalse(
            result["verification"].verification_passed
        )

        explanation = result["explanation"]

        self.assertEqual(
            explanation["susceptibility"]["verification_status"],
            "FAIL",
        )

        self.assertIsNone(
            explanation["contribution_ranking"]
        )

        self.assertIsNone(
            explanation["interpretation"]["dominant_factor"]
        )

    def test_repeated_workflow_produces_identical_explanations(self):
        """Repeated interpretation of the same cell must be deterministic."""

        inputs = self.create_model_inputs()

        first_result = self.run_interpreter_workflow(inputs)
        second_result = self.run_interpreter_workflow(inputs)

        self.assertEqual(
            first_result["explanation"],
            second_result["explanation"],
        )


if __name__ == "__main__":
    unittest.main()
