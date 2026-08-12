"""
GeoAI Flood Risk Agent
----------------------

Phase 6: Flood Conditioning Factor Standardization

This module standardizes the flood conditioning factors used by the
GeoAI Flood Risk Agent.

Continuous factors:
    - Elevation
    - Slope
    - Distance to Rivers
    - Population

Categorical factor:
    - Land Cover

Continuous factors are standardized to a 0–1 scale using Min-Max
normalization.

Factors with an inverse flood-susceptibility relationship use inverse
Min-Max normalization.

Land Cover is categorical and is therefore reclassified using an
explicit class-to-score lookup table.

Important:
    - Original input rasters are never modified.
    - No reprojection or resampling is performed.
    - NoData values are preserved.
    - Invalid numerical values are excluded from calculations.
    - Constant-value rasters raise an error instead of producing
      misleading results.
"""


from pathlib import Path

import numpy as np
import rasterio


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "analysis" / "flood_factors"

OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis" / "standardized"


# ---------------------------------------------------------------------
# INPUT RASTERS
# ---------------------------------------------------------------------

INPUT_RASTERS = {
    "elevation": INPUT_DIR / "elevation.tif",
    "slope": INPUT_DIR / "slope.tif",
    "distance_to_rivers": INPUT_DIR / "distance_to_rivers.tif",
    "population": INPUT_DIR / "population.tif",
    "landcover": INPUT_DIR / "landcover.tif",
}


# ---------------------------------------------------------------------
# OUTPUT RASTERS
# ---------------------------------------------------------------------

OUTPUT_RASTERS = {
    "elevation": OUTPUT_DIR / "elevation_score.tif",
    "slope": OUTPUT_DIR / "slope_score.tif",
    "distance_to_rivers": OUTPUT_DIR / "distance_to_rivers_score.tif",
    "population": OUTPUT_DIR / "population_score.tif",
    "landcover": OUTPUT_DIR / "landcover_score.tif",
}


# ---------------------------------------------------------------------
# LAND COVER RECLASSIFICATION
# ---------------------------------------------------------------------
#
# WorldCover class codes are categorical identifiers.
# They are NOT treated as numerical measurements.
#
# Scores represent relative contribution to flood susceptibility.
#
# 10 = Tree Cover
# 20 = Shrubland
# 30 = Grassland
# 40 = Cropland
# 50 = Built-up
# 60 = Bare / Sparse Vegetation
# 80 = Permanent Water
# 90 = Herbaceous Wetland
#
# These are modelling scores, not flood probabilities.
# ---------------------------------------------------------------------

LANDCOVER_SCORES = {
    10: 0.20,
    20: 0.30,
    30: 0.45,
    40: 0.60,
    50: 1.00,
    60: 0.75,
    80: 0.00,
    90: 0.15,
}


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def ensure_output_directory():
    """
    Create the standardized output directory if it does not exist.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def validate_input_raster(path: Path):
    """
    Confirm that an input raster exists.

    Parameters
    ----------
    path : Path
        Raster path.

    Raises
    ------
    FileNotFoundError
        If the raster does not exist.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Input raster not found:\n{path}"
        )


def get_valid_data(array: np.ma.MaskedArray) -> np.ndarray:
    """
    Extract valid finite raster values.

    Parameters
    ----------
    array : numpy.ma.MaskedArray
        Masked raster array.

    Returns
    -------
    numpy.ndarray
        One-dimensional array containing valid finite values.
    """

    values = array.compressed()

    if values.size == 0:
        raise ValueError(
            "Raster contains no valid cells."
        )

    values = values[np.isfinite(values)]

    if values.size == 0:
        raise ValueError(
            "Raster contains no finite valid values."
        )

    return values


