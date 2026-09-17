"""
PHASE 9.9 - SENSITIVITY / ROBUSTNESS ANALYSIS

GeoAI Flood Risk Decision Agent
Nairobi County, Kenya

Purpose
-------
Evaluate how sensitive the final flood-susceptibility surface is to
plausible changes in the MCDA/AHP weights.

Method
------
Baseline:
    Original Phase 8 AHP weights.

Sensitivity scenarios:
    Each factor weight is independently increased and decreased by 10%.

    For each perturbation:
        - Target factor weight is multiplied by 1.10 or 0.90.
        - The remaining weight difference is redistributed proportionally
          among the other four factors.
        - All other model components remain unchanged.

The analysis compares each scenario against the baseline using:
    - Mean absolute difference
    - Maximum absolute difference
    - Spearman rank correlation
    - Same-class agreement
    - Number of changed classification cells
    - High + Very High class retention

Classification
--------------
The original Phase 8 quantile thresholds are kept fixed:

    Q20 = 0.6915898
    Q40 = 0.7606905
    Q60 = 0.8051752
    Q80 = 0.84985673

This is important because recomputing quantiles for every scenario
would force each scenario to contain approximately the same proportion
of cells in each class and would therefore hide meaningful sensitivity.

Outputs
-------
results/phase9_validation/sensitivity_robustness/
    sensitivity_scenario_summary.csv
    sensitivity_scenario_summary.json
    sensitivity_class_stability.csv
    sensitivity_weight_scenarios.csv
    sensitivity_validation_summary.json

Author
------
GeoAI Flood Risk Decision Agent
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import rasterio
from scipy.stats import spearmanr


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MCDA_DIR = PROJECT_ROOT / "data" / "analysis" / "mcda"
ALIGNED_DIR = PROJECT_ROOT / "data" / "analysis" / "aligned"

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "sensitivity_robustness"
)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. INPUT FILES
# ============================================================

BASELINE_RASTER = MCDA_DIR / "flood_susceptibility.tif"

CLASSIFIED_RASTER = MCDA_DIR / "flood_susceptibility_classified.tif"

FACTOR_FILES = {
    "elevation": ALIGNED_DIR / "elevation_score.tif",
    "slope": ALIGNED_DIR / "slope_score.tif",
    "distance_to_rivers": ALIGNED_DIR / "distance_to_rivers_score.tif",
    "landcover": ALIGNED_DIR / "landcover_score.tif",
    "population": ALIGNED_DIR / "population_score.tif",
}


# ============================================================
# 3. BASELINE AHP WEIGHTS
# ============================================================

# Exact documented Phase 8 weights.
BASELINE_WEIGHTS = {
    "elevation": 0.1868744589,
    "slope": 0.1868744589,
    "distance_to_rivers": 0.4352900433,
    "landcover": 0.1285887446,
    "population": 0.0623722944,
}

WEIGHT_SUM_TOLERANCE = 1e-6

# Sensitivity magnitude.
PERTURBATION = 0.10


# ============================================================
# 4. FIXED PHASE 8 CLASSIFICATION THRESHOLDS
# ============================================================

Q20 = 0.6915898
Q40 = 0.7606905
Q60 = 0.8051752
Q80 = 0.84985673


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

def check_file_exists(path):
    """Return True when an input file exists."""
    return path.exists()


def read_raster(path):
    """
    Read a raster as float64 while preserving metadata.

    Returns
    -------
    array : np.ndarray
    profile : dict
    nodata : float or None
    """
    with rasterio.open(path) as src:
        array = src.read(1).astype(np.float64)
        profile = src.profile.copy()
        nodata = src.nodata

    return array, profile, nodata


def valid_mask(array, nodata):
    """
    Build a valid-data mask.

    Handles both explicit NoData values and NaN values.
    """
    mask = np.isfinite(array)

    if nodata is not None:
        mask &= array != nodata

    return mask


def classify_fixed(values):
    """
    Classify continuous susceptibility values using the fixed
    Phase 8 thresholds.

    Classes
    -------
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High
    """

    classes = np.select(
        [
            values <= Q20,
            values <= Q40,
            values <= Q60,
            values <= Q80,
        ],
        [
            1,
            2,
            3,
            4,
        ],
        default=5,
    )

    return classes.astype(np.int16)


def create_perturbed_weights(base_weights, target_factor, direction):
    """
    Create one-factor-at-a-time perturbed weights.

    Parameters
    ----------
    base_weights : dict
        Original normalized weights.

    target_factor : str
        Factor whose weight is perturbed.

    direction : str
        Either "increase" or "decrease".

    Returns
    -------
    dict
        New normalized weights.
    """

    weights = base_weights.copy()

    base_target = base_weights[target_factor]

    if direction == "increase":
        new_target = base_target * (1.0 + PERTURBATION)

    elif direction == "decrease":
        new_target = base_target * (1.0 - PERTURBATION)

    else:
        raise ValueError(
            "direction must be either 'increase' or 'decrease'"
        )

    # Calculate how much total weight remains for all other factors.
    remaining_target_total = 1.0 - new_target

    other_base_total = 1.0 - base_target

    if other_base_total <= 0:
        raise ValueError(
            f"Invalid baseline weight for {target_factor}: "
            f"{base_target}"
        )

    # Preserve the relative proportions of the other factors.
    for factor in weights:
        if factor != target_factor:
            weights[factor] = (
                base_weights[factor]
                * remaining_target_total
                / other_base_total
            )

    weights[target_factor] = new_target

    return weights


def calculate_susceptibility(factors, weights, mask):
    """
    Calculate an MCDA susceptibility surface in memory.

    Only cells valid across all factors are populated.

    Returns
    -------
    np.ndarray
        Susceptibility surface.
    """

    result = np.full(
        next(iter(factors.values())).shape,
        np.nan,
        dtype=np.float64,
    )

    susceptibility = np.zeros(result.shape, dtype=np.float64)

    for factor, array in factors.items():
        susceptibility += array * weights[factor]

    result[mask] = susceptibility[mask]

    return result


def calculate_summary_metrics(
    baseline,
    scenario,
    baseline_classes,
    scenario_classes,
    mask,
):
    """
    Calculate scenario-vs-baseline robustness metrics.
    """

    baseline_valid = baseline[mask]
    scenario_valid = scenario[mask]

    differences = np.abs(scenario_valid - baseline_valid)

    mean_absolute_difference = float(np.mean(differences))
    max_absolute_difference = float(np.max(differences))

    correlation_result = spearmanr(
        baseline_valid,
        scenario_valid,
    )

    spearman_correlation = float(correlation_result.statistic)
    spearman_p_value = float(correlation_result.pvalue)

    baseline_class_valid = baseline_classes[mask]
    scenario_class_valid = scenario_classes[mask]

    same_class = scenario_class_valid == baseline_class_valid

    same_class_agreement = float(
        np.mean(same_class) * 100.0
    )

    changed_cells = int(
        np.sum(~same_class)
    )

    mean_absolute_class_change = float(
        np.mean(
            np.abs(
                scenario_class_valid.astype(np.float64)
                - baseline_class_valid.astype(np.float64)
            )
        )
    )

    # Baseline High + Very High cells.
    baseline_high = baseline_class_valid >= 4

    baseline_high_count = int(
        np.sum(baseline_high)
    )

    retained_high = int(
        np.sum(
            baseline_high
            & (scenario_class_valid >= 4)
        )
    )

    if baseline_high_count > 0:
        high_very_high_retention = (
            retained_high
            / baseline_high_count
            * 100.0
        )
    else:
        high_very_high_retention = np.nan

    # Jaccard overlap for baseline High + Very High area.
    scenario_high = scenario_class_valid >= 4

    intersection = int(
        np.sum(
            baseline_high
            & scenario_high
        )
    )

    union = int(
        np.sum(
            baseline_high
            | scenario_high
        )
    )

    if union > 0:
        high_very_high_jaccard = (
            intersection / union * 100.0
        )
    else:
        high_very_high_jaccard = np.nan

    return {
        "mean_absolute_difference": mean_absolute_difference,
        "max_absolute_difference": max_absolute_difference,
        "spearman_correlation": spearman_correlation,
        "spearman_p_value": spearman_p_value,
        "same_class_agreement_percent": same_class_agreement,
        "changed_class_cells": changed_cells,
        "mean_absolute_class_change": mean_absolute_class_change,
        "baseline_high_very_high_cells": baseline_high_count,
        "retained_high_very_high_cells": retained_high,
        "high_very_high_retention_percent": float(
            high_very_high_retention
        ),
        "high_very_high_jaccard_percent": float(
            high_very_high_jaccard
        ),
    }


def create_class_stability_table(
    scenario_name,
    baseline_classes,
    scenario_classes,
    mask,
):
    """
    Create a 5x5 class transition table for one scenario.

    Rows represent baseline classes.
    Columns represent scenario classes.
    """

    baseline_valid = baseline_classes[mask]
    scenario_valid = scenario_classes[mask]

    records = []

    class_names = {
        1: "Very Low",
        2: "Low",
        3: "Moderate",
        4: "High",
        5: "Very High",
    }

    total_valid = len(baseline_valid)

    for baseline_class in range(1, 6):

        baseline_count = np.sum(
            baseline_valid == baseline_class
        )

        for scenario_class in range(1, 6):

            transition_count = np.sum(
                (baseline_valid == baseline_class)
                & (scenario_valid == scenario_class)
            )

            if baseline_count > 0:
                percent_of_baseline_class = (
                    transition_count
                    / baseline_count
                    * 100.0
                )
            else:
                percent_of_baseline_class = 0.0

            percent_of_all_valid = (
                transition_count
                / total_valid
                * 100.0
            )

            records.append(
                {
                    "scenario": scenario_name,
                    "baseline_class": baseline_class,
                    "baseline_class_name": class_names[
                        baseline_class
                    ],
                    "scenario_class": scenario_class,
                    "scenario_class_name": class_names[
                        scenario_class
                    ],
                    "cells": int(transition_count),
                    "percent_of_baseline_class": float(
                        percent_of_baseline_class
                    ),
                    "percent_of_all_valid_cells": float(
                        percent_of_all_valid
                    ),
                }
            )

    return records


# ============================================================
# 6. MAIN ANALYSIS
# ============================================================

def main():

    print("=" * 72)
    print("PHASE 9.9 - SENSITIVITY / ROBUSTNESS ANALYSIS")
    print("=" * 72)

    # --------------------------------------------------------
    # 6.1 INPUT VALIDATION
    # --------------------------------------------------------

    print("\n1. INPUT FILE VALIDATION")

    all_inputs = {
        "baseline_susceptibility": BASELINE_RASTER,
        "classified_susceptibility": CLASSIFIED_RASTER,
        **FACTOR_FILES,
    }

    missing_inputs = []

    for name, path in all_inputs.items():

        if check_file_exists(path):
            print(f"   PASS: {name} -> {path}")
        else:
            print(f"   FAIL: {name} -> {path}")
            missing_inputs.append(name)

    if missing_inputs:
        raise FileNotFoundError(
            "Missing required input files: "
            + ", ".join(missing_inputs)
        )

    # --------------------------------------------------------
    # 6.2 READ BASELINE RASTER
    # --------------------------------------------------------

    print("\n2. BASELINE SUSCEPTIBILITY")

    baseline, baseline_profile, baseline_nodata = read_raster(
        BASELINE_RASTER
    )

    baseline_valid = valid_mask(
        baseline,
        baseline_nodata
    )

    print(
        f"   Dimensions: "
        f"{baseline_profile['width']} x "
        f"{baseline_profile['height']}"
    )

    print(
        f"   CRS: {baseline_profile['crs']}"
    )

    print(
        f"   Resolution: "
        f"{baseline_profile['transform'].a:.10f} x "
        f"{abs(baseline_profile['transform'].e):.10f} m"
    )

    print(
        f"   Valid cells: "
        f"{np.sum(baseline_valid):,}"
    )

    # --------------------------------------------------------
    # 6.3 READ CLASSIFIED RASTER
    # --------------------------------------------------------

    print("\n3. BASELINE CLASSIFICATION")

    classified, classified_profile, classified_nodata = read_raster(
        CLASSIFIED_RASTER
    )

    classified_valid = valid_mask(
        classified,
        classified_nodata
    )

    if classified.shape != baseline.shape:
        raise ValueError(
            "Baseline and classified susceptibility rasters "
            "have different dimensions."
        )

    if not np.array_equal(
        classified_profile["transform"],
        baseline_profile["transform"],
    ):
        raise ValueError(
            "Baseline and classified susceptibility rasters "
            "have different transforms."
        )

    baseline_classes_from_thresholds = np.full(
        baseline.shape,
        0,
        dtype=np.int16,
    )

    baseline_classes_from_thresholds[baseline_valid] = (
        classify_fixed(
            baseline[baseline_valid]
        )
    )

    existing_classes = classified.astype(np.int16)

    classification_difference = (
        baseline_classes_from_thresholds[baseline_valid]
        != existing_classes[baseline_valid]
    )

    classification_difference_count = int(
        np.sum(classification_difference)
    )

    if classification_difference_count == 0:
        classification_validation_status = "PASS"
        print(
            "   PASS: Fixed Phase 8 thresholds reproduce "
            "the existing classified raster."
        )
    else:
        classification_validation_status = "INVESTIGATE"
        print(
            "   INVESTIGATE: "
            f"{classification_difference_count:,} cells differ "
            "from the existing classified raster."
        )

    # Use the existing Phase 8 classification as the baseline.
    baseline_classes = existing_classes

    # --------------------------------------------------------
    # 6.4 LOAD ALIGNED FACTORS
    # --------------------------------------------------------

    print("\n4. ALIGNED FACTOR VALIDATION")

    factors = {}

    factor_validation_records = []

    for factor_name, path in FACTOR_FILES.items():

        array, profile, nodata = read_raster(path)

        print(f"\n   {factor_name}")
        print(f"      Dimensions: {profile['width']} x {profile['height']}")
        print(f"      CRS: {profile['crs']}")
        print(
            "      Resolution: "
            f"{profile['transform'].a:.10f} x "
            f"{abs(profile['transform'].e):.10f} m"
        )

        dimensions_match = array.shape == baseline.shape

        crs_match = profile["crs"] == baseline_profile["crs"]

        transform_match = (
            profile["transform"]
            == baseline_profile["transform"]
        )

        resolution_match = (
            np.isclose(
                profile["transform"].a,
                baseline_profile["transform"].a,
            )
            and
            np.isclose(
                profile["transform"].e,
                baseline_profile["transform"].e,
            )
        )

        if dimensions_match:
            print("      Dimensions: PASS")
        else:
            print("      Dimensions: FAIL")

        if crs_match:
            print("      CRS: PASS")
        else:
            print("      CRS: FAIL")

        if transform_match:
            print("      Transform: PASS")
        else:
            print("      Transform: FAIL")

        if resolution_match:
            print("      Resolution: PASS")
        else:
            print("      Resolution: FAIL")

        if not (
            dimensions_match
            and crs_match
            and transform_match
            and resolution_match
        ):
            raise ValueError(
                f"Spatial compatibility failed for {factor_name}."
            )

        factors[factor_name] = array

        factor_mask = valid_mask(
            array,
            nodata
        )

        factor_validation_records.append(
            {
                "factor": factor_name,
                "valid_cells": int(np.sum(factor_mask)),
                "min": float(np.nanmin(array[factor_mask])),
                "median": float(np.nanmedian(array[factor_mask])),
                "mean": float(np.nanmean(array[factor_mask])),
                "max": float(np.nanmax(array[factor_mask])),
            }
        )

    # --------------------------------------------------------
    # 6.5 COMMON VALID MCDA FOOTPRINT
    # --------------------------------------------------------

    print("\n5. COMMON VALID MCDA FOOTPRINT")

    common_mask = baseline_valid.copy()

    for factor_array in factors.values():

        common_mask &= np.isfinite(
            factor_array
        )

    common_cells = int(
        np.sum(common_mask)
    )

    total_cells = int(
        baseline.size
    )

    common_percentage = (
        common_cells / total_cells * 100.0
    )

    print(
        f"   Total grid cells: {total_cells:,}"
    )

    print(
        f"   Common valid cells: {common_cells:,}"
    )

    print(
        f"   Common valid percentage: "
        f"{common_percentage:.3f}%"
    )

    if common_cells == 0:
        raise ValueError(
            "No common valid MCDA cells were found."
        )

    # --------------------------------------------------------
    # 6.6 WEIGHT VALIDATION
    # --------------------------------------------------------

    print("\n6. BASELINE AHP WEIGHTS")

    baseline_weight_sum = sum(
        BASELINE_WEIGHTS.values()
    )

    print(
        f"   Weight sum: "
        f"{baseline_weight_sum:.10f}"
    )

    if not np.isclose(
        baseline_weight_sum,
        1.0,
        atol=WEIGHT_SUM_TOLERANCE,
    ):
        raise ValueError(
            "Baseline AHP weights do not sum to 1."
        )

    print("   Weight sum: PASS")

    # --------------------------------------------------------
    # 6.7 BASELINE RECONSTRUCTION
    # --------------------------------------------------------

    print("\n7. BASELINE MCDA RECONSTRUCTION")

    reconstructed_baseline = calculate_susceptibility(
        factors,
        BASELINE_WEIGHTS,
        common_mask,
    )

    baseline_values = baseline[common_mask]
    reconstructed_values = reconstructed_baseline[common_mask]

    reconstruction_difference = np.abs(
        reconstructed_values
        - baseline_values
    )

    reconstruction_max = float(
        np.max(reconstruction_difference)
    )

    reconstruction_mean = float(
        np.mean(reconstruction_difference)
    )

    print(
        f"   Maximum absolute difference: "
        f"{reconstruction_max:.12f}"
    )

    print(
        f"   Mean absolute difference: "
        f"{reconstruction_mean:.12f}"
    )

    # Small numerical differences are expected from raster
    # calculations and stored floating-point precision.
    reconstruction_status = (
        "PASS"
        if reconstruction_max <= 0.001
        else "INVESTIGATE"
    )

    print(
        f"   Reconstruction status: "
        f"{reconstruction_status}"
    )

    # --------------------------------------------------------
    # 6.8 BASELINE CLASS DISTRIBUTION
    # --------------------------------------------------------

    print("\n8. BASELINE CLASS DISTRIBUTION")

    class_names = {
        1: "Very Low",
        2: "Low",
        3: "Moderate",
        4: "High",
        5: "Very High",
    }

    baseline_class_counts = {}

    for class_id in range(1, 6):

        count = int(
            np.sum(
                baseline_classes[common_mask]
                == class_id
            )
        )

        percentage = (
            count / common_cells * 100.0
        )

        baseline_class_counts[class_id] = {
            "name": class_names[class_id],
            "cells": count,
            "percentage": percentage,
        }

        print(
            f"   Class {class_id} "
            f"({class_names[class_id]}): "
            f"{count:,} cells "
            f"({percentage:.3f}%)"
        )

    # --------------------------------------------------------
    # 6.9 CREATE SENSITIVITY SCENARIOS
    # --------------------------------------------------------

    print("\n9. SENSITIVITY SCENARIO DESIGN")

    scenarios = []

    # Baseline scenario.
    scenarios.append(
        {
            "scenario": "baseline",
            "target_factor": "none",
            "direction": "baseline",
            "perturbation_percent": 0.0,
            "weights": BASELINE_WEIGHTS.copy(),
        }
    )

    # Ten one-factor-at-a-time scenarios.
    for factor in BASELINE_WEIGHTS:

        for direction in ["increase", "decrease"]:

            scenario_weights = create_perturbed_weights(
                BASELINE_WEIGHTS,
                factor,
                direction,
            )

            scenario_name = (
                f"{factor}_{'plus10pct' if direction == 'increase' else 'minus10pct'}"
            )

            scenarios.append(
                {
                    "scenario": scenario_name,
                    "target_factor": factor,
                    "direction": direction,
                    "perturbation_percent": (
                        10.0
                        if direction == "increase"
                        else -10.0
                    ),
                    "weights": scenario_weights,
                }
            )

    print(
        f"   Total scenarios: {len(scenarios)}"
    )

    print(
        "   Baseline + 10 one-factor perturbation scenarios."
    )

    # --------------------------------------------------------
    # 6.10 VALIDATE AND SAVE SCENARIO WEIGHTS
    # --------------------------------------------------------

    print("\n10. SCENARIO WEIGHT VALIDATION")

    weight_records = []

    for scenario in scenarios:

        scenario_name = scenario["scenario"]
        weights = scenario["weights"]

        weight_sum = sum(weights.values())

        if not np.isclose(
            weight_sum,
            1.0,
            atol=WEIGHT_SUM_TOLERANCE,
        ):
            raise ValueError(
                f"Weight sum failed for scenario "
                f"{scenario_name}: {weight_sum}"
            )

        record = {
            "scenario": scenario_name,
            "target_factor": scenario["target_factor"],
            "direction": scenario["direction"],
            "perturbation_percent": scenario[
                "perturbation_percent"
            ],
            "weight_sum": weight_sum,
        }

        for factor in BASELINE_WEIGHTS:
            record[f"{factor}_weight"] = weights[factor]

        weight_records.append(record)

        print(
            f"   PASS: {scenario_name} "
            f"(weight sum = {weight_sum:.10f})"
        )

    weight_df = pd.DataFrame(
        weight_records
    )

    weight_csv = (
        RESULTS_DIR
        / "sensitivity_weight_scenarios.csv"
    )

    weight_df.to_csv(
        weight_csv,
        index=False,
    )

    # --------------------------------------------------------
    # 6.11 RUN SENSITIVITY SCENARIOS
    # --------------------------------------------------------

    print("\n11. RUNNING SENSITIVITY SCENARIOS")

    scenario_summary_records = []
    class_stability_records = []

    baseline_scenario_classes = baseline_classes.copy()

    for scenario in scenarios:

        scenario_name = scenario["scenario"]

        print(
            f"\n   Running: {scenario_name}"
        )

        scenario_weights = scenario["weights"]

        scenario_surface = calculate_susceptibility(
            factors,
            scenario_weights,
            common_mask,
        )

        # Baseline scenario is compared against itself.
        if scenario_name == "baseline":

            scenario_classes = baseline_scenario_classes.copy()

            metrics = {
                "mean_absolute_difference": 0.0,
                "max_absolute_difference": 0.0,
                "spearman_correlation": 1.0,
                "spearman_p_value": 0.0,
                "same_class_agreement_percent": 100.0,
                "changed_class_cells": 0,
                "mean_absolute_class_change": 0.0,
                "baseline_high_very_high_cells": int(
                    np.sum(
                        baseline_classes[common_mask] >= 4
                    )
                ),
                "retained_high_very_high_cells": int(
                    np.sum(
                        baseline_classes[common_mask] >= 4
                    )
                ),
                "high_very_high_retention_percent": 100.0,
                "high_very_high_jaccard_percent": 100.0,
            }

        else:

            scenario_classes = np.full(
                baseline_classes.shape,
                0,
                dtype=np.int16,
            )

            scenario_classes[common_mask] = (
                classify_fixed(
                    scenario_surface[common_mask]
                )
            )

            metrics = calculate_summary_metrics(
                baseline,
                scenario_surface,
                baseline_classes,
                scenario_classes,
                common_mask,
            )

        summary_record = {
            "scenario": scenario_name,
            "target_factor": scenario["target_factor"],
            "direction": scenario["direction"],
            "perturbation_percent": scenario[
                "perturbation_percent"
            ],
            **metrics,
        }

        for factor in BASELINE_WEIGHTS:
            summary_record[f"{factor}_weight"] = (
                scenario_weights[factor]
            )

        scenario_summary_records.append(
            summary_record
        )

        class_stability_records.extend(
            create_class_stability_table(
                scenario_name,
                baseline_classes,
                scenario_classes,
                common_mask,
            )
        )

        if scenario_name == "baseline":
            print("      Baseline established.")

        else:
            print(
                "      Mean absolute difference: "
                f"{metrics['mean_absolute_difference']:.8f}"
            )

            print(
                "      Max absolute difference: "
                f"{metrics['max_absolute_difference']:.8f}"
            )

            print(
                "      Spearman correlation: "
                f"{metrics['spearman_correlation']:.6f}"
            )

            print(
                "      Same-class agreement: "
                f"{metrics['same_class_agreement_percent']:.3f}%"
            )

            print(
                "      Changed class cells: "
                f"{metrics['changed_class_cells']:,}"
            )

            print(
                "      High + Very High retention: "
                f"{metrics['high_very_high_retention_percent']:.3f}%"
            )

    # --------------------------------------------------------
    # 6.12 SAVE SCENARIO SUMMARY
    # --------------------------------------------------------

    print("\n12. SAVING SCENARIO RESULTS")

    scenario_summary_df = pd.DataFrame(
        scenario_summary_records
    )

    scenario_csv = (
        RESULTS_DIR
        / "sensitivity_scenario_summary.csv"
    )

    scenario_summary_df.to_csv(
        scenario_csv,
        index=False,
    )

    print(
        f"   PASS: {scenario_csv}"
    )

    # --------------------------------------------------------
    # 6.13 SAVE CLASS STABILITY
    # --------------------------------------------------------

    class_stability_df = pd.DataFrame(
        class_stability_records
    )

    class_stability_csv = (
        RESULTS_DIR
        / "sensitivity_class_stability.csv"
    )

    class_stability_df.to_csv(
        class_stability_csv,
        index=False,
    )

    print(
        f"   PASS: {class_stability_csv}"
    )

    # --------------------------------------------------------
    # 6.14 IDENTIFY MOST SENSITIVE SCENARIOS
    # --------------------------------------------------------

    non_baseline_df = scenario_summary_df[
        scenario_summary_df["scenario"] != "baseline"
    ].copy()

    most_difference_scenario = (
        non_baseline_df.loc[
            non_baseline_df[
                "mean_absolute_difference"
            ].idxmax(),
            "scenario",
        ]
    )

    least_difference_scenario = (
        non_baseline_df.loc[
            non_baseline_df[
                "mean_absolute_difference"
            ].idxmin(),
            "scenario",
        ]
    )

    lowest_correlation_scenario = (
        non_baseline_df.loc[
            non_baseline_df[
                "spearman_correlation"
            ].idxmin(),
            "scenario",
        ]
    )

    lowest_class_agreement_scenario = (
        non_baseline_df.loc[
            non_baseline_df[
                "same_class_agreement_percent"
            ].idxmin(),
            "scenario",
        ]
    )

    lowest_high_retention_scenario = (
        non_baseline_df.loc[
            non_baseline_df[
                "high_very_high_retention_percent"
            ].idxmin(),
            "scenario",
        ]
    )

    # --------------------------------------------------------
    # 6.15 CREATE OVERALL VALIDATION SUMMARY
    # --------------------------------------------------------

    validation_summary = {
        "phase": "9.9",
        "title": "Sensitivity / Robustness Analysis",
        "method": {
            "baseline": "Phase 8 AHP MCDA weights",
            "perturbation": "One-factor-at-a-time +/-10%",
            "redistribution": (
                "Weight difference redistributed proportionally "
                "among the remaining factors"
            ),
            "scenario_count": len(scenarios),
            "baseline_plus_scenarios": len(scenarios),
            "classification_method": (
                "Fixed Phase 8 quantile thresholds"
            ),
            "thresholds": {
                "Q20": Q20,
                "Q40": Q40,
                "Q60": Q60,
                "Q80": Q80,
            },
            "important_note": (
                "The +/-10% perturbations are controlled "
                "sensitivity scenarios and are not statistical "
                "confidence intervals."
            ),
        },
        "baseline_weights": BASELINE_WEIGHTS,
        "baseline_weight_sum": baseline_weight_sum,
        "grid": {
            "crs": str(baseline_profile["crs"]),
            "width": int(baseline_profile["width"]),
            "height": int(baseline_profile["height"]),
            "resolution_x": float(
                baseline_profile["transform"].a
            ),
            "resolution_y": float(
                abs(baseline_profile["transform"].e)
            ),
            "total_cells": total_cells,
            "common_valid_cells": common_cells,
            "common_valid_percentage": common_percentage,
        },
        "technical_validation": {
            "input_files": "PASS",
            "factor_grid_compatibility": "PASS",
            "weight_normalization": "PASS",
            "baseline_reconstruction": reconstruction_status,
            "classification_reproduction": (
                classification_validation_status
            ),
        },
        "baseline_reconstruction": {
            "maximum_absolute_difference": reconstruction_max,
            "mean_absolute_difference": reconstruction_mean,
        },
        "scenario_interpretation": {
            "largest_mean_absolute_difference": (
                most_difference_scenario
            ),
            "smallest_mean_absolute_difference": (
                least_difference_scenario
            ),
            "lowest_spearman_correlation": (
                lowest_correlation_scenario
            ),
            "lowest_same_class_agreement": (
                lowest_class_agreement_scenario
            ),
            "lowest_high_very_high_retention": (
                lowest_high_retention_scenario
            ),
        },
        "outputs": {
            "scenario_summary": str(
                scenario_csv.relative_to(PROJECT_ROOT)
            ),
            "class_stability": str(
                class_stability_csv.relative_to(PROJECT_ROOT)
            ),
            "weight_scenarios": str(
                weight_csv.relative_to(PROJECT_ROOT)
            ),
        },
    }

    validation_json = (
        RESULTS_DIR
        / "sensitivity_validation_summary.json"
    )

    with open(
        validation_json,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            validation_summary,
            f,
            indent=4,
        )

    # Also save the scenario summary as JSON.
    scenario_json = (
        RESULTS_DIR
        / "sensitivity_scenario_summary.json"
    )

    scenario_json_records = (
        scenario_summary_df
        .replace({np.nan: None})
        .to_dict(orient="records")
    )

    with open(
        scenario_json,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            scenario_json_records,
            f,
            indent=4,
        )

    print(
        f"   PASS: {scenario_json}"
    )

    print(
        f"   PASS: {validation_json}"
    )

    # --------------------------------------------------------
    # 6.16 FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 72)
    print("PHASE 9.9 - ANALYSIS COMPLETE")
    print("=" * 72)

    print(
        "\nScenario count: "
        f"{len(scenarios)}"
    )

    print(
        "\nLargest mean absolute difference:"
        f"\n   {most_difference_scenario}"
    )

    print(
        "\nSmallest mean absolute difference:"
        f"\n   {least_difference_scenario}"
    )

    print(
        "\nLowest Spearman correlation:"
        f"\n   {lowest_correlation_scenario}"
    )

    print(
        "\nLowest same-class agreement:"
        f"\n   {lowest_class_agreement_scenario}"
    )

    print(
        "\nLowest High + Very High retention:"
        f"\n   {lowest_high_retention_scenario}"
    )

    print("\nOutputs:")
    print(
        f"   {scenario_csv}"
    )
    print(
        f"   {scenario_json}"
    )
    print(
        f"   {class_stability_csv}"
    )
    print(
        f"   {weight_csv}"
    )
    print(
        f"   {validation_json}"
    )

    print("\nStatus:")
    print(
        "   PHASE_9_9_SENSITIVITY_ANALYSIS_COMPLETED"
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
