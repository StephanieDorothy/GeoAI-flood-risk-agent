"""
Phase 11 — Reusable Interpreter Workflow.

Coordinates the existing deterministic interpreter components
for one selected raster cell.

Model inputs must already have been loaded and validated.
This module does not read, modify, or regenerate model rasters.
"""

from __future__ import annotations

from src.interpreter.input_loader import ModelInputs
from src.interpreter.cell_selector import (
    select_raster_cell,
)
from src.interpreter.factor_evidence import (
    extract_factor_evidence,
)
from src.interpreter.weighted_contributions import (
    calculate_weighted_contributions,
)
from src.interpreter.score_verification import (
    verify_susceptibility_score,
)
from src.interpreter.explanation_generator import (
    generate_deterministic_explanation,
)


def run_interpreter_workflow(
    model_inputs: ModelInputs,
    row: int,
    column: int,
) -> dict:
    """
    Run the complete deterministic interpretation workflow.

    Parameters
    ----------
    model_inputs:
        Previously loaded and validated ModelInputs.

    row:
        Zero-based raster row index.

    column:
        Zero-based raster column index.

    Returns
    -------
    dict:
        Structured results containing:
        selection, evidence, contributions, verification,
        and explanation.

    Raises
    ------
    TypeError:
        If model_inputs is not a ModelInputs object, or if
        row or column has an invalid type.

    ValueError:
        If the selected cell is outside the raster, contains
        NoData, or fails validation in an existing component.

    Notes
    -----
    The workflow deliberately does not call load_model_inputs().
    Applications should load and validate the model once, then
    reuse those inputs for multiple cell interpretation requests.

    A failed score verification is retained in the returned
    result. The explanation generator is responsible for
    withholding normal contribution rankings in that case.
    """

    if not isinstance(model_inputs, ModelInputs):
        raise TypeError(
            "model_inputs must be a validated ModelInputs object."
        )

    # 1. Select and validate the requested raster cell.
    selection = select_raster_cell(
        model_inputs,
        row,
        column,
    )

    # 2. Extract the five standardized factor scores.
    evidence = extract_factor_evidence(
        model_inputs,
        selection,
    )

    # 3. Calculate each factor's weighted contribution.
    contributions = calculate_weighted_contributions(
        model_inputs,
        evidence,
    )

    # 4. Verify the reconstructed susceptibility score.
    verification = verify_susceptibility_score(
        contributions,
    )

    # 5. Generate the deterministic structured explanation.
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
