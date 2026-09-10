"""
Susceptibility-Class Distribution Analysis

This script analyzes the distribution of valid cells across the
five flood susceptibility classes produced by the Phase 8 MCDA
classification.

Project:
    GeoAI Flood Risk Decision Agent
    Nairobi County, Kenya

Input:
    data/analysis/mcda/flood_susceptibility_classified.tif

Classes:
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High

Purpose:
    Phase 9.2 - Susceptibility-Class Distribution Analysis

The analysis:
    - validates the classified raster structure
    - excludes NoData cells
    - counts cells in each susceptibility class
    - calculates class percentages
    - checks that all valid cells have valid classes
    - checks that all five classes are present
    - compares the observed distribution with the expected
      approximately 20% per class resulting from quantile
      classification
    - saves machine-readable CSV and JSON results

Important:
    The susceptibility classes are relative categories.
    They are not probabilities of flooding.
"""

from pathlib import Path
import csv
import json

import numpy as np
import rasterio


# =====================================================================
# 1. PROJECT PATHS
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MCDA_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "class_distribution"
)

INPUT_FILE = (
    MCDA_DIR
    / "flood_susceptibility_classified.tif"
)

CSV_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_class_distribution.csv"
)

JSON_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_class_distribution.json"
)


# =====================================================================
# 2. EXPECTED RASTER PROPERTIES
# =====================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603

EXPECTED_HEIGHT = 1019

EXPECTED_NODATA = 0


# =====================================================================
# 3. CLASS DEFINITIONS
# =====================================================================

CLASS_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}

EXPECTED_CLASSES = set(CLASS_NAMES.keys())

EXPECTED_PERCENTAGE = 20.0


# =====================================================================
# 4. HELPER FUNCTION
# =====================================================================

def print_header(title):
    """Print a consistent section header."""

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# =====================================================================
# 5. VALIDATE INPUT RASTER
# =====================================================================

def validate_input_raster(src):
    """
    Validate the structural properties of the classified raster.
    """

    print_header("1. INPUT RASTER VALIDATION")

    actual_crs = (
        src.crs.to_string()
        if src.crs
        else None
    )

    print(f"Expected CRS       : {EXPECTED_CRS}")
    print(f"Actual CRS         : {actual_crs}")

    if actual_crs != EXPECTED_CRS:
        raise ValueError(
            "Classified raster CRS does not "
            "match the expected EPSG:32737."
        )

    print("CRS                : PASS")

    dimensions_ok = (
        src.width == EXPECTED_WIDTH
        and src.height == EXPECTED_HEIGHT
    )

    print(
        f"Expected dimensions: "
        f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
    )

    print(
        f"Actual dimensions  : "
        f"{src.width} x {src.height}"
    )

    if not dimensions_ok:
        raise ValueError(
            "Classified raster dimensions do not "
            "match the expected MCDA grid."
        )

    print("Dimensions         : PASS")

    actual_nodata = src.nodata

    print(f"Expected NoData    : {EXPECTED_NODATA}")
    print(f"Actual NoData      : {actual_nodata}")

    if actual_nodata is None:
        raise ValueError(
            "Classified raster does not define "
            "a NoData value."
        )

    if not np.isclose(
        actual_nodata,
        EXPECTED_NODATA,
    ):
        raise ValueError(
            "Classified raster NoData value does "
            "not match the expected value."
        )

    print("NoData value       : PASS")


# =====================================================================
# 6. EXTRACT VALID CELLS
# =====================================================================

def extract_valid_cells(array, nodata):
    """
    Extract valid classified cells and remove NoData.
    """

    print_header("2. VALID CELL EXTRACTION")

    valid_mask = (
        np.isfinite(array)
        & (array != nodata)
    )

    valid_values = array[valid_mask]

    if valid_values.size == 0:
        raise ValueError(
            "The classified raster contains "
            "no valid cells."
        )

    print(
        f"Total raster cells : {array.size}"
    )

    print(
        f"NoData cells       : "
        f"{array.size - valid_values.size}"
    )

    print(
        f"Valid cells        : "
        f"{valid_values.size}"
    )

    print("Valid-cell extraction: PASS")

    return valid_values


# =====================================================================
# 7. VALIDATE CLASS VALUES
# =====================================================================

def validate_class_values(valid_values):
    """
    Verify that every valid cell contains a class code from 1 to 5.
    """

    print_header("3. CLASS VALUE VALIDATION")

    unique_values = set(
        np.unique(valid_values).tolist()
    )

    print(
        "Observed class values: "
        f"{sorted(unique_values)}"
    )

    invalid_values = (
        unique_values
        - EXPECTED_CLASSES
    )

    if invalid_values:
        raise ValueError(
            "Invalid class values detected: "
            f"{sorted(invalid_values)}"
        )

    print(
        "All valid cells use classes 1-5: PASS"
    )

    missing_classes = (
        EXPECTED_CLASSES
        - unique_values
    )

    if missing_classes:
        raise ValueError(
            "One or more expected classes "
            "are missing: "
            f"{sorted(missing_classes)}"
        )

    print(
        "All five classes are present     : PASS"
    )


