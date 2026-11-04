
"""
Phase 10.4 — Raster Cell Selection.

Selects and validates a raster cell using previously validated
ModelInputs from Phase 10.3.

This module is read-only. It does not modify any model raster.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
from typing import Any

import numpy as np
from rasterio.transform import xy

from src.interpreter.input_loader import ModelInputs


@dataclass(frozen=True)
class CellSelection:
    """Structured information about a selected raster cell."""

    row: int
    column: int

    x: float
    y: float

    crs: Any

    susceptibility_score: float


def select_raster_cell(
    model_inputs: ModelInputs,
    row: int,
    column: int,
) -> CellSelection:
    """
    Validate and select one cell from the susceptibility raster.

    Parameters
    ----------
    model_inputs:
        Validated model inputs returned by load_model_inputs().

    row:
        Zero-based raster row index.

    column:
        Zero-based raster column index.

    Returns
    -------
    CellSelection:
        Selected cell indices, cell-centre coordinates,
        CRS, and susceptibility score.

    Raises
    ------
    TypeError:
        If row or column is not an integer.

    ValueError:
        If an index is negative, outside the raster,
        or points to a NoData cell.
    """

    # 1. Validate index types.
    # Boolean values are excluded even though bool is an int subclass.
    if (
        isinstance(row, bool)
        or not isinstance(row, Integral)
    ):
        raise TypeError(
            f"Row must be an integer. Received: {type(row).__name__}."
        )

    if (
        isinstance(column, bool)
        or not isinstance(column, Integral)
    ):
        raise TypeError(
            f"Column must be an integer. "
            f"Received: {type(column).__name__}."
        )

    row = int(row)
    column = int(column)

    # 2. Validate raster boundaries.
    if row < 0 or row >= model_inputs.height:
        raise ValueError(
            f"Row index {row} is outside the raster. "
            f"Valid range: 0 to {model_inputs.height - 1}."
        )

    if column < 0 or column >= model_inputs.width:
        raise ValueError(
            f"Column index {column} is outside the raster. "
            f"Valid range: 0 to {model_inputs.width - 1}."
        )

    # 3. Check whether the selected cell contains valid data.
    if not bool(model_inputs.valid_mask[row, column]):
        raise ValueError(
            f"Cell at row {row}, column {column} contains NoData "
            "or is outside the common valid-data footprint."
        )

    # 4. Retrieve the susceptibility score.
    score = float(
        model_inputs.susceptibility[row, column]
    )

    if not np.isfinite(score):
        raise ValueError(
            "Selected cell has a non-finite susceptibility score."
        )

    # 5. Convert the raster indices to cell-centre coordinates.
    x, y = xy(
        model_inputs.transform,
        row,
        column,
        offset="center",
    )

    # 6. Return the structured selection.
    return CellSelection(
        row=row,
        column=column,
        x=float(x),
        y=float(y),
        crs=model_inputs.crs,
        susceptibility_score=score,
    )
