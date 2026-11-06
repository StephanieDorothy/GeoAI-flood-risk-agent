
"""
Phase 10.6 — Calculate Weighted Factor Contributions.

Calculates the individual weighted contribution of each standardized
factor score using the authoritative AHP weights supplied by ModelInputs.

This module does not calculate the total weighted sum or reconstruct
the stored susceptibility score. Those tasks belong to Phase 10.7.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER
from src.interpreter.factor_evidence import FactorEvidence
from src.interpreter.input_loader import ModelInputs


WEIGHT_SUM_TOLERANCE = 1e-8


@dataclass(frozen=True)
class FactorContribution:
    """Score, AHP weight, and weighted contribution for one factor."""

    factor_score: float
    weight: float
    weighted_contribution: float


@dataclass(frozen=True)
class WeightedContributions:
    """Structured weighted factor contributions for one raster cell."""

    row: int
    column: int

    x: float
    y: float
    crs: Any

    susceptibility_score: float

    factor_contributions: dict[str, FactorContribution]


def calculate_weighted_contributions(
    model_inputs: ModelInputs,
    evidence: FactorEvidence,
) -> WeightedContributions:
    """
    Calculate individual weighted contributions for all five factors.

    The calculation for each factor is:

        weighted_contribution = factor_score * AHP_weight

    Parameters
    ----------
    model_inputs:
        Validated model inputs containing the authoritative AHP weights.

    evidence:
        Factor evidence returned by extract_factor_evidence().

    Returns
    -------
    WeightedContributions:
        Cell information and a structured contribution for each factor.

    Raises
    ------
    TypeError:
        If the supplied objects have incorrect types.

    ValueError:
        If factors or weights are missing, unexpected values are present,
        scores or weights are invalid, or the AHP weights do not sum
        to approximately one.
    """

    # 1. Validate supplied objects.
    if not isinstance(model_inputs, ModelInputs):
        raise TypeError(
            "model_inputs must be a validated ModelInputs object."
        )

    if not isinstance(evidence, FactorEvidence):
        raise TypeError(
            "evidence must be a FactorEvidence object."
        )

    # 2. Validate factor score availability.
    expected_factors = set(FACTOR_ORDER)
    supplied_factors = set(evidence.factor_scores.keys())

    missing_factors = expected_factors - supplied_factors
    unexpected_factors = supplied_factors - expected_factors

    if missing_factors:
        raise ValueError(
            "Missing factor scores: "
            + ", ".join(sorted(missing_factors))
        )

    if unexpected_factors:
        raise ValueError(
            "Unexpected factor scores: "
            + ", ".join(sorted(unexpected_factors))
        )

    # 3. Validate AHP weight availability.
    supplied_weights = set(model_inputs.weights.keys())

    missing_weights = expected_factors - supplied_weights
    unexpected_weights = supplied_weights - expected_factors

    if missing_weights:
        raise ValueError(
            "Missing AHP weights: "
            + ", ".join(sorted(missing_weights))
        )

    if unexpected_weights:
        raise ValueError(
            "Unexpected AHP weights: "
            + ", ".join(sorted(unexpected_weights))
        )

    # 4. Validate factor scores and AHP weights.
    validated_scores: dict[str, float] = {}
    validated_weights: dict[str, float] = {}

    for factor in FACTOR_ORDER:
        score = float(evidence.factor_scores[factor])
        weight = float(model_inputs.weights[factor])

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

        validated_scores[factor] = score
        validated_weights[factor] = weight

    # 5. Confirm that the five AHP weights form a normalized set.
    weight_sum = sum(validated_weights.values())

    if not np.isclose(
        weight_sum,
        1.0,
        rtol=0.0,
        atol=WEIGHT_SUM_TOLERANCE,
    ):
        raise ValueError(
            "The five AHP weights must sum to approximately 1.0. "
            f"Received {weight_sum:.12f}."
        )

    # 6. Calculate each factor's individual weighted contribution.
    # Do not calculate the total weighted sum here.
    contributions: dict[str, FactorContribution] = {}

    for factor in FACTOR_ORDER:
        score = validated_scores[factor]
        weight = validated_weights[factor]

        contribution = score * weight

        contributions[factor] = FactorContribution(
            factor_score=score,
            weight=weight,
            weighted_contribution=contribution,
        )

    # 7. Return structured factor-level evidence.
    return WeightedContributions(
        row=evidence.row,
        column=evidence.column,
        x=evidence.x,
        y=evidence.y,
        crs=evidence.crs,
        susceptibility_score=evidence.susceptibility_score,
        factor_contributions=contributions,
    )
