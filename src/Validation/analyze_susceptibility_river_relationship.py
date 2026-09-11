
"""
GeoAI Flood Risk Decision Agent
Phase 9.4 - River-Proximity Relationship Analysis

Purpose
-------
Evaluate whether the flood susceptibility model behaves consistently
with the established inverse relationship between river distance and
flood susceptibility.

Expected relationship
---------------------
Closer to rivers -> higher susceptibility contribution
Farther from rivers -> lower susceptibility contribution

The analysis examines:

1. Input raster compatibility
2. Valid-cell overlap
3. River distance statistics by susceptibility class
4. Standardized river-score statistics by susceptibility class
5. Continuous susceptibility versus river distance
6. Spearman rank correlation
7. Monotonic class-order assessment
8. CSV and JSON evidence outputs

Inputs
------
data/analysis/flood_factors/distance_to_rivers.tif
data/analysis/aligned/distance_to_rivers_score.tif
data/analysis/mcda/flood_susceptibility.tif
data/analysis/mcda/flood_susceptibility_classified.tif

Outputs
-------
results/phase9_validation/river_relationship/
    susceptibility_river_relationship.csv
    susceptibility_river_relationship.json

Classification
--------------
1 = Very Low
2 = Low
3 = Moderate
4 = High
5 = Very High

CRS
---
EPSG:32737

Important
---------
This analysis evaluates model behaviour and internal consistency.
It does not establish predictive accuracy against observed flood events.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DISTANCE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "flood_factors"
    / "distance_to_rivers.tif"
)

RIVER_SCORE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
    / "distance_to_rivers_score.tif"
)

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

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "river_relationship"
)

SUMMARY_CSV = (
    RESULTS_DIR
    / "susceptibility_river_relationship.csv"
)

SUMMARY_JSON = (
    RESULTS_DIR
    / "susceptibility_river_relationship.json"
)


# ============================================================================
# EXPECTED RASTER SPECIFICATION
# ============================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019

EXPECTED_CLASSES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}

CLASS_CODES = list(EXPECTED_CLASSES.keys())


# ============================================================================
# GENERAL HELPERS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted terminal section header."""

    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def read_raster(path: Path):
    """
    Open a raster and return its array and spatial metadata.

    Returns
    -------
    tuple
        array, profile information
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required raster was not found:\n{path}"
        )

    src = rasterio.open(path)

    array = src.read(1)

    metadata = {
        "crs": src.crs,
        "width": src.width,
        "height": src.height,
        "transform": src.transform,
        "resolution": src.res,
        "nodata": src.nodata,
        "dtype": src.dtypes[0],
    }

    return src, array, metadata


def validate_spatial_compatibility(
    reference_metadata: dict,
    other_metadata: dict,
    reference_name: str,
    other_name: str,
) -> None:
    """
    Validate that two rasters share the same spatial grid.
    """

    crs_match = (
        reference_metadata["crs"]
        == other_metadata["crs"]
    )

    dimensions_match = (
        reference_metadata["width"]
        == other_metadata["width"]
        and
        reference_metadata["height"]
        == other_metadata["height"]
    )

    transform_match = np.allclose(
        reference_metadata["transform"],
        other_metadata["transform"],
    )

    resolution_match = np.allclose(
        reference_metadata["resolution"],
        other_metadata["resolution"],
    )

    print(
        f"{other_name} CRS match: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"{other_name} dimensions match: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )

    print(
        f"{other_name} transform match: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )

    print(
        f"{other_name} resolution match: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    if not crs_match:
        raise ValueError(
            f"CRS mismatch between "
            f"{reference_name} and {other_name}."
        )

    if not dimensions_match:
        raise ValueError(
            f"Dimension mismatch between "
            f"{reference_name} and {other_name}."
        )

    if not transform_match:
        raise ValueError(
            f"Transform mismatch between "
            f"{reference_name} and {other_name}."
        )

    if not resolution_match:
        raise ValueError(
            f"Resolution mismatch between "
            f"{reference_name} and {other_name}."
        )


def valid_mask_from_raster(
    array: np.ndarray,
    nodata,
) -> np.ndarray:
    """
    Create a robust valid-data mask.

    Handles explicit NoData values and NaN values.
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


