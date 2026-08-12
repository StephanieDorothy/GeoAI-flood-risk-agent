"""
GeoAI Flood Risk Agent
Phase 6 — Standardized Factor Validation

Purpose
-------
Validates standardized flood-conditioning factors before MCDA.

Validation includes:
1. CRS consistency
2. Raster dimensions
3. Raster transform
4. Raster resolution
5. Valid cell counts
6. Standardized 0–1 range
7. Expected relationship between source and standardized factor
8. Land Cover categorical reclassification

Important
---------
This script validates standardized rasters only.

It does NOT:
- modify source rasters
- modify standardized rasters
- reproject rasters
- resample rasters
- perform MCDA
"""

from pathlib import Path

import numpy as np
import rasterio


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FLOOD_FACTORS_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "flood_factors"
)

STANDARDIZED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "standardized"
)


# ---------------------------------------------------------------------
# FACTOR DEFINITIONS
# ---------------------------------------------------------------------

CONTINUOUS_FACTORS = {
    "elevation": {
        "source": "elevation.tif",
        "score": "elevation_score.tif",
        "relationship": "negative",
    },
    "slope": {
        "source": "slope.tif",
        "score": "slope_score.tif",
        "relationship": "negative",
    },
    "distance_to_rivers": {
        "source": "distance_to_rivers.tif",
        "score": "distance_to_rivers_score.tif",
        "relationship": "negative",
    },
    "population": {
        "source": "population.tif",
        "score": "population_score.tif",
        "relationship": "positive",
    },
}


# ---------------------------------------------------------------------
# LAND COVER METHODOLOGY
# ---------------------------------------------------------------------

LANDCOVER_MAPPING = {
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
# GENERAL HELPERS
# ---------------------------------------------------------------------

def print_header(title):
    """Print a formatted section header."""

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def get_raster_paths(source_name, score_name):
    """Return source and standardized raster paths."""

    source_path = FLOOD_FACTORS_DIR / source_name
    score_path = STANDARDIZED_DIR / score_name

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source raster not found:\n{source_path}"
        )

    if not score_path.exists():
        raise FileNotFoundError(
            f"Standardized raster not found:\n{score_path}"
        )

    return source_path, score_path


