"""
Phase 9.11.4 — Spatial Validation Against Independent UNOSAT Flood Observations

Purpose
-------
Compare the GeoAI flood-susceptibility model against an independent
UNOSAT satellite-derived flood observation for Nairobi, acquired on
1 May 2024.

This script evaluates:

1. Raster/grid compatibility
2. Common observed validation footprint
3. Observed flood/non-flood counts
4. Observed flood rate by susceptibility class
5. Distribution of observed flood cells across susceptibility classes
6. High + Very High susceptibility performance
7. Continuous susceptibility statistics for flood vs non-flood cells
8. Monotonicity of observed flood rate across susceptibility classes
9. Basic spatial overlap statistics

Important
---------
This is an external spatial validation.

The UNOSAT reference data were not used to construct the MCDA
susceptibility model.

This analysis does NOT yet constitute a complete statistical
predictive evaluation. Threshold-independent metrics such as ROC/AUC,
precision-recall analysis, and additional statistical tests are
reserved for Phase 9.11.5.

Reference raster values:
    1      = observed flood
    0      = observed non-flood
    -9999  = unobserved

Model classes:
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High

Coordinate Reference System:
    EPSG:32737

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
    Convert NumPy/Pandas values into JSON-serializable Python values.
    """

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
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


def transforms_match(transform_a, transform_b, tolerance=1e-9):
    """
    Compare raster affine transforms within numerical tolerance.
    """

    return all(
        abs(float(a) - float(b)) <= tolerance
        for a, b in zip(transform_a, transform_b)
    )


def print_check(label: str, passed: bool):
    """
    Print a standardized validation check.
    """

    status = "PASS" if passed else "FAIL"
    print(f"{label}: {status}")


# ---------------------------------------------------------------------
# MAIN VALIDATION
# ---------------------------------------------------------------------