# =====================================================================
# 8. CALCULATE CLASS DISTRIBUTION
# =====================================================================

def calculate_distribution(valid_values):
    """
    Calculate cell counts and percentages for each class.
    """

    print_header("4. CLASS DISTRIBUTION ANALYSIS")

    total_valid = int(valid_values.size)

    results = []

    for class_code in range(1, 6):

        count = int(
            np.count_nonzero(
                valid_values == class_code
            )
        )

        percentage = (
            count
            / total_valid
            * 100.0
        )

        deviation = (
            percentage
            - EXPECTED_PERCENTAGE
        )

        absolute_deviation = abs(
            deviation
        )

        class_name = CLASS_NAMES[
            class_code
        ]

        results.append(
            {
                "class_code": class_code,
                "class_name": class_name,
                "cell_count": count,
                "percentage": percentage,
                "expected_percentage": (
                    EXPECTED_PERCENTAGE
                ),
                "deviation_from_expected_percentage": (
                    deviation
                ),
                "absolute_deviation_percentage": (
                    absolute_deviation
                ),
            }
        )

        print(
            f"{class_code} - "
            f"{class_name:10s}: "
            f"{count:8d} cells "
            f"({percentage:7.3f}%)"
        )

    return results


# =====================================================================
# 9. VALIDATE TOTAL DISTRIBUTION
# =====================================================================

def validate_total_distribution(
    results,
    total_valid,
):
    """
    Confirm that class counts account for every valid cell.
    """

    print_header("5. DISTRIBUTION COMPLETENESS")

    total_classified = sum(
        item["cell_count"]
        for item in results
    )

    total_percentage = sum(
        item["percentage"]
        for item in results
    )

    print(
        f"Valid cells              : "
        f"{total_valid}"
    )

    print(
        f"Sum of class counts      : "
        f"{total_classified}"
    )

    print(
        f"Sum of class percentages : "
        f"{total_percentage:.6f}%"
    )

    counts_ok = (
        total_classified
        == total_valid
    )

    percentages_ok = np.isclose(
        total_percentage,
        100.0,
        atol=1e-6,
    )

    if not counts_ok:
        raise ValueError(
            "Class counts do not account for "
            "all valid cells."
        )

    if not percentages_ok:
        raise ValueError(
            "Class percentages do not sum "
            "to 100%."
        )

    print(
        "All valid cells accounted for : PASS"
    )

    print(
        "Percentages sum to 100%        : PASS"
    )


# =====================================================================
# 10. ASSESS QUANTILE DISTRIBUTION
# =====================================================================

def assess_quantile_distribution(results):
    """
    Assess how closely the observed class distribution
    follows the expected approximately 20% per class
    quantile structure.

    This is an interpretation check, not a predictive
    accuracy assessment.
    """

    print_header("6. QUANTILE DISTRIBUTION ASSESSMENT")

    largest_deviation = max(
        item["absolute_deviation_percentage"]
        for item in results
    )

    most_deviant_class = max(
        results,
        key=lambda item: item[
            "absolute_deviation_percentage"
        ],
    )

    print(
        "Expected share per class : "
        f"{EXPECTED_PERCENTAGE:.1f}%"
    )

    print(
        "Largest absolute deviation: "
        f"{largest_deviation:.3f} percentage points"
    )

    print(
        "Most deviating class      : "
        f"{most_deviant_class['class_name']}"
    )

    # -------------------------------------------------------------
    # Quantile classification can produce small deviations from
    # 20% because multiple cells can have identical values at
    # classification thresholds.
    #
    # We therefore do not treat a small deviation as a failure.
    # -------------------------------------------------------------

    if largest_deviation <= 2.0:

        distribution_status = "CONSISTENT"

        print(
            "Quantile distribution assessment: "
            "CONSISTENT"
        )

    elif largest_deviation <= 5.0:

        distribution_status = "MINOR_DEVIATION"

        print(
            "Quantile distribution assessment: "
            "MINOR DEVIATION"
        )

        print(
            "Interpretation: The distribution is "
            "reasonably close to the expected "
            "quantile structure, with some deviation."
        )

    else:

        distribution_status = "INVESTIGATE"

        print(
            "Quantile distribution assessment: "
            "INVESTIGATE"
        )

        print(
            "Interpretation: The observed class "
            "distribution differs substantially "
            "from the expected quantile structure."
        )

    return (
        distribution_status,
        largest_deviation,
        most_deviant_class["class_name"],
    )


# =====================================================================
# 11. SAVE CSV RESULTS
# =====================================================================

