"""
Phase 9.7 - Population Exposure Analysis

Purpose
-------
Investigate the spatial relationship between population exposure and
the modeled flood-susceptibility surface.

Important methodological distinction
-------------------------------------
The original population raster is a source dataset and is NOT required
to have the same spatial grid as the final MCDA susceptibility raster.

The already aligned population_score raster is used for cell-by-cell
analysis against the MCDA susceptibility surface because it was prepared
on the common MCDA analysis grid.

The raw population raster is retained for source-data validation and
descriptive statistics only.

This analysis does NOT establish causation and does NOT constitute
external validation against observed flood events.

Outputs
-------
results/phase9_validation/population_exposure/
    susceptibility_population_exposure.csv
    susceptibility_population_exposure.json
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

RAW_POPULATION_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "population"
    / "population_32737.tif"
)

POPULATION_SCORE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
    / "population_score.tif"
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
    / "population_exposure"
)

CSV_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_population_exposure.csv"
)

JSON_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_population_exposure.json"
)


# ============================================================================
# EXPECTED MCDA REFERENCE GRID
# ============================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019

EXPECTED_CLASS_VALUES = {1, 2, 3, 4, 5}

CLASS_LABELS = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title):
    """Print a formatted terminal section header."""

    print("=" * 72)
    print(title)
    print("=" * 72)


def validate_file(path, label):
    """Validate that an input file exists."""

    print(f"{label}:")
    print(path)

    exists = path.exists()

    print(f"Exists: {'PASS' if exists else 'FAIL'}")
    print()

    if not exists:
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )


def read_raster(path):
    """
    Read a single-band raster.

    Returns
    -------
    array : numpy.ndarray
    metadata : dict
    valid_mask : numpy.ndarray
    """

    with rasterio.open(path) as src:

        array = src.read(1)

        nodata = src.nodata

        if nodata is None:

            valid_mask = np.isfinite(array)

        else:

            valid_mask = (
                np.isfinite(array)
                & (~np.isclose(array, nodata))
            )

        metadata = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "resolution": src.res,
            "nodata": nodata,
            "bounds": src.bounds,
            "dtype": src.dtypes[0],
        }

    return array, metadata, valid_mask


def compare_spatial_grid(reference, candidate, label):
    """
    Compare a candidate raster against the MCDA reference grid.

    This function is used only for rasters that are expected to already
    occupy the common MCDA grid.
    """

    crs_match = candidate.crs == reference.crs

    dimensions_match = (
        candidate.width == reference.width
        and candidate.height == reference.height
    )

    transform_match = (
        candidate.transform == reference.transform
    )

    resolution_match = (
        np.isclose(
            candidate.res[0],
            reference.res[0]
        )
        and
        np.isclose(
            candidate.res[1],
            reference.res[1]
        )
    )

    print(
        f"{label} CRS match: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"{label} dimensions match: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )

    print(
        f"{label} transform match: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )

    print(
        f"{label} resolution match: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    if not all(
        [
            crs_match,
            dimensions_match,
            transform_match,
            resolution_match,
        ]
    ):
        raise ValueError(
            f"{label} does not match the MCDA reference grid."
        )


def safe_float(value):
    """
    Convert a numeric value to a JSON-compatible float.

    Non-finite values are converted to None.
    """

    if value is None:
        return None

    value = float(value)

    if not np.isfinite(value):
        return None

    return value


def interpret_correlation(value):
    """
    Interpret the strength and direction of a Spearman correlation.
    """

    if value is None:
        return "NOT_AVAILABLE"

    absolute = abs(value)

    if absolute < 0.20:
        strength = "VERY_WEAK"

    elif absolute < 0.40:
        strength = "WEAK"

    elif absolute < 0.60:
        strength = "MODERATE"

    elif absolute < 0.80:
        strength = "STRONG"

    else:
        strength = "VERY_STRONG"

    if value > 0:
        direction = "POSITIVE"

    elif value < 0:
        direction = "NEGATIVE"

    else:
        direction = "NONE"

    return f"{strength}_{direction}"


# ============================================================================
# MAIN
# ============================================================================

def main():

    print_header(
        "PHASE 9.7 - POPULATION EXPOSURE ANALYSIS"
    )

    print()
    print("Project root:")
    print(PROJECT_ROOT)

    print()
    print("Raw population raster:")
    print(RAW_POPULATION_RASTER)

    print()
    print("Population score raster:")
    print(POPULATION_SCORE_RASTER)

    print()
    print("Continuous susceptibility raster:")
    print(CONTINUOUS_SUSCEPTIBILITY_RASTER)

    print()
    print("Classified susceptibility raster:")
    print(CLASSIFIED_SUSCEPTIBILITY_RASTER)

    print()
    print("Results directory:")
    print(RESULTS_DIR)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================================
    # 1. INPUT FILE VALIDATION
    # ========================================================================

    print()
    print_header(
        "1. INPUT FILE VALIDATION"
    )

    validate_file(
        RAW_POPULATION_RASTER,
        "Raw population raster"
    )

    validate_file(
        POPULATION_SCORE_RASTER,
        "Population score raster"
    )

    validate_file(
        CONTINUOUS_SUSCEPTIBILITY_RASTER,
        "Continuous susceptibility"
    )

    validate_file(
        CLASSIFIED_SUSCEPTIBILITY_RASTER,
        "Classified susceptibility"
    )

    # ========================================================================
    # 2. REFERENCE GRID VALIDATION
    # ========================================================================

    print()
    print_header(
        "2. REFERENCE GRID VALIDATION"
    )

    (
        susceptibility,
        susceptibility_meta,
        susceptibility_valid,
    ) = read_raster(
        CONTINUOUS_SUSCEPTIBILITY_RASTER
    )

    (
        classified,
        classified_meta,
        classified_valid,
    ) = read_raster(
        CLASSIFIED_SUSCEPTIBILITY_RASTER
    )

    actual_crs = str(
        susceptibility_meta["crs"]
    )

    print(
        f"Expected CRS: {EXPECTED_CRS}"
    )

    print(
        f"Actual CRS:   {actual_crs}"
    )

    crs_pass = (
        actual_crs == EXPECTED_CRS
    )

    print(
        f"CRS: {'PASS' if crs_pass else 'FAIL'}"
    )

    print(
        f"Expected dimensions: "
        f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
    )

    print(
        "Actual dimensions:   "
        f"{susceptibility_meta['width']} x "
        f"{susceptibility_meta['height']}"
    )

    dimensions_pass = (
        susceptibility_meta["width"]
        == EXPECTED_WIDTH
        and
        susceptibility_meta["height"]
        == EXPECTED_HEIGHT
    )

    print(
        f"Dimensions: "
        f"{'PASS' if dimensions_pass else 'FAIL'}"
    )

    if not crs_pass or not dimensions_pass:

        raise ValueError(
            "The final susceptibility raster does not match "
            "the expected MCDA reference grid."
        )

    # ========================================================================
    # 3. SPATIAL COMPATIBILITY VALIDATION
    # ========================================================================

    print()
    print_header(
        "3. SPATIAL COMPATIBILITY VALIDATION"
    )

    with rasterio.open(
        CONTINUOUS_SUSCEPTIBILITY_RASTER
    ) as reference:

        # --------------------------------------------------------------------
        # RAW POPULATION
        # --------------------------------------------------------------------
        #
        # The raw population raster is intentionally NOT required to match
        # the MCDA grid. It is a source raster.
        # --------------------------------------------------------------------

        with rasterio.open(
            RAW_POPULATION_RASTER
        ) as population_src:

            raw_population_crs_match = (
                population_src.crs
                == reference.crs
            )

            print(
                "Raw population CRS match: "
                f"{'PASS' if raw_population_crs_match else 'FAIL'}"
            )

            print(
                "Raw population grid alignment: "
                "SOURCE GRID — NOT REQUIRED TO MATCH"
            )

            print(
                f"Raw population dimensions: "
                f"{population_src.width} x "
                f"{population_src.height}"
            )

            print(
                f"Raw population resolution: "
                f"{population_src.res[0]:.6f} x "
                f"{population_src.res[1]:.6f} m"
            )

            if not raw_population_crs_match:

                raise ValueError(
                    "Raw population raster CRS does not match "
                    "the MCDA analysis CRS."
                )

        # --------------------------------------------------------------------
        # POPULATION SCORE
        # --------------------------------------------------------------------

        with rasterio.open(
            POPULATION_SCORE_RASTER
        ) as score_src:

            compare_spatial_grid(
                reference,
                score_src,
                "Population score"
            )

        # --------------------------------------------------------------------
        # CLASSIFIED SUSCEPTIBILITY
        # --------------------------------------------------------------------

        with rasterio.open(
            CLASSIFIED_SUSCEPTIBILITY_RASTER
        ) as class_src:

            compare_spatial_grid(
                reference,
                class_src,
                "Classified susceptibility"
            )

    print()
    print(
        "Spatial compatibility of MCDA analysis layers: PASS"
    )

    # ========================================================================
    # 4. READ POPULATION DATA
    # ========================================================================

    print()
    print_header(
        "4. POPULATION DATA VALIDATION"
    )

    (
        raw_population,
        raw_population_meta,
        raw_population_valid,
    ) = read_raster(
        RAW_POPULATION_RASTER
    )

    (
        population_score,
        population_score_meta,
        population_score_valid,
    ) = read_raster(
        POPULATION_SCORE_RASTER
    )

    raw_population_values = (
        raw_population[
            raw_population_valid
        ].astype(float)
    )

    print(
        f"Raw population valid cells: "
        f"{raw_population_values.size:,}"
    )

    print(
        f"Raw population minimum: "
        f"{np.min(raw_population_values):.6f}"
    )

    print(
        f"Raw population median: "
        f"{np.median(raw_population_values):.6f}"
    )

    print(
        f"Raw population maximum: "
        f"{np.max(raw_population_values):.6f}"
    )

    print(
        f"Raw population mean: "
        f"{np.mean(raw_population_values):.6f}"
    )

    negative_population_count = int(
        np.count_nonzero(
            raw_population_values < 0
        )
    )

    print(
        f"Negative population values: "
        f"{negative_population_count:,}"
    )

    population_value_status = (
        "PASS"
        if negative_population_count == 0
        else "INVESTIGATE"
    )

    print(
        "Population value validation: "
        f"{population_value_status}"
    )

    # ========================================================================
    # 5. COMMON MCDA VALID-CELL FOOTPRINT
    # ========================================================================

    print()
    print_header(
        "5. COMMON MCDA VALID-CELL FOOTPRINT"
    )

    common_valid = (
        population_score_valid
        &
        susceptibility_valid
        &
        classified_valid
    )

    total_cells = susceptibility.size

    common_valid_cells = int(
        np.count_nonzero(common_valid)
    )

    print(
        f"Total MCDA raster cells: "
        f"{total_cells:,}"
    )

    print(
        f"Common valid MCDA cells: "
        f"{common_valid_cells:,}"
    )

    common_valid_percentage = (
        common_valid_cells
        / total_cells
        * 100
    )

    print(
        f"Common valid percentage: "
        f"{common_valid_percentage:.3f}%"
    )

    common_footprint_pass = (
        common_valid_cells > 0
    )

    print(
        "Common MCDA footprint: "
        f"{'PASS' if common_footprint_pass else 'FAIL'}"
    )

    if not common_footprint_pass:

        raise ValueError(
            "No common valid cells are available "
            "for population-susceptibility analysis."
        )

    # ========================================================================
    # 6. EXTRACT ALIGNED ANALYSIS VALUES
    # ========================================================================

    print()
    print_header(
        "6. ALIGNED POPULATION-FACTOR ANALYSIS"
    )

    analysis_population_score = (
        population_score[
            common_valid
        ].astype(float)
    )

    analysis_susceptibility = (
        susceptibility[
            common_valid
        ].astype(float)
    )

    analysis_classes = (
        classified[
            common_valid
        ].astype(int)
    )

    print(
        f"Population-score cells analyzed: "
        f"{analysis_population_score.size:,}"
    )

    print(
        f"Population-score minimum: "
        f"{np.min(analysis_population_score):.6f}"
    )

    print(
        f"Population-score median: "
        f"{np.median(analysis_population_score):.6f}"
    )

    print(
        f"Population-score maximum: "
        f"{np.max(analysis_population_score):.6f}"
    )

    print(
        f"Population-score mean: "
        f"{np.mean(analysis_population_score):.6f}"
    )

    score_range_pass = (
        np.min(analysis_population_score) >= 0
        and
        np.max(analysis_population_score) <= 1
    )

    print(
        "Population score 0-1 range: "
        f"{'PASS' if score_range_pass else 'FAIL'}"
    )

    if not score_range_pass:

        raise ValueError(
            "Population score contains values outside "
            "the expected 0-1 range."
        )

    # ========================================================================
    # 7. SUSCEPTIBILITY CLASS VALIDATION
    # ========================================================================

    print()
    print_header(
        "7. SUSCEPTIBILITY CLASS VALIDATION"
    )

    observed_classes = sorted(
        np.unique(
            analysis_classes
        ).tolist()
    )

    print(
        f"Observed classes: "
        f"{observed_classes}"
    )

    classes_pass = (
        set(observed_classes)
        == EXPECTED_CLASS_VALUES
    )

    print(
        "All five susceptibility classes present: "
        f"{'PASS' if classes_pass else 'FAIL'}"
    )

    if not classes_pass:

        raise ValueError(
            "Unexpected susceptibility class values detected."
        )

    # ========================================================================
    # 8. POPULATION SCORE BY SUSCEPTIBILITY CLASS
    # ========================================================================

    print()
    print_header(
        "8. POPULATION-FACTOR DISTRIBUTION "
        "BY SUSCEPTIBILITY CLASS"
    )

    rows = []

    for class_value in range(1, 6):

        mask = (
            analysis_classes
            == class_value
        )

        class_population_score = (
            analysis_population_score[
                mask
            ]
        )

        class_susceptibility = (
            analysis_susceptibility[
                mask
            ]
        )

        row = {

            "class_value": class_value,

            "class_label": (
                CLASS_LABELS[class_value]
            ),

            "cell_count": int(
                np.count_nonzero(mask)
            ),

            "cell_share_percent": safe_float(
                np.count_nonzero(mask)
                / common_valid_cells
                * 100
            ),

            "mean_population_score": safe_float(
                np.mean(
                    class_population_score
                )
            ),

            "median_population_score": safe_float(
                np.median(
                    class_population_score
                )
            ),

            "minimum_population_score": safe_float(
                np.min(
                    class_population_score
                )
            ),

            "maximum_population_score": safe_float(
                np.max(
                    class_population_score
                )
            ),

            "mean_susceptibility": safe_float(
                np.mean(
                    class_susceptibility
                )
            ),
        }

        rows.append(row)

        print(
            f"{class_value} - "
            f"{CLASS_LABELS[class_value]}"
        )

        print(
            f"  Cells: "
            f"{row['cell_count']:,}"
        )

        print(
            f"  Cell share: "
            f"{row['cell_share_percent']:.3f}%"
        )

        print(
            f"  Mean population score: "
            f"{row['mean_population_score']:.6f}"
        )

        print(
            f"  Median population score: "
            f"{row['median_population_score']:.6f}"
        )

        print(
            f"  Mean susceptibility: "
            f"{row['mean_susceptibility']:.6f}"
        )

    # ========================================================================
    # 9. HIGH + VERY HIGH POPULATION-FACTOR EXPOSURE
    # ========================================================================

    print()
    print_header(
        "9. HIGH AND VERY-HIGH POPULATION-FACTOR EXPOSURE"
    )

    high_very_high_mask = np.isin(
        analysis_classes,
        [4, 5]
    )

    high_very_high_cells = int(
        np.count_nonzero(
            high_very_high_mask
        )
    )

    high_very_high_cell_share = (
        high_very_high_cells
        / common_valid_cells
        * 100
    )

    high_very_high_population_score_mean = (
        np.mean(
            analysis_population_score[
                high_very_high_mask
            ]
        )
    )

    print(
        f"High + Very High cells: "
        f"{high_very_high_cells:,}"
    )

    print(
        f"Share of MCDA cells: "
        f"{high_very_high_cell_share:.3f}%"
    )

    print(
        f"Mean population score in "
        f"High + Very High areas: "
        f"{high_very_high_population_score_mean:.6f}"
    )

    # ========================================================================
    # 10. CONTINUOUS RELATIONSHIP
    # ========================================================================

    print()
    print_header(
        "10. CONTINUOUS POPULATION VS SUSCEPTIBILITY"
    )

    population_corr, population_p = spearmanr(
        analysis_population_score,
        analysis_susceptibility
    )

    print(
        "Population score vs continuous susceptibility:"
    )

    print(
        f"Spearman correlation: "
        f"{population_corr:.6f}"
    )

    print(
        f"p-value: "
        f"{population_p:.6e}"
    )

    print(
        "Interpretation: "
        f"{interpret_correlation(population_corr)}"
    )

    # ========================================================================
    # 11. CLASS-ORDER RELATIONSHIP
    # ========================================================================

    print()
    print_header(
        "11. CLASS-ORDER RELATIONSHIP ASSESSMENT"
    )

    mean_population_score_by_class = [
        row[
            "mean_population_score"
        ]
        for row in rows
    ]

    population_score_monotonic = all(
        x <= y
        for x, y in zip(
            mean_population_score_by_class,
            mean_population_score_by_class[1:]
        )
    )

    print(
        "Mean population score increases "
        "with susceptibility class: "
        f"{'PASS' if population_score_monotonic else 'INVESTIGATE'}"
    )

    # ========================================================================
    # 12. OVERALL ASSESSMENT
    # ========================================================================

    print()
    print_header(
        "12. OVERALL POPULATION-EXPOSURE ASSESSMENT"
    )

    if (
        population_corr >= 0.60
        and population_score_monotonic
    ):

        relationship_status = (
            "CONSISTENT"
        )

    elif (
        population_corr >= 0.30
        or population_score_monotonic
    ):

        relationship_status = (
            "PARTIALLY_CONSISTENT"
        )

    else:

        relationship_status = (
            "WEAK_RELATIONSHIP"
        )

    print(
        "Population-factor vs susceptibility relationship:"
    )

    print(
        relationship_status
    )

    # ========================================================================
    # 13. SAVE CSV
    # ========================================================================

    print()
    print_header(
        "13. SAVE CSV RESULTS"
    )

    dataframe = pd.DataFrame(
        rows
    )

    dataframe.to_csv(
        CSV_OUTPUT,
        index=False
    )

    print(
        "CSV saved to:"
    )

    print(
        CSV_OUTPUT
    )

    print(
        "CSV output: PASS"
    )

    # ========================================================================
    # 14. SAVE JSON
    # ========================================================================

    print()
    print_header(
        "14. SAVE JSON RESULTS"
    )

    json_results = {

        "phase": "9.7",

        "analysis": (
            "Population Exposure Analysis"
        ),

        "project_root": str(
            PROJECT_ROOT
        ),

        "methodological_note": (
            "The raw population raster is treated as a "
            "source dataset and is not required to match "
            "the final MCDA grid. Cell-by-cell analysis "
            "uses the already aligned population_score "
            "raster on the common MCDA grid."
        ),

        "inputs": {

            "raw_population_raster": str(
                RAW_POPULATION_RASTER
            ),

            "population_score_raster": str(
                POPULATION_SCORE_RASTER
            ),

            "continuous_susceptibility_raster": str(
                CONTINUOUS_SUSCEPTIBILITY_RASTER
            ),

            "classified_susceptibility_raster": str(
                CLASSIFIED_SUSCEPTIBILITY_RASTER
            ),
        },

        "reference_grid": {

            "crs": EXPECTED_CRS,

            "width": EXPECTED_WIDTH,

            "height": EXPECTED_HEIGHT,
        },

        "raw_population_source_statistics": {

            "valid_cells": int(
                raw_population_values.size
            ),

            "minimum": safe_float(
                np.min(
                    raw_population_values
                )
            ),

            "median": safe_float(
                np.median(
                    raw_population_values
                )
            ),

            "maximum": safe_float(
                np.max(
                    raw_population_values
                )
            ),

            "mean": safe_float(
                np.mean(
                    raw_population_values
                )
            ),

            "negative_value_count": int(
                negative_population_count
            ),
        },

        "common_mcda_footprint": {

            "total_cells": int(
                total_cells
            ),

            "common_valid_cells": int(
                common_valid_cells
            ),

            "common_valid_percentage": safe_float(
                common_valid_percentage
            ),
        },

        "population_score_statistics": {

            "minimum": safe_float(
                np.min(
                    analysis_population_score
                )
            ),

            "median": safe_float(
                np.median(
                    analysis_population_score
                )
            ),

            "maximum": safe_float(
                np.max(
                    analysis_population_score
                )
            ),

            "mean": safe_float(
                np.mean(
                    analysis_population_score
                )
            ),
        },

        "population_by_susceptibility_class": rows,

        "high_and_very_high_areas": {

            "cell_count": int(
                high_very_high_cells
            ),

            "cell_share_percent": safe_float(
                high_very_high_cell_share
            ),

            "mean_population_score": safe_float(
                high_very_high_population_score_mean
            ),
        },

        "continuous_relationship": {

            "population_score_vs_susceptibility": {

                "spearman_rho": safe_float(
                    population_corr
                ),

                "p_value": safe_float(
                    population_p
                ),

                "interpretation": (
                    interpret_correlation(
                        population_corr
                    )
                ),
            },
        },

        "class_order_relationship": {

            "mean_population_score_increases": bool(
                population_score_monotonic
            ),
        },

        "overall_status": (
            relationship_status
        ),

        "scientific_note": (
            "This analysis evaluates spatial association "
            "between the population factor and modeled "
            "flood susceptibility. It does not establish "
            "causation, does not establish flood-event "
            "prediction accuracy, and does not constitute "
            "external validation against observed flood "
            "events."
        ),
    }

    with open(
        JSON_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            json_results,
            file,
            indent=4
        )

    print(
        "JSON saved to:"
    )

    print(
        JSON_OUTPUT
    )

    print(
        "JSON output: PASS"
    )

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print()
    print_header(
        "PHASE 9.7 POPULATION EXPOSURE ANALYSIS COMPLETED"
    )

    print(
        "Common valid MCDA cells analyzed: "
        f"{common_valid_cells:,}"
    )

    print()
    print(
        "Population-factor vs susceptibility status:"
    )

    print(
        relationship_status
    )

    print()
    print(
        "Population score vs continuous susceptibility "
        "Spearman correlation:"
    )

    print(
        f"{population_corr:.6f}"
    )

    print()
    print(
        "Mean population score increases "
        "with susceptibility class:"
    )

    print(
        "PASS"
        if population_score_monotonic
        else "INVESTIGATE"
    )

    print()
    print(
        "Outputs:"
    )

    print(
        CSV_OUTPUT
    )

    print(
        JSON_OUTPUT
    )

    print("=" * 72)


if __name__ == "__main__":
    main()