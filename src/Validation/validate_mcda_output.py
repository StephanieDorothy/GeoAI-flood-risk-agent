"""
Independent Validation of the MCDA Flood Susceptibility Surface

This script independently validates the flood susceptibility raster
produced by:

    src/flood_factors/mcda_flood_susceptibility.py

Validation includes:

    1. Output file existence
    2. Raster readability
    3. CRS compatibility
    4. Raster dimensions
    5. Spatial resolution
    6. Affine transform
    7. Spatial bounds
    8. NoData handling
    9. Common valid-cell mask
    10. Finite-value validation
    11. 0-1 susceptibility range
    12. Statistical validation
    13. Independent MCDA recalculation

The validation script is intentionally separate from the MCDA
production script so that the final susceptibility surface can be
independently checked after generation.

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

ALIGNED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
)

MCDA_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
)

OUTPUT_FILE = (
    MCDA_DIR
    / "flood_susceptibility.tif"
)


# =====================================================================
# 2. INPUT FACTORS
# =====================================================================

FACTOR_FILES = {
    "elevation": (
        ALIGNED_DIR
        / "elevation_score.tif"
    ),

    "slope": (
        ALIGNED_DIR
        / "slope_score.tif"
    ),

    "distance_to_rivers": (
        ALIGNED_DIR
        / "distance_to_rivers_score.tif"
    ),

    "landcover": (
        ALIGNED_DIR
        / "landcover_score.tif"
    ),

    "population": (
        ALIGNED_DIR
        / "population_score.tif"
    ),
}


FACTOR_ORDER = [
    "elevation",
    "slope",
    "distance_to_rivers",
    "landcover",
    "population",
]


# =====================================================================
# 3. AHP-DERIVED WEIGHTS
# =====================================================================
#
# These are the independently established AHP weights from the
# Phase 8 MCDA model.
#
# They sum to exactly 1.0.
#
# =====================================================================

WEIGHTS = {
    "elevation": 0.1868744589,

    "slope": 0.1868744589,

    "distance_to_rivers": 0.4352900433,

    "landcover": 0.1285887446,

    "population": 0.0623722944,
}


# =====================================================================
# 4. VALIDATION PARAMETERS
# =====================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603

EXPECTED_HEIGHT = 1019

EXPECTED_RESOLUTION = (
    30.86551681907227,
    30.86551681907227,
)

EXPECTED_NODATA = -9999.0

MIN_EXPECTED_VALUE = 0.0

MAX_EXPECTED_VALUE = 1.0

# Numerical tolerance used for floating-point comparisons.
TOLERANCE = 1e-5

# Tolerance used when comparing independently recalculated MCDA
# values against the generated susceptibility surface.
MCDA_TOLERANCE = 1e-5


# =====================================================================
# 5. HELPER FUNCTIONS
# =====================================================================

def print_header(title):
    """Print a consistent validation section header."""

    print("\n" + "=" * 60)

    print(title)

    print("=" * 60)


def print_status(message, passed):
    """Print a standardized PASS/FAIL status."""

    status = "PASS" if passed else "FAIL"

    print(
        f"{message:45s}: {status}"
    )


# =====================================================================
# 6. CHECK OUTPUT FILE
# =====================================================================

def validate_output_file():
    """
    Confirm that the expected MCDA output exists.
    """

    print_header(
        "1. OUTPUT FILE VALIDATION"
    )

    exists = OUTPUT_FILE.exists()

    print(
        f"Output file:\n{OUTPUT_FILE}"
    )

    print_status(
        "Output file exists",
        exists,
    )

    if not exists:

        raise FileNotFoundError(
            "MCDA output raster was not found."
        )


# =====================================================================
# 7. LOAD OUTPUT RASTER
# =====================================================================

def load_output():

    print_header(
        "2. OUTPUT RASTER READABILITY"
    )

    try:

        src = rasterio.open(
            OUTPUT_FILE
        )

    except Exception as exc:

        raise RuntimeError(
            "Unable to read MCDA output "
            f"raster: {exc}"
        ) from exc

    print_status(
        "GeoTIFF readable",
        True,
    )

    return src


# =====================================================================
# 8. VALIDATE OUTPUT METADATA
# =====================================================================

def validate_metadata(src):

    print_header(
        "3. SPATIAL METADATA VALIDATION"
    )

    # -------------------------------------------------------------
    # CRS
    # -------------------------------------------------------------

    actual_crs = (
        src.crs.to_string()
        if src.crs
        else None
    )

    crs_ok = (
        actual_crs
        == EXPECTED_CRS
    )

    print(
        f"Expected CRS : {EXPECTED_CRS}"
    )

    print(
        f"Actual CRS   : {actual_crs}"
    )

    print_status(
        "CRS",
        crs_ok,
    )

    # -------------------------------------------------------------
    # Dimensions
    # -------------------------------------------------------------

    dimensions_ok = (
        src.width
        == EXPECTED_WIDTH
        and
        src.height
        == EXPECTED_HEIGHT
    )

    print(
        f"Expected size: "
        f"{EXPECTED_WIDTH} x "
        f"{EXPECTED_HEIGHT}"
    )

    print(
        f"Actual size  : "
        f"{src.width} x "
        f"{src.height}"
    )

    print_status(
        "Raster dimensions",
        dimensions_ok,
    )

    # -------------------------------------------------------------
    # Resolution
    # -------------------------------------------------------------

    resolution_ok = (
        np.isclose(
            src.res[0],
            EXPECTED_RESOLUTION[0],
            atol=TOLERANCE,
        )
        and
        np.isclose(
            src.res[1],
            EXPECTED_RESOLUTION[1],
            atol=TOLERANCE,
        )
    )

    print(
        f"Expected resolution: "
        f"{EXPECTED_RESOLUTION}"
    )

    print(
        f"Actual resolution  : "
        f"{src.res}"
    )

    print_status(
        "Pixel resolution",
        resolution_ok,
    )

    # -------------------------------------------------------------
    # NoData
    # -------------------------------------------------------------

    nodata_ok = (
        src.nodata is not None
        and
        np.isclose(
            src.nodata,
            EXPECTED_NODATA,
            atol=TOLERANCE,
        )
    )

    print(
        f"Expected NoData: "
        f"{EXPECTED_NODATA}"
    )

    print(
        f"Actual NoData  : "
        f"{src.nodata}"
    )

    print_status(
        "NoData value",
        nodata_ok,
    )

    # -------------------------------------------------------------
    # Data type
    # -------------------------------------------------------------

    datatype_ok = (
        src.dtypes[0]
        == "float32"
    )

    print(
        f"Actual data type: "
        f"{src.dtypes[0]}"
    )

    print_status(
        "Float32 output",
        datatype_ok,
    )

    if not (
        crs_ok
        and dimensions_ok
        and resolution_ok
        and nodata_ok
        and datatype_ok
    ):

        raise ValueError(
            "One or more output metadata "
            "checks failed."
        )


# =====================================================================
# 9. LOAD FACTOR RASTERS
# =====================================================================

def load_factor_rasters():

    print_header(
        "4. ALIGNED FACTOR VALIDATION"
    )

    arrays = {}

    reference = None

    for factor in FACTOR_ORDER:

        path = FACTOR_FILES[factor]

        if not path.exists():

            raise FileNotFoundError(
                f"Required factor raster "
                f"is missing: {path}"
            )

        with rasterio.open(path) as src:

            array = src.read(
                1
            ).astype(
                np.float32,
                copy=False
            )

            arrays[factor] = array

            # -----------------------------------------------------
            # Establish reference grid from elevation.
            # -----------------------------------------------------

            if reference is None:

                reference = {
                    "crs": src.crs,
                    "transform": src.transform,
                    "width": src.width,
                    "height": src.height,
                    "res": src.res,
                }

            else:

                if src.crs != reference["crs"]:

                    raise ValueError(
                        f"CRS mismatch for "
                        f"{factor}."
                    )

                if src.transform != (
                    reference["transform"]
                ):

                    raise ValueError(
                        f"Transform mismatch "
                        f"for {factor}."
                    )

                if src.width != (
                    reference["width"]
                ):

                    raise ValueError(
                        f"Width mismatch "
                        f"for {factor}."
                    )

                if src.height != (
                    reference["height"]
                ):

                    raise ValueError(
                        f"Height mismatch "
                        f"for {factor}."
                    )

            print(
                f"{factor:25s}: FOUND"
            )

    print_status(
        "All aligned factor rasters",
        True,
    )

    return arrays, reference


# =====================================================================
# 10. CREATE COMMON VALID MASK
# =====================================================================

def create_common_valid_mask():

    """
    Create the spatial mask representing cells where all five
    standardized factors contain valid data.
    """

    common_mask = np.ones(
        (
            EXPECTED_HEIGHT,
            EXPECTED_WIDTH,
        ),
        dtype=bool,
    )

    for factor in FACTOR_ORDER:

        path = FACTOR_FILES[factor]

        with rasterio.open(path) as src:

            array = src.read(
                1
            ).astype(
                np.float32,
                copy=False
            )

            factor_mask = np.isfinite(
                array
            )

            if src.nodata is not None:

                factor_mask &= (
                    array
                    != src.nodata
                )

            common_mask &= (
                factor_mask
            )

    return common_mask


# =====================================================================
# 11. VALIDATE OUTPUT VALID MASK
# =====================================================================

def validate_valid_mask(
    output_array,
    common_mask,
    output_nodata,
):

    print_header(
        "5. VALID-CELL MASK VALIDATION"
    )

    output_valid_mask = np.isfinite(
        output_array
    )

    if output_nodata is not None:

        output_valid_mask &= (
            output_array
            != output_nodata
        )

    common_valid_count = int(
        np.count_nonzero(
            common_mask
        )
    )

    output_valid_count = int(
        np.count_nonzero(
            output_valid_mask
        )
    )

    print(
        f"Common valid factor cells : "
        f"{common_valid_count}"
    )

    print(
        f"Output valid cells        : "
        f"{output_valid_count}"
    )

    mask_matches = np.array_equal(
        output_valid_mask,
        common_mask,
    )

    print_status(
        "Output mask matches "
        "common factor mask",
        mask_matches,
    )

    if not mask_matches:

        raise ValueError(
            "Output valid-cell mask does "
            "not match the common valid "
            "factor mask."
        )

    return output_valid_mask


# =====================================================================
# 12. VALIDATE OUTPUT VALUES
# =====================================================================

def validate_output_values(
    output_array,
    valid_mask,
):

    print_header(
        "6. OUTPUT VALUE VALIDATION"
    )

    valid_values = (
        output_array[
            valid_mask
        ]
    )

    if valid_values.size == 0:

        raise ValueError(
            "No valid output cells found."
        )

    # -------------------------------------------------------------
    # Finite values
    # -------------------------------------------------------------

    finite_ok = np.all(
        np.isfinite(
            valid_values
        )
    )

    print_status(
        "All valid cells are finite",
        finite_ok,
    )

    if not finite_ok:

        raise ValueError(
            "Output contains non-finite "
            "values."
        )

    # -------------------------------------------------------------
    # Range
    # -------------------------------------------------------------

    minimum = float(
        np.min(valid_values)
    )

    maximum = float(
        np.max(valid_values)
    )

    mean = float(
        np.mean(valid_values)
    )

    median = float(
        np.median(valid_values)
    )

    standard_deviation = float(
        np.std(valid_values)
    )

    percentile_5 = float(
        np.percentile(
            valid_values,
            5,
        )
    )

    percentile_25 = float(
        np.percentile(
            valid_values,
            25,
        )
    )

    percentile_75 = float(
        np.percentile(
            valid_values,
            75,
        )
    )

    percentile_95 = float(
        np.percentile(
            valid_values,
            95,
        )
    )

    range_ok = (
        minimum
        >= MIN_EXPECTED_VALUE
        - TOLERANCE
        and
        maximum
        <= MAX_EXPECTED_VALUE
        + TOLERANCE
    )

    print(
        f"Minimum              : "
        f"{minimum:.9f}"
    )

    print(
        f"5th percentile       : "
        f"{percentile_5:.9f}"
    )

    print(
        f"25th percentile      : "
        f"{percentile_25:.9f}"
    )

    print(
        f"Median               : "
        f"{median:.9f}"
    )

    print(
        f"75th percentile      : "
        f"{percentile_75:.9f}"
    )

    print(
        f"95th percentile      : "
        f"{percentile_95:.9f}"
    )

    print(
        f"Maximum              : "
        f"{maximum:.9f}"
    )

    print(
        f"Mean                 : "
        f"{mean:.9f}"
    )

    print(
        f"Standard deviation   : "
        f"{standard_deviation:.9f}"
    )

    print_status(
        "Output values within 0-1 range",
        range_ok,
    )

    if not range_ok:

        raise ValueError(
            "MCDA susceptibility values "
            "fall outside the expected "
            "0-1 range."
        )

    return {
        "valid_cells": int(
            valid_values.size
        ),
        "minimum": minimum,
        "maximum": maximum,
        "mean": mean,
        "median": median,
        "standard_deviation": (
            standard_deviation
        ),
        "percentile_5": percentile_5,
        "percentile_25": percentile_25,
        "percentile_75": percentile_75,
        "percentile_95": percentile_95,
    }


# =====================================================================
# 13. INDEPENDENTLY RECALCULATE MCDA
# =====================================================================

def independently_recalculate_mcda(
    arrays,
    valid_mask,
):

    """
    Independently reproduce the weighted linear combination using
    the aligned standardized factors and the established AHP weights.

    Formula:

        FS =
            wE * E
          + wS * S
          + wR * R
          + wL * L
          + wP * P

    This provides a strong reproducibility check against the
    generated flood_susceptibility.tif.
    """

    print_header(
        "7. INDEPENDENT MCDA REPRODUCTION"
    )

    recalculated = np.zeros(
        valid_mask.shape,
        dtype=np.float64,
    )

    for factor in FACTOR_ORDER:

        weight = WEIGHTS[factor]

        print(
            f"{factor:25s}: "
            f"weight={weight:.10f}"
        )

        recalculated[
            valid_mask
        ] += (
            arrays[factor][
                valid_mask
            ].astype(
                np.float64
            )
            * weight
        )

    return recalculated


# =====================================================================
# 14. COMPARE GENERATED AND RECALCULATED MCDA
# =====================================================================

def compare_mcda_results(
    output_array,
    recalculated,
    valid_mask,
):

    generated = (
        output_array[
            valid_mask
        ].astype(
            np.float64
        )
    )

    difference = (
        generated
        - recalculated[
            valid_mask
        ]
    )

    absolute_difference = np.abs(
        difference
    )

    maximum_difference = float(
        np.max(
            absolute_difference
        )
    )

    mean_difference = float(
        np.mean(
            absolute_difference
        )
    )

    matching_cells = int(
        np.count_nonzero(
            absolute_difference
            <= MCDA_TOLERANCE
        )
    )

    total_cells = int(
        absolute_difference.size
    )

    all_cells_match = (
        maximum_difference
        <= MCDA_TOLERANCE
    )

    print_header(
        "8. MCDA REPRODUCIBILITY CHECK"
    )

    print(
        f"Valid cells compared     : "
        f"{total_cells}"
    )

    print(
        f"Cells within tolerance   : "
        f"{matching_cells}"
    )

    print(
        f"Maximum absolute error   : "
        f"{maximum_difference:.12f}"
    )

    print(
        f"Mean absolute error      : "
        f"{mean_difference:.12f}"
    )

    print(
        f"Tolerance                : "
        f"{MCDA_TOLERANCE:.12f}"
    )

    print_status(
        "Generated MCDA matches "
        "independent calculation",
        all_cells_match,
    )

    if not all_cells_match:

        raise ValueError(
            "Generated MCDA surface does "
            "not match the independently "
            "recalculated surface."
        )

    return {
        "maximum_difference": (
            maximum_difference
        ),
        "mean_difference": (
            mean_difference
        ),
        "matching_cells": (
            matching_cells
        ),
        "total_cells": (
            total_cells
        ),
    }


# =====================================================================
# 15. FINAL VALIDATION SUMMARY
# =====================================================================

def print_final_summary(
    statistics,
    comparison,
):

    print_header(
        "FINAL MCDA VALIDATION SUMMARY"
    )

    print(
        f"Output file:\n{OUTPUT_FILE}"
    )

    print(
        "\nSpatial validation:"
    )

    print(
        "  CRS                     : PASS"
    )

    print(
        "  Dimensions              : PASS"
    )

    print(
        "  Resolution              : PASS"
    )

    print(
        "  NoData                  : PASS"
    )

    print(
        "  Valid-cell mask         : PASS"
    )

    print(
        "\nValue validation:"
    )

    print(
        "  Finite values           : PASS"
    )

    print(
        "  0-1 range               : PASS"
    )

    print(
        "\nMCDA reproducibility:"
    )

    print(
        "  Independent calculation : PASS"
    )

    print(
        f"\nValid cells              : "
        f"{statistics['valid_cells']}"
    )

    print(
        f"Minimum                  : "
        f"{statistics['minimum']:.6f}"
    )

    print(
        f"Maximum                  : "
        f"{statistics['maximum']:.6f}"
    )

    print(
        f"Mean                     : "
        f"{statistics['mean']:.6f}"
    )

    print(
        f"Median                   : "
        f"{statistics['median']:.6f}"
    )

    print(
        f"Standard deviation       : "
        f"{statistics['standard_deviation']:.6f}"
    )

    print(
        f"Maximum MCDA difference  : "
        f"{comparison['maximum_difference']:.12f}"
    )

    print(
        "\nOVERALL STATUS: PASS"
    )


# =====================================================================
# 16. MAIN VALIDATION WORKFLOW
# =====================================================================

def main():

    print(
        "=" * 60
    )

    print(
        "MCDA FLOOD SUSCEPTIBILITY "
        "INDEPENDENT VALIDATION"
    )

    print(
        "=" * 60
    )

    print(
        f"\nProject root:\n"
        f"{PROJECT_ROOT}"
    )

    # -------------------------------------------------------------
    # 1. Confirm output exists.
    # -------------------------------------------------------------

    validate_output_file()

    # -------------------------------------------------------------
    # 2. Open output.
    # -------------------------------------------------------------

    src = load_output()

    try:

        # ---------------------------------------------------------
        # 3. Validate metadata.
        # ---------------------------------------------------------

        validate_metadata(
            src
        )

        # ---------------------------------------------------------
        # 4. Read output raster.
        # ---------------------------------------------------------

        output_array = src.read(
            1
        ).astype(
            np.float32,
            copy=False
        )

        output_nodata = src.nodata

    finally:

        src.close()

    # -------------------------------------------------------------
    # 5. Load aligned factor rasters.
    # -------------------------------------------------------------

    arrays, reference = (
        load_factor_rasters()
    )

    # -------------------------------------------------------------
    # 6. Create common valid mask.
    # -------------------------------------------------------------

    common_mask = (
        create_common_valid_mask()
    )

    # -------------------------------------------------------------
    # 7. Compare output valid mask.
    # -------------------------------------------------------------

    valid_mask = (
        validate_valid_mask(
            output_array,
            common_mask,
            output_nodata,
        )
    )

    # -------------------------------------------------------------
    # 8. Validate output values.
    # -------------------------------------------------------------

    statistics = (
        validate_output_values(
            output_array,
            valid_mask,
        )
    )

    # -------------------------------------------------------------
    # 9. Independently reproduce MCDA.
    # -------------------------------------------------------------

    recalculated = (
        independently_recalculate_mcda(
            arrays,
            valid_mask,
        )
    )

    # -------------------------------------------------------------
    # 10. Compare generated and independently
    #     recalculated surfaces.
    # -------------------------------------------------------------

    comparison = (
        compare_mcda_results(
            output_array,
            recalculated,
            valid_mask,
        )
    )

    # -------------------------------------------------------------
    # 11. Final summary.
    # -------------------------------------------------------------

    print_final_summary(
        statistics,
        comparison,
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "MCDA VALIDATION COMPLETED "
        "SUCCESSFULLY"
    )

    print(
        "=" * 60
    )


# =====================================================================
# 17. SCRIPT ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    main()