def save_csv(results):
    """
    Save class distribution results as CSV.
    """

    print_header("7. SAVE CSV RESULTS")

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "class_code",
        "class_name",
        "cell_count",
        "percentage",
        "expected_percentage",
        "deviation_from_expected_percentage",
        "absolute_deviation_percentage",
    ]

    with open(
        CSV_OUTPUT,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in results:
            writer.writerow(row)

    print(
        f"CSV results saved to:\n"
        f"{CSV_OUTPUT}"
    )

    print("CSV output: PASS")


# =====================================================================
# 12. SAVE JSON RESULTS
# =====================================================================

def save_json(
    results,
    total_cells,
    valid_cells,
    nodata_cells,
    distribution_status,
    largest_deviation,
    most_deviant_class,
):
    """
    Save complete analysis results as JSON.
    """

    print_header("8. SAVE JSON RESULTS")

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "project": (
            "GeoAI Flood Risk Decision Agent"
        ),
        "study_area": (
            "Nairobi County, Kenya"
        ),
        "phase": "Phase 9.2",
        "analysis": (
            "Susceptibility-Class "
            "Distribution Analysis"
        ),
        "input_raster": str(
            INPUT_FILE.relative_to(
                PROJECT_ROOT
            )
        ),
        "classification_method": (
            "Quantile classification"
        ),
        "interpretation": (
            "Relative susceptibility classes; "
            "not flood probabilities."
        ),
        "expected_percentage_per_class": (
            EXPECTED_PERCENTAGE
        ),
        "total_raster_cells": total_cells,
        "valid_cells": valid_cells,
        "nodata_cells": nodata_cells,
        "classes": results,
        "quantile_distribution_status": (
            distribution_status
        ),
        "largest_absolute_deviation_percentage_points": (
            largest_deviation
        ),
        "most_deviating_class": (
            most_deviant_class
        ),
    }

    with open(
        JSON_OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
        )

    print(
        f"JSON results saved to:\n"
        f"{JSON_OUTPUT}"
    )

    print("JSON output: PASS")


# =====================================================================
# 13. MAIN WORKFLOW
# =====================================================================

def main():
    """
    Run the complete Phase 9.2 analysis.
    """

    print("=" * 70)
    print(
        "PHASE 9.2 - SUSCEPTIBILITY-CLASS "
        "DISTRIBUTION ANALYSIS"
    )
    print("=" * 70)

    print(
        f"\nProject root:\n"
        f"{PROJECT_ROOT}"
    )

    print(
        f"\nInput raster:\n"
        f"{INPUT_FILE}"
    )

    print(
        f"\nResults directory:\n"
        f"{RESULTS_DIR}"
    )

    # -------------------------------------------------------------
    # Confirm input exists.
    # -------------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Classified susceptibility raster "
            "was not found:\n"
            f"{INPUT_FILE}"
        )

    print(
        "\nInput raster exists: PASS"
    )

    # -------------------------------------------------------------
    # Open raster.
    # -------------------------------------------------------------

    with rasterio.open(
        INPUT_FILE
    ) as src:

        # ---------------------------------------------------------
        # Validate raster.
        # ---------------------------------------------------------

        validate_input_raster(src)

        # ---------------------------------------------------------
        # Read classified raster.
        # ---------------------------------------------------------

        array = src.read(
            1
        )

        nodata = src.nodata

        # ---------------------------------------------------------
        # Extract valid cells.
        # ---------------------------------------------------------

        valid_values = (
            extract_valid_cells(
                array,
                nodata,
            )
        )

        total_cells = int(
            array.size
        )

        valid_cells = int(
            valid_values.size
        )

        nodata_cells = (
            total_cells
            - valid_cells
        )

        # ---------------------------------------------------------
        # Validate class values.
        # ---------------------------------------------------------

        validate_class_values(
            valid_values
        )

        # ---------------------------------------------------------
        # Calculate distribution.
        # ---------------------------------------------------------

        results = (
            calculate_distribution(
                valid_values
            )
        )

    # -------------------------------------------------------------
    # Validate that all valid cells are represented.
    # -------------------------------------------------------------

    validate_total_distribution(
        results,
        valid_cells,
    )

    # -------------------------------------------------------------
    # Assess quantile distribution.
    # -------------------------------------------------------------

    (
        distribution_status,
        largest_deviation,
        most_deviant_class,
    ) = assess_quantile_distribution(
        results
    )

    # -------------------------------------------------------------
    # Save CSV.
    # -------------------------------------------------------------

    save_csv(results)

    # -------------------------------------------------------------
    # Save JSON.
    # -------------------------------------------------------------

    save_json(
        results=results,
        total_cells=total_cells,
        valid_cells=valid_cells,
        nodata_cells=nodata_cells,
        distribution_status=distribution_status,
        largest_deviation=largest_deviation,
        most_deviant_class=most_deviant_class,
    )

    # -------------------------------------------------------------
    # Final status.
    # -------------------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "PHASE 9.2 ANALYSIS COMPLETED"
    )
    print("=" * 70)

    print(
        f"Valid cells analyzed : "
        f"{valid_cells}"
    )

    print(
        f"Distribution status  : "
        f"{distribution_status}"
    )

    print(
        f"Results directory:\n"
        f"{RESULTS_DIR}"
    )

    print("=" * 70)


# =====================================================================
# 14. SCRIPT ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    main()