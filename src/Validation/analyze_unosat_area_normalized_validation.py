"""
PHASE 9.11.4 — AREA-NORMALIZED UNOSAT SPATIAL VALIDATION

Purpose
-------
Evaluate whether observed UNOSAT flood locations are disproportionately
concentrated within susceptibility classes after accounting for the amount
of each class that was actually observable by the UNOSAT reference dataset.

This diagnostic addresses unequal spatial representation of susceptibility
classes within the external observation domain.

The analysis does NOT modify:
    - MCDA weights
    - susceptibility factors
    - classification thresholds
    - UNOSAT reference data
    - model outputs

This is a diagnostic step before formal statistical evaluation in Phase 9.11.5.

Definitions
-----------
Observed domain:
    Pixels where the UNOSAT reference raster contains either:
        1 = observed flood
        0 = observed non-flood

Unobserved:
    Pixels coded as:
        -9999

Flood enrichment ratio:

    observed flood share
    --------------------
    observed domain share

A value:
    > 1.0 = flood concentration greater than expected from observed area
    = 1.0 = flood concentration proportional to observed area
    < 1.0 = flood concentration lower than expected from observed area

Relative flood-rate ratio:

    class observed flood rate
    -------------------------
    overall observed flood rate

This provides a second normalized measure of class-level flood incidence.

Important
---------
These measures describe the spatial relationship between the susceptibility
model and the specific UNOSAT-observed flood event. They are not probability
estimates, predictive accuracy measures, or causal estimates.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import rasterio


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

OUTPUT_CSV = (
    OUTPUT_DIR
    / "unosat_area_normalized_validation.csv"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "unosat_area_normalized_validation.json"
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
# HELPER FUNCTIONS
# =============================================================================

def validate_file(path: Path, label: str) -> None:
    """Confirm that a required input file exists."""
    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found:\n{path}"
        )


def raster_metadata(path: Path) -> dict:
    """Read essential raster metadata."""
    with rasterio.open(path) as src:
        return {
            "crs": str(src.crs),
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
            "count": src.count,
        }


def transforms_match(transform_a, transform_b, tolerance=1e-9) -> bool:
    """Compare raster transforms with numerical tolerance."""
    return all(
        abs(a - b) <= tolerance
        for a, b in zip(transform_a, transform_b)
    )


def print_section(title: str) -> None:
    """Print a formatted section heading."""
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def safe_ratio(numerator: float, denominator: float) -> float:
    """Return numerator / denominator, or NaN if denominator is zero."""
    if denominator == 0:
        return float("nan")
    return numerator / denominator


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():

    print("=" * 80)
    print("PHASE 9.11.4 — AREA-NORMALIZED UNOSAT SPATIAL VALIDATION")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
    # 2. READ RASTERS
    # -------------------------------------------------------------------------

    print_section("2. RASTER COMPATIBILITY")

    with rasterio.open(SUSCEPTIBILITY_RASTER) as src:
        susceptibility = src.read(1).astype(np.float64)
        susceptibility_meta = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
        }

    with rasterio.open(CLASSIFIED_RASTER) as src:
        classified = src.read(1)
        classified_meta = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
        }

    with rasterio.open(UNOSAT_REFERENCE_RASTER) as src:
        reference = src.read(1).astype(np.float64)
        reference_meta = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": src.nodata,
        }

    spatial_checks = {
        "susceptibility_vs_classified_crs":
            susceptibility_meta["crs"] == classified_meta["crs"],

        "susceptibility_vs_reference_crs":
            susceptibility_meta["crs"] == reference_meta["crs"],

        "susceptibility_vs_classified_dimensions":
            (
                susceptibility_meta["width"] == classified_meta["width"]
                and
                susceptibility_meta["height"] == classified_meta["height"]
            ),

        "susceptibility_vs_reference_dimensions":
            (
                susceptibility_meta["width"] == reference_meta["width"]
                and
                susceptibility_meta["height"] == reference_meta["height"]
            ),

        "susceptibility_vs_classified_transform":
            transforms_match(
                susceptibility_meta["transform"],
                classified_meta["transform"]
            ),

        "susceptibility_vs_reference_transform":
            transforms_match(
                susceptibility_meta["transform"],
                reference_meta["transform"]
            ),

        "susceptibility_vs_classified_resolution":
            np.allclose(
                susceptibility_meta["resolution"],
                classified_meta["resolution"]
            ),

        "susceptibility_vs_reference_resolution":
            np.allclose(
                susceptibility_meta["resolution"],
                reference_meta["resolution"]
            ),
    }

    for check_name, passed in spatial_checks.items():
        print(
            f"{check_name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(spatial_checks.values()):
        raise ValueError(
            "Raster spatial compatibility validation failed."
        )

    print("Overall raster compatibility: PASS")

    # -------------------------------------------------------------------------
    # 3. DEFINE VALID MODEL AND OBSERVATION MASKS
    # -------------------------------------------------------------------------

    print_section("3. VALIDATION MASKS")

    model_valid = (
        np.isfinite(susceptibility)
        & (susceptibility != -9999)
        & (classified > 0)
        & (classified <= 5)
    )

    observed_domain = (
        (reference == 0)
        | (reference == 1)
    )

    common_observed = model_valid & observed_domain

    observed_flood = common_observed & (reference == 1)
    observed_nonflood = common_observed & (reference == 0)

    total_raster_cells = susceptibility.size
    valid_model_cells = int(np.count_nonzero(model_valid))
    observed_cells = int(np.count_nonzero(common_observed))
    flood_cells = int(np.count_nonzero(observed_flood))
    nonflood_cells = int(np.count_nonzero(observed_nonflood))

    print(f"Total raster cells: {total_raster_cells:,}")
    print(f"Valid MCDA cells: {valid_model_cells:,}")
    print(f"Observed validation cells: {observed_cells:,}")
    print(f"Observed flood cells: {flood_cells:,}")
    print(f"Observed non-flood cells: {nonflood_cells:,}")

    if observed_cells == 0:
        raise ValueError(
            "No observed UNOSAT validation cells were found."
        )

    if flood_cells == 0:
        raise ValueError(
            "No observed UNOSAT flood cells were found."
        )

    overall_flood_rate = flood_cells / observed_cells

    print(
        f"Overall observed flood rate: "
        f"{overall_flood_rate:.6%}"
    )

    # -------------------------------------------------------------------------
    # 4. MCDA CLASS DISTRIBUTION
    # -------------------------------------------------------------------------

    print_section("4. MCDA CLASS DISTRIBUTION")

    model_class_counts = {}

    for class_id in range(1, 6):
        count = int(
            np.count_nonzero(
                model_valid & (classified == class_id)
            )
        )

        model_class_counts[class_id] = count

        print(
            f"{CLASS_NAMES[class_id]}: "
            f"{count:,} cells"
        )

    # -------------------------------------------------------------------------
    # 5. AREA-NORMALIZED CLASS ANALYSIS
    # -------------------------------------------------------------------------

    print_section("5. AREA-NORMALIZED CLASS ANALYSIS")

    rows = []

    for class_id in range(1, 6):

        class_name = CLASS_NAMES[class_id]

        class_mask = (
            common_observed
            & (classified == class_id)
        )

        class_observed_cells = int(
            np.count_nonzero(class_mask)
        )

        class_flood_cells = int(
            np.count_nonzero(
                class_mask & (reference == 1)
            )
        )

        class_nonflood_cells = int(
            np.count_nonzero(
                class_mask & (reference == 0)
            )
        )

        model_class_cells = model_class_counts[class_id]

        observed_domain_share = safe_ratio(
            class_observed_cells,
            observed_cells
        )

        observed_flood_share = safe_ratio(
            class_flood_cells,
            flood_cells
        )

        observed_flood_rate = safe_ratio(
            class_flood_cells,
            class_observed_cells
        )

        expected_flood_cells = (
            class_observed_cells
            * overall_flood_rate
        )

        flood_enrichment_ratio = safe_ratio(
            class_flood_cells,
            expected_flood_cells
        )

        relative_flood_rate = safe_ratio(
            observed_flood_rate,
            overall_flood_rate
        )

        model_area_share = safe_ratio(
            model_class_cells,
            valid_model_cells
        )

        observation_coverage = safe_ratio(
            class_observed_cells,
            model_class_cells
        )

        observed_flood_excess = (
            class_flood_cells
            - expected_flood_cells
        )

        if flood_enrichment_ratio > 1.0:
            enrichment_interpretation = "ABOVE_EXPECTED"
        elif flood_enrichment_ratio < 1.0:
            enrichment_interpretation = "BELOW_EXPECTED"
        else:
            enrichment_interpretation = "PROPORTIONAL"

        rows.append({
            "class_id": class_id,
            "class_name": class_name,
            "model_class_cells": model_class_cells,
            "model_area_share": model_area_share,
            "observed_cells": class_observed_cells,
            "observed_domain_share": observed_domain_share,
            "observation_coverage": observation_coverage,
            "observed_flood_cells": class_flood_cells,
            "observed_nonflood_cells": class_nonflood_cells,
            "observed_flood_share": observed_flood_share,
            "observed_flood_rate": observed_flood_rate,
            "overall_observed_flood_rate": overall_flood_rate,
            "expected_flood_cells": expected_flood_cells,
            "observed_flood_excess": observed_flood_excess,
            "flood_enrichment_ratio": flood_enrichment_ratio,
            "relative_flood_rate": relative_flood_rate,
            "enrichment_interpretation": enrichment_interpretation,
        })

    class_df = pd.DataFrame(rows)

    for _, row in class_df.iterrows():

        print()
        print(f"{row['class_name']}")
        print("-" * 40)

        print(
            f"Model cells: "
            f"{int(row['model_class_cells']):,}"
        )

        print(
            f"Observed cells: "
            f"{int(row['observed_cells']):,}"
        )

        print(
            f"Observed-domain share: "
            f"{row['observed_domain_share']:.4%}"
        )

        print(
            f"Observation coverage: "
            f"{row['observation_coverage']:.4%}"
        )

        print(
            f"Observed flood cells: "
            f"{int(row['observed_flood_cells']):,}"
        )

        print(
            f"Observed flood share: "
            f"{row['observed_flood_share']:.4%}"
        )

        print(
            f"Observed flood rate: "
            f"{row['observed_flood_rate']:.4%}"
        )

        print(
            f"Expected flood cells: "
            f"{row['expected_flood_cells']:.2f}"
        )

        print(
            f"Flood enrichment ratio: "
            f"{row['flood_enrichment_ratio']:.4f}"
        )

        print(
            f"Relative flood rate: "
            f"{row['relative_flood_rate']:.4f}"
        )

        print(
            f"Interpretation: "
            f"{row['enrichment_interpretation']}"
        )

    # -------------------------------------------------------------------------
    # 6. GROUPED ANALYSIS
    # -------------------------------------------------------------------------

    print_section("6. LOWER-THREE VS HIGH+VERY-HIGH ANALYSIS")

    grouped_definitions = {
        "Very Low + Low + Moderate": [1, 2, 3],
        "High + Very High": [4, 5],
    }

    grouped_rows = []

    for group_name, class_ids in grouped_definitions.items():

        group_class_mask = np.isin(
            classified,
            class_ids
        )

        group_observed_mask = (
            common_observed
            & group_class_mask
        )

        group_flood_mask = (
            observed_flood
            & group_class_mask
        )

        group_observed_cells = int(
            np.count_nonzero(group_observed_mask)
        )

        group_flood_cells = int(
            np.count_nonzero(group_flood_mask)
        )

        group_nonflood_cells = int(
            np.count_nonzero(
                group_observed_mask
                & (reference == 0)
            )
        )

        group_domain_share = safe_ratio(
            group_observed_cells,
            observed_cells
        )

        group_flood_share = safe_ratio(
            group_flood_cells,
            flood_cells
        )

        group_flood_rate = safe_ratio(
            group_flood_cells,
            group_observed_cells
        )

        expected_flood_cells = (
            group_observed_cells
            * overall_flood_rate
        )

        enrichment_ratio = safe_ratio(
            group_flood_cells,
            expected_flood_cells
        )

        relative_flood_rate = safe_ratio(
            group_flood_rate,
            overall_flood_rate
        )

        grouped_rows.append({
            "group_name": group_name,
            "observed_cells": group_observed_cells,
            "observed_domain_share": group_domain_share,
            "observed_flood_cells": group_flood_cells,
            "observed_nonflood_cells": group_nonflood_cells,
            "observed_flood_share": group_flood_share,
            "observed_flood_rate": group_flood_rate,
            "expected_flood_cells": expected_flood_cells,
            "flood_enrichment_ratio": enrichment_ratio,
            "relative_flood_rate": relative_flood_rate,
        })

        print()
        print(group_name)
        print("-" * 40)

        print(
            f"Observed cells: "
            f"{group_observed_cells:,}"
        )

        print(
            f"Observed-domain share: "
            f"{group_domain_share:.4%}"
        )

        print(
            f"Observed flood cells: "
            f"{group_flood_cells:,}"
        )

        print(
            f"Observed flood share: "
            f"{group_flood_share:.4%}"
        )

        print(
            f"Observed flood rate: "
            f"{group_flood_rate:.4%}"
        )

        print(
            f"Expected flood cells: "
            f"{expected_flood_cells:.2f}"
        )

        print(
            f"Flood enrichment ratio: "
            f"{enrichment_ratio:.4f}"
        )

        print(
            f"Relative flood rate: "
            f"{relative_flood_rate:.4f}"
        )

    grouped_df = pd.DataFrame(grouped_rows)

    # -------------------------------------------------------------------------
    # 7. CONTINUOUS SUSCEPTIBILITY ANALYSIS
    # -------------------------------------------------------------------------

    print_section("7. CONTINUOUS SUSCEPTIBILITY AREA-NORMALIZED ANALYSIS")

    observed_scores = susceptibility[common_observed]

    score_percentiles = {
        "minimum": float(np.min(observed_scores)),
        "p05": float(np.percentile(observed_scores, 5)),
        "p25": float(np.percentile(observed_scores, 25)),
        "median": float(np.median(observed_scores)),
        "p75": float(np.percentile(observed_scores, 75)),
        "p95": float(np.percentile(observed_scores, 95)),
        "maximum": float(np.max(observed_scores)),
        "mean": float(np.mean(observed_scores)),
    }

    flood_scores = susceptibility[observed_flood]
    nonflood_scores = susceptibility[observed_nonflood]

    continuous_summary = {
        "observed_domain_score_distribution": score_percentiles,
        "flood_score_mean": float(np.mean(flood_scores)),
        "flood_score_median": float(np.median(flood_scores)),
        "nonflood_score_mean": float(np.mean(nonflood_scores)),
        "nonflood_score_median": float(np.median(nonflood_scores)),
        "mean_difference_flood_minus_nonflood": float(
            np.mean(flood_scores)
            - np.mean(nonflood_scores)
        ),
        "median_difference_flood_minus_nonflood": float(
            np.median(flood_scores)
            - np.median(nonflood_scores)
        ),
    }

    print(
        f"Observed-domain mean susceptibility: "
        f"{score_percentiles['mean']:.6f}"
    )

    print(
        f"Observed-domain median susceptibility: "
        f"{score_percentiles['median']:.6f}"
    )

    print(
        f"Flood mean susceptibility: "
        f"{continuous_summary['flood_score_mean']:.6f}"
    )

    print(
        f"Non-flood mean susceptibility: "
        f"{continuous_summary['nonflood_score_mean']:.6f}"
    )

    print(
        f"Mean difference (flood - non-flood): "
        f"{continuous_summary['mean_difference_flood_minus_nonflood']:.6f}"
    )

    print(
        f"Median difference (flood - non-flood): "
        f"{continuous_summary['median_difference_flood_minus_nonflood']:.6f}"
    )

    # -------------------------------------------------------------------------
    # 8. DIAGNOSTIC INTERPRETATION
    # -------------------------------------------------------------------------

    print_section("8. DIAGNOSTIC INTERPRETATION")

    enrichment_values = class_df[
        "flood_enrichment_ratio"
    ].to_numpy()

    max_enrichment_class = class_df.loc[
        class_df["flood_enrichment_ratio"].idxmax()
    ]

    min_enrichment_class = class_df.loc[
        class_df["flood_enrichment_ratio"].idxmin()
    ]

    high_very_high = grouped_df[
        grouped_df["group_name"] == "High + Very High"
    ].iloc[0]

    lower_three = grouped_df[
        grouped_df["group_name"] == "Very Low + Low + Moderate"
    ].iloc[0]

    print(
        f"Highest flood enrichment: "
        f"{max_enrichment_class['class_name']} "
        f"({max_enrichment_class['flood_enrichment_ratio']:.4f})"
    )

    print(
        f"Lowest flood enrichment: "
        f"{min_enrichment_class['class_name']} "
        f"({min_enrichment_class['flood_enrichment_ratio']:.4f})"
    )

    print(
        f"High + Very High enrichment: "
        f"{high_very_high['flood_enrichment_ratio']:.4f}"
    )

    print(
        f"Very Low + Low + Moderate enrichment: "
        f"{lower_three['flood_enrichment_ratio']:.4f}"
    )

    # -------------------------------------------------------------------------
    # 9. DIAGNOSTIC STATUS
    # -------------------------------------------------------------------------

    high_vh_enrichment = float(
        high_very_high["flood_enrichment_ratio"]
    )

    lower_three_enrichment = float(
        lower_three["flood_enrichment_ratio"]
    )

    if high_vh_enrichment > 1.0:
        grouped_interpretation = (
            "HIGH_VERY_HIGH_ABOVE_EXPECTED"
        )
    elif high_vh_enrichment < 1.0:
        grouped_interpretation = (
            "HIGH_VERY_HIGH_BELOW_EXPECTED"
        )
    else:
        grouped_interpretation = (
            "HIGH_VERY_HIGH_PROPORTIONAL"
        )

    if (
        np.all(enrichment_values > 0)
        and np.isfinite(enrichment_values).all()
    ):
        diagnostic_status = (
            "AREA_NORMALIZED_DIAGNOSTIC_COMPLETED"
        )
    else:
        diagnostic_status = (
            "AREA_NORMALIZED_DIAGNOSTIC_REQUIRES_REVIEW"
        )

    # -------------------------------------------------------------------------
    # 10. SAVE CSV
    # -------------------------------------------------------------------------

    print_section("10. OUTPUT")

    class_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    print(
        f"Class-level CSV written:\n"
        f"{OUTPUT_CSV}"
    )

    # -------------------------------------------------------------------------
    # 11. SAVE JSON
    # -------------------------------------------------------------------------

    json_payload = {
        "phase": "9.11.4",
        "analysis": "Area-Normalized UNOSAT Spatial Validation",

        "purpose": (
            "Assess whether observed UNOSAT flood locations are "
            "disproportionately concentrated within susceptibility "
            "classes after accounting for unequal observation coverage."
        ),

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

        "spatial_validation": {
            "total_raster_cells": total_raster_cells,
            "valid_model_cells": valid_model_cells,
            "observed_validation_cells": observed_cells,
            "observed_flood_cells": flood_cells,
            "observed_nonflood_cells": nonflood_cells,
            "overall_observed_flood_rate": overall_flood_rate,
        },

        "class_results": class_df.to_dict(
            orient="records"
        ),

        "group_results": grouped_df.to_dict(
            orient="records"
        ),

        "continuous_analysis": continuous_summary,

        "diagnostic_interpretation": {
            "highest_enrichment_class": (
                max_enrichment_class["class_name"]
            ),
            "highest_enrichment_ratio": float(
                max_enrichment_class[
                    "flood_enrichment_ratio"
                ]
            ),
            "lowest_enrichment_class": (
                min_enrichment_class["class_name"]
            ),
            "lowest_enrichment_ratio": float(
                min_enrichment_class[
                    "flood_enrichment_ratio"
                ]
            ),
            "high_very_high_interpretation": (
                grouped_interpretation
            ),
            "high_very_high_enrichment_ratio": (
                high_vh_enrichment
            ),
            "lower_three_enrichment_ratio": (
                lower_three_enrichment
            ),
        },

        "interpretation_notes": [
            (
                "Flood enrichment ratio compares observed flood "
                "share with observed-domain area share."
            ),
            (
                "A ratio above 1 indicates more observed flood "
                "than expected from the amount of observed area "
                "represented by that class."
            ),
            (
                "A ratio below 1 indicates less observed flood "
                "than expected from the represented observed area."
            ),
            (
                "Relative flood rate compares each class flood "
                "rate with the overall observed flood rate."
            ),
            (
                "These measures are descriptive diagnostics and "
                "do not establish statistical significance."
            ),
            (
                "The UNOSAT product represents one observed flood "
                "event and should not be interpreted as a general "
                "flood probability surface."
            ),
            (
                "No MCDA weights, factors, thresholds, or reference "
                "data were modified during this analysis."
            ),
        ],

        "diagnostic_status": diagnostic_status,
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            json_payload,
            f,
            indent=2
        )

    print(
        f"JSON summary written:\n"
        f"{OUTPUT_JSON}"
    )

    print()
    print("=" * 80)
    print(diagnostic_status)
    print("=" * 80)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()