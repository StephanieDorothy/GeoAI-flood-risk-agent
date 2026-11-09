"""
Generate deterministic explanations for individual flood-susceptibility
raster cells.

This module interprets existing model evidence. It does not:
- Recalculate the flood-susceptibility model.
- Modify factor scores, AHP weights, or classification thresholds.
- Infer calibrated flood probabilities.
- Infer original land-cover categories from standardized scores.

The combined susceptibility score is a relative MCDA index, not a
probability or a flood forecast.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.flood_factors.mcda_flood_susceptibility import FACTOR_ORDER

from src.interpreter.weighted_contributions import (
    WeightedContributions,
)

from src.interpreter.score_verification import (
    ScoreVerification,
)


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

FACTOR_VALIDATION_TOLERANCE = 1e-8
WEIGHT_SUM_TOLERANCE = 1e-8
COORDINATE_TOLERANCE = 1e-9
SCORE_MATCH_TOLERANCE = 1e-8

FACTOR_DESCRIPTIONS = {
    "elevation": (
        "A higher factor score represents lower elevation under the "
        "model's inverse standardisation. Lower-lying terrain may be "
        "more susceptible to flood accumulation."
    ),
    "slope": (
        "A higher factor score represents gentler terrain under the "
        "model's inverse standardisation. Slope is a terrain indicator "
        "and does not independently establish flood occurrence."
    ),
    "distance_to_rivers": (
        "A higher factor score represents a location closer to mapped "
        "rivers under the model's inverse standardisation. Proximity "
        "indicates potential river-related susceptibility, not a "
        "confirmed flood event."
    ),
    "landcover": (
        "The score is assigned using the model's land-cover lookup "
        "table. The original land-cover category is not retained in "
        "the current evidence object, so it cannot be identified "
        "reliably from this evidence alone."
    ),
    "population": (
        "A higher factor score represents a higher standardized "
        "population value. This is relevant to population exposure "
        "and is not itself a physical terrain or hydrological "
        "susceptibility indicator."
    ),
}

PHYSICAL_SUSCEPTIBILITY_FACTORS = (
    "elevation",
    "slope",
    "distance_to_rivers",
    "landcover",
)

FACTOR_LABELS = {
    "elevation": "Elevation",
    "slope": "Slope",
    "distance_to_rivers": "Distance to rivers",
    "landcover": "Land cover",
    "population": "Population",
}


# ---------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------

def _require_finite_number(
    value: Any,
    field_name: str,
) -> float:
    """Return a finite float or raise a clear validation error."""

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be a numeric value, not a boolean."
        )

    try:
        numeric_value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            f"{field_name} must be a finite numeric value."
        ) from exc

    if not math.isfinite(numeric_value):
        raise ValueError(
            f"{field_name} must be finite."
        )

    return numeric_value


def _validate_unit_interval(
    value: Any,
    field_name: str,
) -> float:
    """Validate a finite score or weight in the range [0, 1]."""

    numeric_value = _require_finite_number(
        value,
        field_name,
    )

    if not 0.0 <= numeric_value <= 1.0:
        raise ValueError(
            f"{field_name} must be between 0 and 1."
        )

    return numeric_value


def _validate_cell_identity(
    contributions: WeightedContributions,
    verification: ScoreVerification,
) -> None:
    """Ensure both evidence objects refer to exactly the same cell."""

    if contributions.row != verification.row:
        raise ValueError(
            "Cell row mismatch between contributions and verification."
        )

    if contributions.column != verification.column:
        raise ValueError(
            "Cell column mismatch between contributions and verification."
        )

    contribution_x = _require_finite_number(
        contributions.x,
        "Contribution x coordinate",
    )

    verification_x = _require_finite_number(
        verification.x,
        "Verification x coordinate",
    )

    contribution_y = _require_finite_number(
        contributions.y,
        "Contribution y coordinate",
    )

    verification_y = _require_finite_number(
        verification.y,
        "Verification y coordinate",
    )

    if not math.isclose(
        contribution_x,
        verification_x,
        rel_tol=0.0,
        abs_tol=COORDINATE_TOLERANCE,
    ):
        raise ValueError(
            "Cell x-coordinate mismatch between evidence objects."
        )

    if not math.isclose(
        contribution_y,
        verification_y,
        rel_tol=0.0,
        abs_tol=COORDINATE_TOLERANCE,
    ):
        raise ValueError(
            "Cell y-coordinate mismatch between evidence objects."
        )

    if contributions.crs != verification.crs:
        raise ValueError(
            "CRS mismatch between contributions and verification."
        )


def _validate_contributions(
    contributions: WeightedContributions,
) -> dict[str, dict[str, float]]:
    """
    Validate the five factor contributions.

    Returns a normalized dictionary containing each factor's score,
    weight, and weighted contribution.
    """

    expected_factors = tuple(FACTOR_ORDER)

    if set(contributions.factor_contributions) != set(expected_factors):
        raise ValueError(
            "Factor contributions must contain exactly the five "
            "model factors."
        )

    if len(contributions.factor_contributions) != len(expected_factors):
        raise ValueError(
            "Duplicate or unexpected factor contributions detected."
        )

    validated = {}
    weight_total = 0.0

    for factor in expected_factors:
        item = contributions.factor_contributions[factor]

        factor_score = _validate_unit_interval(
            item.factor_score,
            f"{factor} factor score",
        )

        weight = _validate_unit_interval(
            item.weight,
            f"{factor} AHP weight",
        )

        weighted_contribution = _require_finite_number(
            item.weighted_contribution,
            f"{factor} weighted contribution",
        )

        expected_contribution = factor_score * weight

        if not math.isclose(
            weighted_contribution,
            expected_contribution,
            rel_tol=0.0,
            abs_tol=FACTOR_VALIDATION_TOLERANCE,
        ):
            raise ValueError(
                f"{factor} weighted contribution does not match "
                "factor score multiplied by AHP weight."
            )

        if weighted_contribution < 0.0:
            raise ValueError(
                f"{factor} weighted contribution cannot be negative."
            )

        weight_total += weight

        validated[factor] = {
            "factor_score": factor_score,
            "weight": weight,
            "weighted_contribution": weighted_contribution,
        }

    if not math.isclose(
        weight_total,
        1.0,
        rel_tol=0.0,
        abs_tol=WEIGHT_SUM_TOLERANCE,
    ):
        raise ValueError(
            f"AHP weights must sum to 1.0. Received {weight_total:.12f}."
        )

    return validated


def _validate_verification(
    contributions: WeightedContributions,
    verification: ScoreVerification,
    validated_factors: dict[str, dict[str, float]],
) -> dict[str, Any]:
    """Validate the numerical score-verification evidence."""

    if not isinstance(verification.verification_passed, bool):
        raise ValueError(
            "Verification status must be a boolean."
        )

    reconstructed_score = _validate_unit_interval(
        verification.reconstructed_score,
        "Reconstructed susceptibility score",
    )

    stored_score = _validate_unit_interval(
        verification.stored_score,
        "Stored susceptibility score",
    )

    absolute_difference = _require_finite_number(
        verification.absolute_difference,
        "Absolute score difference",
    )

    tolerance = _require_finite_number(
        verification.tolerance,
        "Verification tolerance",
    )

    if absolute_difference < 0.0:
        raise ValueError(
            "Absolute score difference cannot be negative."
        )

    if tolerance <= 0.0:
        raise ValueError(
            "Verification tolerance must be greater than zero."
        )

    # Independently reconstruct the score from the five validated
    # weighted contributions. Match Phase 10.7 by summing in Python
    # float precision and casting the final result to float32.
    reconstructed_from_contributions = float(
        np.float32(
            sum(
                validated_factors[factor]["weighted_contribution"]
                for factor in FACTOR_ORDER
            )
        )
    )

    if not math.isclose(
        reconstructed_from_contributions,
        reconstructed_score,
        rel_tol=0.0,
        abs_tol=SCORE_MATCH_TOLERANCE,
    ):
        raise ValueError(
            "The sum of weighted factor contributions does not match "
            "the reconstructed score in the verification evidence."
        )

    expected_difference = abs(
        reconstructed_score - stored_score
    )

    if not math.isclose(
        absolute_difference,
        expected_difference,
        rel_tol=0.0,
        abs_tol=SCORE_MATCH_TOLERANCE,
    ):
        raise ValueError(
            "Reported absolute difference does not match the "
            "reconstructed and stored scores."
        )

    expected_status = absolute_difference <= tolerance

    if verification.verification_passed != expected_status:
        raise ValueError(
            "Verification status is inconsistent with the "
            "reported difference and tolerance."
        )

    contribution_score = _validate_unit_interval(
        contributions.susceptibility_score,
        "Contribution susceptibility score",
    )

    if not math.isclose(
        contribution_score,
        stored_score,
        rel_tol=0.0,
        abs_tol=SCORE_MATCH_TOLERANCE,
    ):
        raise ValueError(
            "Stored susceptibility score does not match the score "
            "in the weighted contributions."
        )

    return {
        "stored_score": stored_score,
        "reconstructed_score": reconstructed_score,
        "absolute_difference": absolute_difference,
        "tolerance": tolerance,
        "verification_passed": verification.verification_passed,
        "status": "PASS" if verification.verification_passed else "FAIL",
    }


# ---------------------------------------------------------------------
# Explanation generation
# ---------------------------------------------------------------------

def generate_deterministic_explanation(
    contributions: WeightedContributions,
    verification: ScoreVerification,
) -> dict[str, Any]:
    """
    Generate a structured deterministic explanation for one raster cell.

    Parameters
    ----------
    contributions:
        Weighted factor evidence produced by Phase 10.6.

    verification:
        Score verification produced by Phase 10.7.

    Returns
    -------
    dict
        Structured location, score verification, factor evidence,
        contribution ranking, interpretation, and limitations.

    Notes
    -----
    A failed verification does not prevent the numerical evidence
    from being reported. However, the normal interpretation and
    contribution ranking are withheld to avoid presenting an
    unverified result as a verified explanation.
    """

    if not isinstance(contributions, WeightedContributions):
        raise TypeError(
            "contributions must be a WeightedContributions object."
        )

    if not isinstance(verification, ScoreVerification):
        raise TypeError(
            "verification must be a ScoreVerification object."
        )

    # Validate that both objects refer to the same selected cell.
    _validate_cell_identity(
        contributions,
        verification,
    )

    # Validate and normalize the factor evidence.
    validated_factors = _validate_contributions(
        contributions,
    )

    # Validate the numerical verification result.
    validated_verification = _validate_verification(
        contributions,
        verification,
        validated_factors,
    )

    # -------------------------------------------------------------
    # Location
    # -------------------------------------------------------------

    location = {
        "row": contributions.row,
        "column": contributions.column,
        "x": _require_finite_number(
            contributions.x,
            "Cell x coordinate",
        ),
        "y": _require_finite_number(
            contributions.y,
            "Cell y coordinate",
        ),
        "crs": str(contributions.crs),
    }

    # -------------------------------------------------------------
    # Factor evidence
    # -------------------------------------------------------------

    factor_evidence = {}

    for factor in FACTOR_ORDER:
        values = validated_factors[factor]

        factor_evidence[factor] = {
            "label": FACTOR_LABELS[factor],
            "factor_score": values["factor_score"],
            "ahp_weight": values["weight"],
            "weighted_contribution": values["weighted_contribution"],
            "interpretation": FACTOR_DESCRIPTIONS[factor],
        }

    # -------------------------------------------------------------
    # Contribution ranking
    # -------------------------------------------------------------

    # Sorting is deterministic:
    # 1. Largest weighted contribution first.
    # 2. FACTOR_ORDER resolves equal-contribution ties.
    factor_order_index = {
        factor: index
        for index, factor in enumerate(FACTOR_ORDER)
    }

    ranked_factors = sorted(
        FACTOR_ORDER,
        key=lambda factor: (
            -validated_factors[factor]["weighted_contribution"],
            factor_order_index[factor],
        ),
    )

    contribution_ranking = [
        {
            "rank": rank,
            "factor": factor,
            "label": FACTOR_LABELS[factor],
            "factor_score": validated_factors[factor]["factor_score"],
            "ahp_weight": validated_factors[factor]["weight"],
            "weighted_contribution": (
                validated_factors[factor]["weighted_contribution"]
            ),
            "factor_type": (
                "exposure-related"
                if factor == "population"
                else "physical-susceptibility indicator"
            ),
        }
        for rank, factor in enumerate(ranked_factors, start=1)
    ]

    # -------------------------------------------------------------
    # Interpretation
    # -------------------------------------------------------------

    if validated_verification["verification_passed"]:

        dominant_factor = ranked_factors[0]

        physical_factors_ranked = [
            factor
            for factor in ranked_factors
            if factor in PHYSICAL_SUSCEPTIBILITY_FACTORS
        ]

        dominant_physical_factor = physical_factors_ranked[0]

        overall_interpretation = (
            f"The selected cell has a stored relative flood-susceptibility "
            f"index of {validated_verification['stored_score']:.6f}. "
            f"The largest weighted contribution is from "
            f"{FACTOR_LABELS[dominant_factor].lower()}, with a weighted "
            f"contribution of "
            f"{validated_factors[dominant_factor]['weighted_contribution']:.6f}. "
            f"Among the physical-susceptibility indicators, the largest "
            f"weighted contribution is from "
            f"{FACTOR_LABELS[dominant_physical_factor].lower()}, with a "
            f"weighted contribution of "
            f"{validated_factors[dominant_physical_factor]['weighted_contribution']:.6f}. "
            f"These rankings describe the influence of the factors under "
            f"the existing MCDA scores and AHP weights; they do not establish "
            f"causation or prove that flooding will occur."
        )

        verification_interpretation = (
            "The reconstructed score agrees with the stored "
            "susceptibility score within the configured numerical tolerance."
        )

    else:

        dominant_factor = None
        dominant_physical_factor = None

        overall_interpretation = (
            "A normal susceptibility interpretation has been withheld "
            "because score verification failed. The numerical factor "
            "evidence is retained for diagnostic review, but the combined "
            "result must not be presented as verified."
        )

        verification_interpretation = (
            "The reconstructed score differs from the stored score by "
            "more than the configured numerical tolerance. The result "
            "has failed numerical verification."
        )

        # Do not present a normal contribution ranking for an
        # unverified combined score.
        contribution_ranking = None

    interpretation = {
        "overall": overall_interpretation,
        "verification": verification_interpretation,
        "dominant_factor": dominant_factor,
        "dominant_physical_susceptibility_factor": (
            dominant_physical_factor
        ),
        "population_exposure_note": (
            "Population is included in the existing MCDA combination, "
            "but it represents an exposure-related indicator. A high "
            "population contribution should not be interpreted as "
            "evidence of greater physical flood susceptibility."
        ),
    }

    # -------------------------------------------------------------
    # Limitations
    # -------------------------------------------------------------

    limitations = [
        (
            "The susceptibility score is a relative MCDA index. "
            "It is not a calibrated flood probability."
        ),
        (
            "The result is not a dynamic flood forecast and does not "
            "guarantee that flooding will or will not occur."
        ),
        (
            "Population represents an exposure-related indicator, "
            "not a direct physical flood-susceptibility process."
        ),
        (
            "Numerical score verification checks consistency between "
            "the stored score and its weighted reconstruction. It does "
            "not demonstrate predictive accuracy."
        ),
        (
            "The current factor evidence stores standardized scores, "
            "not the original raw measurements or land-cover category."
        ),
        (
            "Phase 9 event-level validation against the UNOSAT May 2024 "
            "flood extent showed weak and negative agreement with the "
            "model's susceptibility ranking. The temporal mismatch "
            "between the 2021 model inputs and the 2024 reference data "
            "remains an important limitation."
        ),
    ]

    # -------------------------------------------------------------
    # Structured output
    # -------------------------------------------------------------

    return {
        "location": location,
        "susceptibility": {
            "stored_score": validated_verification["stored_score"],
            "reconstructed_score": (
                validated_verification["reconstructed_score"]
            ),
            "absolute_difference": (
                validated_verification["absolute_difference"]
            ),
            "verification_tolerance": (
                validated_verification["tolerance"]
            ),
            "verification_status": (
                validated_verification["status"]
            ),
            "verification_passed": (
                validated_verification["verification_passed"]
            ),
        },
        "factor_evidence": factor_evidence,
        "contribution_ranking": contribution_ranking,
        "interpretation": interpretation,
        "limitations": limitations,
    }