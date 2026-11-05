"""
Phase 10.5 — Extract Factor Evidence.

Extracts the five standardized factor scores and stored susceptibility
score for a previously selected raster cell.

This module is read-only. It does not modify model inputs or rasters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER
from src.interpreter.cell_selector import CellSelection
from src.interpreter.input_loader import ModelInputs


@dataclass(frozen=True)
class FactorEvidence:
    """Structured factor evidence for one selected raster cell."""

    row: int
    column: int

    x: float
    y: float
    crs: Any

    factor_scores: dict[str, float]

    susceptibility_score: float


def extract_factor_evidence(
    model_inputs: ModelInputs,
    selection: CellSelection,
) -> FactorEvidence:
    """
    Extract all five factor scores and the stored susceptibility
    score for a previously selected raster cell.

    Parameters
    ----------
    model_inputs:
        Validated model inputs returned by load_model_inputs().

    selection:
        Valid cell selection returned by select_raster_cell().

    Returns
    -------
    FactorEvidence:
        Cell location, five factor scores, and stored susceptibility
        score.

    Raises
    ------
    TypeError:
        If the supplied objects have incorrect types.

    ValueError:
        If required factors are missing, arrays are incompatible,
        the selected cell is invalid, or extracted values are invalid.
    """

    # 1. Validate supplied objects.
    if not isinstance(model_inputs, ModelInputs):
        raise TypeError(
            "model_inputs must be a validated ModelInputs object."
        )

    if not isinstance(selection, CellSelection):
        raise TypeError(
            "selection must be a CellSelection object."
        )

    row = selection.row
    column = selection.column

    # 2. Validate raster dimensions and array shapes.
    expected_shape = (
        model_inputs.height,
        model_inputs.width,
    )

    if model_inputs.valid_mask.shape != expected_shape:
        raise ValueError(
            "The valid-data mask shape does not match "
            "the declared raster dimensions."
        )

    if model_inputs.susceptibility.shape != expected_shape:
        raise ValueError(
            "The susceptibility array shape does not match "
            "the declared raster dimensions."
        )

    # 3. Validate factor availability.
    missing_factors = [
        factor
        for factor in FACTOR_ORDER
        if factor not in model_inputs.factor_arrays
    ]

    if missing_factors:
        raise ValueError(
            "Missing required factor arrays: "
            + ", ".join(missing_factors)
        )

    # 4. Validate factor array shapes.
    for factor in FACTOR_ORDER:
        array = model_inputs.factor_arrays[factor]

        if array.shape != expected_shape:
            raise ValueError(
                f"{factor} array shape {array.shape} does not "
                f"match expected shape {expected_shape}."
            )

    # 5. Validate selected cell boundaries.
    if (
        isinstance(row, bool)
        or not isinstance(row, (int, np.integer))
    ):
        raise ValueError(
            "Selected row must be an integer."
        )

    if (
        isinstance(column, bool)
        or not isinstance(column, (int, np.integer))
    ):
        raise ValueError(
            "Selected column must be an integer."
        )

    row = int(row)
    column = int(column)

    if not (
        0 <= row < model_inputs.height
        and 0 <= column < model_inputs.width
    ):
        raise ValueError(
            f"Selected cell ({row}, {column}) is outside "
            "the raster dimensions."
        )

    # 6. Confirm that the selected cell belongs to the
    # common valid-data footprint.
    if not bool(model_inputs.valid_mask[row, column]):
        raise ValueError(
            f"Cell at row {row}, column {column} is outside "
            "the common valid-data footprint."
        )

    # 7. Extract and validate all five factor scores.
    factor_scores: dict[str, float] = {}

    for factor in FACTOR_ORDER:
        value = float(
            model_inputs.factor_arrays[factor][row, column]
        )

        if not np.isfinite(value):
            raise ValueError(
                f"The {factor} score at row {row}, "
                f"column {column} is not finite."
            )

        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"The {factor} score at row {row}, "
                f"column {column} is outside the accepted "
                f"0–1 range: {value}."
            )

        factor_scores[factor] = value

    # 8. Retrieve and validate the stored susceptibility score.
    stored_score = float(
        model_inputs.susceptibility[row, column]
    )

    if not np.isfinite(stored_score):
        raise ValueError(
            "The stored susceptibility score is not finite."
        )

    if np.isclose(
        stored_score,
        model_inputs.nodata,
        rtol=0.0,
        atol=0.0,
    ):
        raise ValueError(
            "The selected cell contains a NoData "
            "susceptibility value."
        )

    # 9. Confirm consistency with the original cell selection.
    if not np.isclose(
        stored_score,
        selection.susceptibility_score,
        rtol=0.0,
        atol=0.0,
    ):
        raise ValueError(
            "The susceptibility score in CellSelection does "
            "not match the stored model-input value."
        )

    # 10. Return structured evidence.
    return FactorEvidence(
        row=row,
        column=column,
        x=float(selection.x),
        y=float(selection.y),
        crs=selection.crs,
        factor_scores=factor_scores,
        susceptibility_score=stored_score,
    )