def write_standardized_raster(
    output_path: Path,
    source_profile: dict,
    standardized_array: np.ndarray,
    nodata_value: float = -9999.0,
):
    """
    Write a standardized raster to disk.

    Parameters
    ----------
    output_path : Path
        Destination raster.

    source_profile : dict
        Rasterio profile from the source raster.

    standardized_array : numpy.ndarray
        Standardized raster values.

    nodata_value : float
        NoData value used in the output raster.
    """

    profile = source_profile.copy()

    profile.update(
        dtype="float32",
        count=1,
        nodata=nodata_value,
        compress="lzw",
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with rasterio.open(
        output_path,
        "w",
        **profile,
    ) as dst:

        dst.write(
            standardized_array.astype(np.float32),
            1,
        )


# ---------------------------------------------------------------------
# CONTINUOUS NORMALIZATION
# ---------------------------------------------------------------------

def normalize_continuous_raster(
    input_path: Path,
    output_path: Path,
    inverse: bool = False,
):
    """
    Normalize a continuous raster to the range 0–1.

    Parameters
    ----------
    input_path : Path
        Source raster.

    output_path : Path
        Destination standardized raster.

    inverse : bool, default=False
        If False:
            Positive Min-Max normalization.

        If True:
            Inverse Min-Max normalization.

    Returns
    -------
    dict
        Summary statistics for the standardized raster.
    """

    validate_input_raster(input_path)

    print()
    print("=" * 70)
    print(f"Processing: {input_path.name}")
    print("=" * 70)

    with rasterio.open(input_path) as src:

        data = src.read(
            1,
            masked=True,
        )

        valid_values = get_valid_data(data)

        minimum = float(valid_values.min())
        maximum = float(valid_values.max())

        print(
            f"Valid cells: {valid_values.size}"
        )

        print(
            f"Minimum: {minimum}"
        )

        print(
            f"Maximum: {maximum}"
        )

        if np.isclose(
            minimum,
            maximum,
        ):
            raise ValueError(
                f"Cannot normalize {input_path.name}: "
                f"minimum and maximum values are identical."
            )

        denominator = maximum - minimum

        result = np.full(
            data.shape,
            -9999.0,
            dtype=np.float32,
        )

        mask = np.ma.getmaskarray(data)

        values = data.filled(
            np.nan
        ).astype(
            np.float64
        )

        valid_mask = (
            ~mask
            & np.isfinite(values)
        )

        if inverse:

            normalized = (
                maximum - values
            ) / denominator

        else:

            normalized = (
                values - minimum
            ) / denominator

        normalized = np.clip(
            normalized,
            0.0,
            1.0,
        )

        result[valid_mask] = normalized[
            valid_mask
        ].astype(np.float32)

        write_standardized_raster(
            output_path=output_path,
            source_profile=src.profile,
            standardized_array=result,
        )

    valid_output = result[
        result != -9999.0
    ]

    print(
        f"Standardized minimum: "
        f"{valid_output.min()}"
    )

    print(
        f"Standardized maximum: "
        f"{valid_output.max()}"
    )

    print(
        f"Output: {output_path}"
    )

    return {
        "input": str(input_path),
        "output": str(output_path),
        "valid_cells": int(
            valid_output.size
        ),
        "source_min": minimum,
        "source_max": maximum,
        "standardized_min": float(
            valid_output.min()
        ),
        "standardized_max": float(
            valid_output.max()
        ),
    }


# ---------------------------------------------------------------------
# LAND COVER RECLASSIFICATION
# ---------------------------------------------------------------------

def reclassify_landcover(
    input_path: Path,
    output_path: Path,
):
    """
    Reclassify categorical WorldCover classes into 0–1
    flood-susceptibility contribution scores.

    Parameters
    ----------
    input_path : Path
        Source Land Cover raster.

    output_path : Path
        Destination standardized Land Cover raster.

    Returns
    -------
    dict
        Summary information about the reclassification.
    """

    validate_input_raster(input_path)

    print()
    print("=" * 70)
    print(f"Processing: {input_path.name}")
    print("=" * 70)

    with rasterio.open(input_path) as src:

        data = src.read(
            1,
            masked=True,
        )

        valid_values = get_valid_data(data)

        unique_classes = np.unique(
            valid_values
        )

        print(
            "Detected Land Cover classes:"
        )

        print(
            unique_classes
        )

        detected_classes = set(
            int(value)
            for value in unique_classes
        )

        expected_classes = set(
            LANDCOVER_SCORES.keys()
        )

        unexpected_classes = (
            detected_classes
            - expected_classes
        )

        if unexpected_classes:

            raise ValueError(
                "Unexpected Land Cover class(es) detected: "
                f"{sorted(unexpected_classes)}\n"
                "Update LANDCOVER_SCORES only after "
                "the class meaning has been verified."
            )

        # -------------------------------------------------------------
        # Create the output array.
        #
        # -9999 is used only in the OUTPUT float32 raster.
        # It is NOT inserted into the uint8 source raster.
        # -------------------------------------------------------------

        result = np.full(
            data.shape,
            -9999.0,
            dtype=np.float32,
        )

        # -------------------------------------------------------------
        # Identify valid cells directly from the mask.
        # -------------------------------------------------------------

        valid_mask = (
            ~np.ma.getmaskarray(data)
        )

        # -------------------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT use:
        #
        # data.filled(-99999)
        #
        # because the source raster is uint8.
        #
        # Also do NOT convert to int16 and then fill with -99999,
        # because -99999 is outside the int16 range.
        #
        # Instead, access the underlying raster values directly.
        # The valid_mask ensures that masked cells are never assigned
        # a Land Cover score.
        # -------------------------------------------------------------

        raw_values = np.asarray(
            data.data,
            dtype=np.int16,
        )

        # -------------------------------------------------------------
        # Reclassify every expected Land Cover class.
        # -------------------------------------------------------------

        for class_code, score in (
            LANDCOVER_SCORES.items()
        ):

            class_mask = (
                valid_mask
                & (
                    raw_values
                    == class_code
                )
            )

            result[class_mask] = score

            count = int(
                np.count_nonzero(
                    class_mask
                )
            )

            if count > 0:

                print(
                    f"Class {class_code}: "
                    f"{count:,} cells → "
                    f"score {score}"
                )

        # -------------------------------------------------------------
        # Check that every valid source cell received a score.
        # -------------------------------------------------------------

        unresolved_mask = (
            valid_mask
            & (
                result
                == -9999.0
            )
        )

        unresolved_count = int(
            np.count_nonzero(
                unresolved_mask
            )
        )

        if unresolved_count > 0:

            raise ValueError(
                f"{unresolved_count:,} valid cells "
                "could not be assigned a Land Cover score."
            )

        # -------------------------------------------------------------
        # Write the standardized Land Cover raster.
        # -------------------------------------------------------------

        write_standardized_raster(
            output_path=output_path,
            source_profile=src.profile,
            standardized_array=result,
        )

    # -------------------------------------------------------------
    # Output statistics
    # -------------------------------------------------------------

    valid_output = result[
        result != -9999.0
    ]

    print(
        f"Standardized minimum: "
        f"{valid_output.min()}"
    )

    print(
        f"Standardized maximum: "
        f"{valid_output.max()}"
    )

    print(
        f"Output: {output_path}"
    )

    return {
        "input": str(input_path),
        "output": str(output_path),
        "valid_cells": int(
            valid_output.size
        ),
        "standardized_min": float(
            valid_output.min()
        ),
        "standardized_max": float(
            valid_output.max()
        ),
        "classes": sorted(
            detected_classes
        ),
    }


# ---------------------------------------------------------------------
# MAIN PROCESSING WORKFLOW
# ---------------------------------------------------------------------

def main():
    """
    Run the complete Phase 6 standardization workflow.
    """

    print()
    print("=" * 70)
    print(
        "GEOAI FLOOD RISK AGENT"
    )
    print(
        "PHASE 6 — FACTOR STANDARDIZATION"
    )
    print("=" * 70)

    print()

    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Input directory: {INPUT_DIR}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    ensure_output_directory()

    # ---------------------------------------------------------------
    # ELEVATION
    # Lower elevation → higher susceptibility
    # ---------------------------------------------------------------

    normalize_continuous_raster(
        input_path=INPUT_RASTERS[
            "elevation"
        ],
        output_path=OUTPUT_RASTERS[
            "elevation"
        ],
        inverse=True,
    )

    # ---------------------------------------------------------------
    # SLOPE
    # Lower slope → higher susceptibility
    # ---------------------------------------------------------------

    normalize_continuous_raster(
        input_path=INPUT_RASTERS[
            "slope"
        ],
        output_path=OUTPUT_RASTERS[
            "slope"
        ],
        inverse=True,
    )

    # ---------------------------------------------------------------
    # DISTANCE TO RIVERS
    # Shorter distance → higher susceptibility
    # ---------------------------------------------------------------

    normalize_continuous_raster(
        input_path=INPUT_RASTERS[
            "distance_to_rivers"
        ],
        output_path=OUTPUT_RASTERS[
            "distance_to_rivers"
        ],
        inverse=True,
    )

    # ---------------------------------------------------------------
    # POPULATION
    # Higher population → higher exposure
    # ---------------------------------------------------------------

    normalize_continuous_raster(
        input_path=INPUT_RASTERS[
            "population"
        ],
        output_path=OUTPUT_RASTERS[
            "population"
        ],
        inverse=False,
    )

    # ---------------------------------------------------------------
    # LAND COVER
    # Categorical reclassification
    # ---------------------------------------------------------------

    reclassify_landcover(
        input_path=INPUT_RASTERS[
            "landcover"
        ],
        output_path=OUTPUT_RASTERS[
            "landcover"
        ],
    )

    # ---------------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "PHASE 6 STANDARDIZATION COMPLETED"
    )
    print("=" * 70)

    print()
    print(
        "Standardized rasters generated:"
    )

    for name, path in (
        OUTPUT_RASTERS.items()
    ):

        print(
            f"  {name}:"
        )

        print(
            f"    {path}"
        )

    print()
    print("Important:")

    print(
        "- Original flood-factor rasters "
        "were not modified."
    )

    print(
        "- Continuous factors were "
        "standardized to 0–1."
    )

    print(
        "- Inverse relationships were "
        "applied where required."
    )

    print(
        "- Population used positive "
        "normalization."
    )

    print(
        "- Land Cover used categorical "
        "reclassification."
    )

    print(
        "- No reprojection or resampling "
        "was performed."
    )

    print(
        "- Spatial alignment will be "
        "handled separately before MCDA."
    )


# ---------------------------------------------------------------------
# SCRIPT ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()