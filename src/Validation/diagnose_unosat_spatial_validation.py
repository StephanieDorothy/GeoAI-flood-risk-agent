"""
Phase 9.11.4 — Diagnostic Investigation of UNOSAT Spatial Validation

Purpose
-------
Investigate the spatial composition of the independent UNOSAT
validation domain relative to the MCDA flood-susceptibility model.

This diagnostic is performed after the initial Phase 9.11.4
spatial validation produced an unexpected weak negative association
between continuous susceptibility and observed UNOSAT flooding.

The purpose is NOT to modify the model.

The diagnostic evaluates whether the independent observation domain
intersects the five susceptibility classes unevenly and whether this
spatial sampling structure may influence class-based validation
statistics.

Analyses
--------
1. Input validation
2. Raster compatibility
3. Valid MCDA modelling footprint
4. UNOSAT observed footprint
5. Representation of each susceptibility class in the MCDA model
6. Representation of each susceptibility class in the UNOSAT domain
7. Observation coverage by susceptibility class
8. Observed flood distribution by susceptibility class
9. Flood concentration relative to model-area representation
10. Continuous susceptibility distributions
11. High + Very High vs Low + Moderate representation
12. Spatial-validation diagnostic interpretation

Reference raster values:
    1      = observed flood
    0      = observed non-flood
    -9999  = unobserved

MCDA classification:
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High

CRS:
    EPSG:32737

Important
---------
This diagnostic does not establish predictive accuracy.

It is intended to determine whether the observed validation domain
has an uneven spatial representation of the susceptibility classes.

No model weights, thresholds, factors, or reference data are changed.

Author
------
GeoAI Flood Risk Decision Agent
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MCDA_CONTINUOUS = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility.tif"
)

MCDA_CLASSIFIED = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility_classified.tif"
)

UNOSAT_REFERENCE = (
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


# ---------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------

EXPECTED_CRS = "EPSG:32737"

REFERENCE_FLOOD = 1
REFERENCE_NON_FLOOD = 0
REFERENCE_NODATA = -9999

CLASS_LABELS = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# ---------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------

def json_safe(value):
    """
    Convert NumPy/Pandas values to JSON-compatible Python values.
    """

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if pd.isna(value):
        return None

    return value


def raster_metadata(path: Path) -> dict:
    """
    Read important raster metadata.
    """

    with rasterio.open(path) as src:

        return {
            "crs": src.crs.to_string() if src.crs else None,
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
            "transform": tuple(src.transform),
            "resolution": tuple(src.res),
            "bounds": tuple(src.bounds),
        }


def transforms_match(
    transform_a,
    transform_b,
    tolerance=1e-9,
):
    """
    Compare affine transforms within numerical tolerance.
    """

    return all(
        abs(float(a) - float(b)) <= tolerance
        for a, b in zip(transform_a, transform_b)
    )


def print_check(label: str, passed: bool):
    """
    Print a standardized PASS/FAIL result.
    """

    status = "PASS" if passed else "FAIL"
    print(f"{label}: {status}")


def calculate_quantiles(values: np.ndarray) -> dict:
    """
    Calculate selected distribution statistics.
    """

    values = values.astype(np.float64)

    return {
        "count": int(values.size),
        "min": float(np.min(values)),
        "p05": float(np.percentile(values, 5)),
        "p25": float(np.percentile(values, 25)),
        "median": float(np.median(values)),
        "p75": float(np.percentile(values, 75)),
        "p95": float(np.percentile(values, 95)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
    }


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 80)
    print("PHASE 9.11.4 — UNOSAT SPATIAL VALIDATION DIAGNOSTIC")
    print("=" * 80)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------------------
    # 1. INPUT VALIDATION
    # -----------------------------------------------------------------

    print("\n1. INPUT VALIDATION")
    print("-" * 80)

    input_paths = {
        "MCDA continuous susceptibility": MCDA_CONTINUOUS,
        "MCDA classified susceptibility": MCDA_CLASSIFIED,
        "UNOSAT aligned reference": UNOSAT_REFERENCE,
    }

    all_inputs_exist = True

    for label, path in input_paths.items():

        exists = path.exists()

        print(f"{label}:")
        print(f"  {path}")
        print(
            f"  Exists: "
            f"{'PASS' if exists else 'FAIL'}"
        )

        if not exists:
            all_inputs_exist = False

    if not all_inputs_exist:

        raise FileNotFoundError(
            "One or more required diagnostic inputs are missing."
        )

    # -----------------------------------------------------------------
    # 2. METADATA
    # -----------------------------------------------------------------

    print("\n2. RASTER METADATA")
    print("-" * 80)

    continuous_meta = raster_metadata(
        MCDA_CONTINUOUS
    )

    classified_meta = raster_metadata(
        MCDA_CLASSIFIED
    )

    reference_meta = raster_metadata(
        UNOSAT_REFERENCE
    )

    print("MCDA continuous:")
    print(f"  CRS: {continuous_meta['crs']}")
    print(
        f"  Dimensions: "
        f"{continuous_meta['width']} x "
        f"{continuous_meta['height']}"
    )
    print(
        f"  Resolution: "
        f"{continuous_meta['resolution']}"
    )

    print("\nMCDA classified:")
    print(f"  CRS: {classified_meta['crs']}")
    print(
        f"  Dimensions: "
        f"{classified_meta['width']} x "
        f"{classified_meta['height']}"
    )
    print(
        f"  Resolution: "
        f"{classified_meta['resolution']}"
    )

    print("\nUNOSAT reference:")
    print(f"  CRS: {reference_meta['crs']}")
    print(
        f"  Dimensions: "
        f"{reference_meta['width']} x "
        f"{reference_meta['height']}"
    )
    print(
        f"  Resolution: "
        f"{reference_meta['resolution']}"
    )

    # -----------------------------------------------------------------
    # 3. SPATIAL COMPATIBILITY
    # -----------------------------------------------------------------

    print("\n3. SPATIAL COMPATIBILITY")
    print("-" * 80)

    crs_pass = (
        continuous_meta["crs"] == EXPECTED_CRS
        and classified_meta["crs"] == EXPECTED_CRS
        and reference_meta["crs"] == EXPECTED_CRS
    )

    dimensions_pass = (
        continuous_meta["width"]
        == classified_meta["width"]
        == reference_meta["width"]
        and
        continuous_meta["height"]
        == classified_meta["height"]
        == reference_meta["height"]
    )

    transform_pass = (
        transforms_match(
            continuous_meta["transform"],
            classified_meta["transform"],
        )
        and
        transforms_match(
            continuous_meta["transform"],
            reference_meta["transform"],
        )
    )

    resolution_pass = (
        np.allclose(
            continuous_meta["resolution"],
            classified_meta["resolution"],
            rtol=0,
            atol=1e-9,
        )
        and
        np.allclose(
            continuous_meta["resolution"],
            reference_meta["resolution"],
            rtol=0,
            atol=1e-9,
        )
    )

    print_check(
        "CRS",
        crs_pass,
    )

    print_check(
        "Dimensions",
        dimensions_pass,
    )

    print_check(
        "Affine transform",
        transform_pass,
    )

    print_check(
        "Resolution",
        resolution_pass,
    )

    if not all(
        [
            crs_pass,
            dimensions_pass,
            transform_pass,
            resolution_pass,
        ]
    ):

        raise ValueError(
            "Raster compatibility failed."
        )

    # -----------------------------------------------------------------
    # 4. READ ARRAYS
    # -----------------------------------------------------------------

    print("\n4. READING RASTERS")
    print("-" * 80)

    with rasterio.open(MCDA_CONTINUOUS) as src:
        continuous = src.read(1)

    with rasterio.open(MCDA_CLASSIFIED) as src:
        classified = src.read(1)

    with rasterio.open(UNOSAT_REFERENCE) as src:
        reference = src.read(1)

    print(
        f"Continuous shape: "
        f"{continuous.shape}"
    )

    print(
        f"Classified shape: "
        f"{classified.shape}"
    )

    print(
        f"Reference shape: "
        f"{reference.shape}"
    )

    # -----------------------------------------------------------------
    # 5. BUILD MASKS
    # -----------------------------------------------------------------

    print("\n5. VALIDATION MASKS")
    print("-" * 80)

    continuous_valid = (
        np.isfinite(continuous)
        & (continuous != -9999)
    )

    classified_valid = (
        np.isfinite(classified)
        & (classified != 0)
    )

    reference_observed = (
        np.isfinite(reference)
        &
        (
            (reference == REFERENCE_FLOOD)
            |
            (reference == REFERENCE_NON_FLOOD)
        )
    )

    reference_flood = (
        reference == REFERENCE_FLOOD
    )

    reference_non_flood = (
        reference == REFERENCE_NON_FLOOD
    )

    mcda_valid = (
        continuous_valid
        & classified_valid
    )

    observed_validation = (
        mcda_valid
        & reference_observed
    )

    print(
        f"Total cells: "
        f"{continuous.size:,}"
    )

    print(
        f"Valid MCDA cells: "
        f"{int(mcda_valid.sum()):,}"
    )

    print(
        f"Observed validation cells: "
        f"{int(observed_validation.sum()):,}"
    )

    print(
        f"Observed flood cells: "
        f"{int((observed_validation & reference_flood).sum()):,}"
    )

    print(
        f"Observed non-flood cells: "
        f"{int((observed_validation & reference_non_flood).sum()):,}"
    )

    # -----------------------------------------------------------------
    # 6. MODEL-AREA CLASS REPRESENTATION
    # -----------------------------------------------------------------

    print("\n6. MCDA CLASS REPRESENTATION")
    print("-" * 80)

    total_mcda_valid = int(
        mcda_valid.sum()
    )

    model_class_records = []

    for class_value in range(1, 6):

        class_mask = (
            mcda_valid
            & (classified == class_value)
        )

        class_cells = int(
            class_mask.sum()
        )

        class_percentage = (
            class_cells
            / total_mcda_valid
            * 100
        )

        model_class_records.append(
            {
                "class_value": class_value,
                "class_label": CLASS_LABELS[class_value],
                "total_mcda_cells": class_cells,
                "percent_of_valid_mcda": class_percentage,
            }
        )

        print(
            f"{class_value} - "
            f"{CLASS_LABELS[class_value]}:"
        )

        print(
            f"  MCDA cells: "
            f"{class_cells:,}"
        )

        print(
            f"  Percent of valid MCDA: "
            f"{class_percentage:.4f}%"
        )

    # -----------------------------------------------------------------
    # 7. OBSERVATION REPRESENTATION BY CLASS
    # -----------------------------------------------------------------

    print("\n7. UNOSAT OBSERVATION REPRESENTATION")
    print("-" * 80)

    observed_total = int(
        observed_validation.sum()
    )

    flood_total = int(
        (observed_validation & reference_flood).sum()
    )

    non_flood_total = int(
        (observed_validation & reference_non_flood).sum()
    )

    class_records = []

    for class_value in range(1, 6):

        class_mask = (
            observed_validation
            & (classified == class_value)
        )

        observed_cells = int(
            class_mask.sum()
        )

        flood_cells = int(
            (
                class_mask
                & reference_flood
            ).sum()
        )

        non_flood_cells = int(
            (
                class_mask
                & reference_non_flood
            ).sum()
        )

        model_class_cells = model_class_records[
            class_value - 1
        ]["total_mcda_cells"]

        observation_coverage = (
            observed_cells
            / model_class_cells
            * 100
        )

        observation_domain_share = (
            observed_cells
            / observed_total
            * 100
        )

        flood_rate = (
            flood_cells
            / observed_cells
            * 100
            if observed_cells > 0
            else np.nan
        )

        flood_concentration = (
            flood_cells
            / flood_total
            * 100
            if flood_total > 0
            else np.nan
        )

        flood_share_relative_to_model = (
            flood_concentration
            / model_class_records[
                class_value - 1
            ]["percent_of_valid_mcda"]
        )

        class_records.append(
            {
                "class_value": class_value,
                "class_label": CLASS_LABELS[class_value],
                "total_mcda_cells": model_class_cells,
                "percent_of_valid_mcda": (
                    model_class_records[
                        class_value - 1
                    ]["percent_of_valid_mcda"]
                ),
                "observed_cells": observed_cells,
                "percent_of_observation_domain": (
                    observation_domain_share
                ),
                "observation_coverage_percent": (
                    observation_coverage
                ),
                "observed_flood_cells": flood_cells,
                "observed_non_flood_cells": (
                    non_flood_cells
                ),
                "observed_flood_rate_percent": (
                    flood_rate
                ),
                "percent_of_all_observed_flood": (
                    flood_concentration
                ),
                "flood_concentration_to_model_area_ratio": (
                    flood_share_relative_to_model
                ),
            }
        )

        print(
            f"{class_value} - "
            f"{CLASS_LABELS[class_value]}:"
        )

        print(
            f"  MCDA cells: "
            f"{model_class_cells:,}"
        )

        print(
            f"  Observed cells: "
            f"{observed_cells:,}"
        )

        print(
            f"  Observation coverage of class: "
            f"{observation_coverage:.4f}%"
        )

        print(
            f"  Share of observation domain: "
            f"{observation_domain_share:.4f}%"
        )

        print(
            f"  Flood cells: "
            f"{flood_cells:,}"
        )

        print(
            f"  Flood rate: "
            f"{flood_rate:.4f}%"
        )

        print(
            f"  Share of all observed flood: "
            f"{flood_concentration:.4f}%"
        )

        print(
            f"  Flood concentration / "
            f"model-area share: "
            f"{flood_share_relative_to_model:.4f}"
        )

    class_df = pd.DataFrame(
        class_records
    )

    # -----------------------------------------------------------------
    # 8. CONTINUOUS SUSCEPTIBILITY DISTRIBUTIONS
    # -----------------------------------------------------------------

    print("\n8. CONTINUOUS SUSCEPTIBILITY DISTRIBUTIONS")
    print("-" * 80)

    flood_scores = continuous[
        observed_validation
        & reference_flood
    ].astype(np.float64)

    non_flood_scores = continuous[
        observed_validation
        & reference_non_flood
    ].astype(np.float64)

    observed_scores = continuous[
        observed_validation
    ].astype(np.float64)

    mcda_scores = continuous[
        mcda_valid
    ].astype(np.float64)

    distribution_records = []

    distributions = {
        "all_valid_mcda": mcda_scores,
        "observed_domain": observed_scores,
        "observed_flood": flood_scores,
        "observed_non_flood": non_flood_scores,
    }

    for name, values in distributions.items():

        stats = calculate_quantiles(values)

        stats["population"] = name

        distribution_records.append(
            stats
        )

        print(f"\n{name}:")

        print(
            f"  Count: "
            f"{stats['count']:,}"
        )

        print(
            f"  Min: "
            f"{stats['min']:.6f}"
        )

        print(
            f"  P05: "
            f"{stats['p05']:.6f}"
        )

        print(
            f"  P25: "
            f"{stats['p25']:.6f}"
        )

        print(
            f"  Median: "
            f"{stats['median']:.6f}"
        )

        print(
            f"  P75: "
            f"{stats['p75']:.6f}"
        )

        print(
            f"  P95: "
            f"{stats['p95']:.6f}"
        )

        print(
            f"  Max: "
            f"{stats['max']:.6f}"
        )

        print(
            f"  Mean: "
            f"{stats['mean']:.6f}"
        )

    distribution_df = pd.DataFrame(
        distribution_records
    )

    # -----------------------------------------------------------------
    # 9. FLOOD VS NON-FLOOD DISTRIBUTION SHIFT
    # -----------------------------------------------------------------

    print("\n9. FLOOD VS NON-FLOOD DISTRIBUTION SHIFT")
    print("-" * 80)

    flood_mean = float(
        np.mean(flood_scores)
    )

    non_flood_mean = float(
        np.mean(non_flood_scores)
    )

    flood_median = float(
        np.median(flood_scores)
    )

    non_flood_median = float(
        np.median(non_flood_scores)
    )

    mean_difference = (
        flood_mean
        - non_flood_mean
    )

    median_difference = (
        flood_median
        - non_flood_median
    )

    print(
        f"Flood mean: "
        f"{flood_mean:.6f}"
    )

    print(
        f"Non-flood mean: "
        f"{non_flood_mean:.6f}"
    )

    print(
        f"Mean difference: "
        f"{mean_difference:.6f}"
    )

    print(
        f"Flood median: "
        f"{flood_median:.6f}"
    )

    print(
        f"Non-flood median: "
        f"{non_flood_median:.6f}"
    )

    print(
        f"Median difference: "
        f"{median_difference:.6f}"
    )

    # -----------------------------------------------------------------
    # 10. HIGH + VERY HIGH VS LOWER CLASSES
    # -----------------------------------------------------------------

    print("\n10. GROUPED SUSCEPTIBILITY REPRESENTATION")
    print("-" * 80)

    low_moderate_mask = (
        observed_validation
        & np.isin(
            classified,
            [1, 2, 3],
        )
    )

    high_very_high_mask = (
        observed_validation
        & np.isin(
            classified,
            [4, 5],
        )
    )

    low_moderate_observed = int(
        low_moderate_mask.sum()
    )

    high_very_high_observed = int(
        high_very_high_mask.sum()
    )

    low_moderate_flood = int(
        (
            low_moderate_mask
            & reference_flood
        ).sum()
    )

    high_very_high_flood = int(
        (
            high_very_high_mask
            & reference_flood
        ).sum()
    )

    low_moderate_flood_rate = (
        low_moderate_flood
        / low_moderate_observed
        * 100
    )

    high_very_high_flood_rate = (
        high_very_high_flood
        / high_very_high_observed
        * 100
    )

    print(
        f"Very Low + Low + Moderate observed cells: "
        f"{low_moderate_observed:,}"
    )

    print(
        f"High + Very High observed cells: "
        f"{high_very_high_observed:,}"
    )

    print(
        f"Lower three classes flood cells: "
        f"{low_moderate_flood:,}"
    )

    print(
        f"High + Very High flood cells: "
        f"{high_very_high_flood:,}"
    )

    print(
        f"Lower three classes flood rate: "
        f"{low_moderate_flood_rate:.4f}%"
    )

    print(
        f"High + Very High flood rate: "
        f"{high_very_high_flood_rate:.4f}%"
    )

    # -----------------------------------------------------------------
    # 11. SPEARMAN CORRELATION
    # -----------------------------------------------------------------

    print("\n11. CONTINUOUS SUSCEPTIBILITY VS OBSERVED FLOOD")
    print("-" * 80)

    try:

        from scipy.stats import spearmanr

        observed_susceptibility = continuous[
            observed_validation
        ].astype(np.float64)

        observed_flood_binary = (
            reference[observed_validation]
            == REFERENCE_FLOOD
        ).astype(np.int8)

        correlation, p_value = spearmanr(
            observed_susceptibility,
            observed_flood_binary,
        )

        print(
            f"Spearman correlation: "
            f"{correlation:.6f}"
        )

        print(
            f"P-value: "
            f"{p_value:.6e}"
        )

        spearman_available = True

    except ImportError:

        correlation = np.nan
        p_value = np.nan
        spearman_available = False

        print(
            "SciPy is not installed; "
            "Spearman correlation unavailable."
        )

    # -----------------------------------------------------------------
    # 12. DIAGNOSTIC FLAGS
    # -----------------------------------------------------------------

    print("\n12. DIAGNOSTIC FLAGS")
    print("-" * 80)

    observation_coverages = class_df[
        "observation_coverage_percent"
    ].to_numpy(dtype=float)

    coverage_range = (
        float(np.max(observation_coverages))
        - float(np.min(observation_coverages))
    )

    class_observation_balance = (
        coverage_range < 10.0
    )

    flood_rates = class_df[
        "observed_flood_rate_percent"
    ].to_numpy(dtype=float)

    monotonic_non_decreasing = bool(
        np.all(np.diff(flood_rates) >= 0)
    )

    observation_balance_status = (
        "RELATIVELY_BALANCED"
        if class_observation_balance
        else "UNEQUAL_CLASS_REPRESENTATION"
    )

    monotonicity_status = (
        "MONOTONIC_NON_DECREASING"
        if monotonic_non_decreasing
        else "NON_MONOTONIC"
    )

    print(
        f"Observation representation status: "
        f"{observation_balance_status}"
    )

    print(
        f"Observation coverage range across classes: "
        f"{coverage_range:.4f} percentage points"
    )

    print(
        f"Flood-rate monotonicity: "
        f"{monotonicity_status}"
    )

    if not class_observation_balance:

        print(
            "\nInterpretation flag:"
        )

        print(
            "The UNOSAT observation domain does not "
            "intersect the five susceptibility classes "
            "equally. Class-based flood rates should "
            "therefore be interpreted in the context "
            "of unequal spatial representation."
        )

    if not monotonic_non_decreasing:

        print(
            "\nInterpretation flag:"
        )

        print(
            "Observed flood rates do not increase "
            "monotonically with susceptibility class. "
            "This is an empirical validation result and "
            "should not be corrected by changing model "
            "weights or class thresholds."
        )

    # -----------------------------------------------------------------
    # 13. OUTPUTS
    # -----------------------------------------------------------------

    print("\n13. WRITING DIAGNOSTIC OUTPUTS")
    print("-" * 80)

    class_csv = (
        OUTPUT_DIR
        / "unosat_spatial_validation_class_diagnostic.csv"
    )

    class_df.to_csv(
        class_csv,
        index=False,
    )

    distribution_csv = (
        OUTPUT_DIR
        / "unosat_spatial_validation_score_distributions.csv"
    )

    distribution_df.to_csv(
        distribution_csv,
        index=False,
    )

    diagnostic_summary = {
        "phase": "9.11.4",
        "diagnostic": (
            "UNOSAT spatial validation domain "
            "representation"
        ),
        "reference_dataset": {
            "source": "UNOSAT Product 3834",
            "event_code": "FL20240426KEN",
            "sensor": "Pleiades",
            "acquisition_date": "2024-05-01",
        },
        "spatial_compatibility": {
            "crs_pass": crs_pass,
            "dimensions_pass": dimensions_pass,
            "transform_pass": transform_pass,
            "resolution_pass": resolution_pass,
        },
        "population_counts": {
            "total_cells": int(continuous.size),
            "valid_mcda_cells": total_mcda_valid,
            "observed_validation_cells": observed_total,
            "observed_flood_cells": flood_total,
            "observed_non_flood_cells": non_flood_total,
        },
        "class_results": class_records,
        "continuous_distributions": distribution_records,
        "flood_vs_non_flood": {
            "flood_mean": flood_mean,
            "non_flood_mean": non_flood_mean,
            "mean_difference": mean_difference,
            "flood_median": flood_median,
            "non_flood_median": non_flood_median,
            "median_difference": median_difference,
        },
        "grouped_results": {
            "lower_three_observed_cells": (
                low_moderate_observed
            ),
            "high_very_high_observed_cells": (
                high_very_high_observed
            ),
            "lower_three_flood_cells": (
                low_moderate_flood
            ),
            "high_very_high_flood_cells": (
                high_very_high_flood
            ),
            "lower_three_flood_rate_percent": (
                low_moderate_flood_rate
            ),
            "high_very_high_flood_rate_percent": (
                high_very_high_flood_rate
            ),
        },
        "spearman": {
            "available": spearman_available,
            "correlation": (
                float(correlation)
                if spearman_available
                else None
            ),
            "p_value": (
                float(p_value)
                if spearman_available
                else None
            ),
        },
        "diagnostic_assessment": {
            "observation_representation_status": (
                observation_balance_status
            ),
            "observation_coverage_range_percentage_points": (
                coverage_range
            ),
            "flood_rate_monotonicity": (
                monotonicity_status
            ),
            "interpretation": (
                "The diagnostic evaluates whether the independent "
                "UNOSAT observation domain represents the MCDA "
                "susceptibility classes evenly. Unequal class "
                "representation can affect raw class-based flood "
                "rates and should be considered when interpreting "
                "external spatial validation results."
            ),
        },
        "model_integrity": {
            "weights_changed": False,
            "classification_thresholds_changed": False,
            "reference_data_changed": False,
        },
        "status": (
            "PHASE_9_11_4_UNOSAT_SPATIAL_VALIDATION_DIAGNOSTIC_COMPLETED"
        ),
    }

    json_path = (
        OUTPUT_DIR
        / "unosat_spatial_validation_diagnostic.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            diagnostic_summary,
            f,
            indent=2,
            ensure_ascii=False,
            default=json_safe,
        )

    print(
        f"Class diagnostic CSV:\n"
        f"  {class_csv}"
    )

    print(
        f"Score distribution CSV:\n"
        f"  {distribution_csv}"
    )

    print(
        f"Diagnostic JSON:\n"
        f"  {json_path}"
    )

    # -----------------------------------------------------------------
    # 14. FINAL STATUS
    # -----------------------------------------------------------------

    print("\n" + "=" * 80)

    print(
        "PHASE_9_11_4_UNOSAT_SPATIAL_VALIDATION_DIAGNOSTIC_COMPLETED"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()