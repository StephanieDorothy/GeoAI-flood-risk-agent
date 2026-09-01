"""
Independent Validation of Classified Flood Susceptibility

This script independently validates the classified flood
susceptibility raster produced from the continuous MCDA surface.

Input:
    data/analysis/mcda/flood_susceptibility.tif

Classified output:
    data/analysis/mcda/flood_susceptibility_classified.tif

Classification:
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High

Method:
    Quantile classification using the validated MCDA thresholds.

Project:
    GeoAI Flood Risk Decision Agent
    Nairobi County, Kenya
"""

from pathlib import Path

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

CONTINUOUS_RASTER = (
    MCDA_DIR
    / "flood_susceptibility.tif"
)

CLASSIFIED_RASTER = (
    MCDA_DIR
    / "flood_susceptibility_classified.tif"
)


# =====================================================================
# 2. EXPECTED RASTER PROPERTIES
# =====================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603

EXPECTED_HEIGHT = 1019

EXPECTED_RESOLUTION = (
    30.86551681907227,
    30.86551681907227,
)

EXPECTED_CONTINUOUS_NODATA = -9999.0

EXPECTED_CLASS_NODATA = 0


# =====================================================================
# 3. VALIDATED CLASSIFICATION THRESHOLDS
# =====================================================================

Q20 = 0.6915898

Q40 = 0.7606905

Q60 = 0.8051752

Q80 = 0.84985673


# =====================================================================
# 4. CLASS DEFINITIONS
# =====================================================================

CLASS_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# =====================================================================
# 5. VALIDATION TOLERANCE
# =====================================================================

THRESHOLD_TOLERANCE = 1e-7


# =====================================================================
# 6. HELPER FUNCTION
# =====================================================================

def print_header(title):
    """Print a consistent validation section."""

    print("\n" + "=" * 60)

    print(title)

    print("=" * 60)


# =====================================================================
# 7. VALIDATE FILE EXISTENCE
# =====================================================================

def validate_file_existence():

    print_header(
        "1. FILE EXISTENCE VALIDATION"
    )

    continuous_exists = (
        CONTINUOUS_RASTER.exists()
    )

    classified_exists = (
        CLASSIFIED_RASTER.exists()
    )

    print(
        f"Continuous MCDA raster exists"
        f"              : "
        f"{'PASS' if continuous_exists else 'FAIL'}"
    )

    print(
        f"Classified raster exists"
        f"                    : "
        f"{'PASS' if classified_exists else 'FAIL'}"
    )

    if not continuous_exists:

        raise FileNotFoundError(
            "Continuous MCDA raster was not found:\n"
            f"{CONTINUOUS_RASTER}"
        )

    if not classified_exists:

        raise FileNotFoundError(
            "Classified susceptibility raster was not found:\n"
            f"{CLASSIFIED_RASTER}"
        )


# =====================================================================
# 8. VALIDATE SPATIAL METADATA
# =====================================================================

