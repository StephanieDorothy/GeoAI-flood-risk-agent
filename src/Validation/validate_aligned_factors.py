"""
GeoAI Flood Risk Decision Agent
--------------------------------
Phase 7 — Spatial Alignment Validation

Script:
    validate_aligned_factors.py

Purpose:
    Independently validate the five standardized flood-conditioning
    factors after spatial alignment.

Reference raster:
    data/analysis/aligned/elevation_score.tif

Aligned factors:
    1. Elevation
    2. Slope
    3. Distance to Rivers
    4. Population
    5. Land Cover

Validation categories:
    1. File existence
    2. CRS
    3. Raster dimensions
    4. Resolution
    5. Transform
    6. Bounds
    7. Data type
    8. NoData
    9. NaN / infinite values
    10. Standardized value range
    11. Valid-cell count
    12. Exact value preservation for factors that were already aligned

Important:
    This script validates the outputs produced by
    align_standardized_factors.py.

    It does NOT modify any raster.

Author:
    Dorothy Stephanie
"""

from pathlib import Path

import numpy as np
import rasterio


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALIGNED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
)

STANDARDIZED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "standardized"
)


# ============================================================================
# RASTER DEFINITIONS
# ============================================================================

RASTERS = {
    "Elevation": "elevation_score.tif",
    "Slope": "slope_score.tif",
    "Distance to Rivers": "distance_to_rivers_score.tif",
    "Population": "population_score.tif",
    "Land Cover": "landcover_score.tif",
}


# ============================================================================
# FACTORS THAT SHOULD NOT HAVE CHANGED
# ============================================================================

UNCHANGED_FACTORS = {
    "Elevation",
    "Slope",
    "Distance to Rivers",
}


# ============================================================================
# EXPECTED VALUES
# ============================================================================

EXPECTED_NODATA = -9999.0
EXPECTED_DTYPE = "float32"

MIN_SCORE = 0.0
MAX_SCORE = 1.0


# ============================================================================
# COUNTERS
# ============================================================================

TOTAL_CHECKS = 0
PASSED_CHECKS = 0
FAILED_CHECKS = 0


# ============================================================================
# OUTPUT FUNCTIONS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section header."""

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def record_check(
    check_name: str,
    passed: bool,
    details: str = "",
) -> None:
    """
    Record and display one validation result.
    """

    global TOTAL_CHECKS
    global PASSED_CHECKS
    global FAILED_CHECKS

    TOTAL_CHECKS += 1

    if passed:
        PASSED_CHECKS += 1
        status = "PASS"
    else:
        FAILED_CHECKS += 1
        status = "FAIL"

    if details:
        print(
            f"{check_name:<30} {status:<6} {details}"
        )
    else:
        print(
            f"{check_name:<30} {status}"
        )


# ============================================================================
# FILE CHECK
# ============================================================================

def check_file_exists(
    path: Path,
    factor_name: str,
) -> None:
    """Check whether an aligned raster exists."""

    record_check(
        f"{factor_name} file exists",
        path.exists(),
        str(path),
    )


# ============================================================================
# REFERENCE GRID
# ============================================================================

def load_reference() -> dict:
    """
    Load the spatial definition of the aligned elevation raster.
    """

    reference_path = (
        ALIGNED_DIR
        / RASTERS["Elevation"]
    )

    if not reference_path.exists():
        raise FileNotFoundError(
            "Reference raster not found:\n"
            f"{reference_path}"
        )

    with rasterio.open(reference_path) as src:

        reference = {
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
            "resolution": src.res,
            "bounds": src.bounds,
            "nodata": src.nodata,
            "dtype": src.dtypes[0],
        }

    return reference


# ============================================================================
# REFERENCE INFORMATION
# ============================================================================

def print_reference_information(
    reference: dict,
) -> None:
    """Print the reference grid information."""

    print_header("REFERENCE GRID")

    print(
        f"CRS:          {reference['crs']}"
    )

    print(
        f"Dimensions:   "
        f"{reference['width']} × "
        f"{reference['height']}"
    )

    print(
        f"Resolution:   "
        f"{reference['resolution'][0]:.12f} × "
        f"{reference['resolution'][1]:.12f}"
    )

    print(
        f"NoData:       "
        f"{reference['nodata']}"
    )

    print(
        f"Data type:    "
        f"{reference['dtype']}"
    )

    print(
        "Bounds:       "
        f"left={reference['bounds'].left:.6f}, "
        f"bottom={reference['bounds'].bottom:.6f}, "
        f"right={reference['bounds'].right:.6f}, "
        f"top={reference['bounds'].top:.6f}"
    )


# ============================================================================
# GRID VALIDATION
# ============================================================================

