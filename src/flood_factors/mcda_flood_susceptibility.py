"""
MCDA Flood Susceptibility Modelling

This module combines five aligned and standardized flood-conditioning
factors using an AHP-derived weighted linear combination.

Factors:
    1. Elevation
    2. Slope
    3. Distance to Rivers
    4. Land Cover
    5. Population

Method:
    Analytic Hierarchy Process (AHP)
        +
    Weighted Linear Combination (WLC)

Output:
    data/analysis/mcda/flood_susceptibility.tif

The script:
    - uses project-relative paths;
    - calculates AHP-derived factor weights;
    - validates AHP consistency;
    - validates input raster compatibility;
    - correctly handles raster NoData values;
    - validates standardized factor ranges using valid cells only;
    - performs the MCDA weighted overlay;
    - preserves the reference raster's spatial metadata;
    - generates a continuous flood susceptibility surface;
    - reports output statistics;
    - stores methodological metadata in the output GeoTIFF.
"""

from pathlib import Path

import numpy as np
import rasterio


# ---------------------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------------------

# Project root:
# GeoAI-flood-risk-agent/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALIGNED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "flood_susceptibility.tif"
)


# ---------------------------------------------------------------------
# 2. FACTOR INPUTS
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# 3. AHP FACTOR ORDER
# ---------------------------------------------------------------------

FACTOR_ORDER = [
    "elevation",
    "slope",
    "distance_to_rivers",
    "landcover",
    "population",
]


# ---------------------------------------------------------------------
# 4. AHP PAIRWISE COMPARISON MATRIX
# ---------------------------------------------------------------------
#
# Factor order:
#     1. Elevation
#     2. Slope
#     3. Distance to Rivers
#     4. Land Cover
#     5. Population
#
# AHP scale:
#     1 = equal importance
#     3 = moderate importance
#     5 = strong importance
#     7 = very strong importance
#     9 = extreme importance
#
# Reciprocal values represent the opposite relationship.
#
# Matrix:
#
#                 E     S     R     L     P
# Elevation       1     1    1/3    2     3
# Slope           1     1    1/3    2     3
# Rivers          3     3     1     3     5
# Land Cover      1/2   1/2   1/3    1     3
# Population      1/3   1/3   1/5   1/3    1
#
# ---------------------------------------------------------------------

AHP_MATRIX = np.array(
    [
        [1, 1, 1 / 3, 2, 3],
        [1, 1, 1 / 3, 2, 3],
        [3, 3, 1, 3, 5],
        [1 / 2, 1 / 2, 1 / 3, 1, 3],
        [1 / 3, 1 / 3, 1 / 5, 1 / 3, 1],
    ],
    dtype=np.float64,
)


# ---------------------------------------------------------------------
# 5. AHP CONSISTENCY PARAMETERS
# ---------------------------------------------------------------------

# Random Index for a 5 x 5 AHP matrix.
RI = 1.12

# Common AHP acceptance threshold.
CR_THRESHOLD = 0.10


# ---------------------------------------------------------------------
# 6. RASTER VALIDATION PARAMETERS
# ---------------------------------------------------------------------

EXPECTED_MIN = 0.0
EXPECTED_MAX = 1.0

# Output NoData value.
OUTPUT_NODATA = -9999.0

# Floating-point tolerance.
RANGE_TOLERANCE = 1e-6


# ---------------------------------------------------------------------
# 7. CALCULATE AHP WEIGHTS
# ---------------------------------------------------------------------