def validate_spatial_metadata(
    continuous,
    classified,
):

    print_header(
        "2. SPATIAL METADATA VALIDATION"
    )

    # -------------------------------------------------------------
    # CRS
    # -------------------------------------------------------------

    continuous_crs = (
        continuous.crs.to_string()
        if continuous.crs
        else None
    )

    classified_crs = (
        classified.crs.to_string()
        if classified.crs
        else None
    )

    continuous_crs_ok = (
        continuous_crs
        == EXPECTED_CRS
    )

    classified_crs_ok = (
        classified_crs
        == EXPECTED_CRS
    )

    print(
        f"Expected CRS : {EXPECTED_CRS}"
    )

    print(
        f"Continuous CRS : {continuous_crs}"
    )

    print(
        f"Classified CRS : {classified_crs}"
    )

    print(
        f"Continuous CRS validation"
        f"                  : "
        f"{'PASS' if continuous_crs_ok else 'FAIL'}"
    )

    print(
        f"Classified CRS validation"
        f"                  : "
        f"{'PASS' if classified_crs_ok else 'FAIL'}"
    )

    # -------------------------------------------------------------
    # Dimensions
    # -------------------------------------------------------------

    continuous_dimensions_ok = (
        continuous.width
        == EXPECTED_WIDTH
        and
        continuous.height
        == EXPECTED_HEIGHT
    )

    classified_dimensions_ok = (
        classified.width
        == EXPECTED_WIDTH
        and
        classified.height
        == EXPECTED_HEIGHT
    )

    print(
        f"Expected dimensions : "
        f"{EXPECTED_WIDTH} x "
        f"{EXPECTED_HEIGHT}"
    )

    print(
        f"Continuous dimensions : "
        f"{continuous.width} x "
        f"{continuous.height}"
    )

    print(
        f"Classified dimensions : "
        f"{classified.width} x "
        f"{classified.height}"
    )

    print(
        f"Continuous dimensions"
        f"                  : "
        f"{'PASS' if continuous_dimensions_ok else 'FAIL'}"
    )

    print(
        f"Classified dimensions"
        f"                  : "
        f"{'PASS' if classified_dimensions_ok else 'FAIL'}"
    )

    # -------------------------------------------------------------
    # Resolution
    # -------------------------------------------------------------

    continuous_resolution_ok = all(
        np.isclose(
            actual,
            expected,
            rtol=0,
            atol=1e-9,
        )
        for actual, expected
        in zip(
            continuous.res,
            EXPECTED_RESOLUTION,
        )
    )

    classified_resolution_ok = all(
        np.isclose(
            actual,
            expected,
            rtol=0,
            atol=1e-9,
        )
        for actual, expected
        in zip(
            classified.res,
            EXPECTED_RESOLUTION,
        )
    )

    print(
        f"Expected resolution : "
        f"{EXPECTED_RESOLUTION}"
    )

    print(
        f"Continuous resolution : "
        f"{continuous.res}"
    )

    print(
        f"Classified resolution : "
        f"{classified.res}"
    )

    print(
        f"Continuous resolution"
        f"                  : "
        f"{'PASS' if continuous_resolution_ok else 'FAIL'}"
    )

    print(
        f"Classified resolution"
        f"                  : "
        f"{'PASS' if classified_resolution_ok else 'FAIL'}"
    )

    # -------------------------------------------------------------
    # Bounds
    # -------------------------------------------------------------

    bounds_match = all(
        np.isclose(
            actual,
            expected,
            rtol=0,
            atol=1e-6,
        )
        for actual, expected
        in zip(
            classified.bounds,
            continuous.bounds,
        )
    )

    print(
        f"Classified bounds match continuous"
        f"      : "
        f"{'PASS' if bounds_match else 'FAIL'}"
    )

    # -------------------------------------------------------------
    # NoData
    # -------------------------------------------------------------

    continuous_nodata_ok = (
        continuous.nodata is not None
        and
        np.isclose(
            continuous.nodata,
            EXPECTED_CONTINUOUS_NODATA,
        )
    )

    classified_nodata_ok = (
        classified.nodata is not None
        and
        np.isclose(
            classified.nodata,
            EXPECTED_CLASS_NODATA,
        )
    )

    print(
        f"Expected continuous NoData : "
        f"{EXPECTED_CONTINUOUS_NODATA}"
    )

    print(
        f"Actual continuous NoData   : "
        f"{continuous.nodata}"
    )

    print(
        f"Expected classified NoData : "
        f"{EXPECTED_CLASS_NODATA}"
    )

    print(
        f"Actual classified NoData   : "
        f"{classified.nodata}"
    )

    print(
        f"Continuous NoData"
        f"                  : "
        f"{'PASS' if continuous_nodata_ok else 'FAIL'}"
    )

    print(
        f"Classified NoData"
        f"                  : "
        f"{'PASS' if classified_nodata_ok else 'FAIL'}"
    )

    # -------------------------------------------------------------
    # Final spatial validation
    # -------------------------------------------------------------

    all_spatial_checks = all(
        [
            continuous_crs_ok,
            classified_crs_ok,
            continuous_dimensions_ok,
            classified_dimensions_ok,
            continuous_resolution_ok,
            classified_resolution_ok,
            bounds_match,
            continuous_nodata_ok,
            classified_nodata_ok,
        ]
    )

    if not all_spatial_checks:

        raise ValueError(
            "Spatial metadata validation failed."
        )

    print(
        "Overall spatial metadata validation"
        "       : PASS"
    )


# =====================================================================
# 9. READ RASTER ARRAYS
# =====================================================================

def read_rasters(
    continuous,
    classified,
):

    print_header(
        "3. RASTER DATA VALIDATION"
    )

    continuous_array = (
        continuous.read(1)
    )

    classified_array = (
        classified.read(1)
    )

    print(
        f"Continuous raster shape"
        f"                  : "
        f"{continuous_array.shape}"
    )

    print(
        f"Classified raster shape"
        f"                  : "
        f"{classified_array.shape}"
    )

    shape_match = (
        continuous_array.shape
        ==
        classified_array.shape
    )

    print(
        f"Raster array shapes match"
        f"                 : "
        f"{'PASS' if shape_match else 'FAIL'}"
    )

    if not shape_match:

        raise ValueError(
            "Continuous and classified "
            "raster shapes do not match."
        )

    return (
        continuous_array,
        classified_array,
    )


