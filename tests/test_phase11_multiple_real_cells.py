import unittest

import numpy as np

from src.interpreter.input_loader import load_model_inputs
from src.interpreter.workflow import run_interpreter_workflow


class TestPhase11MultipleRealCells(unittest.TestCase):
    """Validate the reusable workflow against real production rasters."""

    @classmethod
    def setUpClass(cls):
        """Load and validate production inputs once."""

        cls.inputs = load_model_inputs()

        cls.rows, cls.columns = np.where(cls.inputs.valid_mask)

        cls.scores = (
            cls.inputs.susceptibility[
                cls.inputs.valid_mask
            ].astype(np.float64)
        )

        cls.percentiles = [
            ("LOW_P10", 10),
            ("MEDIAN_P50", 50),
            ("HIGH_P90", 90),
        ]

    def test_complete_interpreter_on_three_production_cells(self):
        """Test the shared workflow on three unique real cells."""

        selected_cells = set()
        passed_count = 0

        print("\nPHASE 11 — MULTI-CELL PRODUCTION WORKFLOW VALIDATION")
        print("=" * 70)
        print(f"Valid production cells: {len(self.scores):,}")

        for label, percentile in self.percentiles:

            with self.subTest(percentile=label):

                target = np.percentile(
                    self.scores,
                    percentile,
                )

                candidate_order = np.argsort(
                    np.abs(self.scores - target)
                )

                selected_index = None

                for candidate in candidate_order:

                    row = int(self.rows[candidate])
                    column = int(self.columns[candidate])

                    if (row, column) not in selected_cells:
                        selected_index = int(candidate)
                        selected_cells.add((row, column))
                        break

                if selected_index is None:
                    self.fail(
                        f"Could not select a unique cell for {label}"
                    )
                    continue

                row = int(self.rows[selected_index])
                column = int(self.columns[selected_index])

                # Run the same reusable workflow intended for the application.
                result = run_interpreter_workflow(
                    self.inputs,
                    row,
                    column,
                )

                selection = result["selection"]
                evidence = result["evidence"]
                contributions = result["contributions"]
                verification = result["verification"]
                explanation = result["explanation"]

                self.assertEqual(
                    selection.row,
                    row,
                )

                self.assertEqual(
                    selection.column,
                    column,
                )

                self.assertEqual(
                    len(evidence.factor_scores),
                    5,
                    "Exactly five factor scores must be extracted.",
                )

                self.assertEqual(
                    len(contributions.factor_contributions),
                    5,
                )

                self.assertTrue(
                    verification.verification_passed,
                    f"{label}: score verification failed.",
                )

                self.assertAlmostEqual(
                    verification.absolute_difference,
                    0.0,
                    places=7,
                )

                self.assertEqual(
                    explanation["susceptibility"][
                        "verification_status"
                    ],
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

                self.assertIsNotNone(
                    explanation["interpretation"]["dominant_factor"],
                )

                self.assertGreaterEqual(
                    len(explanation["limitations"]),
                    1,
                )

                # Count this cell only after all assertions pass.
                passed_count += 1

                print("\n" + "-" * 70)
                print(f"TEST: {label}")
                print(f"Target percentile: P{percentile}")
                print(f"Target index: {target:.8f}")
                print(
                    f"Selected cell: row={row}, column={column}"
                )
                print(
                    "Stored score: "
                    f"{verification.stored_score:.8f}"
                )
                print(
                    "Reconstructed score: "
                    f"{verification.reconstructed_score:.8f}"
                )
                print(
                    "Absolute difference: "
                    f"{verification.absolute_difference:.12f}"
                )
                print(
                    "Dominant factor: "
                    f"{explanation['interpretation']['dominant_factor']}"
                )
                print(
                    "Verification: "
                    f"{explanation['susceptibility']['verification_status']}"
                )

        self.assertEqual(
            len(selected_cells),
            3,
            "Three unique production cells must be selected.",
        )

        self.assertEqual(
            passed_count,
            3,
            "All three production-cell workflows must pass.",
        )

        if passed_count == 3:
            print("\n" + "=" * 70)
            print("ALL THREE PRODUCTION WORKFLOWS PASSED")
            print("=" * 70)


if __name__ == "__main__":
    unittest.main(verbosity=2)