def calculate_ahp_weights():
    """
    Calculate AHP factor weights and consistency statistics.

    The weighting process is:

        1. Calculate column sums.
        2. Normalize the comparison matrix.
        3. Calculate row averages.
        4. Calculate lambda_max.
        5. Calculate the Consistency Index (CI).
        6. Calculate the Consistency Ratio (CR).

    Returns:
        weights:
            Dictionary containing the AHP weight for each factor.

        consistency_ratio:
            AHP consistency ratio.

        consistency_index:
            AHP consistency index.

        lambda_max:
            Principal eigenvalue estimate.
    """

    matrix = AHP_MATRIX.copy()

    number_of_factors = matrix.shape[0]

    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            "AHP comparison matrix must be square."
        )

    if number_of_factors != len(FACTOR_ORDER):
        raise ValueError(
            "Number of factors does not match "
            "the AHP matrix."
        )

    # -------------------------------------------------------------
    # Step 1: Calculate column sums
    # -------------------------------------------------------------

    column_sums = matrix.sum(axis=0)

    # -------------------------------------------------------------
    # Step 2: Normalize comparison matrix
    # -------------------------------------------------------------

    normalized_matrix = (
        matrix / column_sums
    )

    # -------------------------------------------------------------
    # Step 3: Calculate priority vector
    # -------------------------------------------------------------

    weights_array = (
        normalized_matrix.mean(axis=1)
    )

    # Normalize again to guarantee a sum of 1.
    weights_array = (
        weights_array
        / weights_array.sum()
    )

    # -------------------------------------------------------------
    # Step 4: Calculate weighted-sum vector
    # -------------------------------------------------------------

    weighted_sum_vector = (
        matrix @ weights_array
    )

    # -------------------------------------------------------------
    # Step 5: Calculate consistency vector
    # -------------------------------------------------------------

    consistency_vector = (
        weighted_sum_vector
        / weights_array
    )

    # -------------------------------------------------------------
    # Step 6: Calculate lambda_max
    # -------------------------------------------------------------

    lambda_max = float(
        np.mean(consistency_vector)
    )

    # -------------------------------------------------------------
    # Step 7: Calculate Consistency Index
    # -------------------------------------------------------------

    consistency_index = (
        lambda_max - number_of_factors
    ) / (
        number_of_factors - 1
    )

    # -------------------------------------------------------------
    # Step 8: Calculate Consistency Ratio
    # -------------------------------------------------------------

    consistency_ratio = (
        consistency_index / RI
    )

    weights = {
        factor: float(weight)
        for factor, weight in zip(
            FACTOR_ORDER,
            weights_array
        )
    }

    # -------------------------------------------------------------
    # Display AHP results
    # -------------------------------------------------------------

    print("\nAHP WEIGHTING")
    print("-" * 60)

    print("\nPairwise comparison matrix:")

    for row in matrix:

        print(
            "  ".join(
                f"{value:8.4f}"
                for value in row
            )
        )

    print("\nDerived factor weights:")

    for factor, weight in weights.items():

        print(
            f"{factor:25s}: "
            f"{weight:.10f} "
            f"({weight * 100:.4f}%)"
        )

    weight_sum = sum(
        weights.values()
    )

    print(
        f"\nWeight sum                : "
        f"{weight_sum:.10f}"
    )

    print(
        f"Lambda max                : "
        f"{lambda_max:.10f}"
    )

    print(
        f"Consistency Index (CI)    : "
        f"{consistency_index:.10f}"
    )

    print(
        f"Random Index (RI)         : "
        f"{RI:.2f}"
    )

    print(
        f"Consistency Ratio (CR)    : "
        f"{consistency_ratio:.10f}"
    )

    if consistency_ratio < CR_THRESHOLD:

        print(
            "Consistency status        : PASS"
        )

    else:

        raise ValueError(
            "AHP consistency ratio exceeds "
            f"the acceptable threshold of "
            f"{CR_THRESHOLD}."
        )

    if not np.isclose(
        weight_sum,
        1.0,
        atol=1e-10
    ):

        raise ValueError(
            "AHP weights do not sum to 1."
        )

    return (
        weights,
        consistency_ratio,
        consistency_index,
        lambda_max,
    )


# ---------------------------------------------------------------------
# 8. VALIDATE WEIGHTS
# ---------------------------------------------------------------------

def validate_weights(weights):
    """
    Perform final validation of the calculated weights.
    """

    print("\nWEIGHT VALIDATION")
    print("-" * 60)

    for factor, weight in weights.items():

        if weight < 0:

            raise ValueError(
                f"Negative weight detected "
                f"for '{factor}'."
            )

        print(
            f"{factor:25s}: "
            f"{weight:.10f}"
        )

    weight_sum = sum(
        weights.values()
    )

    print(
        f"{'Weight sum':25s}: "
        f"{weight_sum:.10f}"
    )

    if not np.isclose(
        weight_sum,
        1.0,
        atol=1e-10
    ):

        raise ValueError(
            "MCDA weights must sum to 1."
        )

    print(
        "Status                    : PASS"
    )


# ---------------------------------------------------------------------
# 9. CHECK INPUT FILES
# ---------------------------------------------------------------------

def check_input_files():
    """
    Confirm that all required raster inputs exist.
    """

    print("\nINPUT FILE VALIDATION")
    print("-" * 60)

    missing_files = []

    for factor, path in FACTOR_FILES.items():

        if path.exists():

            print(
                f"{factor:25s}: FOUND"
            )

        else:

            print(
                f"{factor:25s}: MISSING"
            )

            missing_files.append(path)

    if missing_files:

        print("\nMissing input files:")

        for path in missing_files:

            print(
                f"  - {path}"
            )

        raise FileNotFoundError(
            "One or more required MCDA "
            "input rasters are missing."
        )

    print(
        "Status                    : PASS"
    )