def main():

    print("=" * 80)
    print("PHASE 9.11.4 — SPATIAL VALIDATION AGAINST UNOSAT")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------
    # 1. INPUT CHECKS
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
        print(f"  Exists: {'PASS' if exists else 'FAIL'}")

        if not exists:
            all_inputs_exist = False

    if not all_inputs_exist:
        raise FileNotFoundError(
            "One or more required Phase 9.11.4 inputs are missing."
        )

    # -----------------------------------------------------------------
    # 2. READ RASTER METADATA
    # -----------------------------------------------------------------

    print("\n2. RASTER METADATA")
    print("-" * 80)

    continuous_meta = raster_metadata(MCDA_CONTINUOUS)
    classified_meta = raster_metadata(MCDA_CLASSIFIED)
    reference_meta = raster_metadata(UNOSAT_REFERENCE)

    print("Continuous susceptibility:")
    print(f"  CRS: {continuous_meta['crs']}")
    print(
        f"  Dimensions: "
        f"{continuous_meta['width']} x {continuous_meta['height']}"
    )
    print(f"  Resolution: {continuous_meta['resolution']}")
    print(f"  NoData: {continuous_meta['nodata']}")

    print("\nClassified susceptibility:")
    print(f"  CRS: {classified_meta['crs']}")
    print(
        f"  Dimensions: "
        f"{classified_meta['width']} x {classified_meta['height']}"
    )
    print(f"  Resolution: {classified_meta['resolution']}")
    print(f"  NoData: {classified_meta['nodata']}")

    print("\nUNOSAT reference:")
    print(f"  CRS: {reference_meta['crs']}")
    print(
        f"  Dimensions: "
        f"{reference_meta['width']} x {reference_meta['height']}"
    )
    print(f"  Resolution: {reference_meta['resolution']}")
    print(f"  NoData: {reference_meta['nodata']}")

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
        continuous_meta["width"] == classified_meta["width"]
        == reference_meta["width"]
        and continuous_meta["height"] == classified_meta["height"]
        == reference_meta["height"]
    )

    transform_pass = (
        transforms_match(
            continuous_meta["transform"],
            classified_meta["transform"],
        )
        and transforms_match(
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
        and np.allclose(
            continuous_meta["resolution"],
            reference_meta["resolution"],
            rtol=0,
            atol=1e-9,
        )
    )

    print_check("CRS", crs_pass)
    print_check("Dimensions", dimensions_pass)
    print_check("Affine transform", transform_pass)
    print_check("Resolution", resolution_pass)

    if not all(
        [
            crs_pass,
            dimensions_pass,
            transform_pass,
            resolution_pass,
        ]
    ):
        raise ValueError(
            "Raster spatial compatibility failed. "
            "External validation cannot proceed."
        )

    # -----------------------------------------------------------------
    # 4. READ ARRAYS
    # -----------------------------------------------------------------

    print("\n4. READING VALIDATION ARRAYS")
    print("-" * 80)

    with rasterio.open(MCDA_CONTINUOUS) as src:
        continuous = src.read(1)

    with rasterio.open(MCDA_CLASSIFIED) as src:
        classified = src.read(1)

    with rasterio.open(UNOSAT_REFERENCE) as src:
        reference = src.read(1)

    print(f"Continuous array shape: {continuous.shape}")
    print(f"Classified array shape: {classified.shape}")
    print(f"Reference array shape: {reference.shape}")

    # -----------------------------------------------------------------
    # 5. BUILD COMMON VALIDATION MASK
    # -----------------------------------------------------------------

    print("\n5. COMMON VALIDATION FOOTPRINT")
    print("-" * 80)

    continuous_valid = np.isfinite(continuous) & (continuous != -9999)

    classified_valid = np.isfinite(classified) & (classified != 0)

    reference_observed = (
        np.isfinite(reference)
        & (
            (reference == REFERENCE_FLOOD)
            | (reference == REFERENCE_NON_FLOOD)
        )
    )

    common_validation_mask = (
        continuous_valid
        & classified_valid
        & reference_observed
    )

    total_cells = continuous.size
    common_cells = int(common_validation_mask.sum())

    flood_mask = (
        common_validation_mask
        & (reference == REFERENCE_FLOOD)
    )

    non_flood_mask = (
        common_validation_mask
        & (reference == REFERENCE_NON_FLOOD)
    )

    flood_cells = int(flood_mask.sum())
    non_flood_cells = int(non_flood_mask.sum())

    print(f"Total raster cells: {total_cells:,}")
    print(f"Common observed validation cells: {common_cells:,}")
    print(
        f"Common observed validation coverage: "
        f"{common_cells / total_cells * 100:.3f}%"
    )
    print(f"Observed flood cells: {flood_cells:,}")
    print(f"Observed non-flood cells: {non_flood_cells:,}")

    if common_cells == 0:
        raise ValueError(
            "No common observed validation cells were found."
        )

    # -----------------------------------------------------------------
    # 6. GLOBAL OBSERVED FLOOD RATE
    # -----------------------------------------------------------------

    print("\n6. OVERALL OBSERVED FLOOD RATE")
    print("-" * 80)

    overall_flood_rate = (
        flood_cells / common_cells * 100
    )

    print(
        f"Observed flood rate within validation domain: "
        f"{overall_flood_rate:.4f}%"
    )

    # -----------------------------------------------------------------
    # 7. CLASS-BASED VALIDATION
    # -----------------------------------------------------------------

    print("\n7. OBSERVED FLOOD RATE BY SUSCEPTIBILITY CLASS")
    print("-" * 80)

    class_records = []

    for class_value in range(1, 6):

        class_mask = (
            common_validation_mask
            & (classified == class_value)
        )

        observed_cells = int(class_mask.sum())

        class_flood_mask = (
            class_mask
            & (reference == REFERENCE_FLOOD)
        )

        class_non_flood_mask = (
            class_mask
            & (reference == REFERENCE_NON_FLOOD)
        )

        class_flood_cells = int(class_flood_mask.sum())
        class_non_flood_cells = int(class_non_flood_mask.sum())

        if observed_cells > 0:
            flood_rate = (
                class_flood_cells
                / observed_cells
                * 100
            )
        else:
            flood_rate = np.nan

        class_records.append(
            {
                "class_value": class_value,
                "class_label": CLASS_LABELS[class_value],
                "observed_cells": observed_cells,
                "observed_flood_cells": class_flood_cells,
                "observed_non_flood_cells": class_non_flood_cells,
                "observed_flood_rate_percent": flood_rate,
            }
        )

        print(
            f"{class_value} - {CLASS_LABELS[class_value]}:"
        )
        print(
            f"  Observed cells: {observed_cells:,}"
        )
        print(
            f"  Flood cells: {class_flood_cells:,}"
        )
        print(
            f"  Non-flood cells: {class_non_flood_cells:,}"
        )
        print(
            f"  Observed flood rate: {flood_rate:.4f}%"
        )

    class_df = pd.DataFrame(class_records)

    # -----------------------------------------------------------------
    # 8. FLOOD DISTRIBUTION ACROSS CLASSES
    # -----------------------------------------------------------------

    print("\n8. DISTRIBUTION OF OBSERVED FLOODING")
    print("-" * 80)

    class_df["flood_cells_percent_of_all_flood"] = (
        class_df["observed_flood_cells"]
        / flood_cells
        * 100
    )

    for _, row in class_df.iterrows():

        print(
            f"{int(row['class_value'])} - "
            f"{row['class_label']}: "
            f"{int(row['observed_flood_cells']):,} flood cells "
            f"({row['flood_cells_percent_of_all_flood']:.4f}%)"
        )

    # -----------------------------------------------------------------
    # 9. HIGH + VERY HIGH ANALYSIS
    # -----------------------------------------------------------------

    print("\n9. HIGH + VERY HIGH VALIDATION")
    print("-" * 80)

    high_very_high_mask = (
        common_validation_mask
        & np.isin(classified, [4, 5])
    )

    high_very_high_cells = int(
        high_very_high_mask.sum()
    )

    high_very_high_flood_cells = int(
        (
            high_very_high_mask
            & (reference == REFERENCE_FLOOD)
        ).sum()
    )

    high_very_high_non_flood_cells = int(
        (
            high_very_high_mask
            & (reference == REFERENCE_NON_FLOOD)
        ).sum()
    )

    high_very_high_flood_concentration = (
        high_very_high_flood_cells
        / flood_cells
        * 100
    )

    high_very_high_flood_rate = (
        high_very_high_flood_cells
        / high_very_high_cells
        * 100
    )

    print(
        f"Observed High + Very High cells: "
        f"{high_very_high_cells:,}"
    )

    print(
        f"Observed flood cells in High + Very High: "
        f"{high_very_high_flood_cells:,}"
    )

    print(
        f"Observed non-flood cells in High + Very High: "
        f"{high_very_high_non_flood_cells:,}"
    )

    print(
        f"Flood concentration in High + Very High: "
        f"{high_very_high_flood_concentration:.4f}%"
    )

    print(
        f"Observed flood rate in High + Very High: "
        f"{high_very_high_flood_rate:.4f}%"
    )

    # -----------------------------------------------------------------
    # 10. CONTINUOUS SUSCEPTIBILITY COMPARISON
    # -----------------------------------------------------------------

    print("\n10. CONTINUOUS SUSCEPTIBILITY — FLOOD VS NON-FLOOD")
    print("-" * 80)

    flood_scores = continuous[flood_mask].astype(np.float64)
    non_flood_scores = continuous[non_flood_mask].astype(np.float64)

    flood_stats = {
        "count": int(flood_scores.size),
        "min": float(np.min(flood_scores)),
        "mean": float(np.mean(flood_scores)),
        "median": float(np.median(flood_scores)),
        "std": float(np.std(flood_scores)),
        "max": float(np.max(flood_scores)),
    }

    non_flood_stats = {
        "count": int(non_flood_scores.size),
        "min": float(np.min(non_flood_scores)),
        "mean": float(np.mean(non_flood_scores)),
        "median": float(np.median(non_flood_scores)),
        "std": float(np.std(non_flood_scores)),
        "max": float(np.max(non_flood_scores)),
    }

    print("Observed flood cells:")
    for key, value in flood_stats.items():
        print(f"  {key}: {value:.6f}" if isinstance(value, float) else f"  {key}: {value:,}")

    print("\nObserved non-flood cells:")
    for key, value in non_flood_stats.items():
        print(f"  {key}: {value:.6f}" if isinstance(value, float) else f"  {key}: {value:,}")

    mean_difference = (
        flood_stats["mean"]
        - non_flood_stats["mean"]
    )

    median_difference = (
        flood_stats["median"]
        - non_flood_stats["median"]
    )

    print(
        f"\nMean susceptibility difference "
        f"(flood - non-flood): {mean_difference:.6f}"
    )

    print(
        f"Median susceptibility difference "
        f"(flood - non-flood): {median_difference:.6f}"
    )

    # -----------------------------------------------------------------
    # 11. CLASS MONOTONICITY
    # -----------------------------------------------------------------

    print("\n11. MONOTONICITY OF OBSERVED FLOOD RATE")
    print("-" * 80)

    flood_rates = class_df[
        "observed_flood_rate_percent"
    ].to_numpy(dtype=float)

    monotonic_increasing = bool(
        np.all(np.diff(flood_rates) >= 0)
    )

    strictly_increasing = bool(
        np.all(np.diff(flood_rates) > 0)
    )

    print(
        "Observed flood rate sequence:"
    )

    print(
        " -> ".join(
            f"{value:.4f}%"
            for value in flood_rates
        )
    )

    print_check(
        "Monotonic non-decreasing flood rate",
        monotonic_increasing,
    )

    print_check(
        "Strictly increasing flood rate",
        strictly_increasing,
    )

    # -----------------------------------------------------------------
    # 12. SPEARMAN RANK CORRELATION
    # -----------------------------------------------------------------

    print("\n12. SPEARMAN ASSOCIATION")
    print("-" * 80)

    try:

        from scipy.stats import spearmanr

        susceptibility_values = continuous[
            common_validation_mask
        ].astype(np.float64)

        observed_flood_values = (
            reference[common_validation_mask] == REFERENCE_FLOOD
        ).astype(np.int8)

        correlation, p_value = spearmanr(
            susceptibility_values,
            observed_flood_values,
        )

        correlation_status = (
            "POSITIVE"
            if correlation > 0
            else "NEGATIVE"
            if correlation < 0
            else "ZERO"
        )

        print(
            f"Spearman correlation: "
            f"{correlation:.6f}"
        )

        print(
            f"P-value: "
            f"{p_value:.6e}"
        )

        print(
            f"Direction: "
            f"{correlation_status}"
        )

        spearman_available = True

    except ImportError:

        correlation = np.nan
        p_value = np.nan
        spearman_available = False

        print(
            "SciPy is not installed. "
            "Spearman correlation was not calculated."
        )

    # -----------------------------------------------------------------
    # 13. BASIC SPATIAL OVERLAP
    # -----------------------------------------------------------------

    print("\n13. FLOOD OVERLAP WITH HIGH-SUSCEPTIBILITY AREAS")
    print("-" * 80)

    overlap_count = high_very_high_flood_cells

    overlap_percentage_of_observed_flood = (
        overlap_count / flood_cells * 100
    )

    print(
        f"Observed flood cells overlapping High + Very High: "
        f"{overlap_count:,}"
    )

    print(
        f"Percentage of observed flood cells in "
        f"High + Very High: "
        f"{overlap_percentage_of_observed_flood:.4f}%"
    )

    # -----------------------------------------------------------------
    # 14. CLASS SUMMARY CSV
    # -----------------------------------------------------------------

    class_csv = (
        OUTPUT_DIR
        / "unosat_validation_by_susceptibility_class.csv"
    )

    class_df.to_csv(
        class_csv,
        index=False,
    )

    print(
        f"\nClass validation CSV written:\n"
        f"  {class_csv}"
    )

    # -----------------------------------------------------------------
    # 15. JSON SUMMARY
    # -----------------------------------------------------------------

    validation_summary = {
        "phase": "9.11.4",
        "title": (
            "Spatial Validation Against Independent UNOSAT "
            "Flood Observation"
        ),
        "reference_dataset": {
            "source": "UNOSAT Product 3834",
            "event_code": "FL20240426KEN",
            "sensor": "Pleiades",
            "acquisition_date": "2024-05-01",
            "reference_values": {
                "1": "observed flood",
                "0": "observed non-flood",
                "-9999": "unobserved",
            },
        },
        "model": {
            "crs": EXPECTED_CRS,
            "classification": {
                "1": "Very Low",
                "2": "Low",
                "3": "Moderate",
                "4": "High",
                "5": "Very High",
            },
        },
        "spatial_compatibility": {
            "crs_pass": crs_pass,
            "dimensions_pass": dimensions_pass,
            "transform_pass": transform_pass,
            "resolution_pass": resolution_pass,
        },
        "validation_domain": {
            "total_raster_cells": total_cells,
            "common_observed_cells": common_cells,
            "coverage_percent": (
                common_cells / total_cells * 100
            ),
            "observed_flood_cells": flood_cells,
            "observed_non_flood_cells": non_flood_cells,
            "overall_observed_flood_rate_percent": (
                overall_flood_rate
            ),
        },
        "class_results": class_records,
        "high_very_high": {
            "observed_cells": high_very_high_cells,
            "observed_flood_cells": high_very_high_flood_cells,
            "observed_non_flood_cells": (
                high_very_high_non_flood_cells
            ),
            "flood_concentration_percent": (
                high_very_high_flood_concentration
            ),
            "flood_rate_percent": (
                high_very_high_flood_rate
            ),
        },
        "continuous_susceptibility": {
            "flood": flood_stats,
            "non_flood": non_flood_stats,
            "mean_difference_flood_minus_non_flood": (
                mean_difference
            ),
            "median_difference_flood_minus_non_flood": (
                median_difference
            ),
        },
        "monotonicity": {
            "monotonic_non_decreasing": monotonic_increasing,
            "strictly_increasing": strictly_increasing,
            "class_flood_rates": flood_rates.tolist(),
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
        "interpretation_scope": (
            "External spatial validation against an independent "
            "satellite-derived flood observation. This phase does "
            "not by itself establish predictive accuracy or flood "
            "probability. Threshold-independent statistical "
            "evaluation is reserved for Phase 9.11.5."
        ),
        "status": "PHASE_9_11_4_SPATIAL_VALIDATION_COMPLETED",
    }

    json_path = (
        OUTPUT_DIR
        / "unosat_spatial_validation_summary.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            validation_summary,
            f,
            indent=2,
            ensure_ascii=False,
            default=json_safe,
        )

    print(
        f"JSON validation summary written:\n"
        f"  {json_path}"
    )

    # -----------------------------------------------------------------
    # 16. FINAL STATUS
    # -----------------------------------------------------------------

    print("\n" + "=" * 80)
    print(
        "PHASE_9_11_4_SPATIAL_VALIDATION_COMPLETED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()