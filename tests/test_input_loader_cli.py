"""Tests for the Phase 11 input-loader command-line report."""

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from src.interpreter import input_loader


class TestInputLoaderCLI(unittest.TestCase):
    """Test CLI reporting and loader-failure behaviour."""

    def setUp(self):
        self.mock_inputs = SimpleNamespace(
            crs="EPSG:32737",
            width=1603,
            height=1019,
            resolution=30.865516819,
            nodata=-9999.0,
            weights={
                factor: 0.2
                for factor in input_loader.FACTOR_ORDER
            },
            consistency_ratio=0.0269475117,
            valid_cell_count=553860,
            max_reconstruction_error=0.000000029880,
        )

    def test_main_prints_complete_success_report(self):
        """A successful loader call must produce the complete report."""

        output = io.StringIO()

        with patch.object(
            input_loader,
            "load_model_inputs",
            return_value=self.mock_inputs,
        ):
            with redirect_stdout(output):
                input_loader.main()

        report = output.getvalue()

        self.assertIn("PHASE 11", report)
        self.assertIn("INPUT VALIDATION: PASS", report)
        self.assertIn("CRS: EPSG:32737", report)
        self.assertIn("Raster dimensions: 1603 × 1019", report)
        self.assertIn("Resolution: 30.865516819", report)
        self.assertIn("NoData: -9999.0", report)

        for factor in input_loader.FACTOR_ORDER:
            self.assertIn(f"{factor}: PASS", report)
            self.assertIn(f"{factor} weight:", report)

        self.assertIn("AHP consistency ratio:", report)
        self.assertIn("Common valid cells: 553,860", report)
        self.assertIn("Spatial alignment: PASS", report)
        self.assertIn("Factor score ranges: PASS", report)
        self.assertIn("Output mask agreement: PASS", report)
        self.assertIn("AHP metadata agreement: PASS", report)
        self.assertIn("Susceptibility reconstruction: PASS", report)
        self.assertIn("Maximum reconstruction error:", report)
        self.assertIn("No model files were modified.", report)

    def test_main_propagates_loader_failure_without_success_report(self):
        """A loader failure must propagate and must not print PASS."""

        output = io.StringIO()

        with patch.object(
            input_loader,
            "load_model_inputs",
            side_effect=FileNotFoundError("missing elevation raster"),
        ):
            with redirect_stdout(output):
                with self.assertRaisesRegex(
                    FileNotFoundError,
                    "missing elevation raster",
                ):
                    input_loader.main()

        report = output.getvalue()

        self.assertIn("PHASE 11", report)
        self.assertNotIn("INPUT VALIDATION: PASS", report)
        self.assertNotIn("No model files were modified.", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
