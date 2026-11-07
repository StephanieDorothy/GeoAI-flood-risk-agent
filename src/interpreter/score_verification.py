
"""
Phase 10.7 — Reconstruct and Verify the Susceptibility Score.

Reconstructs the susceptibility score for one selected raster cell
using the weighted factor contributions calculated in Phase 10.6.

The reconstructed value is converted to float32 to match the original
MCDA model's output precision before comparison with the stored score.

This module does not modify any model input or output raster.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER
from src.interpreter.input_loader import RECONSTRUCTION_TOLERANCE
from src.interpreter.weighted_contributions import (
    FactorContribution,
    WeightedContributions,
)


@dataclass(frozen=True)
class ScoreVerification:
    """Reconstructed score and verification result for one raster cell."""

    row: int
    column: int

    x: float
    y: float
    crs: Any

    reconstructed_score: float
    stored_score: float

    absolute_difference: float
    tolerance: float

    verification_passed: bool


def verify_susceptibility_score(
    contributions: WeightedContributions,
) -> ScoreVerification:
    """
    Reconstruct and verify the susceptibility score for one raster cell.

    The reconstruction follows the original MCDA calculation:

        1. Accumulate the five weighted contributions in FACTOR_ORDER
           using float64 arithmetic.
        2. Convert the final result to float32.
        3. Compare it with the stored susceptibility score.
        4. Apply RECONSTRUCTION_TOLERANCE.

    Parameters
    ----------
    contributions:
        Weighted factor contributions returned by
        calculate_weighted_contributions().

    Returns
    -------
    ScoreVerification:
        Structured reconstruction and verification result.

    Raises
    ------
    TypeError:
        If the supplied object or factor contributions have
        incorrect types.

    ValueError:
        If factor contributions are missing, unexpected, non-finite,
        or outside their accepted range, or if the stored score
        is invalid.
    """

    # 1. Validate the supplied object.
    if not isinstance(contributions, WeightedContributions):
        raise TypeError(
            "contributions must be a WeightedContributions object."
        )

    # 2. Validate the five factor contributions.
    expected_factors = set(FACTOR_ORDER)
    supplied_factors = set(
        contributions.factor_contributions.keys()
    )

    missing_factors = expected_factors - supplied_factors
    unexpected_factors = supplied_factors - expected_factors

    if missing_factors:
        raise ValueError(
            "Missing factor contributions: "
            + ", ".join(sorted(missing_factors))
        )

    if unexpected_factors:
        raise ValueError(
            "Unexpected factor contributions: "
            + ", ".join(sorted(unexpected_factors))
        )

    # 3. Validate each contribution before reconstruction.
    validated_contributions: dict[str, float] = {}

    for factor in FACTOR_ORDER:
        item = contributions.factor_contributions[factor]

        if not isinstance(item, FactorContribution):
            raise TypeError(
                f"The {factor} contribution must be a "
                "FactorContribution object."
            )

        score = float(item.factor_score)
        weight = float(item.weight)
        weighted_contribution = float(
            item.weighted_contribution
        )

        if not np.isfinite(score):
            raise ValueError(
                f"The {factor} factor score is not finite."
            )

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                f"The {factor} factor score is outside "
                f"the accepted 0–1 range: {score}."
            )

        if not np.isfinite(weight):
            raise ValueError(
                f"The {factor} AHP weight is not finite."
            )

        if not 0.0 <= weight <= 1.0:
            raise ValueError(
                f"The {factor} AHP weight is outside "
                f"the accepted 0–1 range: {weight}."
            )

        if not np.isfinite(weighted_contribution):
            raise ValueError(
                f"The {factor} weighted contribution is not finite."
            )

        if not 0.0 <= weighted_contribution <= 1.0:
            raise ValueError(
                f"The {factor} weighted contribution is outside "
                f"the accepted 0–1 range: {weighted_contribution}."
            )

        validated_contributions[factor] = weighted_contribution

    # 4. Validate the stored susceptibility score.
    stored_score = float(contributions.susceptibility_score)

    if not np.isfinite(stored_score):
        raise ValueError(
            "The stored susceptibility score is not finite."
        )

    if not 0.0 <= stored_score <= 1.0:
        raise ValueError(
            "The stored susceptibility score is outside "
            f"the accepted 0–1 range: {stored_score}."
        )

    # 5. Reconstruct the score using float64 accumulation.
    reconstructed_sum = np.float64(0.0)

    for factor in FACTOR_ORDER:
        reconstructed_sum += np.float64(
            validated_contributions[factor]
        )

    # Match the original MCDA model's float32 output precision.
    reconstructed_score = float(
        np.float32(reconstructed_sum)
    )

    if not np.isfinite(reconstructed_score):
        raise ValueError(
            "The reconstructed susceptibility score is not finite."
        )

    # 6. Calculate the absolute difference.
    absolute_difference = abs(
        reconstructed_score - stored_score
    )

    # 7. Apply the established reconstruction tolerance.
    verification_passed = (
        absolute_difference <= RECONSTRUCTION_TOLERANCE
    )

    # 8. Return the structured verification result.
    return ScoreVerification(
        row=contributions.row,
        column=contributions.column,
        x=contributions.x,
        y=contributions.y,
        crs=contributions.crs,
        reconstructed_score=reconstructed_score,
        stored_score=stored_score,
        absolute_difference=absolute_difference,
        tolerance=RECONSTRUCTION_TOLERANCE,
        verification_passed=verification_passed,
    )