# ---------------------------------------------------------------------
# 10. LOAD AND VALIDATE RASTERS
# ---------------------------------------------------------------------

def load_and_validate_rasters():
    """
    Load all aligned standardized factor rasters.

    Validates:
        - CRS
        - transform
        - width
        - height
        - finite values
        - raster NoData
        - standardized 0-1 range

    NoData cells are excluded from the
    standardized factor range validation.

    Returns:
        reference_profile
        arrays
        valid_mask
    """

    arrays = {}

    reference_profile = None
    reference_crs = None
    reference_transform = None
    reference_width = None
    reference_height = None

    # Store each raster's NoData value.
    nodata_values = {}

    print(
        "\nRASTER COMPATIBILITY VALIDATION"
    )
    print("-" * 60)

    for factor in FACTOR_ORDER:

        path = FACTOR_FILES[factor]

        with rasterio.open(path) as src:

            # -----------------------------------------------------
            # Read the raster as a regular NumPy array.
            # -----------------------------------------------------

            array = src.read(
                1
            ).astype(
                np.float32,
                copy=False
            )

            # -----------------------------------------------------
            # Establish the reference grid.
            # -----------------------------------------------------

            if reference_profile is None:

                reference_profile = (
                    src.profile.copy()
                )

                reference_crs = src.crs
                reference_transform = (
                    src.transform
                )
                reference_width = src.width
                reference_height = src.height

            # -----------------------------------------------------
            # Validate subsequent rasters.
            # -----------------------------------------------------

            else:

                if src.crs != reference_crs:

                    raise ValueError(
                        f"CRS mismatch detected "
                        f"for '{factor}'. "
                        f"Expected "
                        f"{reference_crs}, "
                        f"found {src.crs}."
                    )

                if (
                    src.transform
                    != reference_transform
                ):

                    raise ValueError(
                        f"Transform/grid mismatch "
                        f"detected for '{factor}'."
                    )

                if src.width != reference_width:

                    raise ValueError(
                        f"Width mismatch detected "
                        f"for '{factor}'."
                    )

                if src.height != reference_height:

                    raise ValueError(
                        f"Height mismatch detected "
                        f"for '{factor}'."
                    )

            arrays[factor] = array
            nodata_values[factor] = (
                src.nodata
            )

            print(
                f"{factor:25s}: "
                f"{src.width} x "
                f"{src.height}, "
                f"CRS={src.crs}"
            )

    print(
        "Status                    : PASS"
    )

    # -----------------------------------------------------------------
    # Create common valid-data mask.
    # -----------------------------------------------------------------

    valid_mask = np.ones(
        (
            reference_height,
            reference_width
        ),
        dtype=bool,
    )

    print(
        "\nFACTOR RANGE VALIDATION"
    )
    print("-" * 60)

    for factor in FACTOR_ORDER:

        array = arrays[factor]

        # -------------------------------------------------------------
        # Start with finite values.
        # -------------------------------------------------------------

        factor_valid_mask = np.isfinite(
            array
        )

        # -------------------------------------------------------------
        # Remove raster NoData values.
        # -------------------------------------------------------------

        nodata = nodata_values[factor]

        if nodata is not None:

            factor_valid_mask &= (
                array != nodata
            )

        # -------------------------------------------------------------
        # Update common valid-data mask.
        # -------------------------------------------------------------

        valid_mask &= (
            factor_valid_mask
        )

        if not np.any(
            factor_valid_mask
        ):

            raise ValueError(
                f"No valid cells found "
                f"in '{factor}'."
            )

        # -------------------------------------------------------------
        # IMPORTANT:
        #
        # Calculate statistics using VALID
        # cells only.
        # -------------------------------------------------------------

        valid_values = array[
            factor_valid_mask
        ]

        minimum = float(
            np.min(valid_values)
        )

        maximum = float(
            np.max(valid_values)
        )

        print(
            f"{factor:25s}: "
            f"min={minimum:.6f}, "
            f"max={maximum:.6f}"
        )

        # -------------------------------------------------------------
        # Validate standardized 0-1 range.
        #
        # NoData values such as -9999 are NOT
        # included in this test.
        # -------------------------------------------------------------

        if (
            minimum
            < EXPECTED_MIN
            - RANGE_TOLERANCE
            or
            maximum
            > EXPECTED_MAX
            + RANGE_TOLERANCE
        ):

            raise ValueError(
                f"Standardized factor "
                f"'{factor}' contains "
                f"VALID values outside "
                f"the expected 0-1 range."
            )

    # -----------------------------------------------------------------
    # Count common valid cells.
    # -----------------------------------------------------------------

    valid_cell_count = int(
        np.count_nonzero(
            valid_mask
        )
    )

    print(
        f"\nCommon valid cells       : "
        f"{valid_cell_count}"
    )

    if valid_cell_count == 0:

        raise ValueError(
            "No common valid cells exist "
            "across the five factor rasters."
        )

    print(
        "Status                    : PASS"
    )

    return (
        reference_profile,
        arrays,
        valid_mask,
    )


