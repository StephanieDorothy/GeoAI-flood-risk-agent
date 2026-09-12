
"""
GeoAI Flood Risk Decision Agent
Phase 9.5 - Terrain Characteristics Relationship Analysis

Purpose
-------
Investigate whether the final flood susceptibility surface behaves
consistently with the terrain characteristics used in the MCDA model.

Terrain factors analyzed:

1. Elevation
2. Slope

The analysis compares:
    - Raw elevation
    - Standardized elevation score
    - Raw slope
    - Standardized slope score
    - Continuous flood susceptibility
    - Classified flood susceptibility

The analysis investigates:
    - Spatial compatibility
    - Common valid-cell overlap
    - Terrain value ranges
    - Terrain characteristics by susceptibility class
    - Continuous susceptibility relationships
    - Spearman correlations
    - Directional consistency with the MCDA factor transformations

This script is a VALIDATION analysis only.

It does NOT:
    - modify MCDA weights
    - modify factor rasters
    - modify susceptibility rasters
    - modify classification thresholds
    - regenerate project outputs
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import rasterio


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw terrain factors
RAW_ELEVATION_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "flood_factors"
    / "elevation.tif"
)

RAW_SLOPE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "flood_factors"
    / "slope.tif"
)

# Standardized terrain factors
ELEVATION_SCORE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
    / "elevation_score.tif"
)

SLOPE_SCORE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
    / "slope_score.tif"
)

# Final susceptibility outputs
CONTINUOUS_SUSCEPTIBILITY_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility.tif"
)

CLASSIFIED_SUSCEPTIBILITY_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility_classified.tif"
)

# Results
RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "terrain_relationship"
)

CSV_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_terrain_relationship.csv"
)

JSON_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_terrain_relationship.json"
)


# ============================================================================
# EXPECTED PROJECT SPECIFICATION
# ============================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019

EXPECTED_CLASSES = [1, 2, 3, 4, 5]

CLASS_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section heading."""

    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def open_raster(path: Path):
    """
    Open a raster and read its first band.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required raster does not exist:\n{path}"
        )

    src = rasterio.open(path)

    array = src.read(1)

    return src, array


def get_valid_mask(
    array: np.ndarray,
    nodata,
) -> np.ndarray:
    """
    Return a boolean mask for valid finite cells.
    """

    if nodata is None:
        mask = np.ones(
            array.shape,
            dtype=bool,
        )
    else:
        mask = array != nodata

    if np.issubdtype(array.dtype, np.floating):
        mask &= np.isfinite(array)

    return mask


def calculate_spearman(
    x: np.ndarray,
    y: np.ndarray,
) -> float:
    """
    Calculate Spearman rank correlation without requiring scipy.

    Ties are handled using average ranks.
    """

    if x.size != y.size:
        raise ValueError(
            "Spearman inputs must have the same number of values."
        )

    if x.size < 2:
        return float("nan")

    def rank_average(values: np.ndarray) -> np.ndarray:
        """
        Return average ranks for tied values.
        """

        order = np.argsort(
            values,
            kind="mergesort",
        )

        sorted_values = values[order]

        ranks = np.empty(
            values.size,
            dtype=np.float64,
        )

        start = 0

        while start < values.size:

            end = start + 1

            while (
                end < values.size
                and
                sorted_values[end]
                == sorted_values[start]
            ):
                end += 1

            average_rank = (
                (start + 1) + end
            ) / 2.0

            ranks[
                order[start:end]
            ] = average_rank

            start = end

        return ranks

    x_ranks = rank_average(x)
    y_ranks = rank_average(y)

    x_centered = (
        x_ranks
        -
        np.mean(x_ranks)
    )

    y_centered = (
        y_ranks
        -
        np.mean(y_ranks)
    )

    denominator = np.sqrt(
        np.sum(x_centered ** 2)
        *
        np.sum(y_centered ** 2)
    )

    if denominator == 0:
        return float("nan")

    return float(
        np.sum(
            x_centered
            *
            y_centered
        )
        /
        denominator
    )


def interpret_correlation(
    correlation: float,
) -> str:
    """
    Provide a simple descriptive interpretation of
    Spearman correlation magnitude.
    """

    if np.isnan(correlation):
        return "UNDEFINED"

    magnitude = abs(correlation)

    if magnitude >= 0.80:
        strength = "VERY_STRONG"
    elif magnitude >= 0.60:
        strength = "STRONG"
    elif magnitude >= 0.40:
        strength = "MODERATE"
    elif magnitude >= 0.20:
        strength = "WEAK"
    else:
        strength = "VERY_WEAK"

    if correlation > 0:
        direction = "POSITIVE"
    elif correlation < 0:
        direction = "NEGATIVE"
    else:
        direction = "NONE"

    return f"{strength}_{direction}"


def describe_values(
    name: str,
    values: np.ndarray,
    unit: str = "",
) -> dict:
    """
    Calculate descriptive statistics for valid numeric values.
    """

    if values.size == 0:
        raise ValueError(
            f"No valid values available for {name}."
        )

    percentiles = np.percentile(
        values,
        [5, 25, 50, 75, 95],
    )

    result = {
        "count": int(values.size),
        "minimum": float(np.min(values)),
        "p05": float(percentiles[0]),
        "p25": float(percentiles[1]),
        "median": float(percentiles[2]),
        "p75": float(percentiles[3]),
        "p95": float(percentiles[4]),
        "maximum": float(np.max(values)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "unit": unit,
    }

    print(f"\n{name}")

    print(
        f"  Count   : {result['count']:,}"
    )

    print(
        f"  Minimum : "
        f"{result['minimum']:.6f} {unit}".rstrip()
    )

    print(
        f"  P05     : "
        f"{result['p05']:.6f} {unit}".rstrip()
    )

    print(
        f"  P25     : "
        f"{result['p25']:.6f} {unit}".rstrip()
    )

    print(
        f"  Median  : "
        f"{result['median']:.6f} {unit}".rstrip()
    )

    print(
        f"  P75     : "
        f"{result['p75']:.6f} {unit}".rstrip()
    )

    print(
        f"  P95     : "
        f"{result['p95']:.6f} {unit}".rstrip()
    )

    print(
        f"  Maximum : "
        f"{result['maximum']:.6f} {unit}".rstrip()
    )

    print(
        f"  Mean    : "
        f"{result['mean']:.6f} {unit}".rstrip()
    )

    print(
        f"  Std     : "
        f"{result['std']:.6f} {unit}".rstrip()
    )

    return result


def compare_spatial_grid(
    reference,
    candidate,
    candidate_name: str,
) -> None:
    """
    Verify that a candidate raster matches the reference raster grid.
    """

    crs_match = (
        reference.crs == candidate.crs
    )

    dimensions_match = (
        reference.width == candidate.width
        and
        reference.height == candidate.height
    )

    resolution_match = np.allclose(
        reference.res,
        candidate.res,
    )

    transform_match = np.allclose(
        reference.transform,
        candidate.transform,
    )

    print(
        f"{candidate_name} CRS: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"{candidate_name} dimensions: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )

    print(
        f"{candidate_name} resolution: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    print(
        f"{candidate_name} transform: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )

    if not (
        crs_match
        and dimensions_match
        and resolution_match
        and transform_match
    ):
        raise ValueError(
            f"{candidate_name} does not match "
            "the reference spatial grid."
        )


def assess_monotonic_relationship(
    values_by_class: list[float],
    direction: str,
) -> tuple[str, bool]:
    """
    Assess whether class means follow an expected monotonic direction.

    direction:
        "increasing"
        "decreasing"
    """

    values = np.asarray(
        values_by_class,
        dtype=np.float64,
    )

    if direction == "increasing":

        is_monotonic = bool(
            np.all(
                np.diff(values) >= 0
            )
        )

    elif direction == "decreasing":

        is_monotonic = bool(
            np.all(
                np.diff(values) <= 0
            )
        )

    else:

        raise ValueError(
            "Direction must be 'increasing' "
            "or 'decreasing'."
        )

    if is_monotonic:
        return "PASS", True

    return "INVESTIGATE", False


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run the Phase 9.5 terrain relationship analysis."""

    print("=" * 72)
    print(
        "PHASE 9.5 - TERRAIN CHARACTERISTICS RELATIONSHIP ANALYSIS"
    )
    print("=" * 72)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nRaw elevation raster:")
    print(RAW_ELEVATION_RASTER)

    print("\nRaw slope raster:")
    print(RAW_SLOPE_RASTER)

    print("\nElevation score raster:")
    print(ELEVATION_SCORE_RASTER)

    print("\nSlope score raster:")
    print(SLOPE_SCORE_RASTER)

    print("\nContinuous susceptibility raster:")
    print(CONTINUOUS_SUSCEPTIBILITY_RASTER)

    print("\nClassified susceptibility raster:")
    print(CLASSIFIED_SUSCEPTIBILITY_RASTER)

    print("\nResults directory:")
    print(RESULTS_DIR)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================================
    # 1. INPUT VALIDATION
    # ========================================================================

    print_header(
        "1. INPUT FILE VALIDATION"
    )

    input_paths = {
        "Raw elevation":
            RAW_ELEVATION_RASTER,

        "Raw slope":
            RAW_SLOPE_RASTER,

        "Elevation score":
            ELEVATION_SCORE_RASTER,

        "Slope score":
            SLOPE_SCORE_RASTER,

        "Continuous susceptibility":
            CONTINUOUS_SUSCEPTIBILITY_RASTER,

        "Classified susceptibility":
            CLASSIFIED_SUSCEPTIBILITY_RASTER,
    }

    for name, path in input_paths.items():

        print(f"\n{name}:")
        print(path)

        if not path.exists():
            raise FileNotFoundError(
                f"{name} raster was not found:\n{path}"
            )

        print("Exists: PASS")

    # ========================================================================
    # OPEN RASTERS
    # ========================================================================

    raw_elevation_src = None
    raw_slope_src = None
    elevation_score_src = None
    slope_score_src = None
    continuous_src = None
    classified_src = None

    try:

        raw_elevation_src, raw_elevation = open_raster(
            RAW_ELEVATION_RASTER
        )

        raw_slope_src, raw_slope = open_raster(
            RAW_SLOPE_RASTER
        )

        elevation_score_src, elevation_score = open_raster(
            ELEVATION_SCORE_RASTER
        )

        slope_score_src, slope_score = open_raster(
            SLOPE_SCORE_RASTER
        )

        continuous_src, continuous_susceptibility = (
            open_raster(
                CONTINUOUS_SUSCEPTIBILITY_RASTER
            )
        )

        classified_src, classified_susceptibility = (
            open_raster(
                CLASSIFIED_SUSCEPTIBILITY_RASTER
            )
        )

        # ====================================================================
        # 2. REFERENCE GRID VALIDATION
        # ====================================================================

        print_header(
            "2. REFERENCE GRID VALIDATION"
        )

        print(
            f"Expected CRS: {EXPECTED_CRS}"
        )

        print(
            f"Actual CRS:   {continuous_src.crs}"
        )

        if (
            continuous_src.crs is None
            or
            continuous_src.crs.to_string()
            != EXPECTED_CRS
        ):
            raise ValueError(
                "Continuous susceptibility CRS does not "
                "match the expected project CRS."
            )

        print("CRS: PASS")

        print(
            f"Expected dimensions: "
            f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
        )

        print(
            f"Actual dimensions:   "
            f"{continuous_src.width} x "
            f"{continuous_src.height}"
        )

        if (
            continuous_src.width
            != EXPECTED_WIDTH
            or
            continuous_src.height
            != EXPECTED_HEIGHT
        ):
            raise ValueError(
                "Continuous susceptibility dimensions "
                "do not match the expected analysis grid."
            )

        print("Dimensions: PASS")

        # ====================================================================
        # 3. SPATIAL COMPATIBILITY
        # ====================================================================

        print_header(
            "3. SPATIAL COMPATIBILITY VALIDATION"
        )

        compare_spatial_grid(
            continuous_src,
            raw_elevation_src,
            "Raw elevation",
        )

        compare_spatial_grid(
            continuous_src,
            raw_slope_src,
            "Raw slope",
        )

        compare_spatial_grid(
            continuous_src,
            elevation_score_src,
            "Elevation score",
        )

        compare_spatial_grid(
            continuous_src,
            slope_score_src,
            "Slope score",
        )

        compare_spatial_grid(
            continuous_src,
            classified_src,
            "Classified susceptibility",
        )

        print(
            "Spatial compatibility: PASS"
        )

        # ====================================================================
        # 4. VALID-CELL OVERLAP
        # ====================================================================

        print_header(
            "4. VALID-CELL OVERLAP"
        )

        elevation_valid = get_valid_mask(
            raw_elevation,
            raw_elevation_src.nodata,
        )

        slope_valid = get_valid_mask(
            raw_slope,
            raw_slope_src.nodata,
        )

        elevation_score_valid = get_valid_mask(
            elevation_score,
            elevation_score_src.nodata,
        )

        slope_score_valid = get_valid_mask(
            slope_score,
            slope_score_src.nodata,
        )

        continuous_valid = get_valid_mask(
            continuous_susceptibility,
            continuous_src.nodata,
        )

        classified_valid = get_valid_mask(
            classified_susceptibility,
            classified_src.nodata,
        )

        total_cells = int(
            continuous_valid.size
        )

        common_mask = (
            elevation_valid
            &
            slope_valid
            &
            elevation_score_valid
            &
            slope_score_valid
            &
            continuous_valid
            &
            classified_valid
        )

        common_cells = int(
            np.count_nonzero(common_mask)
        )

        print(
            f"Total raster cells: "
            f"{total_cells:,}"
        )

        print(
            f"Common valid cells: "
            f"{common_cells:,}"
        )

        print(
            f"Common valid percentage: "
            f"{common_cells / total_cells * 100:.3f}%"
        )

        if common_cells == 0:
            raise ValueError(
                "No common valid cells were found."
            )

        print(
            "Common valid-cell overlap: PASS"
        )

        # ====================================================================
        # EXTRACT COMMON VALUES
        # ====================================================================

        elevation_values = (
            raw_elevation[common_mask]
            .astype(np.float64)
        )

        slope_values = (
            raw_slope[common_mask]
            .astype(np.float64)
        )

        elevation_score_values = (
            elevation_score[common_mask]
            .astype(np.float64)
        )

        slope_score_values = (
            slope_score[common_mask]
            .astype(np.float64)
        )

        susceptibility_values = (
            continuous_susceptibility[common_mask]
            .astype(np.float64)
        )

        class_values = (
            classified_susceptibility[common_mask]
            .astype(np.int16)
        )

        # ====================================================================
        # 5. ELEVATION RANGE
        # ====================================================================

        print_header(
            "5. ELEVATION VALUE VALIDATION"
        )

        elevation_statistics = describe_values(
            "Elevation within common MCDA footprint",
            elevation_values,
            "m",
        )

        # ====================================================================
        # 6. SLOPE RANGE
        # ====================================================================

        print_header(
            "6. SLOPE VALUE VALIDATION"
        )

        slope_statistics = describe_values(
            "Slope within common MCDA footprint",
            slope_values,
            "degrees",
        )

        # ====================================================================
        # 7. STANDARDIZED TERRAIN SCORE RANGES
        # ====================================================================

        print_header(
            "7. STANDARDIZED TERRAIN SCORE VALIDATION"
        )

        elevation_score_statistics = describe_values(
            "Elevation standardized score",
            elevation_score_values,
        )

        slope_score_statistics = describe_values(
            "Slope standardized score",
            slope_score_values,
        )

        elevation_score_range_pass = bool(
            elevation_score_statistics["minimum"]
            >= 0.0
            and
            elevation_score_statistics["maximum"]
            <= 1.0
        )

        slope_score_range_pass = bool(
            slope_score_statistics["minimum"]
            >= 0.0
            and
            slope_score_statistics["maximum"]
            <= 1.0
        )

        print(
            "\nElevation score 0-1 range: "
            f"{'PASS' if elevation_score_range_pass else 'FAIL'}"
        )

        print(
            "Slope score 0-1 range: "
            f"{'PASS' if slope_score_range_pass else 'FAIL'}"
        )

        # ====================================================================
        # 8. CLASS VALUES
        # ====================================================================

        print_header(
            "8. SUSCEPTIBILITY CLASS VALIDATION"
        )

        observed_classes = sorted(
            np.unique(class_values).tolist()
        )

        print(
            f"Observed classes: "
            f"{observed_classes}"
        )

        class_values_pass = (
            observed_classes
            == EXPECTED_CLASSES
        )

        print(
            "All five susceptibility classes present: "
            f"{'PASS' if class_values_pass else 'FAIL'}"
        )

        if not class_values_pass:
            raise ValueError(
                "Unexpected susceptibility class values."
            )

        # ====================================================================
        # 9. TERRAIN CHARACTERISTICS BY CLASS
        # ====================================================================

        print_header(
            "9. TERRAIN CHARACTERISTICS BY SUSCEPTIBILITY CLASS"
        )

        class_results = {}

        elevation_class_means = []
        elevation_score_class_means = []
        slope_class_means = []
        slope_score_class_means = []
        susceptibility_class_means = []

        for class_code in EXPECTED_CLASSES:

            class_mask = (
                class_values == class_code
            )

            class_count = int(
                np.count_nonzero(class_mask)
            )

            if class_count == 0:
                raise ValueError(
                    f"Class {class_code} contains no cells."
                )

            class_elevation = (
                elevation_values[class_mask]
            )

            class_elevation_score = (
                elevation_score_values[class_mask]
            )

            class_slope = (
                slope_values[class_mask]
            )

            class_slope_score = (
                slope_score_values[class_mask]
            )

            class_susceptibility = (
                susceptibility_values[class_mask]
            )

            mean_elevation = float(
                np.mean(class_elevation)
            )

            median_elevation = float(
                np.median(class_elevation)
            )

            mean_elevation_score = float(
                np.mean(class_elevation_score)
            )

            mean_slope = float(
                np.mean(class_slope)
            )

            median_slope = float(
                np.median(class_slope)
            )

            mean_slope_score = float(
                np.mean(class_slope_score)
            )

            mean_susceptibility = float(
                np.mean(class_susceptibility)
            )

            elevation_class_means.append(
                mean_elevation
            )

            elevation_score_class_means.append(
                mean_elevation_score
            )

            slope_class_means.append(
                mean_slope
            )

            slope_score_class_means.append(
                mean_slope_score
            )

            susceptibility_class_means.append(
                mean_susceptibility
            )

            class_results[str(class_code)] = {
                "class_name":
                    CLASS_NAMES[class_code],

                "cell_count":
                    class_count,

                "mean_elevation_m":
                    mean_elevation,

                "median_elevation_m":
                    median_elevation,

                "mean_elevation_score":
                    mean_elevation_score,

                "mean_slope_degrees":
                    mean_slope,

                "median_slope_degrees":
                    median_slope,

                "mean_slope_score":
                    mean_slope_score,

                "mean_continuous_susceptibility":
                    mean_susceptibility,
            }

            print(
                f"\n{class_code} - "
                f"{CLASS_NAMES[class_code]}"
            )

            print(
                f"  Cells: "
                f"{class_count:,}"
            )

            print(
                f"  Mean elevation: "
                f"{mean_elevation:.3f} m"
            )

            print(
                f"  Median elevation: "
                f"{median_elevation:.3f} m"
            )

            print(
                f"  Mean elevation score: "
                f"{mean_elevation_score:.6f}"
            )

            print(
                f"  Mean slope: "
                f"{mean_slope:.3f} degrees"
            )

            print(
                f"  Median slope: "
                f"{median_slope:.3f} degrees"
            )

            print(
                f"  Mean slope score: "
                f"{mean_slope_score:.6f}"
            )

            print(
                f"  Mean susceptibility: "
                f"{mean_susceptibility:.6f}"
            )

        # ====================================================================
        # 10. CLASS-ORDER RELATIONSHIPS
        # ====================================================================

        print_header(
            "10. CLASS-ORDER RELATIONSHIP ASSESSMENT"
        )

        # The exact expected direction depends on how the factor was
        # standardized. We therefore test the relationship between
        # the standardized score and susceptibility first.
        #
        # For both terrain factors, a higher standardized score should
        # correspond to a higher contribution to susceptibility.
        #
        # This is the key model-consistency check.

        elevation_score_order_status, elevation_score_monotonic = (
            assess_monotonic_relationship(
                elevation_score_class_means,
                "increasing",
            )
        )

        slope_score_order_status, slope_score_monotonic = (
            assess_monotonic_relationship(
                slope_score_class_means,
                "increasing",
            )
        )

        susceptibility_order_status, susceptibility_monotonic = (
            assess_monotonic_relationship(
                susceptibility_class_means,
                "increasing",
            )
        )

        print(
            "Mean elevation score increases with "
            "susceptibility class: "
            f"{elevation_score_order_status}"
        )

        print(
            "Mean slope score increases with "
            "susceptibility class: "
            f"{slope_score_order_status}"
        )

        print(
            "Mean continuous susceptibility increases "
            "with class: "
            f"{susceptibility_order_status}"
        )

        # ====================================================================
        # 11. CONTINUOUS SUSCEPTIBILITY CORRELATIONS
        # ====================================================================

        print_header(
            "11. CONTINUOUS SUSCEPTIBILITY VS TERRAIN"
        )

        elevation_vs_susceptibility = calculate_spearman(
            elevation_values,
            susceptibility_values,
        )

        elevation_score_vs_susceptibility = calculate_spearman(
            elevation_score_values,
            susceptibility_values,
        )

        slope_vs_susceptibility = calculate_spearman(
            slope_values,
            susceptibility_values,
        )

        slope_score_vs_susceptibility = calculate_spearman(
            slope_score_values,
            susceptibility_values,
        )

        print(
            "Elevation vs continuous susceptibility:"
        )

        print(
            f"  Spearman correlation: "
            f"{elevation_vs_susceptibility:.6f}"
        )

        print(
            "  Interpretation: "
            f"{interpret_correlation(elevation_vs_susceptibility)}"
        )

        print(
            "\nElevation score vs continuous susceptibility:"
        )

        print(
            f"  Spearman correlation: "
            f"{elevation_score_vs_susceptibility:.6f}"
        )

        print(
            "  Interpretation: "
            f"{interpret_correlation(elevation_score_vs_susceptibility)}"
        )

        print(
            "\nSlope vs continuous susceptibility:"
        )

        print(
            f"  Spearman correlation: "
            f"{slope_vs_susceptibility:.6f}"
        )

        print(
            "  Interpretation: "
            f"{interpret_correlation(slope_vs_susceptibility)}"
        )

        print(
            "\nSlope score vs continuous susceptibility:"
        )

        print(
            f"  Spearman correlation: "
            f"{slope_score_vs_susceptibility:.6f}"
        )

        print(
            "  Interpretation: "
            f"{interpret_correlation(slope_score_vs_susceptibility)}"
        )

        # ====================================================================
        # 12. DIRECTIONAL CONSISTENCY
        # ====================================================================

        print_header(
            "12. TERRAIN DIRECTIONAL CONSISTENCY"
        )

        elevation_direction_consistent = (
            elevation_score_vs_susceptibility >= 0
        )

        slope_direction_consistent = (
            slope_score_vs_susceptibility >= 0
        )

        print(
            "Elevation score vs susceptibility direction: "
            f"{'CONSISTENT' if elevation_direction_consistent else 'INVESTIGATE'}"
        )

        print(
            "Slope score vs susceptibility direction: "
            f"{'CONSISTENT' if slope_direction_consistent else 'INVESTIGATE'}"
        )

        # ====================================================================
        # 13. OVERALL ASSESSMENT
        # ====================================================================

        print_header(
            "13. OVERALL TERRAIN-RELATIONSHIP ASSESSMENT"
        )

        directional_pass = (
            elevation_direction_consistent
            and
            slope_direction_consistent
        )

        class_order_pass = (
            elevation_score_monotonic
            and
            slope_score_monotonic
            and
            susceptibility_monotonic
        )

        if directional_pass and class_order_pass:

            overall_status = "CONSISTENT"

        elif directional_pass:

            overall_status = "PARTIALLY_CONSISTENT"

        else:

            overall_status = "INVESTIGATE"

        print(
            "Terrain relationship status:"
        )

        print(
            overall_status
        )

        # ====================================================================
        # 14. SAVE CSV
        # ====================================================================

        print_header(
            "14. SAVE CSV RESULTS"
        )

        csv_rows = []

        for class_code in EXPECTED_CLASSES:

            result = class_results[
                str(class_code)
            ]

            csv_rows.append(
                {
                    "class_code":
                        class_code,

                    "class_name":
                        result["class_name"],

                    "cell_count":
                        result["cell_count"],

                    "mean_elevation_m":
                        result["mean_elevation_m"],

                    "median_elevation_m":
                        result["median_elevation_m"],

                    "mean_elevation_score":
                        result["mean_elevation_score"],

                    "mean_slope_degrees":
                        result["mean_slope_degrees"],

                    "median_slope_degrees":
                        result["median_slope_degrees"],

                    "mean_slope_score":
                        result["mean_slope_score"],

                    "mean_continuous_susceptibility":
                        result[
                            "mean_continuous_susceptibility"
                        ],
                }
            )

        fieldnames = [
            "class_code",
            "class_name",
            "cell_count",
            "mean_elevation_m",
            "median_elevation_m",
            "mean_elevation_score",
            "mean_slope_degrees",
            "median_slope_degrees",
            "mean_slope_score",
            "mean_continuous_susceptibility",
        ]

        with open(
            CSV_OUTPUT,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(
                csv_rows
            )

        if not CSV_OUTPUT.exists():
            raise RuntimeError(
                "CSV output was not created."
            )

        print(
            f"CSV saved to:\n"
            f"{CSV_OUTPUT}"
        )

        print(
            "CSV output: PASS"
        )

        # ====================================================================
        # 15. SAVE JSON
        # ====================================================================

        print_header(
            "15. SAVE JSON RESULTS"
        )

        report = {
            "phase":
                "9.5",

            "analysis":
                "Terrain Characteristics Relationship Analysis",

            "purpose":
                "Investigate relationships between elevation, "
                "slope, and the final flood susceptibility surface.",

            "project_crs":
                EXPECTED_CRS,

            "expected_dimensions": {
                "width":
                    EXPECTED_WIDTH,

                "height":
                    EXPECTED_HEIGHT,
            },

            "inputs": {
                "raw_elevation":
                    str(
                        RAW_ELEVATION_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "raw_slope":
                    str(
                        RAW_SLOPE_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "elevation_score":
                    str(
                        ELEVATION_SCORE_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "slope_score":
                    str(
                        SLOPE_SCORE_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "continuous_susceptibility":
                    str(
                        CONTINUOUS_SUSCEPTIBILITY_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "classified_susceptibility":
                    str(
                        CLASSIFIED_SUSCEPTIBILITY_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),
            },

            "cell_accounting": {
                "total_cells":
                    total_cells,

                "common_valid_cells":
                    common_cells,

                "common_valid_percentage":
                    float(
                        common_cells
                        /
                        total_cells
                        *
                        100
                    ),
            },

            "elevation_statistics":
                elevation_statistics,

            "slope_statistics":
                slope_statistics,

            "elevation_score_statistics":
                elevation_score_statistics,

            "slope_score_statistics":
                slope_score_statistics,

            "terrain_score_range_validation": {
                "elevation_score_0_1":
                    elevation_score_range_pass,

                "slope_score_0_1":
                    slope_score_range_pass,
            },

            "observed_classes":
                observed_classes,

            "class_results":
                class_results,

            "class_order_assessment": {
                "elevation_score_increases":
                    elevation_score_monotonic,

                "slope_score_increases":
                    slope_score_monotonic,

                "continuous_susceptibility_increases":
                    susceptibility_monotonic,
            },

            "correlations": {
                "elevation_vs_continuous_susceptibility":
                    {
                        "spearman":
                            elevation_vs_susceptibility,

                        "interpretation":
                            interpret_correlation(
                                elevation_vs_susceptibility
                            ),
                    },

                "elevation_score_vs_continuous_susceptibility":
                    {
                        "spearman":
                            elevation_score_vs_susceptibility,

                        "interpretation":
                            interpret_correlation(
                                elevation_score_vs_susceptibility
                            ),
                    },

                "slope_vs_continuous_susceptibility":
                    {
                        "spearman":
                            slope_vs_susceptibility,

                        "interpretation":
                            interpret_correlation(
                                slope_vs_susceptibility
                            ),
                    },

                "slope_score_vs_continuous_susceptibility":
                    {
                        "spearman":
                            slope_score_vs_susceptibility,

                        "interpretation":
                            interpret_correlation(
                                slope_score_vs_susceptibility
                            ),
                    },
            },

            "directional_consistency": {
                "elevation":
                    elevation_direction_consistent,

                "slope":
                    slope_direction_consistent,
            },

            "overall_status":
                overall_status,

            "model_modified":
                False,

            "classification_modified":
                False,
        }

        with open(
            JSON_OUTPUT,
            "w",
            encoding="utf-8",
        ) as json_file:

            json.dump(
                report,
                json_file,
                indent=4,
            )

        if not JSON_OUTPUT.exists():
            raise RuntimeError(
                "JSON output was not created."
            )

        print(
            f"JSON saved to:\n"
            f"{JSON_OUTPUT}"
        )

        print(
            "JSON output: PASS"
        )

    finally:

        if raw_elevation_src is not None:
            raw_elevation_src.close()

        if raw_slope_src is not None:
            raw_slope_src.close()

        if elevation_score_src is not None:
            elevation_score_src.close()

        if slope_score_src is not None:
            slope_score_src.close()

        if continuous_src is not None:
            continuous_src.close()

        if classified_src is not None:
            classified_src.close()

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print("\n" + "=" * 72)
    print(
        "PHASE 9.5 ANALYSIS COMPLETED"
    )
    print("=" * 72)

    print(
        "\nCommon valid cells:"
    )

    print(
        f"{common_cells:,}"
    )

    print(
        "\nElevation vs continuous susceptibility:"
    )

    print(
        f"{elevation_vs_susceptibility:.6f}"
    )

    print(
        "\nElevation score vs continuous susceptibility:"
    )

    print(
        f"{elevation_score_vs_susceptibility:.6f}"
    )

    print(
        "\nSlope vs continuous susceptibility:"
    )

    print(
        f"{slope_vs_susceptibility:.6f}"
    )

    print(
        "\nSlope score vs continuous susceptibility:"
    )

    print(
        f"{slope_score_vs_susceptibility:.6f}"
    )

    print(
        "\nTerrain relationship status:"
    )

    print(
        overall_status
    )

    print(
        "\nOutputs:"
    )

    print(
        CSV_OUTPUT
    )

    print(
        JSON_OUTPUT
    )


if __name__ == "__main__":
    main()