def spearman_rank_correlation(
    x: np.ndarray,
    y: np.ndarray,
) -> float:
    """
    Calculate Spearman rank correlation without SciPy.

    Tied values are assigned their average rank.

    Parameters
    ----------
    x, y : np.ndarray
        One-dimensional numeric arrays.

    Returns
    -------
    float
        Spearman rank correlation coefficient.
    """

    if len(x) != len(y):
        raise ValueError(
            "Correlation arrays must have equal length."
        )

    if len(x) < 2:
        return float("nan")

    x_series = pd.Series(x)
    y_series = pd.Series(y)

    x_ranks = x_series.rank(
        method="average"
    ).to_numpy()

    y_ranks = y_series.rank(
        method="average"
    ).to_numpy()

    x_centered = (
        x_ranks - np.mean(x_ranks)
    )

    y_centered = (
        y_ranks - np.mean(y_ranks)
    )

    denominator = (
        np.sqrt(
            np.sum(x_centered ** 2)
            *
            np.sum(y_centered ** 2)
        )
    )

    if denominator == 0:
        return float("nan")

    correlation = (
        np.sum(
            x_centered * y_centered
        )
        / denominator
    )

    return float(correlation)


def interpret_correlation(
    correlation: float,
) -> str:
    """
    Provide a conservative interpretation of the Spearman correlation.
    """

    if np.isnan(correlation):
        return "UNDETERMINED"

    if correlation <= -0.70:
        return "STRONG_NEGATIVE"

    if correlation <= -0.40:
        return "MODERATE_NEGATIVE"

    if correlation <= -0.20:
        return "WEAK_NEGATIVE"

    if correlation < 0.20:
        return "VERY_WEAK_OR_NO_MONOTONIC_RELATIONSHIP"

    if correlation < 0.40:
        return "WEAK_POSITIVE"

    if correlation < 0.70:
        return "MODERATE_POSITIVE"

    return "STRONG_POSITIVE"


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main() -> None:
    """
    Execute Phase 9.4 river-proximity relationship analysis.
    """

    print("=" * 72)
    print("PHASE 9.4 - RIVER-PROXIMITY RELATIONSHIP ANALYSIS")
    print("=" * 72)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nRaw distance raster:")
    print(RAW_DISTANCE_RASTER)

    print("\nRiver score raster:")
    print(RIVER_SCORE_RASTER)

    print("\nContinuous susceptibility raster:")
    print(CONTINUOUS_SUSCEPTIBILITY_RASTER)

    print("\nClassified susceptibility raster:")
    print(CLASSIFIED_SUSCEPTIBILITY_RASTER)

    print("\nResults directory:")
    print(RESULTS_DIR)

    # ------------------------------------------------------------------------
    # Create results directory.
    # ------------------------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------------
    # Confirm all input files exist.
    # ------------------------------------------------------------------------

    print_header("1. INPUT FILE VALIDATION")

    input_paths = {
        "Raw distance": RAW_DISTANCE_RASTER,
        "River score": RIVER_SCORE_RASTER,
        "Continuous susceptibility":
            CONTINUOUS_SUSCEPTIBILITY_RASTER,
        "Classified susceptibility":
            CLASSIFIED_SUSCEPTIBILITY_RASTER,
    }

    for name, path in input_paths.items():

        print(f"{name}:")
        print(path)

        if not path.exists():
            raise FileNotFoundError(
                f"{name} raster not found:\n{path}"
            )

        print("Exists: PASS\n")

    # ------------------------------------------------------------------------
    # Open all rasters.
    # ------------------------------------------------------------------------

    raw_distance_src = None
    river_score_src = None
    continuous_src = None
    classified_src = None

    try:

        (
            raw_distance_src,
            raw_distance,
            raw_distance_meta,
        ) = read_raster(
            RAW_DISTANCE_RASTER
        )

        (
            river_score_src,
            river_score,
            river_score_meta,
        ) = read_raster(
            RIVER_SCORE_RASTER
        )

        (
            continuous_src,
            continuous_susceptibility,
            continuous_meta,
        ) = read_raster(
            CONTINUOUS_SUSCEPTIBILITY_RASTER
        )

        (
            classified_src,
            classified_susceptibility,
            classified_meta,
        ) = read_raster(
            CLASSIFIED_SUSCEPTIBILITY_RASTER
        )

        # --------------------------------------------------------------------
        # Validate CRS and dimensions.
        # --------------------------------------------------------------------

        print_header("2. SPATIAL COMPATIBILITY VALIDATION")

        print(
            f"Expected CRS: {EXPECTED_CRS}"
        )

        print(
            f"Reference CRS: "
            f"{continuous_meta['crs']}"
        )

        if (
            continuous_meta["crs"] is None
            or
            continuous_meta["crs"].to_string()
            != EXPECTED_CRS
        ):
            raise ValueError(
                "Continuous susceptibility raster CRS "
                "does not match the expected project CRS."
            )

        print("Reference CRS: PASS")

        print(
            f"Expected dimensions: "
            f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
        )

        print(
            f"Reference dimensions: "
            f"{continuous_meta['width']} x "
            f"{continuous_meta['height']}"
        )

        if (
            continuous_meta["width"]
            != EXPECTED_WIDTH
            or
            continuous_meta["height"]
            != EXPECTED_HEIGHT
        ):
            raise ValueError(
                "Continuous susceptibility raster dimensions "
                "do not match the project grid."
            )

        print("Reference dimensions: PASS")

        validate_spatial_compatibility(
            continuous_meta,
            raw_distance_meta,
            "continuous susceptibility",
            "raw distance",
        )

        validate_spatial_compatibility(
            continuous_meta,
            river_score_meta,
            "continuous susceptibility",
            "river score",
        )

        validate_spatial_compatibility(
            continuous_meta,
            classified_meta,
            "continuous susceptibility",
            "classified susceptibility",
        )

        print("Spatial compatibility: PASS")

        # --------------------------------------------------------------------
        # Build valid masks.
        # --------------------------------------------------------------------

        print_header("3. VALID-CELL OVERLAP")

        raw_distance_valid = valid_mask_from_raster(
            raw_distance,
            raw_distance_meta["nodata"],
        )

        river_score_valid = valid_mask_from_raster(
            river_score,
            river_score_meta["nodata"],
        )

        continuous_valid = valid_mask_from_raster(
            continuous_susceptibility,
            continuous_meta["nodata"],
        )

        classified_valid = valid_mask_from_raster(
            classified_susceptibility,
            classified_meta["nodata"],
        )

        common_valid = (
            raw_distance_valid
            &
            river_score_valid
            &
            continuous_valid
            &
            classified_valid
        )

        total_cells = int(
            common_valid.size
        )

        common_valid_cells = int(
            np.count_nonzero(common_valid)
        )

        print(
            f"Total raster cells: "
            f"{total_cells:,}"
        )

        print(
            f"Common valid cells: "
            f"{common_valid_cells:,}"
        )

        if common_valid_cells == 0:
            raise ValueError(
                "No common valid cells exist across the "
                "required rasters."
            )

        print("Common valid-cell overlap: PASS")

        # --------------------------------------------------------------------
        # Extract common valid values.
        # --------------------------------------------------------------------

        distance_values = (
            raw_distance[common_valid]
            .astype(np.float64)
        )

        river_score_values = (
            river_score[common_valid]
            .astype(np.float64)
        )

        susceptibility_values = (
            continuous_susceptibility[common_valid]
            .astype(np.float64)
        )

        class_values = (
            classified_susceptibility[common_valid]
            .astype(np.int16)
        )

        # --------------------------------------------------------------------
        # Validate distance values.
        # --------------------------------------------------------------------

        print_header("4. RIVER-DISTANCE VALUE VALIDATION")

        print(
            f"Minimum distance: "
            f"{np.min(distance_values):.6f} m"
        )

        print(
            f"Median distance: "
            f"{np.median(distance_values):.6f} m"
        )

        print(
            f"Maximum distance: "
            f"{np.max(distance_values):.6f} m"
        )

        if np.min(distance_values) < 0:
            raise ValueError(
                "Negative river-distance values were detected."
            )

        if not np.all(
            np.isfinite(distance_values)
        ):
            raise ValueError(
                "Non-finite river-distance values were detected."
            )

        print("Distance values: PASS")

        # --------------------------------------------------------------------
        # Validate river score.
        # --------------------------------------------------------------------

        print_header("5. STANDARDIZED RIVER-SCORE VALIDATION")

        print(
            f"Minimum river score: "
            f"{np.min(river_score_values):.6f}"
        )

        print(
            f"Maximum river score: "
            f"{np.max(river_score_values):.6f}"
        )

        print(
            f"Mean river score: "
            f"{np.mean(river_score_values):.6f}"
        )

        if (
            np.min(river_score_values) < -1e-6
            or
            np.max(river_score_values) > 1 + 1e-6
        ):
            raise ValueError(
                "River score contains values outside "
                "the expected 0-1 range."
            )

        print("River score 0-1 range: PASS")

        # --------------------------------------------------------------------
        # Validate classes.
        # --------------------------------------------------------------------

        print_header("6. SUSCEPTIBILITY CLASS VALIDATION")

        observed_classes = np.unique(
            class_values
        )

        print(
            "Observed classes:",
            observed_classes.tolist(),
        )

        expected_class_set = set(
            CLASS_CODES
        )

        observed_class_set = set(
            int(value)
            for value in observed_classes
        )

        unexpected_classes = (
            observed_class_set
            - expected_class_set
        )

        if unexpected_classes:
            raise ValueError(
                "Unexpected susceptibility classes found: "
                f"{sorted(unexpected_classes)}"
            )

        missing_classes = (
            expected_class_set
            - observed_class_set
        )

        if missing_classes:
            raise ValueError(
                "Expected susceptibility classes are missing: "
                f"{sorted(missing_classes)}"
            )

        print(
            "All five susceptibility classes present: PASS"
        )

        # --------------------------------------------------------------------
        # Calculate statistics by class.
        # --------------------------------------------------------------------

        print_header(
            "7. RIVER DISTANCE BY SUSCEPTIBILITY CLASS"
        )

        records = []

        for class_code, class_name in EXPECTED_CLASSES.items():

            class_mask = (
                class_values == class_code
            )

            class_distances = (
                distance_values[class_mask]
            )

            class_river_scores = (
                river_score_values[class_mask]
            )

            class_susceptibility = (
                susceptibility_values[class_mask]
            )

            cell_count = int(
                len(class_distances)
            )

            if cell_count == 0:
                raise ValueError(
                    f"No valid cells found for class "
                    f"{class_code}."
                )

            record = {
                "class_code": class_code,
                "class_name": class_name,
                "cell_count": cell_count,

                "mean_river_distance_m":
                    float(
                        np.mean(
                            class_distances
                        )
                    ),

                "median_river_distance_m":
                    float(
                        np.median(
                            class_distances
                        )
                    ),

                "minimum_river_distance_m":
                    float(
                        np.min(
                            class_distances
                        )
                    ),

                "maximum_river_distance_m":
                    float(
                        np.max(
                            class_distances
                        )
                    ),

                "std_river_distance_m":
                    float(
                        np.std(
                            class_distances
                        )
                    ),

                "mean_river_score":
                    float(
                        np.mean(
                            class_river_scores
                        )
                    ),

                "median_river_score":
                    float(
                        np.median(
                            class_river_scores
                        )
                    ),

                "mean_continuous_susceptibility":
                    float(
                        np.mean(
                            class_susceptibility
                        )
                    ),

                "median_continuous_susceptibility":
                    float(
                        np.median(
                            class_susceptibility
                        )
                    ),
            }

            records.append(record)

            print(
                f"{class_code} - {class_name}"
            )

            print(
                f"  Cells: "
                f"{cell_count:,}"
            )

            print(
                f"  Mean river distance: "
                f"{record['mean_river_distance_m']:.3f} m"
            )

            print(
                f"  Median river distance: "
                f"{record['median_river_distance_m']:.3f} m"
            )

            print(
                f"  Mean river score: "
                f"{record['mean_river_score']:.6f}"
            )

            print(
                f"  Mean susceptibility: "
                f"{record['mean_continuous_susceptibility']:.6f}"
            )

        # --------------------------------------------------------------------
        # Assess class-order relationship.
        # --------------------------------------------------------------------

        print_header(
            "8. CLASS-ORDER RELATIONSHIP ASSESSMENT"
        )

        mean_distances = np.array(
            [
                record[
                    "mean_river_distance_m"
                ]
                for record in records
            ]
        )

        mean_river_scores = np.array(
            [
                record[
                    "mean_river_score"
                ]
                for record in records
            ]
        )

        mean_susceptibility = np.array(
            [
                record[
                    "mean_continuous_susceptibility"
                ]
                for record in records
            ]
        )

        # Expected:
        # Higher class -> lower distance.
        distance_differences = np.diff(
            mean_distances
        )

        distance_monotonic = bool(
            np.all(
                distance_differences <= 0
            )
        )

        # Expected:
        # Higher class -> higher river score.
        score_differences = np.diff(
            mean_river_scores
        )

        score_monotonic = bool(
            np.all(
                score_differences >= 0
            )
        )

        # Expected:
        # Higher class -> higher continuous susceptibility.
        susceptibility_differences = np.diff(
            mean_susceptibility
        )

        susceptibility_monotonic = bool(
            np.all(
                susceptibility_differences >= 0
            )
        )

        print(
            "Mean river distance decreases "
            "with susceptibility class: "
            f"{'PASS' if distance_monotonic else 'INVESTIGATE'}"
        )

        print(
            "Mean river score increases "
            "with susceptibility class: "
            f"{'PASS' if score_monotonic else 'INVESTIGATE'}"
        )

        print(
            "Mean continuous susceptibility increases "
            "with class: "
            f"{'PASS' if susceptibility_monotonic else 'INVESTIGATE'}"
        )

        # --------------------------------------------------------------------
        # Continuous relationship.
        # --------------------------------------------------------------------

        print_header(
            "9. CONTINUOUS SUSCEPTIBILITY VS RIVER DISTANCE"
        )

        spearman_distance = (
            spearman_rank_correlation(
                distance_values,
                susceptibility_values,
            )
        )

        spearman_score = (
            spearman_rank_correlation(
                river_score_values,
                susceptibility_values,
            )
        )

        distance_interpretation = (
            interpret_correlation(
                spearman_distance
            )
        )

        score_interpretation = (
            interpret_correlation(
                spearman_score
            )
        )

        print(
            "Spearman correlation:"
        )

        print(
            "River distance vs continuous susceptibility: "
            f"{spearman_distance:.6f}"
        )

        print(
            "Interpretation: "
            f"{distance_interpretation}"
        )

        print()

        print(
            "River score vs continuous susceptibility: "
            f"{spearman_score:.6f}"
        )

        print(
            "Interpretation: "
            f"{score_interpretation}"
        )

        # --------------------------------------------------------------------
        # Overall river relationship status.
        # --------------------------------------------------------------------

        if (
            distance_monotonic
            and score_monotonic
            and spearman_distance <= -0.40
        ):

            relationship_status = (
                "CONSISTENT_WITH_EXPECTED_RIVER_RELATIONSHIP"
            )

        elif (
            spearman_distance <= -0.20
            or
            distance_monotonic
            or
            score_monotonic
        ):

            relationship_status = (
                "PARTIALLY_CONSISTENT"
            )

        else:

            relationship_status = (
                "INVESTIGATE_RIVER_RELATIONSHIP"
            )

        print_header(
            "10. OVERALL RIVER-RELATIONSHIP ASSESSMENT"
        )

        print(
            "River relationship status:"
        )

        print(
            relationship_status
        )

        # --------------------------------------------------------------------
        # Save CSV.
        # --------------------------------------------------------------------

        print_header("11. SAVE CSV RESULTS")

        summary_df = pd.DataFrame(
            records
        )

        summary_df.to_csv(
            SUMMARY_CSV,
            index=False,
        )

        if not SUMMARY_CSV.exists():
            raise RuntimeError(
                "CSV output was not created."
            )

        print(
            f"CSV saved to:\n{SUMMARY_CSV}"
        )

        print("CSV output: PASS")

        # --------------------------------------------------------------------
        # Prepare JSON report.
        # --------------------------------------------------------------------

        json_report = {
            "phase": "9.4",
            "analysis":
                "River-Proximity Relationship Analysis",

            "expected_relationship":
                "Closer to rivers -> higher susceptibility",

            "project_crs":
                EXPECTED_CRS,

            "input_rasters": {
                "raw_distance":
                    str(
                        RAW_DISTANCE_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "river_score":
                    str(
                        RIVER_SCORE_RASTER.relative_to(
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

            "total_cells":
                total_cells,

            "common_valid_cells":
                common_valid_cells,

            "distance_statistics": {
                "minimum_m":
                    float(
                        np.min(
                            distance_values
                        )
                    ),

                "median_m":
                    float(
                        np.median(
                            distance_values
                        )
                    ),

                "maximum_m":
                    float(
                        np.max(
                            distance_values
                        )
                    ),

                "mean_m":
                    float(
                        np.mean(
                            distance_values
                        )
                    ),

                "std_m":
                    float(
                        np.std(
                            distance_values
                        )
                    ),
            },

            "continuous_relationship": {
                "spearman_distance_vs_susceptibility":
                    spearman_distance,

                "distance_relationship_interpretation":
                    distance_interpretation,

                "spearman_river_score_vs_susceptibility":
                    spearman_score,

                "river_score_relationship_interpretation":
                    score_interpretation,
            },

            "class_order_assessment": {
                "mean_distance_decreases_with_class":
                    distance_monotonic,

                "mean_river_score_increases_with_class":
                    score_monotonic,

                "mean_susceptibility_increases_with_class":
                    susceptibility_monotonic,
            },

            "relationship_status":
                relationship_status,

            "class_statistics":
                records,
        }

        # --------------------------------------------------------------------
        # Save JSON.
        # --------------------------------------------------------------------

        print_header("12. SAVE JSON RESULTS")

        with open(
            SUMMARY_JSON,
            "w",
            encoding="utf-8",
        ) as json_file:

            json.dump(
                json_report,
                json_file,
                indent=4,
            )

        if not SUMMARY_JSON.exists():
            raise RuntimeError(
                "JSON output was not created."
            )

        print(
            f"JSON saved to:\n{SUMMARY_JSON}"
        )

        print("JSON output: PASS")

    finally:

        if raw_distance_src is not None:
            raw_distance_src.close()

        if river_score_src is not None:
            river_score_src.close()

        if continuous_src is not None:
            continuous_src.close()

        if classified_src is not None:
            classified_src.close()

    # ------------------------------------------------------------------------
    # Final report.
    # ------------------------------------------------------------------------

    print("\n" + "=" * 72)
    print("PHASE 9.4 ANALYSIS COMPLETED")
    print("=" * 72)

    print(
        "\nRiver relationship status:"
    )

    print(
        relationship_status
    )

    print(
        "\nSpearman river distance vs "
        "continuous susceptibility:"
    )

    print(
        f"{spearman_distance:.6f}"
    )

    print(
        "\nSpearman river score vs "
        "continuous susceptibility:"
    )

    print(
        f"{spearman_score:.6f}"
    )

    print(
        "\nMean river distance decreases "
        "with susceptibility class:"
    )

    print(
        "PASS"
        if distance_monotonic
        else "INVESTIGATE"
    )

    print(
        "\nOutputs:"
    )

    print(
        SUMMARY_CSV
    )

    print(
        SUMMARY_JSON
    )


if __name__ == "__main__":
    main()