def validate_grid(
    src,
    reference: dict,
    factor_name: str,
) -> None:
    """
    Validate that an aligned raster has exactly the same
    spatial grid as the reference.
    """

    print_header(
        f"{factor_name.upper()} — SPATIAL GRID VALIDATION"
    )

    record_check(
        "CRS",
        src.crs == reference["crs"],
        f"{src.crs}",
    )

    record_check(
        "Width",
        src.width == reference["width"],
        f"{src.width}",
    )

    record_check(
        "Height",
        src.height == reference["height"],
        f"{src.height}",
    )

    record_check(
        "Resolution",
        src.res == reference["resolution"],
        (
            f"{src.res[0]:.12f} × "
            f"{src.res[1]:.12f}"
        ),
    )

    record_check(
        "Transform",
        src.transform == reference["transform"],
        str(src.transform),
    )

    record_check(
        "Bounds",
        src.bounds == reference["bounds"],
        (
            f"left={src.bounds.left:.6f}, "
            f"bottom={src.bounds.bottom:.6f}, "
            f"right={src.bounds.right:.6f}, "
            f"top={src.bounds.top:.6f}"
        ),
    )


# ============================================================================
# DATA STRUCTURE VALIDATION
# ============================================================================

def validate_data_structure(
    src,
    factor_name: str,
) -> None:
    """Validate datatype and NoData metadata."""

    print_header(
        f"{factor_name.upper()} — DATA STRUCTURE"
    )

    record_check(
        "Data type",
        src.dtypes[0] == EXPECTED_DTYPE,
        src.dtypes[0],
    )

    record_check(
        "NoData metadata",
        src.nodata == EXPECTED_NODATA,
        str(src.nodata),
    )


# ============================================================================
# VALUE VALIDATION
# ============================================================================

def validate_values(
    data: np.ndarray,
    factor_name: str,
) -> dict:
    """
    Validate numerical values within an aligned raster.

    Returns summary statistics.
    """

    print_header(
        f"{factor_name.upper()} — VALUE VALIDATION"
    )

    valid_mask = (
        data != EXPECTED_NODATA
    )

    valid_values = data[valid_mask]

    if valid_values.size == 0:

        record_check(
            "Valid cells exist",
            False,
            "No valid cells found.",
        )

        return {
            "valid_count": 0,
            "nodata_count": data.size,
            "minimum": None,
            "maximum": None,
            "mean": None,
            "nan_count": 0,
            "inf_count": 0,
        }

    record_check(
        "Valid cells exist",
        True,
        f"{valid_values.size:,}",
    )

    # ------------------------------------------------------------------------
    # NaN
    # ------------------------------------------------------------------------

    nan_count = np.isnan(
        valid_values
    ).sum()

    record_check(
        "NaN values",
        nan_count == 0,
        f"{nan_count:,}",
    )

    # ------------------------------------------------------------------------
    # Infinite values
    # ------------------------------------------------------------------------

    inf_count = np.isinf(
        valid_values
    ).sum()

    record_check(
        "Infinite values",
        inf_count == 0,
        f"{inf_count:,}",
    )

    # ------------------------------------------------------------------------
    # Minimum
    # ------------------------------------------------------------------------

    minimum = float(
        np.min(valid_values)
    )

    record_check(
        "Minimum >= 0",
        minimum >= MIN_SCORE,
        f"{minimum:.6f}",
    )

    # ------------------------------------------------------------------------
    # Maximum
    # ------------------------------------------------------------------------

    maximum = float(
        np.max(valid_values)
    )

    record_check(
        "Maximum <= 1",
        maximum <= MAX_SCORE,
        f"{maximum:.6f}",
    )

    # ------------------------------------------------------------------------
    # Mean
    # ------------------------------------------------------------------------

    mean = float(
        np.mean(valid_values)
    )

    # ------------------------------------------------------------------------
    # NoData count
    # ------------------------------------------------------------------------

    nodata_count = int(
        np.sum(
            data == EXPECTED_NODATA
        )
    )

    print(
        f"\nValid cells:   {valid_values.size:,}"
    )

    print(
        f"NoData cells:  {nodata_count:,}"
    )

    print(
        f"Minimum:       {minimum:.6f}"
    )

    print(
        f"Maximum:       {maximum:.6f}"
    )

    print(
        f"Mean:          {mean:.6f}"
    )

    return {
        "valid_count": int(valid_values.size),
        "nodata_count": nodata_count,
        "minimum": minimum,
        "maximum": maximum,
        "mean": mean,
        "nan_count": int(nan_count),
        "inf_count": int(inf_count),
    }


# ============================================================================
# EXACT VALUE COMPARISON
# ============================================================================

def validate_unchanged_factor(
    factor_name: str,
    aligned_data: np.ndarray,
) -> None:
    """
    Compare aligned factors that should not have changed against
    their Phase 6 standardized originals.
    """

    print_header(
        f"{factor_name.upper()} — VALUE PRESERVATION"
    )

    original_path = (
        STANDARDIZED_DIR
        / RASTERS[factor_name]
    )

    if not original_path.exists():

        record_check(
            "Original raster exists",
            False,
            str(original_path),
        )

        return

    with rasterio.open(original_path) as src:

        original_data = src.read(1)

    record_check(
        "Shape unchanged",
        original_data.shape == aligned_data.shape,
        (
            f"Original={original_data.shape}, "
            f"Aligned={aligned_data.shape}"
        ),
    )

    if original_data.shape != aligned_data.shape:
        return

    # ------------------------------------------------------------------------
    # Compare values exactly.
    #
    # Both rasters are copied without resampling, so their values should
    # remain identical.
    # ------------------------------------------------------------------------

    identical = np.array_equal(
        original_data,
        aligned_data,
    )

    record_check(
        "Values preserved exactly",
        identical,
    )

    if not identical:

        difference = (
            aligned_data.astype(np.float64)
            - original_data.astype(np.float64)
        )

        valid_difference = difference[
            original_data != EXPECTED_NODATA
        ]

        if valid_difference.size > 0:

            print(
                "Maximum absolute difference: "
                f"{np.max(np.abs(valid_difference))}"
            )


