"""
PHASE 9.11.5 — STATISTICAL EVALUATION OF UNOSAT EXTERNAL VALIDATION

Purpose
-------
Statistically evaluate the relationship between the frozen MCDA flood
susceptibility surface and the UNOSAT-observed flood reference for
1 May 2024.

Analyses
--------
1. Input and raster spatial-compatibility validation
2. Five-class by two-category contingency table
3. Pearson chi-square test of association
4. Cramer's V effect size
5. Class-level flood rates and relative flood rates
6. Mann-Whitney U comparison of continuous susceptibility scores
7. Spearman rank correlation between susceptibility and flood status
8. ROC curve and AUC, including direction of discrimination
9. Explicit reporting of spatial-dependence and temporal-generalization
   limitations

Important scientific limitations
---------------------------------
Raster cells are spatially dependent. Conventional p-values from cell-level
tests may be overly optimistic because neighbouring pixels are not
independent observations.

This script therefore reports descriptive results and effect sizes alongside
conventional test statistics. It does not interpret cell-level p-values as
definitive evidence of generalizable predictive performance.

The analysis evaluates one UNOSAT-observed event. It does not estimate
general flood probability and does not establish performance across other
events or years.

No model weights, factors, thresholds, rasters, or reference data are changed.
"""

from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import rasterio

from scipy.stats import (
    chi2_contingency,
    mannwhitneyu,
    spearmanr,
)

from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
)


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUSCEPTIBILITY_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility.tif"
)

CLASSIFIED_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility_classified.tif"
)

UNOSAT_REFERENCE_RASTER = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
    / "unosat_flood_reference_aligned.tif"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
)

CLASS_RESULTS_CSV = (
    OUTPUT_DIR
    / "unosat_statistical_class_results.csv"
)

CONTINGENCY_CSV = (
    OUTPUT_DIR
    / "unosat_statistical_contingency_table.csv"
)

SUMMARY_JSON = (
    OUTPUT_DIR
    / "unosat_statistical_evaluation_summary.json"
)

ROC_CSV = (
    OUTPUT_DIR
    / "unosat_statistical_roc_curve.csv"
)


# =============================================================================
# CLASS DEFINITIONS
# =============================================================================

CLASS_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# =============================================================================
# HELPERS
# =============================================================================

