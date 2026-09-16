"""
PHASE 9.8 - FACTOR INFLUENCE ANALYSIS

Purpose
-------
Evaluate how the five standardized MCDA factors relate to the final
continuous flood-susceptibility surface.

This analysis does NOT modify:
    - MCDA factor weights
    - factor standardization
    - susceptibility calculations
    - susceptibility classification thresholds

It evaluates the existing model using the common valid MCDA footprint.

Factors
-------
1. Elevation
2. Slope
3. Distance to rivers
4. Land cover
5. Population

Outputs
-------
results/phase9_validation/factor_influence/
    susceptibility_factor_influence.csv
    susceptibility_factor_influence.json
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import rasterio
from scipy.stats import spearmanr


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALIGNED_DIR = PROJECT_ROOT / "data" / "analysis" / "aligned"
MCDA_DIR = PROJECT_ROOT / "data" / "analysis" / "mcda"

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "factor_influence"
)

SUSCEPTIBILITY_RASTER = MCDA_DIR / "flood_susceptibility.tif"


# ============================================================================
# FACTOR DEFINITIONS
# ============================================================================

FACTORS = {
    "elevation": {
        "label": "Elevation",
        "path": ALIGNED_DIR / "elevation_score.tif",
        "weight": 0.186900,
    },
    "slope": {
        "label": "Slope",
        "path": ALIGNED_DIR / "slope_score.tif",
        "weight": 0.186900,
    },
    "distance_to_rivers": {
        "label": "Distance to rivers",
        "path": ALIGNED_DIR / "distance_to_rivers_score.tif",
        "weight": 0.435300,
    },
    "landcover": {
        "label": "Land cover",
        "path": ALIGNED_DIR / "landcover_score.tif",
        "weight": 0.128600,
    },
    "population": {
        "label": "Population",
        "path": ALIGNED_DIR / "population_score.tif",
        "weight": 0.062400,
    },
}


EXPECTED_CRS = "EPSG:32737"
EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019
EXPECTED_NODATA = -9999


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_separator():
    print("=" * 72)


def validate_raster_exists(path, label):
    exists = path.exists()

    print(f"{label}:")
    print(path)
    print(f"Exists: {'PASS' if exists else 'FAIL'}")
    print()

    if not exists:
        raise FileNotFoundError(
            f"{label} does not exist: {path}"
        )


def read_raster(path):
    with rasterio.open(path) as src:
        array = src.read(1).astype(np.float64)

        profile = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "res": src.res,
            "nodata": src.nodata,
        }

    return array, profile


def validate_reference_grid(profile):
    print("REFERENCE GRID VALIDATION")

    actual_crs = str(profile["crs"])
    actual_width = profile["width"]
    actual_height = profile["height"]

    print(f"Expected CRS: {EXPECTED_CRS}")
    print(f"Actual CRS:   {actual_crs}")

    if actual_crs != EXPECTED_CRS:
        raise ValueError(
            f"Unexpected CRS: {actual_crs}"
        )

    print("CRS: PASS")

    print(
        f"Expected dimensions: "
        f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
    )

    print(
        f"Actual dimensions:   "
        f"{actual_width} x {actual_height}"
    )

    if (
        actual_width != EXPECTED_WIDTH
        or actual_height != EXPECTED_HEIGHT
    ):
        raise ValueError(
            "Reference raster dimensions do not match "
            "the expected MCDA grid."
        )

    print("Dimensions: PASS")
    print()


def compare_spatial_grid(
    factor_profile,
    reference_profile,
    factor_name,
):
    checks = []

    crs_match = (
        factor_profile["crs"]
        == reference_profile["crs"]
    )

    dimensions_match = (
        factor_profile["width"]
        == reference_profile["width"]
        and factor_profile["height"]
        == reference_profile["height"]
    )

    transform_match = np.allclose(
        tuple(factor_profile["transform"]),
        tuple(reference_profile["transform"]),
        rtol=0,
        atol=1e-9,
    )

    resolution_match = np.allclose(
        factor_profile["res"],
        reference_profile["res"],
        rtol=0,
        atol=1e-9,
    )

    checks.extend(
        [
            crs_match,
            dimensions_match,
            transform_match,
            resolution_match,
        ]
    )

    print(
        f"{factor_name} CRS match: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"{factor_name} dimensions match: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )

    print(
        f"{factor_name} transform match: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )

    print(
        f"{factor_name} resolution match: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    if not all(checks):
        raise ValueError(
            f"{factor_name} does not match the reference "
            "MCDA spatial grid."
        )


def valid_mask(array, nodata):
    if nodata is None:
        return np.isfinite(array)

    return (
        np.isfinite(array)
        & (array != nodata)
    )


def safe_statistics(values):
    values = np.asarray(values, dtype=np.float64)

    if values.size == 0:
        return {
            "minimum": None,
            "p05": None,
            "median": None,
            "p95": None,
            "maximum": None,
            "mean": None,
            "std": None,
        }

    return {
        "minimum": float(np.min(values)),
        "p05": float(np.percentile(values, 5)),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
        "maximum": float(np.max(values)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
    }


def interpret_correlation(rho):
    absolute_rho = abs(rho)

    if absolute_rho < 0.20:
        strength = "VERY_WEAK"
    elif absolute_rho < 0.40:
        strength = "WEAK"
    elif absolute_rho < 0.60:
        strength = "MODERATE"
    elif absolute_rho < 0.80:
        strength = "STRONG"
    else:
        strength = "VERY_STRONG"

    if rho > 0:
        direction = "POSITIVE"
    elif rho < 0:
        direction = "NEGATIVE"
    else:
        direction = "NONE"

    return f"{strength}_{direction}"


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():

    print_separator()
    print("PHASE 9.8 - FACTOR INFLUENCE ANALYSIS")
    print_separator()
    print()

    print("Project root:")
    print(PROJECT_ROOT)
    print()

    print("Continuous susceptibility raster:")
    print(SUSCEPTIBILITY_RASTER)
    print()

    print("Results directory:")
    print(RESULTS_DIR)
    print()

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------------
    # 1. INPUT FILE VALIDATION
    # ------------------------------------------------------------------------

    print_separator()
    print("1. INPUT FILE VALIDATION")
    print_separator()

    validate_raster_exists(
        SUSCEPTIBILITY_RASTER,
        "Continuous susceptibility",
    )

    for factor in FACTORS.values():
        validate_raster_exists(
            factor["path"],
            f'{factor["label"]} score',
        )

    # ------------------------------------------------------------------------
    # 2. REFERENCE GRID VALIDATION
    # ------------------------------------------------------------------------

    print_separator()
    print("2. REFERENCE GRID VALIDATION")
    print_separator()

    susceptibility, susceptibility_profile = read_raster(
        SUSCEPTIBILITY_RASTER
    )

    validate_reference_grid(
        susceptibility_profile
    )

    # ------------------------------------------------------------------------
    # 3. FACTOR GRID COMPATIBILITY
    # ------------------------------------------------------------------------

    print_separator()
    print("3. FACTOR GRID COMPATIBILITY VALIDATION")
    print_separator()

    factor_arrays = {}
    factor_profiles = {}

    for factor_name, factor_info in FACTORS.items():

        array, profile = read_raster(
            factor_info["path"]
        )

        factor_arrays[factor_name] = array
        factor_profiles[factor_name] = profile

        compare_spatial_grid(
            profile,
            susceptibility_profile,
            factor_info["label"],
        )

        print()

    print("Factor spatial compatibility: PASS")
    print()

    # ------------------------------------------------------------------------
    # 4. COMMON VALID MCDA FOOTPRINT
    # ------------------------------------------------------------------------

    print_separator()
    print("4. COMMON VALID MCDA FOOTPRINT")
    print_separator()

    susceptibility_valid = valid_mask(
        susceptibility,
        susceptibility_profile["nodata"],
    )

    combined_mask = susceptibility_valid.copy()

    for factor_name in FACTORS:
        profile = factor_profiles[factor_name]

        combined_mask &= valid_mask(
            factor_arrays[factor_name],
            profile["nodata"],
        )

    total_cells = susceptibility.size
    common_valid_cells = int(np.sum(combined_mask))

    common_valid_percentage = (
        common_valid_cells
        / total_cells
        * 100
    )

    print(f"Total raster cells: {total_cells:,}")
    print(
        f"Common valid MCDA cells: "
        f"{common_valid_cells:,}"
    )
    print(
        f"Common valid percentage: "
        f"{common_valid_percentage:.3f}%"
    )

    if common_valid_cells == 0:
        raise ValueError(
            "No common valid MCDA cells were found."
        )

    print("Common MCDA footprint: PASS")
    print()

    # ------------------------------------------------------------------------
    # 5. AHP WEIGHT VALIDATION
    # ------------------------------------------------------------------------

    print_separator()
    print("5. AHP WEIGHT VALIDATION")
    print_separator()

    weight_sum = sum(
        factor["weight"]
        for factor in FACTORS.values()
    )

    print(f"Sum of supplied AHP weights: {weight_sum:.6f}")

    if not np.isclose(
        weight_sum,
        1.0001,
        atol=0.0002,
    ):
        raise ValueError(
            "Supplied AHP weights do not match "
            "the expected Phase 8 weights."
        )

    print("AHP weight set: PASS")
    print()

    print("Factor weights:")

    for factor_name, factor_info in FACTORS.items():
        print(
            f'{factor_info["label"]}: '
            f'{factor_info["weight"]:.6f}'
        )

    print()

    # ------------------------------------------------------------------------
    # 6. FACTOR STATISTICS
    # ------------------------------------------------------------------------

    print_separator()
    print("6. STANDARDIZED FACTOR STATISTICS")
    print_separator()

    factor_stats = {}

    for factor_name, factor_info in FACTORS.items():

        values = factor_arrays[factor_name][
            combined_mask
        ]

        stats = safe_statistics(values)

        factor_stats[factor_name] = stats

        print(f'{factor_info["label"]}')
        print(
            f'  Minimum: {stats["minimum"]:.6f}'
        )
        print(
            f'  Median:  {stats["median"]:.6f}'
        )
        print(
            f'  Mean:    {stats["mean"]:.6f}'
        )
        print(
            f'  Maximum: {stats["maximum"]:.6f}'
        )
        print()

        in_range = (
            stats["minimum"] >= 0
            and stats["maximum"] <= 1
        )

        if not in_range:
            raise ValueError(
                f'{factor_info["label"]} contains '
                "values outside the expected 0-1 range."
            )

    print("Standardized factor range validation: PASS")
    print()

    # ------------------------------------------------------------------------
    # 7. WEIGHTED FACTOR CONTRIBUTIONS
    # ------------------------------------------------------------------------

    print_separator()
    print("7. WEIGHTED FACTOR CONTRIBUTION ANALYSIS")
    print_separator()

    weighted_contributions = {}

    for factor_name, factor_info in FACTORS.items():

        weighted_values = (
            factor_arrays[factor_name][combined_mask]
            * factor_info["weight"]
        )

        weighted_contributions[factor_name] = (
            weighted_values
        )

        stats = safe_statistics(
            weighted_values
        )

        print(f'{factor_info["label"]}')
        print(
            f'  Weight: {factor_info["weight"]:.6f}'
        )
        print(
            f'  Mean weighted contribution: '
            f'{stats["mean"]:.6f}'
        )
        print(
            f'  Median weighted contribution: '
            f'{stats["median"]:.6f}'
        )
        print(
            f'  Maximum weighted contribution: '
            f'{stats["maximum"]:.6f}'
        )
        print()

    # ------------------------------------------------------------------------
    # 8. RELATIVE MEAN CONTRIBUTION
    # ------------------------------------------------------------------------

    print_separator()
    print("8. RELATIVE MEAN CONTRIBUTION")
    print_separator()

    mean_contributions = {}

    for factor_name in FACTORS:
        mean_contributions[factor_name] = float(
            np.mean(
                weighted_contributions[factor_name]
            )
        )

    total_mean_contribution = sum(
        mean_contributions.values()
    )

    relative_contributions = {}

    for factor_name in FACTORS:
        if total_mean_contribution == 0:
            relative = 0.0
        else:
            relative = (
                mean_contributions[factor_name]
                / total_mean_contribution
                * 100
            )

        relative_contributions[factor_name] = (
            relative
        )

        print(
            f'{FACTORS[factor_name]["label"]}: '
            f'{relative:.3f}%'
        )

    print(
        f"Relative contribution total: "
        f"{sum(relative_contributions.values()):.3f}%"
    )

    print()

    # ------------------------------------------------------------------------
    # 9. FACTOR VS CONTINUOUS SUSCEPTIBILITY
    # ------------------------------------------------------------------------

    print_separator()
    print("9. FACTOR VS CONTINUOUS SUSCEPTIBILITY")
    print_separator()

    susceptibility_values = susceptibility[
        combined_mask
    ]

    results = []

    for factor_name, factor_info in FACTORS.items():

        factor_values = factor_arrays[
            factor_name
        ][combined_mask]

        rho, p_value = spearmanr(
            factor_values,
            susceptibility_values,
        )

        interpretation = interpret_correlation(
            rho
        )

        print(f'{factor_info["label"]}')
        print(
            f'  Spearman correlation: '
            f'{rho:.6f}'
        )
        print(
            f'  p-value: '
            f'{p_value:.6e}'
        )
        print(
            f'  Interpretation: '
            f'{interpretation}'
        )
        print()

        results.append(
            {
                "factor": factor_name,
                "factor_label": factor_info["label"],
                "ahp_weight": factor_info["weight"],
                "factor_mean": factor_stats[
                    factor_name
                ]["mean"],
                "factor_median": factor_stats[
                    factor_name
                ]["median"],
                "factor_minimum": factor_stats[
                    factor_name
                ]["minimum"],
                "factor_maximum": factor_stats[
                    factor_name
                ]["maximum"],
                "mean_weighted_contribution":
                    mean_contributions[
                        factor_name
                    ],
                "relative_mean_contribution_percent":
                    relative_contributions[
                        factor_name
                    ],
                "spearman_correlation":
                    float(rho),
                "spearman_p_value":
                    float(p_value),
                "correlation_interpretation":
                    interpretation,
            }
        )

    # ------------------------------------------------------------------------
    # 10. MODEL RECONSTRUCTION CHECK
    # ------------------------------------------------------------------------

    print_separator()
    print("10. MCDA RECONSTRUCTION CHECK")
    print_separator()

    reconstructed_susceptibility = np.zeros(
        common_valid_cells,
        dtype=np.float64,
    )

    for factor_name, factor_info in FACTORS.items():

        reconstructed_susceptibility += (
            factor_arrays[factor_name][combined_mask]
            * factor_info["weight"]
        )

    observed_susceptibility = susceptibility[
        combined_mask
    ]

    reconstruction_difference = (
        reconstructed_susceptibility
        - observed_susceptibility
    )

    max_absolute_difference = float(
        np.max(
            np.abs(reconstruction_difference)
        )
    )

    mean_absolute_difference = float(
        np.mean(
            np.abs(reconstruction_difference)
        )
    )

    print(
        "Maximum absolute reconstruction difference: "
        f"{max_absolute_difference:.12f}"
    )

    print(
        "Mean absolute reconstruction difference: "
        f"{mean_absolute_difference:.12f}"
    )

    reconstruction_pass = (
        max_absolute_difference <= 0.0005
    )

    print(
        "MCDA reconstruction: "
        f"{'PASS' if reconstruction_pass else 'INVESTIGATE'}"
    )

    if not reconstruction_pass:
        print(
            "WARNING: The reconstructed MCDA surface "
            "differs from the supplied susceptibility "
            "raster beyond the expected tolerance."
        )

    print()

    # ------------------------------------------------------------------------
    # 11. OVERALL INFLUENCE ASSESSMENT
    # ------------------------------------------------------------------------

    print_separator()
    print("11. OVERALL FACTOR-INFLUENCE ASSESSMENT")
    print_separator()

    correlations = {
        result["factor"]:
        result["spearman_correlation"]
        for result in results
    }

    directions = {
        factor_name:
        np.sign(correlation)
        for factor_name, correlation
        in correlations.items()
    }

    positive_factors = [
        factor_name
        for factor_name, direction
        in directions.items()
        if direction > 0
    ]

    negative_factors = [
        factor_name
        for factor_name, direction
        in directions.items()
        if direction < 0
    ]

    print(
        "Factors with positive susceptibility relationship:"
    )

    for factor_name in positive_factors:
        print(
            f'  - {FACTORS[factor_name]["label"]}'
        )

    print()

    print(
        "Factors with negative susceptibility relationship:"
    )

    for factor_name in negative_factors:
        print(
            f'  - {FACTORS[factor_name]["label"]}'
        )

    print()

    print(
        "Overall assessment: "
        "FACTOR_INFLUENCE_ANALYSIS_COMPLETED"
    )

    # ------------------------------------------------------------------------
    # 12. SAVE CSV
    # ------------------------------------------------------------------------

    print_separator()
    print("12. SAVE CSV RESULTS")
    print_separator()

    results_df = pd.DataFrame(results)

    csv_path = (
        RESULTS_DIR
        / "susceptibility_factor_influence.csv"
    )

    results_df.to_csv(
        csv_path,
        index=False,
    )

    print(f"CSV saved: {csv_path}")
    print("CSV output: PASS")
    print()

    # ------------------------------------------------------------------------
    # 13. SAVE JSON
    # ------------------------------------------------------------------------

    print_separator()
    print("13. SAVE JSON RESULTS")
    print_separator()

    json_path = (
        RESULTS_DIR
        / "susceptibility_factor_influence.json"
    )

    json_results = {
        "phase": "9.8",
        "title": "Factor Influence Analysis",
        "project_root": str(PROJECT_ROOT),
        "susceptibility_raster": str(
            SUSCEPTIBILITY_RASTER
        ),
        "expected_crs": EXPECTED_CRS,
        "reference_width": EXPECTED_WIDTH,
        "reference_height": EXPECTED_HEIGHT,
        "total_raster_cells": int(total_cells),
        "common_valid_cells": int(
            common_valid_cells
        ),
        "common_valid_percentage": float(
            common_valid_percentage
        ),
        "ahp_weight_sum": float(weight_sum),
        "factor_weights": {
            factor_name: float(
                factor_info["weight"]
            )
            for factor_name, factor_info
            in FACTORS.items()
        },
        "factor_results": results,
        "reconstruction_check": {
            "maximum_absolute_difference":
                max_absolute_difference,
            "mean_absolute_difference":
                mean_absolute_difference,
            "status":
                "PASS"
                if reconstruction_pass
                else "INVESTIGATE",
        },
        "overall_status":
            "FACTOR_INFLUENCE_ANALYSIS_COMPLETED",
    }

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            json_results,
            file,
            indent=4,
        )

    print(f"JSON saved: {json_path}")
    print("JSON output: PASS")
    print()

    # ------------------------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------------------------

    print_separator()
    print("PHASE 9.8 FACTOR INFLUENCE ANALYSIS COMPLETED")
    print_separator()

    print(
        f"Common valid MCDA cells analyzed: "
        f"{common_valid_cells:,}"
    )

    print(
        "MCDA reconstruction status: "
        f"{'PASS' if reconstruction_pass else 'INVESTIGATE'}"
    )

    print()

    print("Outputs:")

    print(csv_path)
    print(json_path)

    print_separator()


if __name__ == "__main__":
    main()