def validate_spatial_metadata(source, score):
    """
    Validate CRS, dimensions, transform and resolution.
    """

    print("\nSpatial metadata:")

    print(f"  Source CRS: {source.crs}")
    print(f"  Score CRS:  {score.crs}")

    print(
        f"  Source size: "
        f"{source.width} x {source.height}"
    )

    print(
        f"  Score size:  "
        f"{score.width} x {score.height}"
    )

    print(
        f"  Source resolution: "
        f"{source.res}"
    )

    print(
        f"  Score resolution:  "
        f"{score.res}"
    )

    crs_match = source.crs == score.crs
    dimensions_match = (
        source.width == score.width
        and source.height == score.height
    )

    transform_match = np.allclose(
        source.transform,
        score.transform
    )

    resolution_match = np.allclose(
        source.res,
        score.res
    )

    print(
        f"  CRS match: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"  Dimensions match: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )

    print(
        f"  Transform match: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )

    print(
        f"  Resolution match: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    if not crs_match:
        raise ValueError(
            "CRS mismatch between source and standardized raster."
        )

    if not dimensions_match:
        raise ValueError(
            "Raster dimensions do not match."
        )

    if not transform_match:
        raise ValueError(
            "Raster transforms do not match."
        )

    if not resolution_match:
        raise ValueError(
            "Raster resolutions do not match."
        )


def get_valid_data(dataset):
    """
    Read raster as a masked array and return finite valid values.
    """

    data = dataset.read(1, masked=True)

    values = data.compressed()

    values = values[
        np.isfinite(values)
    ]

    return values


# ---------------------------------------------------------------------
# CONTINUOUS FACTOR VALIDATION
# ---------------------------------------------------------------------

def validate_continuous_factor(
    factor_name,
    source_filename,
    score_filename,
    relationship,
):
    """
    Validate a continuous standardized factor.
    """

    print_header(
        f"VALIDATING: {factor_name.upper()}"
    )

    source_path, score_path = get_raster_paths(
        source_filename,
        score_filename,
    )

    with rasterio.open(source_path) as source, \
            rasterio.open(score_path) as score:

        # -------------------------------------------------------------
        # SPATIAL METADATA
        # -------------------------------------------------------------

        validate_spatial_metadata(
            source,
            score,
        )

        # -------------------------------------------------------------
        # READ DATA
        # -------------------------------------------------------------

        source_data = source.read(
            1,
            masked=True,
        )

        score_data = score.read(
            1,
            masked=True,
        )

        source_values = (
            source_data.compressed()
        )

        score_values = (
            score_data.compressed()
        )

        source_values = source_values[
            np.isfinite(source_values)
        ]

        score_values = score_values[
            np.isfinite(score_values)
        ]

        # -------------------------------------------------------------
        # STATISTICS
        # -------------------------------------------------------------

        print("\nSource statistics:")

        print(
            f"  Valid cells: "
            f"{source_values.size}"
        )

        print(
            f"  Minimum: "
            f"{source_values.min()}"
        )

        print(
            f"  Maximum: "
            f"{source_values.max()}"
        )

        print("\nStandardized statistics:")

        print(
            f"  Valid cells: "
            f"{score_values.size}"
        )

        print(
            f"  Minimum: "
            f"{score_values.min()}"
        )

        print(
            f"  Maximum: "
            f"{score_values.max()}"
        )

        # -------------------------------------------------------------
        # VALID CELL COUNT
        # -------------------------------------------------------------

        valid_count_pass = (
            source_values.size
            == score_values.size
        )

        print(
            "Valid cell count: "
            f"{'PASS' if valid_count_pass else 'FAIL'}"
        )

        if not valid_count_pass:
            raise ValueError(
                f"{factor_name}: "
                "source and standardized valid "
                "cell counts do not match."
            )

        # -------------------------------------------------------------
        # 0–1 RANGE
        # -------------------------------------------------------------

        range_pass = (
            score_values.min() >= 0.0
            and score_values.max() <= 1.0
        )

        print(
            "0–1 range check: "
            f"{'PASS' if range_pass else 'FAIL'}"
        )

        if not range_pass:
            raise ValueError(
                f"{factor_name}: "
                "standardized values fall outside "
                "the 0–1 range."
            )

        # -------------------------------------------------------------
        # CORRELATION
        # -------------------------------------------------------------

        # For correlation we need corresponding cells.
        source_mask = (
            ~np.ma.getmaskarray(source_data)
        )

        score_mask = (
            ~np.ma.getmaskarray(score_data)
        )

        valid_mask = (
            source_mask
            & score_mask
            & np.isfinite(
                np.asarray(source_data)
            )
            & np.isfinite(
                np.asarray(score_data)
            )
        )

        source_corresponding = (
            np.asarray(source_data)[valid_mask]
        )

        score_corresponding = (
            np.asarray(score_data)[valid_mask]
        )

        if (
            source_corresponding.size > 1
            and np.std(source_corresponding) > 0
            and np.std(score_corresponding) > 0
        ):

            correlation = np.corrcoef(
                source_corresponding,
                score_corresponding,
            )[0, 1]

            print(
                f"\nSource-score correlation: "
                f"{correlation:.6f}"
            )

            if relationship == "negative":

                relationship_pass = (
                    correlation < 0
                )

                print(
                    "Expected negative correlation: "
                    f"{'PASS' if relationship_pass else 'FAIL'}"
                )

            else:

                relationship_pass = (
                    correlation > 0
                )

                print(
                    "Expected positive correlation: "
                    f"{'PASS' if relationship_pass else 'FAIL'}"
                )

            if not relationship_pass:
                raise ValueError(
                    f"{factor_name}: "
                    "standardization relationship "
                    "does not match methodology."
                )

        else:

            print(
                "\nCorrelation check: SKIPPED "
                "(insufficient variation)"
            )

    print(
        f"\n{factor_name.upper()} VALIDATION: PASS"
    )


# ---------------------------------------------------------------------
# LAND COVER VALIDATION
# ---------------------------------------------------------------------

def validate_landcover():
    """
    Validate categorical Land Cover reclassification.

    Each source class must map to the score defined in
    LANDCOVER_MAPPING.
    """

    print_header(
        "VALIDATING: LAND COVER"
    )

    source_path, score_path = get_raster_paths(
        "landcover.tif",
        "landcover_score.tif",
    )

    with rasterio.open(source_path) as source, \
            rasterio.open(score_path) as score:

        # -------------------------------------------------------------
        # SPATIAL METADATA
        # -------------------------------------------------------------

        validate_spatial_metadata(
            source,
            score,
        )

        # -------------------------------------------------------------
        # READ DATA
        # -------------------------------------------------------------

        source_data = source.read(
            1,
            masked=True,
        )

        score_data = score.read(
            1,
            masked=True,
        )

        source_array = np.asarray(
            source_data
        )

        score_array = np.asarray(
            score_data
        )

        source_mask = (
            ~np.ma.getmaskarray(source_data)
        )

        score_mask = (
            ~np.ma.getmaskarray(score_data)
        )

        valid_mask = (
            source_mask
            & score_mask
        )

        valid_source = (
            source_array[valid_mask]
        )

        valid_scores = (
            score_array[valid_mask]
        )

        # -------------------------------------------------------------
        # SOURCE CLASSES
        # -------------------------------------------------------------

        source_classes = np.unique(
            valid_source
        )

        print(
            "\nDetected source classes:"
        )

        print(source_classes)

        expected_classes = np.array(
            list(LANDCOVER_MAPPING.keys()),
            dtype=float,
        )

        class_check = (
            np.array_equal(
                np.sort(source_classes),
                np.sort(expected_classes),
            )
        )

        print(
            "\nLand Cover class check: "
            f"{'PASS' if class_check else 'FAIL'}"
        )

        if not class_check:

            unexpected_classes = [
                value
                for value in source_classes
                if int(value)
                not in LANDCOVER_MAPPING
            ]

            missing_classes = [
                value
                for value in expected_classes
                if value not in source_classes
            ]

            if unexpected_classes:
                print(
                    "Unexpected source classes:",
                    unexpected_classes,
                )

            if missing_classes:
                print(
                    "Missing expected classes:",
                    missing_classes,
                )

            raise ValueError(
                "Land Cover class validation failed."
            )

        # -------------------------------------------------------------
        # VALID CELL COUNT
        # -------------------------------------------------------------

        source_valid_count = (
            source_data.compressed().size
        )

        score_valid_count = (
            score_data.compressed().size
        )

        valid_count_pass = (
            source_valid_count
            == score_valid_count
        )

        print(
            "\nSource valid cells:",
            source_valid_count,
        )

        print(
            "Standardized valid cells:",
            score_valid_count,
        )

        print(
            "Valid cell count: "
            f"{'PASS' if valid_count_pass else 'FAIL'}"
        )

        if not valid_count_pass:
            raise ValueError(
                "Land Cover source and score "
                "valid cell counts do not match."
            )

        # -------------------------------------------------------------
        # EXPECTED SCORE VALUES
        # -------------------------------------------------------------

        expected_scores = np.array(
            list(LANDCOVER_MAPPING.values()),
            dtype=np.float32,
        )

        print(
            "\nExpected standardized scores:"
        )

        print(
            expected_scores
        )

        print(
            "\nDetected standardized scores:"
        )

        detected_scores = np.unique(
            valid_scores
        )

        print(
            detected_scores
        )

        # -------------------------------------------------------------
        # SCORE RANGE
        # -------------------------------------------------------------

        range_pass = (
            valid_scores.min() >= 0.0
            and valid_scores.max() <= 1.0
        )

        print(
            "\n0–1 range check: "
            f"{'PASS' if range_pass else 'FAIL'}"
        )

        if not range_pass:
            raise ValueError(
                "Land Cover standardized values "
                "fall outside the 0–1 range."
            )

        # -------------------------------------------------------------
        # CLASS → SCORE VALIDATION
        # -------------------------------------------------------------

        mapping_pass = True

        print(
            "\nLand Cover class-to-score validation:"
        )

        for class_value, expected_score in (
            LANDCOVER_MAPPING.items()
        ):

            class_mask = (
                valid_source
                == class_value
            )

            class_scores = (
                valid_scores[class_mask]
            )

            if class_scores.size == 0:

                print(
                    f"  Class {class_value}: "
                    "FAIL — no valid cells"
                )

                mapping_pass = False
                continue

            expected_array = np.full(
                class_scores.shape,
                expected_score,
                dtype=np.float32,
            )

            class_mapping_pass = np.allclose(
                class_scores,
                expected_array,
                atol=1e-5,
            )

            print(
                f"  Class {class_value}: "
                f"expected {expected_score:.2f} → "
                f"{'PASS' if class_mapping_pass else 'FAIL'}"
            )

            if not class_mapping_pass:

                actual_unique = np.unique(
                    class_scores
                )

                print(
                    f"    Actual score(s): "
                    f"{actual_unique}"
                )

                mapping_pass = False

        if not mapping_pass:
            raise ValueError(
                "Land Cover class-to-score "
                "mapping validation failed."
            )

        # -------------------------------------------------------------
        # DETECTED SCORE VALIDATION
        # -------------------------------------------------------------

        for detected_score in detected_scores:

            matched = np.any(
                np.isclose(
                    detected_score,
                    expected_scores,
                    atol=1e-5,
                )
            )

            if not matched:

                raise ValueError(
                    "Unexpected Land Cover "
                    f"score detected: "
                    f"{detected_score}"
                )

        print(
            "\nLand Cover score mapping: PASS"
        )

    print(
        "\nLAND COVER VALIDATION: PASS"
    )


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("\n" + "=" * 70)
    print(
        "GEOAI FLOOD RISK AGENT"
    )
    print(
        "PHASE 6 — STANDARDIZED FACTOR VALIDATION"
    )
    print("=" * 70)

    print(
        f"\nProject root: "
        f"{PROJECT_ROOT}"
    )

    print(
        f"Standardized directory: "
        f"{STANDARDIZED_DIR}"
    )

    # -------------------------------------------------------------
    # CONTINUOUS FACTORS
    # -------------------------------------------------------------

    for factor_name, settings in (
        CONTINUOUS_FACTORS.items()
    ):

        validate_continuous_factor(
            factor_name=factor_name,
            source_filename=settings["source"],
            score_filename=settings["score"],
            relationship=settings["relationship"],
        )

    # -------------------------------------------------------------
    # LAND COVER
    # -------------------------------------------------------------

    validate_landcover()

    # -------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------

    print_header(
        "PHASE 6 STANDARDIZATION VALIDATION COMPLETE"
    )

    print(
        """
All standardized flood-conditioning factors
passed validation.

Validated factors:

  ✓ Elevation
  ✓ Slope
  ✓ Distance to Rivers
  ✓ Population
  ✓ Land Cover

Validation confirmed:

  ✓ CRS consistency
  ✓ Raster dimensions
  ✓ Raster transform
  ✓ Raster resolution
  ✓ Valid cell counts
  ✓ Continuous 0–1 standardization
  ✓ Direction of continuous relationships
  ✓ Land Cover class detection
  ✓ Land Cover class-to-score mapping

No source or standardized raster was modified.

The standardized factors are ready for the
next Phase 6 stage: spatial alignment and
MCDA preparation.
"""
    )


if __name__ == "__main__":
    main()