def validate_file(path: Path, description: str) -> None:
    """Raise an informative error when an input file is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"{description} not found:\n{path}"
        )


def transforms_match(a, b, tolerance=1e-9) -> bool:
    """Compare affine transforms using numerical tolerance."""
    return all(
        abs(x - y) <= tolerance
        for x, y in zip(a, b)
    )


def safe_ratio(numerator, denominator):
    """Return a ratio or None if the denominator is zero."""
    if denominator == 0:
        return None

    return float(numerator / denominator)


def json_safe(value):
    """Convert NumPy and non-finite values to JSON-safe values."""
    if isinstance(value, dict):
        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(v)
            for v in value
        ]

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            return None

        return float(value)

    if isinstance(value, (np.bool_, bool)):
        return bool(value)

    return value


def print_section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def classify_auc_direction(auc):
    """
    Describe AUC direction without assigning a model-quality verdict.

    AUC < 0.5 means the score tends to rank observed flood pixels below
    observed non-flood pixels in this reference sample.
    """
    if auc is None:
        return "UNAVAILABLE"

    if auc < 0.5:
        return "REVERSE_DIRECTION_IN_THIS_REFERENCE_SAMPLE"

    if auc > 0.5:
        return "POSITIVE_DISCRIMINATION_IN_THIS_REFERENCE_SAMPLE"

    return "NO_DISCRIMINATION_IN_THIS_REFERENCE_SAMPLE"


# =============================================================================
# MAIN
# =============================================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 80)
    print("PHASE 9.11.5 — UNOSAT STATISTICAL EVALUATION")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. INPUT VALIDATION
    # -------------------------------------------------------------------------

    print_section("1. INPUT VALIDATION")

    validate_file(
        SUSCEPTIBILITY_RASTER,
        "Continuous susceptibility raster"
    )

    validate_file(
        CLASSIFIED_RASTER,
        "Classified susceptibility raster"
    )

    validate_file(
        UNOSAT_REFERENCE_RASTER,
        "UNOSAT reference raster"
    )

    print("Continuous susceptibility raster: PASS")
    print("Classified susceptibility raster: PASS")
    print("UNOSAT reference raster: PASS")

    # -------------------------------------------------------------------------
    # 2. READ INPUTS AND VALIDATE GRID COMPATIBILITY
    # -------------------------------------------------------------------------

    print_section("2. RASTER COMPATIBILITY")

    with rasterio.open(SUSCEPTIBILITY_RASTER) as src:
        susceptibility = src.read(1).astype(
            np.float64,
            copy=True
        )

        susceptibility_meta = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
        }

    with rasterio.open(CLASSIFIED_RASTER) as src:
        classified = src.read(1).copy()

        classified_meta = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
        }

    with rasterio.open(UNOSAT_REFERENCE_RASTER) as src:
        reference = src.read(1).astype(
            np.float64,
            copy=True
        )

        reference_meta = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
        }

    spatial_checks = {
        "CRS_matches": (
            susceptibility_meta["crs"]
            == classified_meta["crs"]
            == reference_meta["crs"]
        ),

        "dimensions_match": (
            susceptibility_meta["width"]
            == classified_meta["width"]
            == reference_meta["width"]
            and
            susceptibility_meta["height"]
            == classified_meta["height"]
            == reference_meta["height"]
        ),

        "transforms_match": (
            transforms_match(
                susceptibility_meta["transform"],
                classified_meta["transform"]
            )
            and
            transforms_match(
                susceptibility_meta["transform"],
                reference_meta["transform"]
            )
        ),

        "resolutions_match": (
            np.allclose(
                susceptibility_meta["resolution"],
                classified_meta["resolution"]
            )
            and
            np.allclose(
                susceptibility_meta["resolution"],
                reference_meta["resolution"]
            )
        ),
    }

    for name, passed in spatial_checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(spatial_checks.values()):
        raise ValueError(
            "Spatial compatibility checks failed. "
            "Statistical evaluation stopped."
        )

    print("Overall raster compatibility: PASS")

    # -------------------------------------------------------------------------
    # 3. DEFINE OBSERVED VALIDATION SAMPLE
    # -------------------------------------------------------------------------

    print_section("3. DEFINE VALIDATION SAMPLE")

    model_valid = (
        np.isfinite(susceptibility)
        & (susceptibility != -9999)
        & (classified >= 1)
        & (classified <= 5)
    )

    reference_observed = (
        (reference == 0)
        | (reference == 1)
    )

    common_mask = (
        model_valid
        & reference_observed
    )

    y = reference[common_mask].astype(np.uint8)
    scores = susceptibility[common_mask]
    classes = classified[common_mask].astype(np.uint8)

    total_cells = int(susceptibility.size)
    valid_model_cells = int(np.count_nonzero(model_valid))
    observed_cells = int(common_mask.sum())
    flood_cells = int(np.count_nonzero(y == 1))
    nonflood_cells = int(np.count_nonzero(y == 0))

    if observed_cells == 0:
        raise ValueError(
            "No common observed validation cells were found."
        )

    if flood_cells == 0 or nonflood_cells == 0:
        raise ValueError(
            "Both observed flood and non-flood cells are required."
        )

    overall_flood_rate = flood_cells / observed_cells

    print(f"Total raster cells: {total_cells:,}")
    print(f"Valid model cells: {valid_model_cells:,}")
    print(f"Observed validation cells: {observed_cells:,}")
    print(f"Observed flood cells: {flood_cells:,}")
    print(f"Observed non-flood cells: {nonflood_cells:,}")
    print(f"Overall observed flood rate: {overall_flood_rate:.6%}")

    # -------------------------------------------------------------------------
    # 4. CONTINGENCY TABLE
    # -------------------------------------------------------------------------

    print_section("4. SUSCEPTIBILITY CLASS BY FLOOD STATUS")

    contingency = np.zeros(
        (5, 2),
        dtype=np.int64
    )

    class_rows = []

    for class_id in range(1, 6):

        in_class = classes == class_id

        class_total = int(np.count_nonzero(in_class))
        class_flood = int(
            np.count_nonzero(in_class & (y == 1))
        )
        class_nonflood = int(
            np.count_nonzero(in_class & (y == 0))
        )

        contingency[class_id - 1, 0] = class_flood
        contingency[class_id - 1, 1] = class_nonflood

        class_rate = safe_ratio(
            class_flood,
            class_total
        )

        relative_rate = safe_ratio(
            class_rate,
            overall_flood_rate
        )

        expected_flood = class_total * overall_flood_rate

        enrichment = safe_ratio(
            class_flood,
            expected_flood
        )

        class_rows.append({
            "class_id": class_id,
            "class_name": CLASS_NAMES[class_id],
            "observed_cells": class_total,
            "observed_flood_cells": class_flood,
            "observed_nonflood_cells": class_nonflood,
            "observed_flood_rate": class_rate,
            "overall_observed_flood_rate": overall_flood_rate,
            "relative_flood_rate": relative_rate,
            "expected_flood_cells_under_overall_rate": expected_flood,
            "flood_enrichment_ratio": enrichment,
        })

        print(
            f"{CLASS_NAMES[class_id]:12s} | "
            f"Flood: {class_flood:7,d} | "
            f"Non-flood: {class_nonflood:7,d} | "
            f"Flood rate: {class_rate:.4%}"
        )

    class_df = pd.DataFrame(class_rows)

    contingency_df = pd.DataFrame(
        contingency,
        columns=[
            "observed_flood",
            "observed_nonflood"
        ],
        index=[
            CLASS_NAMES[i]
            for i in range(1, 6)
        ]
    )

    contingency_df.index.name = "susceptibility_class"

    contingency_df.to_csv(
        CONTINGENCY_CSV
    )

    print(f"\nContingency table saved: {CONTINGENCY_CSV}")

    # -------------------------------------------------------------------------
    # 5. CHI-SQUARE AND CRAMER'S V
    # -------------------------------------------------------------------------

    print_section("5. CHI-SQUARE TEST AND CRAMER'S V")

    chi2, chi2_p, degrees_freedom, expected = (
        chi2_contingency(
            contingency,
            correction=False
        )
    )

    expected_df = pd.DataFrame(
        expected,
        index=[
            CLASS_NAMES[i]
            for i in range(1, 6)
        ],
        columns=[
            "expected_flood",
            "expected_nonflood"
        ]
    )

    minimum_expected = float(expected.min())

    n = int(contingency.sum())

    # For a 5 x 2 table, min(rows - 1, columns - 1) = 1.
    cramer_v = float(
        np.sqrt(
            chi2
            / (
                n
                * min(
                    contingency.shape[0] - 1,
                    contingency.shape[1] - 1
                )
            )
        )
    )

    print(f"Chi-square statistic: {chi2:.6f}")
    print(f"Degrees of freedom: {degrees_freedom}")
    print(f"Conventional p-value: {chi2_p:.6e}")
    print(f"Cramer's V: {cramer_v:.6f}")
    print(f"Minimum expected cell count: {minimum_expected:.2f}")

    if minimum_expected < 5:
        chi2_assumption_status = (
            "REVIEW_EXPECTED_COUNTS_BELOW_5"
        )
    else:
        chi2_assumption_status = (
            "EXPECTED_COUNTS_MEET_COMMON_MINIMUM_RULE"
        )

    print(
        "Expected-count check: "
        f"{chi2_assumption_status}"
    )

    # -------------------------------------------------------------------------
    # 6. MANN-WHITNEY U TEST
    # -------------------------------------------------------------------------

    print_section("6. CONTINUOUS SCORE COMPARISON")

    flood_scores = scores[y == 1]
    nonflood_scores = scores[y == 0]

    with warnings.catch_warnings():
        warnings.simplefilter(
            "ignore",
            category=RuntimeWarning
        )

        mw_result = mannwhitneyu(
            flood_scores,
            nonflood_scores,
            alternative="two-sided",
            method="asymptotic"
        )

    mann_whitney_u = float(mw_result.statistic)
    mann_whitney_p = float(mw_result.pvalue)

    flood_mean = float(np.mean(flood_scores))
    nonflood_mean = float(np.mean(nonflood_scores))

    flood_median = float(np.median(flood_scores))
    nonflood_median = float(np.median(nonflood_scores))

    mean_difference = flood_mean - nonflood_mean
    median_difference = flood_median - nonflood_median

    # Rank-biserial correlation derived from the Mann-Whitney U statistic.
    # With U defined for the flood group:
    # r_rb = 2U / (n_flood*n_nonflood) - 1
    #
    # This direction means positive values indicate flood scores tend
    # to be higher; negative values indicate they tend to be lower.
    denominator = len(flood_scores) * len(nonflood_scores)

    rank_biserial = (
        2.0 * mann_whitney_u / denominator
    ) - 1.0

    print(f"Flood mean score: {flood_mean:.6f}")
    print(f"Non-flood mean score: {nonflood_mean:.6f}")
    print(f"Flood median score: {flood_median:.6f}")
    print(f"Non-flood median score: {nonflood_median:.6f}")
    print(f"Mean difference (flood - non-flood): {mean_difference:.6f}")
    print(f"Median difference (flood - non-flood): {median_difference:.6f}")
    print(f"Mann-Whitney U: {mann_whitney_u:.6f}")
    print(f"Conventional p-value: {mann_whitney_p:.6e}")
    print(f"Rank-biserial correlation: {rank_biserial:.6f}")

    # -------------------------------------------------------------------------
    # 7. SPEARMAN CORRELATION
    # -------------------------------------------------------------------------

    print_section("7. SPEARMAN CORRELATION")

    with warnings.catch_warnings():
        warnings.simplefilter(
            "ignore",
            category=RuntimeWarning
        )

        spearman_result = spearmanr(
            scores,
            y
        )

    spearman_rho = float(spearman_result.statistic)
    spearman_p = float(spearman_result.pvalue)

    print(f"Spearman rho: {spearman_rho:.6f}")
    print(f"Conventional p-value: {spearman_p:.6e}")

    if spearman_rho < 0:
        spearman_direction = "NEGATIVE"
    elif spearman_rho > 0:
        spearman_direction = "POSITIVE"
    else:
        spearman_direction = "NO_MONOTONIC_DIRECTION"

    print(f"Direction: {spearman_direction}")

    # -------------------------------------------------------------------------
    # 8. ROC AND AUC
    # -------------------------------------------------------------------------

    print_section("8. ROC CURVE AND AUC")

    auc = float(
        roc_auc_score(
            y,
            scores
        )
    )

    false_positive_rate, true_positive_rate, thresholds = (
        roc_curve(
            y,
            scores,
            drop_intermediate=False
        )
    )

    roc_df = pd.DataFrame({
        "false_positive_rate": false_positive_rate,
        "true_positive_rate": true_positive_rate,
        "threshold": thresholds,
    })

    roc_df.to_csv(
        ROC_CSV,
        index=False
    )

    auc_direction = classify_auc_direction(auc)

    print(f"ROC AUC: {auc:.6f}")
    print(f"AUC interpretation: {auc_direction}")
    print(f"ROC curve saved: {ROC_CSV}")

    # -------------------------------------------------------------------------
    # 9. STATISTICAL INTERPRETATION AND LIMITATIONS
    # -------------------------------------------------------------------------

    print_section("9. INTERPRETATION AND LIMITATIONS")

    print(
        "Chi-square assesses association, not causal influence "
        "or predictive accuracy."
    )

    print(
        "Cramer's V quantifies the strength of the categorical "
        "association."
    )

    print(
        "Mann-Whitney compares score distributions; it does not "
        "require normally distributed scores."
    )

    print(
        "Spearman describes the direction and strength of a "
        "monotonic association."
    )

    print(
        "AUC below 0.5 indicates reverse-direction discrimination "
        "in this reference sample."
    )

    print(
        "IMPORTANT: Raster cells may be spatially dependent. "
        "Conventional p-values may therefore overstate the amount "
        "of independent evidence."
    )

    print(
        "IMPORTANT: These results concern one UNOSAT-observed "
        "flood event and do not establish generalization to other events."
    )

    print(
        "No weights, model factors, classification thresholds, "
        "or reference data were changed."
    )

    # -------------------------------------------------------------------------
    # 10. SAVE CLASS-LEVEL RESULTS
    # -------------------------------------------------------------------------

    print_section("10. SAVE OUTPUTS")

    class_df.to_csv(
        CLASS_RESULTS_CSV,
        index=False
    )

    print(f"Class results CSV: {CLASS_RESULTS_CSV}")
    print(f"Contingency CSV: {CONTINGENCY_CSV}")
    print(f"ROC CSV: {ROC_CSV}")

    # -------------------------------------------------------------------------
    # 11. JSON SUMMARY
    # -------------------------------------------------------------------------

    summary = {
        "phase": "9.11.5",
        "analysis": "UNOSAT Statistical Evaluation",

        "validation_event": {
            "reference": "UNOSAT Product 3834",
            "observation_date": "2024-05-01",
            "interpretation_scope": (
                "Spatial comparison with one observed flood event"
            ),
        },

        "inputs": {
            "continuous_susceptibility": str(
                SUSCEPTIBILITY_RASTER
            ),
            "classified_susceptibility": str(
                CLASSIFIED_RASTER
            ),
            "unosat_reference": str(
                UNOSAT_REFERENCE_RASTER
            ),
        },

        "sample": {
            "total_raster_cells": total_cells,
            "valid_model_cells": valid_model_cells,
            "observed_validation_cells": observed_cells,
            "observed_flood_cells": flood_cells,
            "observed_nonflood_cells": nonflood_cells,
            "overall_observed_flood_rate": overall_flood_rate,
        },

        "chi_square": {
            "statistic": float(chi2),
            "degrees_of_freedom": int(degrees_freedom),
            "conventional_p_value": float(chi2_p),
            "cramers_v": cramer_v,
            "minimum_expected_cell_count": minimum_expected,
            "expected_count_assessment": chi2_assumption_status,
        },

        "mann_whitney": {
            "u_statistic": mann_whitney_u,
            "conventional_p_value": mann_whitney_p,
            "flood_mean": flood_mean,
            "nonflood_mean": nonflood_mean,
            "flood_median": flood_median,
            "nonflood_median": nonflood_median,
            "mean_difference_flood_minus_nonflood": mean_difference,
            "median_difference_flood_minus_nonflood": median_difference,
            "rank_biserial_correlation": float(rank_biserial),
        },

        "spearman": {
            "rho": spearman_rho,
            "conventional_p_value": spearman_p,
            "direction": spearman_direction,
        },

        "roc_auc": {
            "auc": auc,
            "directional_interpretation": auc_direction,
            "roc_curve_csv": str(ROC_CSV),
        },

        "class_results": class_df.to_dict(
            orient="records"
        ),

        "spatial_dependence_warning": (
            "Conventional cell-level p-values assume independent "
            "observations or rely on approximations that may not account "
            "for spatial autocorrelation. Raster cells may be dependent. "
            "Interpret p-values cautiously; consider spatial block "
            "resampling or independent event validation for stronger "
            "generalization claims."
        ),

        "generalization_warning": (
            "This is an external comparison against one observed event. "
            "It does not establish predictive performance across other "
            "events, years, or rainfall conditions."
        ),

        "model_integrity": {
            "model_modified": False,
            "weights_modified": False,
            "classification_thresholds_modified": False,
            "reference_data_modified": False,
        },

        "outputs": {
            "class_results_csv": str(CLASS_RESULTS_CSV),
            "contingency_csv": str(CONTINGENCY_CSV),
            "roc_curve_csv": str(ROC_CSV),
            "summary_json": str(SUMMARY_JSON),
        },
    }

    with open(
        SUMMARY_JSON,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            json_safe(summary),
            file,
            indent=2,
            allow_nan=False
        )

    print(f"JSON summary: {SUMMARY_JSON}")

    print()
    print("=" * 80)
    print("PHASE_9_11_5_STATISTICAL_EVALUATION_COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()