# ---------------------------------------------------------------------
# 11. CALCULATE MCDA SUSCEPTIBILITY
# ---------------------------------------------------------------------

def calculate_susceptibility(
    arrays,
    valid_mask,
    weights,
):
    """
    Calculate the MCDA weighted linear combination.

    Formula:

        FS =
            wE * E
          + wS * S
          + wR * R
          + wL * L
          + wP * P

    Returns:
        susceptibility array
    """

    print(
        "\nMCDA WEIGHTED OVERLAY"
    )
    print("-" * 60)

    susceptibility = np.full(
        valid_mask.shape,
        OUTPUT_NODATA,
        dtype=np.float32,
    )

    weighted_sum = np.zeros(
        valid_mask.shape,
        dtype=np.float64,
    )

    for factor in FACTOR_ORDER:

        weight = weights[factor]

        weighted_sum[
            valid_mask
        ] += (
            arrays[factor][
                valid_mask
            ].astype(
                np.float64
            )
            * weight
        )

        print(
            f"{factor:25s}: "
            f"weight={weight:.10f}"
        )

    susceptibility[
        valid_mask
    ] = weighted_sum[
        valid_mask
    ].astype(
        np.float32
    )

    print(
        "Weighted overlay          : "
        "COMPLETE"
    )

    return susceptibility


# ---------------------------------------------------------------------
# 12. VALIDATE OUTPUT VALUES
# ---------------------------------------------------------------------

def validate_output_values(
    susceptibility,
    valid_mask,
):
    """
    Validate the generated susceptibility surface.

    Returns:
        Dictionary of output statistics.
    """

    print(
        "\nOUTPUT VALIDATION"
    )
    print("-" * 60)

    valid_output = susceptibility[
        valid_mask
    ]

    if valid_output.size == 0:

        raise ValueError(
            "The susceptibility raster "
            "contains no valid cells."
        )

    if not np.all(
        np.isfinite(valid_output)
    ):

        raise ValueError(
            "Output contains "
            "non-finite values."
        )

    minimum = float(
        np.min(valid_output)
    )

    maximum = float(
        np.max(valid_output)
    )

    mean = float(
        np.mean(valid_output)
    )

    median = float(
        np.median(valid_output)
    )

    print(
        f"Valid cells               : "
        f"{valid_output.size}"
    )

    print(
        f"Minimum susceptibility    : "
        f"{minimum:.6f}"
    )

    print(
        f"Maximum susceptibility    : "
        f"{maximum:.6f}"
    )

    print(
        f"Mean susceptibility       : "
        f"{mean:.6f}"
    )

    print(
        f"Median susceptibility     : "
        f"{median:.6f}"
    )

    # -------------------------------------------------------------
    # Because all input factors are 0-1 and
    # weights sum to 1, the weighted linear
    # combination should also be 0-1.
    # -------------------------------------------------------------

    if minimum < (
        -RANGE_TOLERANCE
    ):

        raise ValueError(
            "Output contains "
            "values below 0."
        )

    if maximum > (
        1.0
        + RANGE_TOLERANCE
    ):

        raise ValueError(
            "Output contains "
            "values above 1."
        )

    print(
        "Finite-value check        : PASS"
    )

    print(
        "Expected range check      : PASS"
    )

    return {
        "valid_cells": int(
            valid_output.size
        ),
        "minimum": minimum,
        "maximum": maximum,
        "mean": mean,
        "median": median,
    }


# ---------------------------------------------------------------------
# 13. WRITE OUTPUT RASTER
# ---------------------------------------------------------------------