# =====================================================================
# 10. VALIDATE VALID-CELL MASK
# =====================================================================

def validate_valid_cell_mask(
    continuous_array,
    classified_array,
    continuous_nodata,
    classified_nodata,
):

    print_header(
        "4. VALID-CELL MASK VALIDATION"
    )

    continuous_valid = (
        np.isfinite(
            continuous_array
        )
        &
        (
            continuous_array
            != continuous_nodata
        )
    )

    classified_valid = (
        classified_array
        != classified_nodata
    )

    continuous_count = int(
        np.count_nonzero(
            continuous_valid
        )
    )

    classified_count = int(
        np.count_nonzero(
            classified_valid
        )
    )

    masks_match = np.array_equal(
        continuous_valid,
        classified_valid,
    )

    print(
        f"Continuous valid cells"
        f"                    : "
        f"{continuous_count}"
    )

    print(
        f"Classified valid cells"
        f"                    : "
        f"{classified_count}"
    )

    print(
        f"Valid-cell masks match"
        f"                    : "
        f"{'PASS' if masks_match else 'FAIL'}"
    )

    if not masks_match:

        raise ValueError(
            "The classified raster does not "
            "preserve the continuous MCDA "
            "valid-cell footprint."
        )

    if continuous_count != 553860:

        raise ValueError(
            "Unexpected number of valid "
            "MCDA cells."
        )

    print(
        "Expected valid-cell count"
        f"             : PASS"
    )


# =====================================================================
# 11. VALIDATE CLASS VALUES
# =====================================================================

def validate_class_values(
    classified_array,
    classified_nodata,
):

    print_header(
        "5. CLASS VALUE VALIDATION"
    )

    valid_mask = (
        classified_array
        != classified_nodata
    )

    valid_values = (
        classified_array[
            valid_mask
        ]
    )

    finite_ok = np.all(
        np.isfinite(
            valid_values
        )
    )

    print(
        f"All valid class values finite"
        f"              : "
        f"{'PASS' if finite_ok else 'FAIL'}"
    )

    if not finite_ok:

        raise ValueError(
            "Classified raster contains "
            "non-finite valid values."
        )

    minimum = int(
        np.min(valid_values)
    )

    maximum = int(
        np.max(valid_values)
    )

    print(
        f"Minimum class value"
        f"                   : "
        f"{minimum}"
    )

    print(
        f"Maximum class value"
        f"                   : "
        f"{maximum}"
    )

    range_ok = (
        minimum >= 1
        and
        maximum <= 5
    )

    print(
        f"Class values within 1-5"
        f"                   : "
        f"{'PASS' if range_ok else 'FAIL'}"
    )

    if not range_ok:

        raise ValueError(
            "Classified raster contains "
            "values outside classes 1-5."
        )

    unique_classes = set(
        np.unique(
            valid_values
        ).tolist()
    )

    expected_classes = {
        1,
        2,
        3,
        4,
        5,
    }

    all_classes_present = (
        unique_classes
        == expected_classes
    )

    print(
        f"Classes present"
        f"                         : "
        f"{sorted(unique_classes)}"
    )

    print(
        f"All five classes present"
        f"                   : "
        f"{'PASS' if all_classes_present else 'FAIL'}"
    )

    if not all_classes_present:

        raise ValueError(
            "One or more expected "
            "susceptibility classes are missing."
        )


# =====================================================================
# 12. INDEPENDENT CLASSIFICATION REPRODUCTION
# =====================================================================