# ============================================================================
# SINGLE FACTOR VALIDATION
# ============================================================================

def validate_factor(
    factor_name: str,
    filename: str,
    reference: dict,
) -> dict:
    """
    Validate one aligned factor.
    """

    path = ALIGNED_DIR / filename

    print_header(
        f"VALIDATING {factor_name.upper()}"
    )

    check_file_exists(
        path,
        factor_name,
    )

    if not path.exists():
        return {}

    with rasterio.open(path) as src:

        # --------------------------------------------------------------
        # Spatial grid
        # --------------------------------------------------------------

        validate_grid(
            src=src,
            reference=reference,
            factor_name=factor_name,
        )

        # --------------------------------------------------------------
        # Data structure
        # --------------------------------------------------------------

        validate_data_structure(
            src=src,
            factor_name=factor_name,
        )

        # --------------------------------------------------------------
        # Read data
        # --------------------------------------------------------------

        data = src.read(1)

        # --------------------------------------------------------------
        # Value validation
        # --------------------------------------------------------------

        statistics = validate_values(
            data=data,
            factor_name=factor_name,
        )

    # ------------------------------------------------------------------
    # Factors that were already aligned should retain their exact values.
    # ------------------------------------------------------------------

    if factor_name in UNCHANGED_FACTORS:

        validate_unchanged_factor(
            factor_name=factor_name,
            aligned_data=data,
        )

    return statistics


# ============================================================================
# FINAL SUMMARY
# ============================================================================

def print_final_summary(
    results: dict,
) -> None:
    """Print a concise summary of validation statistics."""

    print_header(
        "ALIGNMENT VALIDATION — STATISTICAL SUMMARY"
    )

    print(
        f"{'Factor':<25}"
        f"{'Valid Cells':>15}"
        f"{'NoData':>15}"
        f"{'Min':>12}"
        f"{'Max':>12}"
        f"{'Mean':>12}"
    )

    print("-" * 91)

    for factor_name, stats in results.items():

        if not stats:
            continue

        print(
            f"{factor_name:<25}"
            f"{stats['valid_count']:>15,}"
            f"{stats['nodata_count']:>15,}"
            f"{stats['minimum']:>12.6f}"
            f"{stats['maximum']:>12.6f}"
            f"{stats['mean']:>12.6f}"
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run complete Phase 7 alignment validation."""

    print_header(
        "GEOAI FLOOD RISK DECISION AGENT"
    )

    print(
        "PHASE 7 — LESSON 7.7"
    )

    print(
        "DEDICATED SPATIAL ALIGNMENT VALIDATION"
    )

    print(
        "\nValidation directory:"
    )

    print(
        f"  {ALIGNED_DIR}"
    )

    # ------------------------------------------------------------------------
    # Load reference grid.
    # ------------------------------------------------------------------------

    reference = load_reference()

    print_reference_information(
        reference
    )

    # ------------------------------------------------------------------------
    # Validate all factors.
    # ------------------------------------------------------------------------

    results = {}

    for factor_name, filename in RASTERS.items():

        results[factor_name] = validate_factor(
            factor_name=factor_name,
            filename=filename,
            reference=reference,
        )

    # ------------------------------------------------------------------------
    # Statistical summary.
    # ------------------------------------------------------------------------

    print_final_summary(
        results
    )

    # ------------------------------------------------------------------------
    # Overall result.
    # ------------------------------------------------------------------------

    print_header(
        "OVERALL VALIDATION RESULT"
    )

    print(
        f"Total checks:  {TOTAL_CHECKS}"
    )

    print(
        f"Passed:        {PASSED_CHECKS}"
    )

    print(
        f"Failed:        {FAILED_CHECKS}"
    )

    if FAILED_CHECKS == 0:

        print(
            "\nSTATUS: PASS"
        )

        print(
            """
All dedicated alignment validation checks passed.

The aligned factors:
    - share the reference spatial grid,
    - use the expected data structure,
    - contain valid standardized values,
    - contain no invalid NaN/infinite values,
    - and preserve values for factors that did not require resampling.

NEXT:
    1. Review the statistical results.
    2. Perform visual verification in QGIS.
    3. Document Phase 7.
    4. Update README.md.
    5. Commit and push the reproducible artifacts.

Do not begin MCDA until QGIS verification is also complete.
"""
        )

    else:

        print(
            "\nSTATUS: FAIL"
        )

        print(
            """
One or more validation checks failed.

DO NOT continue to MCDA.

Review the failed checks above before making
any changes to the project.
"""
        )


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()