def write_output(
    susceptibility,
    reference_profile,
    weights,
    consistency_ratio,
):
    """
    Write the final flood susceptibility
    raster to GeoTIFF.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_profile = (
        reference_profile.copy()
    )

    output_profile.update(
        dtype="float32",
        count=1,
        nodata=OUTPUT_NODATA,
        compress="lzw",
    )

    with rasterio.open(
        OUTPUT_FILE,
        "w",
        **output_profile,
    ) as dst:

        dst.write(
            susceptibility,
            1,
        )

        # ---------------------------------------------------------
        # Store methodological metadata.
        # ---------------------------------------------------------

        dst.update_tags(
            model=(
                "MCDA Flood Susceptibility"
            ),
            method=(
                "Weighted Linear Combination"
            ),
            weighting_method="AHP",
            consistency_ratio=(
                f"{consistency_ratio:.10f}"
            ),
            factors=(
                "Elevation;Slope;"
                "Distance to Rivers;"
                "Land Cover;Population"
            ),
            elevation_weight=(
                f"{weights['elevation']:.10f}"
            ),
            slope_weight=(
                f"{weights['slope']:.10f}"
            ),
            distance_to_rivers_weight=(
                f"{weights['distance_to_rivers']:.10f}"
            ),
            landcover_weight=(
                f"{weights['landcover']:.10f}"
            ),
            population_weight=(
                f"{weights['population']:.10f}"
            ),
        )

    print(
        "\nOUTPUT RASTER"
    )
    print("-" * 60)

    print(
        f"Saved to                  : "
        f"{OUTPUT_FILE}"
    )

    print(
        "Status                    : SUCCESS"
    )


# ---------------------------------------------------------------------
# 14. MAIN WORKFLOW
# ---------------------------------------------------------------------

def main():

    print("=" * 60)

    print(
        "MCDA FLOOD SUSCEPTIBILITY MODELLING"
    )

    print("=" * 60)

    print(
        "\nProject root:"
    )

    print(
        PROJECT_ROOT
    )

    print(
        "\nAligned factor directory:"
    )

    print(
        ALIGNED_DIR
    )

    print(
        "\nOutput directory:"
    )

    print(
        OUTPUT_DIR
    )

    # -------------------------------------------------------------
    # Step 1: Calculate AHP weights.
    # -------------------------------------------------------------

    (
        weights,
        consistency_ratio,
        consistency_index,
        lambda_max,
    ) = calculate_ahp_weights()

    # -------------------------------------------------------------
    # Step 2: Validate weights.
    # -------------------------------------------------------------

    validate_weights(
        weights
    )

    # -------------------------------------------------------------
    # Step 3: Check required input files.
    # -------------------------------------------------------------

    check_input_files()

    # -------------------------------------------------------------
    # Step 4: Load and validate aligned rasters.
    # -------------------------------------------------------------

    (
        reference_profile,
        arrays,
        valid_mask,
    ) = load_and_validate_rasters()

    # -------------------------------------------------------------
    # Step 5: Calculate weighted overlay.
    # -------------------------------------------------------------

    susceptibility = (
        calculate_susceptibility(
            arrays,
            valid_mask,
            weights,
        )
    )

    # -------------------------------------------------------------
    # Step 6: Validate output.
    # -------------------------------------------------------------

    statistics = (
        validate_output_values(
            susceptibility,
            valid_mask,
        )
    )

    # -------------------------------------------------------------
    # Step 7: Write final raster.
    # -------------------------------------------------------------

    write_output(
        susceptibility,
        reference_profile,
        weights,
        consistency_ratio,
    )

    # -------------------------------------------------------------
    # Step 8: Final summary.
    # -------------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "MCDA PROCESS COMPLETED "
        "SUCCESSFULLY"
    )

    print(
        "=" * 60
    )

    print(
        "\nFINAL SUMMARY"
    )

    print(
        "-" * 60
    )

    print(
        f"Output file     : "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Valid cells     : "
        f"{statistics['valid_cells']}"
    )

    print(
        f"Minimum         : "
        f"{statistics['minimum']:.6f}"
    )

    print(
        f"Maximum         : "
        f"{statistics['maximum']:.6f}"
    )

    print(
        f"Mean            : "
        f"{statistics['mean']:.6f}"
    )

    print(
        f"Median          : "
        f"{statistics['median']:.6f}"
    )

    print(
        f"AHP CR          : "
        f"{consistency_ratio:.10f}"
    )

    print(
        f"AHP CI          : "
        f"{consistency_index:.10f}"
    )

    print(
        f"Lambda max      : "
        f"{lambda_max:.10f}"
    )

    print(
        "\nFinal AHP weights:"
    )

    for factor in FACTOR_ORDER:

        print(
            f"  {factor:23s}: "
            f"{weights[factor]:.10f}"
        )


# ---------------------------------------------------------------------
# 15. SCRIPT ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()