def independently_reproduce_classes(
    continuous_array,
    continuous_nodata,
    classified_array,
):

    print_header(
        "6. INDEPENDENT CLASSIFICATION REPRODUCTION"
    )

    valid_mask = (
        np.isfinite(
            continuous_array
        )
        &
        (
            continuous_array
            != continuous_nodata
        )
    )

    expected_classes = np.zeros(
        continuous_array.shape,
        dtype=np.uint8,
    )

    # -------------------------------------------------------------
    # Independent classification
    # -------------------------------------------------------------

    expected_classes[
        valid_mask
        &
        (
            continuous_array
            <= Q20
        )
    ] = 1

    expected_classes[
        valid_mask
        &
        (
            continuous_array
            > Q20
        )
        &
        (
            continuous_array
            <= Q40
        )
    ] = 2

    expected_classes[
        valid_mask
        &
        (
            continuous_array
            > Q40
        )
        &
        (
            continuous_array
            <= Q60
        )
    ] = 3

    expected_classes[
        valid_mask
        &
        (
            continuous_array
            > Q60
        )
        &
        (
            continuous_array
            <= Q80
        )
    ] = 4

    expected_classes[
        valid_mask
        &
        (
            continuous_array
            > Q80
        )
    ] = 5

    # -------------------------------------------------------------
    # Compare independent result with saved result.
    # -------------------------------------------------------------

    comparison_mask = valid_mask

    matches = np.array_equal(
        expected_classes[
            comparison_mask
        ],
        classified_array[
            comparison_mask
        ],
    )

    differing_cells = int(
        np.count_nonzero(
            expected_classes[
                comparison_mask
            ]
            !=
            classified_array[
                comparison_mask
            ]
        )
    )

    compared_cells = int(
        np.count_nonzero(
            comparison_mask
        )
    )

    print(
        f"Classification thresholds:"
    )

    print(
        f"20th percentile : {Q20:.8f}"
    )

    print(
        f"40th percentile : {Q40:.8f}"
    )

    print(
        f"60th percentile : {Q60:.8f}"
    )

    print(
        f"80th percentile : {Q80:.8f}"
    )

    print(
        f"Valid cells compared"
        f"                   : "
        f"{compared_cells}"
    )

    print(
        f"Differing cells"
        f"                         : "
        f"{differing_cells}"
    )

    print(
        f"Independent classification match"
        f"       : "
        f"{'PASS' if matches else 'FAIL'}"
    )

    if not matches:

        raise ValueError(
            "Saved classified raster does not "
            "match the independently reproduced "
            "classification."
        )


# =====================================================================
# 13. VALIDATE CLASS COUNTS
# =====================================================================

def validate_class_counts(
    classified_array,
    classified_nodata,
):

    print_header(
        "7. CLASS DISTRIBUTION VALIDATION"
    )

    valid_mask = (
        classified_array
        != classified_nodata
    )

    valid_values = (
        classified_array[
            valid_mask
        ]
    )

    total_valid = (
        valid_values.size
    )

    expected_count = (
        total_valid / 5
    )

    print(
        f"Total valid cells"
        f"                    : "
        f"{total_valid}"
    )

    all_counts_valid = True

    for code in range(1, 6):

        count = int(
            np.count_nonzero(
                valid_values
                == code
            )
        )

        percentage = (
            count
            /
            total_valid
            *
            100.0
        )

        count_ok = (
            count
            ==
            expected_count
        )

        if not count_ok:

            all_counts_valid = False

        print(
            f"{code} - "
            f"{CLASS_NAMES[code]:10s}: "
            f"{count:8d} cells "
            f"({percentage:6.2f}%) "
            f"{'PASS' if count_ok else 'FAIL'}"
        )

    print(
        f"Expected cells per class"
        f"                   : "
        f"{expected_count:.0f}"
    )

    if not all_counts_valid:

        raise ValueError(
            "Class counts are not equally "
            "distributed as expected from "
            "the quantile classification."
        )

    print(
        "Equal quantile class distribution"
        f"       : PASS"
    )


# =====================================================================
# 14. VALIDATE OUTPUT DATA TYPE
# =====================================================================

def validate_output_dtype(
    classified,
):

    print_header(
        "8. OUTPUT DATA TYPE VALIDATION"
    )

    actual_dtype = (
        str(
            classified.dtypes[0]
        )
    )

    print(
        f"Expected data type : uint8"
    )

    print(
        f"Actual data type   : {actual_dtype}"
    )

    dtype_ok = (
        actual_dtype
        == "uint8"
    )

    print(
        f"Unsigned integer class raster"
        f"           : "
        f"{'PASS' if dtype_ok else 'FAIL'}"
    )

    if not dtype_ok:

        raise ValueError(
            "Classified raster is not "
            "stored as uint8."
        )


# =====================================================================
# 15. VALIDATE CLASSIFICATION METADATA
# =====================================================================

