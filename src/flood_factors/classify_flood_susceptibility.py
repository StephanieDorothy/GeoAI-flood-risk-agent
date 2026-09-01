"""
Flood Susceptibility Classification

This script converts the continuous MCDA flood susceptibility
surface into five relative susceptibility classes using
quantile-based thresholds.

Input:
    data/analysis/mcda/flood_susceptibility.tif

Output:
    data/analysis/mcda/flood_susceptibility_classified.tif

Classification method:
    Quantile classification

Classes:
    1 = Very Low
    2 = Low
    3 = Moderate
    4 = High
    5 = Very High

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

INPUT_FILE = (
    MCDA_DIR
    / "flood_susceptibility.tif"
)

OUTPUT_FILE = (
    MCDA_DIR
    / "flood_susceptibility_classified.tif"
)


# =====================================================================
# 2. CLASSIFICATION THRESHOLDS
# =====================================================================
#
# These thresholds were calculated from the validated continuous
# MCDA surface using quantiles:
#
# 20th percentile = 0.6915898
# 40th percentile = 0.7606905
# 60th percentile = 0.8051752
# 80th percentile = 0.84985673
#
# The thresholds are intentionally stored here so the classification
# is fully reproducible.
#
# =====================================================================

Q20 = 0.6915898

Q40 = 0.7606905

Q60 = 0.8051752

Q80 = 0.84985673


# =====================================================================
# 3. CLASS DEFINITIONS
# =====================================================================

CLASS_CODES = {
    "Very Low": 1,
    "Low": 2,
    "Moderate": 3,
    "High": 4,
    "Very High": 5,
}


# =====================================================================
# 4. EXPECTED INPUT PROPERTIES
# =====================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603

EXPECTED_HEIGHT = 1019

EXPECTED_NODATA = -9999.0


# =====================================================================
# 5. HELPER FUNCTION
# =====================================================================

def print_header(title):
    """Print a consistent section header."""

    print("\n" + "=" * 60)

    print(title)

    print("=" * 60)


# =====================================================================
# 6. VALIDATE CLASSIFICATION THRESHOLDS
# =====================================================================

def validate_thresholds():

    print_header(
        "1. CLASSIFICATION THRESHOLD VALIDATION"
    )

    thresholds = [
        Q20,
        Q40,
        Q60,
        Q80,
    ]

    # -------------------------------------------------------------
    # Check that all thresholds are finite.
    # -------------------------------------------------------------

    finite_ok = all(
        np.isfinite(
            value
        )
        for value in thresholds
    )

    if not finite_ok:

        raise ValueError(
            "Classification thresholds "
            "must all be finite."
        )

    # -------------------------------------------------------------
    # Check that thresholds are strictly increasing.
    # -------------------------------------------------------------

    increasing_ok = (
        Q20 < Q40
        and
        Q40 < Q60
        and
        Q60 < Q80
    )

    if not increasing_ok:

        raise ValueError(
            "Classification thresholds "
            "must be strictly increasing."
        )

    # -------------------------------------------------------------
    # Check that thresholds are within the MCDA range.
    # -------------------------------------------------------------

    range_ok = all(
        0.0 <= value <= 1.0
        for value in thresholds
    )

    if not range_ok:

        raise ValueError(
            "Classification thresholds "
            "must fall within the 0-1 "
            "MCDA range."
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
        "Threshold validation              : PASS"
    )


# =====================================================================
# 7. VALIDATE INPUT RASTER
# =====================================================================

def validate_input_raster(src):

    print_header(
        "2. INPUT RASTER VALIDATION"
    )

    actual_crs = (
        src.crs.to_string()
        if src.crs
        else None
    )

    print(
        f"Expected CRS : {EXPECTED_CRS}"
    )

    print(
        f"Actual CRS   : {actual_crs}"
    )

    if actual_crs != EXPECTED_CRS:

        raise ValueError(
            "Input raster CRS does not "
            "match EPSG:32737."
        )

    print(
        "CRS                              : PASS"
    )

    dimensions_ok = (
        src.width == EXPECTED_WIDTH
        and
        src.height == EXPECTED_HEIGHT
    )

    print(
        f"Expected dimensions : "
        f"{EXPECTED_WIDTH} x "
        f"{EXPECTED_HEIGHT}"
    )

    print(
        f"Actual dimensions   : "
        f"{src.width} x "
        f"{src.height}"
    )

    if not dimensions_ok:

        raise ValueError(
            "Input raster dimensions do "
            "not match the expected MCDA "
            "grid."
        )

    print(
        "Raster dimensions                 : PASS"
    )

    nodata_ok = (
        src.nodata is not None
        and
        np.isclose(
            src.nodata,
            EXPECTED_NODATA,
        )
    )

    print(
        f"Expected NoData : {EXPECTED_NODATA}"
    )

    print(
        f"Actual NoData   : {src.nodata}"
    )

    if not nodata_ok:

        raise ValueError(
            "Input raster NoData value does "
            "not match the expected value."
        )

    print(
        "NoData value                     : PASS"
    )


# =====================================================================
# 8. CREATE CLASSIFIED RASTER
# =====================================================================

def classify_raster(
    input_array,
    nodata,
):

    # -------------------------------------------------------------
    # Create valid-data mask.
    # -------------------------------------------------------------

    valid_mask = np.isfinite(
        input_array
    )

    if nodata is not None:

        valid_mask &= (
            input_array
            != nodata
        )

    valid_values = (
        input_array[
            valid_mask
        ]
    )

    if valid_values.size == 0:

        raise ValueError(
            "Input raster contains no "
            "valid MCDA values."
        )

    # -------------------------------------------------------------
    # Validate input values.
    # -------------------------------------------------------------

    minimum = float(
        np.min(valid_values)
    )

    maximum = float(
        np.max(valid_values)
    )

    if minimum < 0.0 or maximum > 1.0:

        raise ValueError(
            "Input MCDA raster contains "
            "values outside the expected "
            "0-1 range."
        )

    # -------------------------------------------------------------
    # Create output initialized to NoData.
    #
    # Class raster uses:
    #
    # 0 = NoData
    # 1 = Very Low
    # 2 = Low
    # 3 = Moderate
    # 4 = High
    # 5 = Very High
    #
    # -------------------------------------------------------------

    classified = np.zeros(
        input_array.shape,
        dtype=np.uint8,
    )

    # -------------------------------------------------------------
    # Apply quantile classification.
    # -------------------------------------------------------------

    classified[
        valid_mask
        &
        (input_array <= Q20)
    ] = 1

    classified[
        valid_mask
        &
        (input_array > Q20)
        &
        (input_array <= Q40)
    ] = 2

    classified[
        valid_mask
        &
        (input_array > Q40)
        &
        (input_array <= Q60)
    ] = 3

    classified[
        valid_mask
        &
        (input_array > Q60)
        &
        (input_array <= Q80)
    ] = 4

    classified[
        valid_mask
        &
        (input_array > Q80)
    ] = 5

    return classified, valid_mask


# =====================================================================
# 9. VALIDATE CLASS DISTRIBUTION
# =====================================================================

def validate_class_distribution(
    classified,
    valid_mask,
):

    print_header(
        "3. CLASS DISTRIBUTION VALIDATION"
    )

    class_names = {
        1: "Very Low",
        2: "Low",
        3: "Moderate",
        4: "High",
        5: "Very High",
    }

    valid_class_values = (
        classified[
            valid_mask
        ]
    )

    total_valid = (
        valid_class_values.size
    )

    print(
        f"Total valid cells: "
        f"{total_valid}"
    )

    for code in range(1, 6):

        count = int(
            np.count_nonzero(
                valid_class_values
                == code
            )
        )

        percentage = (
            count
            / total_valid
            * 100.0
        )

        print(
            f"{code} - "
            f"{class_names[code]:10s}: "
            f"{count:8d} cells "
            f"({percentage:6.2f}%)"
        )

    # -------------------------------------------------------------
    # Ensure every valid cell received a class.
    # -------------------------------------------------------------

    valid_class_mask = (
        classified[
            valid_mask
        ] >= 1
    ) & (
        classified[
            valid_mask
        ] <= 5
    )

    all_classified = np.all(
        valid_class_mask
    )

    if not all_classified:

        raise ValueError(
            "One or more valid MCDA "
            "cells did not receive "
            "a susceptibility class."
        )

    print(
        "All valid cells classified       : PASS"
    )

    # -------------------------------------------------------------
    # Ensure all five classes exist.
    # -------------------------------------------------------------

    classes_present = set(
        np.unique(
            valid_class_values
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
        classes_present
        == expected_classes
    )

    if not all_classes_present:

        raise ValueError(
            "Not all five susceptibility "
            "classes are present."
        )

    print(
        "All five classes present         : PASS"
    )


# =====================================================================
# 10. SAVE CLASSIFIED RASTER
# =====================================================================

def save_classified_raster(
    classified,
    source,
):

    print_header(
        "4. OUTPUT RASTER CREATION"
    )

    profile = source.profile.copy()

    profile.update(
        dtype="uint8",
        count=1,
        nodata=0,
        compress="lzw",
    )

    with rasterio.open(
        OUTPUT_FILE,
        "w",
        **profile,
    ) as dst:

        dst.write(
            classified,
            1,
        )

        # ---------------------------------------------------------
        # Store classification metadata directly in the GeoTIFF.
        # ---------------------------------------------------------

        dst.update_tags(
            classification_method=(
                "Quantile classification"
            ),
            class_1="Very Low",
            class_2="Low",
            class_3="Moderate",
            class_4="High",
            class_5="Very High",
            q20=str(Q20),
            q40=str(Q40),
            q60=str(Q60),
            q80=str(Q80),
            source_raster=(
                "flood_susceptibility.tif"
            ),
        )

    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )

    print(
        "Classified raster creation       : PASS"
    )


# =====================================================================
# 11. VERIFY OUTPUT RASTER
# =====================================================================

def verify_output_raster():

    print_header(
        "5. OUTPUT RASTER VERIFICATION"
    )

    if not OUTPUT_FILE.exists():

        raise FileNotFoundError(
            "Classified output raster was "
            "not created."
        )

    with rasterio.open(
        OUTPUT_FILE
    ) as src:

        array = src.read(
            1
        )

        valid_mask = (
            array
            != src.nodata
        )

        valid_values = (
            array[
                valid_mask
            ]
        )

        # ---------------------------------------------------------
        # Spatial metadata
        # ---------------------------------------------------------

        crs_ok = (
            src.crs.to_string()
            == EXPECTED_CRS
        )

        dimensions_ok = (
            src.width
            == EXPECTED_WIDTH
            and
            src.height
            == EXPECTED_HEIGHT
        )

        # ---------------------------------------------------------
        # Class range
        # ---------------------------------------------------------

        class_range_ok = (
            valid_values.size > 0
            and
            np.min(valid_values) >= 1
            and
            np.max(valid_values) <= 5
        )

        print(
            f"CRS                            : "
            f"{'PASS' if crs_ok else 'FAIL'}"
        )

        print(
            f"Dimensions                     : "
            f"{'PASS' if dimensions_ok else 'FAIL'}"
        )

        print(
            f"Class values 1-5               : "
            f"{'PASS' if class_range_ok else 'FAIL'}"
        )

        if not (
            crs_ok
            and dimensions_ok
            and class_range_ok
        ):

            raise ValueError(
                "Classified output raster "
                "verification failed."
            )


# =====================================================================
# 12. MAIN WORKFLOW
# =====================================================================

def main():

    print(
        "=" * 60
    )

    print(
        "FLOOD SUSCEPTIBILITY CLASSIFICATION"
    )

    print(
        "=" * 60
    )

    print(
        f"\nProject root:\n"
        f"{PROJECT_ROOT}"
    )

    print(
        f"\nInput raster:\n"
        f"{INPUT_FILE}"
    )

    print(
        f"\nOutput raster:\n"
        f"{OUTPUT_FILE}"
    )

    # -------------------------------------------------------------
    # 1. Validate thresholds.
    # -------------------------------------------------------------

    validate_thresholds()

    # -------------------------------------------------------------
    # 2. Confirm input exists.
    # -------------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Continuous MCDA raster not found:\n"
            f"{INPUT_FILE}"
        )

    # -------------------------------------------------------------
    # 3. Open input raster.
    # -------------------------------------------------------------

    with rasterio.open(
        INPUT_FILE
    ) as src:

        # ---------------------------------------------------------
        # Validate input.
        # ---------------------------------------------------------

        validate_input_raster(
            src
        )

        # ---------------------------------------------------------
        # Read continuous susceptibility surface.
        # ---------------------------------------------------------

        input_array = src.read(
            1
        ).astype(
            np.float32,
            copy=False
        )

        # ---------------------------------------------------------
        # Create classified raster.
        # ---------------------------------------------------------

        classified, valid_mask = (
            classify_raster(
                input_array,
                src.nodata,
            )
        )

        # ---------------------------------------------------------
        # Validate class distribution.
        # ---------------------------------------------------------

        validate_class_distribution(
            classified,
            valid_mask,
        )

        # ---------------------------------------------------------
        # Save output.
        # ---------------------------------------------------------

        save_classified_raster(
            classified,
            src,
        )

    # -------------------------------------------------------------
    # 4. Verify saved raster.
    # -------------------------------------------------------------

    verify_output_raster()

    # -------------------------------------------------------------
    # 5. Final status.
    # -------------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "CLASSIFICATION COMPLETED "
        "SUCCESSFULLY"
    )

    print(
        "=" * 60
    )


# =====================================================================
# 13. SCRIPT ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    main()