def validate_classification_metadata(
    classified,
):

    print_header(
        "9. CLASSIFICATION METADATA VALIDATION"
    )

    tags = (
        classified.tags()
    )

    expected_method = (
        "Quantile classification"
    )

    method_ok = (
        tags.get(
            "classification_method"
        )
        ==
        expected_method
    )

    print(
        f"Classification method"
        f"                    : "
        f"{tags.get('classification_method')}"
    )

    print(
        f"Classification method metadata"
        f"         : "
        f"{'PASS' if method_ok else 'FAIL'}"
    )

    threshold_tags = {
        "q20": str(Q20),
        "q40": str(Q40),
        "q60": str(Q60),
        "q80": str(Q80),
    }

    thresholds_ok = True

    for key, expected in (
        threshold_tags.items()
    ):

        actual = tags.get(key)

        match = (
            actual == expected
        )

        if not match:

            thresholds_ok = False

        print(
            f"{key} metadata"
            f"                     : "
            f"{'PASS' if match else 'FAIL'}"
        )

    if not method_ok:

        raise ValueError(
            "Classification method metadata "
            "is incorrect."
        )

    if not thresholds_ok:

        raise ValueError(
            "Classification threshold metadata "
            "does not match the validated values."
        )

    print(
        "Classification metadata"
        f"                  : PASS"
    )


# =====================================================================
# 16. FINAL VALIDATION
# =====================================================================

def main():

    print(
        "=" * 60
    )

    print(
        "CLASSIFIED FLOOD SUSCEPTIBILITY"
    )

    print(
        "INDEPENDENT VALIDATION"
    )

    print(
        "=" * 60
    )

    print(
        f"\nProject root:\n"
        f"{PROJECT_ROOT}"
    )

    print(
        f"\nContinuous MCDA raster:\n"
        f"{CONTINUOUS_RASTER}"
    )

    print(
        f"\nClassified raster:\n"
        f"{CLASSIFIED_RASTER}"
    )

    # -------------------------------------------------------------
    # 1. File existence
    # -------------------------------------------------------------

    validate_file_existence()

    # -------------------------------------------------------------
    # 2. Open both rasters
    # -------------------------------------------------------------

    with rasterio.open(
        CONTINUOUS_RASTER
    ) as continuous:

        with rasterio.open(
            CLASSIFIED_RASTER
        ) as classified:

            # -----------------------------------------------------
            # 3. Spatial metadata
            # -----------------------------------------------------

            validate_spatial_metadata(
                continuous,
                classified,
            )

            # -----------------------------------------------------
            # 4. Read arrays
            # -----------------------------------------------------

            (
                continuous_array,
                classified_array,
            ) = read_rasters(
                continuous,
                classified,
            )

            # -----------------------------------------------------
            # 5. Valid-cell mask
            # -----------------------------------------------------

            validate_valid_cell_mask(
                continuous_array,
                classified_array,
                continuous.nodata,
                classified.nodata,
            )

            # -----------------------------------------------------
            # 6. Class values
            # -----------------------------------------------------

            validate_class_values(
                classified_array,
                classified.nodata,
            )

            # -----------------------------------------------------
            # 7. Independent reproduction
            # -----------------------------------------------------

            independently_reproduce_classes(
                continuous_array,
                continuous.nodata,
                classified_array,
            )

            # -----------------------------------------------------
            # 8. Class counts
            # -----------------------------------------------------

            validate_class_counts(
                classified_array,
                classified.nodata,
            )

            # -----------------------------------------------------
            # 9. Data type
            # -----------------------------------------------------

            validate_output_dtype(
                classified,
            )

            # -----------------------------------------------------
            # 10. Metadata
            # -----------------------------------------------------

            validate_classification_metadata(
                classified,
            )

    # -------------------------------------------------------------
    # FINAL STATUS
    # -------------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "FINAL CLASSIFICATION VALIDATION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        "\nSpatial validation:"
    )

    print(
        "  CRS                         : PASS"
    )

    print(
        "  Dimensions                  : PASS"
    )

    print(
        "  Resolution                  : PASS"
    )

    print(
        "  Bounds                      : PASS"
    )

    print(
        "  NoData                      : PASS"
    )

    print(
        "  Valid-cell mask             : PASS"
    )

    print(
        "\nClassification validation:"
    )

    print(
        "  Class values 1-5            : PASS"
    )

    print(
        "  All five classes            : PASS"
    )

    print(
        "  Class distribution          : PASS"
    )

    print(
        "  Independent reproduction    : PASS"
    )

    print(
        "  Output data type            : PASS"
    )

    print(
        "  Classification metadata     : PASS"
    )

    print(
        "\nValid cells                  : 553860"
    )

    print(
        "Expected cells per class     : 110772"
    )

    print(
        "\nOVERALL STATUS: PASS"
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "CLASSIFIED SUSCEPTIBILITY "
        "VALIDATION COMPLETED SUCCESSFULLY"
    )

    print(
        "=" * 60
    )


# =====================================================================
# 17. SCRIPT ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    main()