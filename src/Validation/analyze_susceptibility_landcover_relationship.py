"""
GeoAI Flood Risk Decision Agent
Phase 9.6 - Land-Cover Relationship Analysis

Purpose
-------
Validate the relationship between land cover and the final flood
susceptibility surface produced by the MCDA model.

Important methodological principle
-----------------------------------
Land-cover classes are categorical values. Their numerical codes
(e.g. 10, 20, 30, 40...) are NOT treated as an ordered continuous
variable.

The analysis therefore:

1. Validates the raw land-cover raster independently.
2. Aligns the raw categorical land-cover raster IN MEMORY to the
   final MCDA analysis grid using nearest-neighbour resampling.
3. Validates the existing standardized land-cover score raster.
4. Checks whether aligned land-cover classes correspond to the
   expected land-cover susceptibility scores.
5. Analyses land-cover class distribution.
6. Analyses land-cover composition within susceptibility classes.
7. Examines land-cover composition within Very High susceptibility.
8. Evaluates the relationship between land-cover score and continuous
   susceptibility.

This script is a validation analysis only.

It does NOT:
- modify raw data;
- modify aligned factor rasters;
- modify MCDA weights;
- modify susceptibility outputs;
- modify classification thresholds;
- write any new analysis raster.

All spatial alignment of the raw categorical land-cover raster is
performed in memory only.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_LANDCOVER_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "flood_factors"
    / "landcover.tif"
)

LANDCOVER_SCORE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
    / "landcover_score.tif"
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
    / "landcover_relationship"
)

CSV_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_landcover_relationship.csv"
)

JSON_OUTPUT = (
    RESULTS_DIR
    / "susceptibility_landcover_relationship.json"
)


# ============================================================================
# EXPECTED PROJECT SPECIFICATION
# ============================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019

EXPECTED_CLASSES = [
    10,
    20,
    30,
    40,
    50,
    60,
    80,
    90,
]

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

LANDCOVER_NAMES = {
    10: "Class 10",
    20: "Class 20",
    30: "Class 30",
    40: "Class 40",
    50: "Class 50",
    60: "Class 60",
    80: "Class 80",
    90: "Class 90",
}

SUSCEPTIBILITY_CLASSES = [
    1,
    2,
    3,
    4,
    5,
]

SUSCEPTIBILITY_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section heading."""

    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def get_valid_mask(
    array: np.ndarray,
    nodata,
) -> np.ndarray:
    """
    Return a boolean mask identifying valid finite cells.
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


def calculate_spearman(
    x: np.ndarray,
    y: np.ndarray,
) -> float:
    """
    Calculate Spearman rank correlation without scipy.

    This function is used for the relationship between the
    standardized land-cover score and continuous susceptibility.

    It is NOT applied to the categorical land-cover class codes.
    """

    if x.size != y.size:
        raise ValueError(
            "Spearman inputs must have the same number of values."
        )

    if x.size < 2:
        return float("nan")

    def rank_average(values: np.ndarray) -> np.ndarray:

        order = np.argsort(
            values,
            kind="mergesort",
        )

        sorted_values = values[order]

        ranks = np.empty(
            values.size,
            dtype=np.float64,
        )

        start = 0

        while start < values.size:

            end = start + 1

            while (
                end < values.size
                and
                sorted_values[end]
                == sorted_values[start]
            ):
                end += 1

            average_rank = (
                (start + 1) + end
            ) / 2.0

            ranks[
                order[start:end]
            ] = average_rank

            start = end

        return ranks

    x_ranks = rank_average(x)
    y_ranks = rank_average(y)

    x_centered = (
        x_ranks
        -
        np.mean(x_ranks)
    )

    y_centered = (
        y_ranks
        -
        np.mean(y_ranks)
    )

    denominator = np.sqrt(
        np.sum(x_centered ** 2)
        *
        np.sum(y_centered ** 2)
    )

    if denominator == 0:
        return float("nan")

    return float(
        np.sum(
            x_centered
            *
            y_centered
        )
        /
        denominator
    )


def interpret_correlation(
    correlation: float,
) -> str:
    """
    Describe the magnitude and direction of a correlation.
    """

    if np.isnan(correlation):
        return "UNDEFINED"

    magnitude = abs(correlation)

    if magnitude >= 0.80:
        strength = "VERY_STRONG"
    elif magnitude >= 0.60:
        strength = "STRONG"
    elif magnitude >= 0.40:
        strength = "MODERATE"
    elif magnitude >= 0.20:
        strength = "WEAK"
    else:
        strength = "VERY_WEAK"

    if correlation > 0:
        direction = "POSITIVE"
    elif correlation < 0:
        direction = "NEGATIVE"
    else:
        direction = "NONE"

    return f"{strength}_{direction}"


def safe_percentage(
    numerator: int,
    denominator: int,
) -> float:
    """Calculate a percentage safely."""

    if denominator == 0:
        return 0.0

    return float(
        numerator
        /
        denominator
        *
        100.0
    )


def validate_grid(
    reference,
    candidate,
    candidate_name: str,
) -> None:
    """
    Validate CRS, dimensions, resolution and transform.
    """

    crs_match = (
        reference.crs == candidate.crs
    )

    dimensions_match = (
        reference.width == candidate.width
        and
        reference.height == candidate.height
    )

    resolution_match = np.allclose(
        reference.res,
        candidate.res,
    )

    transform_match = np.allclose(
        reference.transform,
        candidate.transform,
    )

    print(
        f"{candidate_name} CRS: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"{candidate_name} dimensions: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )

    print(
        f"{candidate_name} resolution: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    print(
        f"{candidate_name} transform: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )

    if not (
        crs_match
        and dimensions_match
        and resolution_match
        and transform_match
    ):
        raise ValueError(
            f"{candidate_name} does not match the reference grid."
        )


def align_categorical_landcover_in_memory(
    src,
    reference,
) -> np.ndarray:
    """
    Reproject/resample the raw categorical land-cover raster into
    the final MCDA analysis grid.

    IMPORTANT:
    This alignment occurs only in memory.

    No new raster is written to disk.

    Nearest-neighbour resampling is used because land-cover values
    are categorical classes.
    """

    destination = np.full(
        (
            reference.height,
            reference.width,
        ),
        -9999,
        dtype=np.int32,
    )

    source_nodata = src.nodata

    reproject(
        source=rasterio.band(src, 1),
        destination=destination,
        src_transform=src.transform,
        src_crs=src.crs,
        src_nodata=source_nodata,
        dst_transform=reference.transform,
        dst_crs=reference.crs,
        dst_nodata=-9999,
        resampling=Resampling.nearest,
    )

    return destination


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run Phase 9.6 land-cover relationship validation."""

    print("=" * 72)
    print(
        "PHASE 9.6 - LAND-COVER RELATIONSHIP ANALYSIS"
    )
    print("=" * 72)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nRaw land-cover raster:")
    print(RAW_LANDCOVER_RASTER)

    print("\nLand-cover score raster:")
    print(LANDCOVER_SCORE_RASTER)

    print("\nContinuous susceptibility raster:")
    print(CONTINUOUS_SUSCEPTIBILITY_RASTER)

    print("\nClassified susceptibility raster:")
    print(CLASSIFIED_SUSCEPTIBILITY_RASTER)

    print("\nResults directory:")
    print(RESULTS_DIR)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================================
    # 1. INPUT FILE VALIDATION
    # ========================================================================

    print_header(
        "1. INPUT FILE VALIDATION"
    )

    input_paths = {
        "Raw land-cover":
            RAW_LANDCOVER_RASTER,

        "Land-cover score":
            LANDCOVER_SCORE_RASTER,

        "Continuous susceptibility":
            CONTINUOUS_SUSCEPTIBILITY_RASTER,

        "Classified susceptibility":
            CLASSIFIED_SUSCEPTIBILITY_RASTER,
    }

    for name, path in input_paths.items():

        print(f"\n{name}:")
        print(path)

        if not path.exists():
            raise FileNotFoundError(
                f"{name} raster does not exist:\n{path}"
            )

        print("Exists: PASS")

    # ========================================================================
    # OPEN RASTERS
    # ========================================================================

    with (
        rasterio.open(RAW_LANDCOVER_RASTER) as raw_landcover_src,
        rasterio.open(LANDCOVER_SCORE_RASTER) as landcover_score_src,
        rasterio.open(
            CONTINUOUS_SUSCEPTIBILITY_RASTER
        ) as continuous_src,
        rasterio.open(
            CLASSIFIED_SUSCEPTIBILITY_RASTER
        ) as classified_src,
    ):

        raw_landcover = raw_landcover_src.read(1)

        landcover_score = landcover_score_src.read(1)

        continuous_susceptibility = (
            continuous_src.read(1)
        )

        classified_susceptibility = (
            classified_src.read(1)
        )

        # ====================================================================
        # 2. REFERENCE GRID VALIDATION
        # ====================================================================

        print_header(
            "2. REFERENCE GRID VALIDATION"
        )

        print(
            f"Expected CRS: {EXPECTED_CRS}"
        )

        print(
            f"Actual CRS:   {continuous_src.crs}"
        )

        if (
            continuous_src.crs is None
            or
            continuous_src.crs.to_string()
            != EXPECTED_CRS
        ):
            raise ValueError(
                "Continuous susceptibility CRS does not "
                "match the expected project CRS."
            )

        print("CRS: PASS")

        print(
            f"Expected dimensions: "
            f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
        )

        print(
            f"Actual dimensions:   "
            f"{continuous_src.width} x "
            f"{continuous_src.height}"
        )

        if (
            continuous_src.width != EXPECTED_WIDTH
            or
            continuous_src.height != EXPECTED_HEIGHT
        ):
            raise ValueError(
                "Continuous susceptibility dimensions "
                "do not match the expected project grid."
            )

        print("Dimensions: PASS")

        # ====================================================================
        # 3. RAW LAND-COVER SOURCE VALIDATION
        # ====================================================================

        print_header(
            "3. RAW LAND-COVER SOURCE VALIDATION"
        )

        print(
            f"Raw land-cover CRS: "
            f"{raw_landcover_src.crs}"
        )

        print(
            f"Raw land-cover dimensions: "
            f"{raw_landcover_src.width} x "
            f"{raw_landcover_src.height}"
        )

        print(
            f"Raw land-cover resolution: "
            f"{raw_landcover_src.res[0]:.6f} x "
            f"{raw_landcover_src.res[1]:.6f} m"
        )

        raw_crs_valid = (
            raw_landcover_src.crs is not None
        )

        print(
            "Raw land-cover CRS available: "
            f"{'PASS' if raw_crs_valid else 'FAIL'}"
        )

        if not raw_crs_valid:
            raise ValueError(
                "Raw land-cover raster has no CRS."
            )

        raw_valid = get_valid_mask(
            raw_landcover,
            raw_landcover_src.nodata,
        )

        raw_values = (
            raw_landcover[
                raw_valid
            ]
            .astype(np.int32)
        )

        raw_observed_classes = sorted(
            np.unique(
                raw_values
            ).tolist()
        )

        print(
            "Observed raw land-cover classes:"
        )

        print(
            raw_observed_classes
        )

        unexpected_raw_classes = sorted(
            set(raw_observed_classes)
            -
            set(EXPECTED_CLASSES)
        )

        if unexpected_raw_classes:

            print(
                "Unexpected raw land-cover classes:"
            )

            print(
                unexpected_raw_classes
            )

            raise ValueError(
                "Unexpected land-cover class values "
                "were found in the raw raster."
            )

        print(
            "Raw land-cover class values: PASS"
        )

        # ====================================================================
        # 4. SPATIAL COMPATIBILITY OF MCDA INPUTS
        # ====================================================================

        print_header(
            "4. MCDA GRID COMPATIBILITY VALIDATION"
        )

        validate_grid(
            continuous_src,
            landcover_score_src,
            "Land-cover score",
        )

        validate_grid(
            continuous_src,
            classified_src,
            "Classified susceptibility",
        )

        print(
            "MCDA grid compatibility: PASS"
        )

        # ====================================================================
        # 5. IN-MEMORY CATEGORICAL LAND-COVER ALIGNMENT
        # ====================================================================

        print_header(
            "5. IN-MEMORY LAND-COVER ALIGNMENT"
        )

        print(
            "Reference grid:"
        )

        print(
            f"  CRS: {continuous_src.crs}"
        )

        print(
            f"  Dimensions: "
            f"{continuous_src.width} x "
            f"{continuous_src.height}"
        )

        print(
            f"  Resolution: "
            f"{continuous_src.res[0]:.6f} x "
            f"{continuous_src.res[1]:.6f} m"
        )

        print(
            "Resampling method: "
            "Nearest Neighbour"
        )

        print(
            "Alignment destination: "
            "Memory only"
        )

        aligned_landcover = (
            align_categorical_landcover_in_memory(
                raw_landcover_src,
                continuous_src,
            )
        )

        aligned_landcover_valid = (
            aligned_landcover != -9999
        )

        aligned_landcover_values = (
            aligned_landcover[
                aligned_landcover_valid
            ]
        )

        aligned_observed_classes = sorted(
            np.unique(
                aligned_landcover_values
            ).tolist()
        )

        print(
            "Aligned land-cover classes:"
        )

        print(
            aligned_observed_classes
        )

        unexpected_aligned_classes = sorted(
            set(aligned_observed_classes)
            -
            set(EXPECTED_CLASSES)
        )

        if unexpected_aligned_classes:

            print(
                "Unexpected aligned classes:"
            )

            print(
                unexpected_aligned_classes
            )

            raise ValueError(
                "Unexpected land-cover classes occurred "
                "after nearest-neighbour alignment."
            )

        print(
            "In-memory categorical alignment: PASS"
        )

        # ====================================================================
        # 6. COMMON VALID-CELL OVERLAP
        # ====================================================================

        print_header(
            "6. COMMON VALID-CELL OVERLAP"
        )

        landcover_score_valid = get_valid_mask(
            landcover_score,
            landcover_score_src.nodata,
        )

        continuous_valid = get_valid_mask(
            continuous_susceptibility,
            continuous_src.nodata,
        )

        classified_valid = get_valid_mask(
            classified_susceptibility,
            classified_src.nodata,
        )

        common_mask = (
            aligned_landcover_valid
            &
            landcover_score_valid
            &
            continuous_valid
            &
            classified_valid
        )

        total_cells = int(
            common_mask.size
        )

        common_cells = int(
            np.count_nonzero(common_mask)
        )

        print(
            f"Total reference-grid cells: "
            f"{total_cells:,}"
        )

        print(
            f"Common valid cells: "
            f"{common_cells:,}"
        )

        print(
            f"Common valid percentage: "
            f"{safe_percentage(common_cells, total_cells):.3f}%"
        )

        if common_cells == 0:
            raise ValueError(
                "No common valid cells were found."
            )

        print(
            "Common valid-cell overlap: PASS"
        )

        # Extract common values
        landcover_values = (
            aligned_landcover[
                common_mask
            ]
            .astype(np.int32)
        )

        landcover_score_values = (
            landcover_score[
                common_mask
            ]
            .astype(np.float64)
        )

        susceptibility_values = (
            continuous_susceptibility[
                common_mask
            ]
            .astype(np.float64)
        )

        class_values = (
            classified_susceptibility[
                common_mask
            ]
            .astype(np.int16)
        )

        # ====================================================================
        # 7. LAND-COVER SCORE RANGE VALIDATION
        # ====================================================================

        print_header(
            "7. LAND-COVER SCORE RANGE VALIDATION"
        )

        score_min = float(
            np.min(
                landcover_score_values
            )
        )

        score_max = float(
            np.max(
                landcover_score_values
            )
        )

        score_mean = float(
            np.mean(
                landcover_score_values
            )
        )

        print(
            f"Minimum land-cover score: "
            f"{score_min:.6f}"
        )

        print(
            f"Maximum land-cover score: "
            f"{score_max:.6f}"
        )

        print(
            f"Mean land-cover score: "
            f"{score_mean:.6f}"
        )

        score_range_pass = (
            score_min >= 0.0
            and
            score_max <= 1.0
        )

        print(
            "Land-cover score 0-1 range: "
            f"{'PASS' if score_range_pass else 'FAIL'}"
        )

        if not score_range_pass:
            raise ValueError(
                "Land-cover score values fall outside 0-1."
            )

        # ====================================================================
        # 8. CLASS-TO-SCORE CONSISTENCY
        # ====================================================================

        print_header(
            "8. LAND-COVER CLASS / SCORE CONSISTENCY"
        )

        class_score_results = {}

        class_score_consistency = True

        for landcover_class in EXPECTED_CLASSES:

            mask = (
                landcover_values
                ==
                landcover_class
            )

            count = int(
                np.count_nonzero(mask)
            )

            expected_score = (
                LANDCOVER_SCORES[
                    landcover_class
                ]
            )

            if count > 0:

                observed_scores = (
                    landcover_score_values[
                        mask
                    ]
                )

                observed_min = float(
                    np.min(
                        observed_scores
                    )
                )

                observed_max = float(
                    np.max(
                        observed_scores
                    )
                )

                observed_mean = float(
                    np.mean(
                        observed_scores
                    )
                )

                score_matches = bool(
                    np.allclose(
                        observed_scores,
                        expected_score,
                        atol=1e-5,
                    )
                )

            else:

                observed_min = None
                observed_max = None
                observed_mean = None
                score_matches = True

            class_score_results[
                str(landcover_class)
            ] = {
                "class_name":
                    LANDCOVER_NAMES[
                        landcover_class
                    ],

                "expected_score":
                    expected_score,

                "cell_count":
                    count,

                "observed_min_score":
                    observed_min,

                "observed_max_score":
                    observed_max,

                "observed_mean_score":
                    observed_mean,

                "score_consistent":
                    score_matches,
            }

            print(
                f"{landcover_class} - "
                f"{LANDCOVER_NAMES[landcover_class]}"
            )

            print(
                f"  Expected score: "
                f"{expected_score:.2f}"
            )

            print(
                f"  Cells: "
                f"{count:,}"
            )

            if count > 0:

                print(
                    f"  Observed score range: "
                    f"{observed_min:.6f} - "
                    f"{observed_max:.6f}"
                )

                print(
                    f"  Observed mean score: "
                    f"{observed_mean:.6f}"
                )

            print(
                "  Score consistency: "
                f"{'PASS' if score_matches else 'FAIL'}"
            )

            if not score_matches:
                class_score_consistency = False

        if not class_score_consistency:
            raise ValueError(
                "One or more land-cover classes do not "
                "match their expected standardized score."
            )

        print(
            "\nLand-cover class/score consistency: PASS"
        )

        # ====================================================================
        # 9. LAND-COVER DISTRIBUTION
        # ====================================================================

        print_header(
            "9. LAND-COVER CLASS DISTRIBUTION"
        )

        landcover_distribution = {}

        for landcover_class in EXPECTED_CLASSES:

            mask = (
                landcover_values
                ==
                landcover_class
            )

            count = int(
                np.count_nonzero(mask)
            )

            percentage = safe_percentage(
                count,
                common_cells,
            )

            landcover_distribution[
                str(landcover_class)
            ] = {
                "class_name":
                    LANDCOVER_NAMES[
                        landcover_class
                    ],

                "assigned_score":
                    LANDCOVER_SCORES[
                        landcover_class
                    ],

                "cell_count":
                    count,

                "percentage":
                    percentage,
            }

            print(
                f"{landcover_class} - "
                f"{LANDCOVER_NAMES[landcover_class]}"
            )

            print(
                f"  Assigned score: "
                f"{LANDCOVER_SCORES[landcover_class]:.2f}"
            )

            print(
                f"  Cells: "
                f"{count:,}"
            )

            print(
                f"  Percentage: "
                f"{percentage:.3f}%"
            )

        # ====================================================================
        # 10. LAND-COVER CHARACTERISTICS BY SUSCEPTIBILITY CLASS
        # ====================================================================

        print_header(
            "10. LAND-COVER CHARACTERISTICS BY SUSCEPTIBILITY CLASS"
        )

        class_results = {}

        class_mean_landcover_scores = []

        class_mean_susceptibility = []

        for susceptibility_class in SUSCEPTIBILITY_CLASSES:

            susceptibility_mask = (
                class_values
                ==
                susceptibility_class
            )

            class_count = int(
                np.count_nonzero(
                    susceptibility_mask
                )
            )

            if class_count == 0:
                raise ValueError(
                    f"Susceptibility class "
                    f"{susceptibility_class} "
                    "contains no cells."
                )

            class_landcover = (
                landcover_values[
                    susceptibility_mask
                ]
            )

            class_scores = (
                landcover_score_values[
                    susceptibility_mask
                ]
            )

            class_susceptibility = (
                susceptibility_values[
                    susceptibility_mask
                ]
            )

            mean_score = float(
                np.mean(
                    class_scores
                )
            )

            mean_susceptibility = float(
                np.mean(
                    class_susceptibility
                )
            )

            class_mean_landcover_scores.append(
                mean_score
            )

            class_mean_susceptibility.append(
                mean_susceptibility
            )

            composition = {}

            for landcover_class in EXPECTED_CLASSES:

                count = int(
                    np.count_nonzero(
                        class_landcover
                        ==
                        landcover_class
                    )
                )

                percentage = safe_percentage(
                    count,
                    class_count,
                )

                composition[
                    str(landcover_class)
                ] = {
                    "class_name":
                        LANDCOVER_NAMES[
                            landcover_class
                        ],

                    "cell_count":
                        count,

                    "percentage":
                        percentage,
                }

            dominant_class = max(
                EXPECTED_CLASSES,
                key=lambda lc:
                    composition[
                        str(lc)
                    ][
                        "cell_count"
                    ],
            )

            dominant_count = composition[
                str(dominant_class)
            ][
                "cell_count"
            ]

            dominant_percentage = (
                safe_percentage(
                    dominant_count,
                    class_count,
                )
            )

            class_results[
                str(susceptibility_class)
            ] = {
                "class_name":
                    SUSCEPTIBILITY_NAMES[
                        susceptibility_class
                    ],

                "cell_count":
                    class_count,

                "mean_landcover_score":
                    mean_score,

                "mean_continuous_susceptibility":
                    mean_susceptibility,

                "dominant_landcover_class":
                    dominant_class,

                "dominant_landcover_name":
                    LANDCOVER_NAMES[
                        dominant_class
                    ],

                "dominant_landcover_percentage":
                    dominant_percentage,

                "landcover_composition":
                    composition,
            }

            print(
                f"\n{susceptibility_class} - "
                f"{SUSCEPTIBILITY_NAMES[susceptibility_class]}"
            )

            print(
                f"  Cells: "
                f"{class_count:,}"
            )

            print(
                f"  Mean land-cover score: "
                f"{mean_score:.6f}"
            )

            print(
                f"  Mean susceptibility: "
                f"{mean_susceptibility:.6f}"
            )

            print(
                f"  Dominant land-cover class: "
                f"{dominant_class} "
                f"({LANDCOVER_NAMES[dominant_class]})"
            )

            print(
                f"  Dominant class percentage: "
                f"{dominant_percentage:.3f}%"
            )

        # ====================================================================
        # 11. VERY HIGH SUSCEPTIBILITY ANALYSIS
        # ====================================================================

        print_header(
            "11. VERY HIGH SUSCEPTIBILITY LAND-COVER ANALYSIS"
        )

        very_high_mask = (
            class_values
            ==
            5
        )

        very_high_count = int(
            np.count_nonzero(
                very_high_mask
            )
        )

        very_high_landcover = (
            landcover_values[
                very_high_mask
            ]
        )

        very_high_scores = (
            landcover_score_values[
                very_high_mask
            ]
        )

        very_high_susceptibility = (
            susceptibility_values[
                very_high_mask
            ]
        )

        very_high_composition = {}

        for landcover_class in EXPECTED_CLASSES:

            count = int(
                np.count_nonzero(
                    very_high_landcover
                    ==
                    landcover_class
                )
            )

            percentage = safe_percentage(
                count,
                very_high_count,
            )

            very_high_composition[
                str(landcover_class)
            ] = {
                "class_name":
                    LANDCOVER_NAMES[
                        landcover_class
                    ],

                "assigned_score":
                    LANDCOVER_SCORES[
                        landcover_class
                    ],

                "cell_count":
                    count,

                "percentage_of_very_high":
                    percentage,
            }

            if count > 0:

                print(
                    f"{landcover_class} - "
                    f"{LANDCOVER_NAMES[landcover_class]}: "
                    f"{count:,} cells "
                    f"({percentage:.3f}%)"
                )

        very_high_mean_score = float(
            np.mean(
                very_high_scores
            )
        )

        very_high_mean_susceptibility = float(
            np.mean(
                very_high_susceptibility
            )
        )

        print(
            f"\nVery High susceptibility cells: "
            f"{very_high_count:,}"
        )

        print(
            f"Mean land-cover score within Very High: "
            f"{very_high_mean_score:.6f}"
        )

        print(
            f"Mean susceptibility within Very High: "
            f"{very_high_mean_susceptibility:.6f}"
        )

        # ====================================================================
        # 12. SCORE VS CONTINUOUS SUSCEPTIBILITY
        # ====================================================================

        print_header(
            "12. LAND-COVER SCORE VS CONTINUOUS SUSCEPTIBILITY"
        )

        score_susceptibility_correlation = (
            calculate_spearman(
                landcover_score_values,
                susceptibility_values,
            )
        )

        correlation_interpretation = (
            interpret_correlation(
                score_susceptibility_correlation
            )
        )

        print(
            "Land-cover score vs continuous susceptibility:"
        )

        print(
            f"  Spearman correlation: "
            f"{score_susceptibility_correlation:.6f}"
        )

        print(
            f"  Interpretation: "
            f"{correlation_interpretation}"
        )

        # ====================================================================
        # 13. SUSCEPTIBILITY CLASS VALIDATION
        # ====================================================================

        print_header(
            "13. SUSCEPTIBILITY CLASS VALIDATION"
        )

        observed_susceptibility_classes = sorted(
            np.unique(
                class_values
            ).tolist()
        )

        print(
            "Observed susceptibility classes:"
        )

        print(
            observed_susceptibility_classes
        )

        susceptibility_classes_pass = (
            observed_susceptibility_classes
            ==
            SUSCEPTIBILITY_CLASSES
        )

        print(
            "All five susceptibility classes present: "
            f"{'PASS' if susceptibility_classes_pass else 'FAIL'}"
        )

        if not susceptibility_classes_pass:
            raise ValueError(
                "Unexpected susceptibility classes found."
            )

        # ====================================================================
        # 14. OVERALL ASSESSMENT
        # ====================================================================

        print_header(
            "14. OVERALL LAND-COVER RELATIONSHIP ASSESSMENT"
        )

        positive_relationship = (
            score_susceptibility_correlation
            >=
            0.0
        )

        very_high_score_above_footprint_mean = (
            very_high_mean_score
            >=
            score_mean
        )

        if (
            class_score_consistency
            and
            positive_relationship
            and
            very_high_score_above_footprint_mean
        ):

            overall_status = (
                "CONSISTENT"
            )

        elif (
            class_score_consistency
            and
            positive_relationship
        ):

            overall_status = (
                "PARTIALLY_CONSISTENT"
            )

        else:

            overall_status = (
                "INVESTIGATE"
            )

        print(
            "Land-cover relationship status:"
        )

        print(
            overall_status
        )

        # ====================================================================
        # 15. SAVE CSV
        # ====================================================================

        print_header(
            "15. SAVE CSV RESULTS"
        )

        csv_rows = []

        for susceptibility_class in SUSCEPTIBILITY_CLASSES:

            result = class_results[
                str(susceptibility_class)
            ]

            for landcover_class in EXPECTED_CLASSES:

                composition = result[
                    "landcover_composition"
                ][
                    str(landcover_class)
                ]

                csv_rows.append(
                    {
                        "susceptibility_class":
                            susceptibility_class,

                        "susceptibility_name":
                            result["class_name"],

                        "landcover_class":
                            landcover_class,

                        "landcover_name":
                            LANDCOVER_NAMES[
                                landcover_class
                            ],

                        "assigned_landcover_score":
                            LANDCOVER_SCORES[
                                landcover_class
                            ],

                        "susceptibility_class_cell_count":
                            result["cell_count"],

                        "landcover_cell_count":
                            composition[
                                "cell_count"
                            ],

                        "landcover_percentage_within_susceptibility_class":
                            composition[
                                "percentage"
                            ],

                        "mean_landcover_score_within_susceptibility_class":
                            result[
                                "mean_landcover_score"
                            ],

                        "mean_continuous_susceptibility":
                            result[
                                "mean_continuous_susceptibility"
                            ],
                    }
                )

        fieldnames = [
            "susceptibility_class",
            "susceptibility_name",
            "landcover_class",
            "landcover_name",
            "assigned_landcover_score",
            "susceptibility_class_cell_count",
            "landcover_cell_count",
            "landcover_percentage_within_susceptibility_class",
            "mean_landcover_score_within_susceptibility_class",
            "mean_continuous_susceptibility",
        ]

        with open(
            CSV_OUTPUT,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(
                csv_rows
            )

        if not CSV_OUTPUT.exists():
            raise RuntimeError(
                "CSV output was not created."
            )

        print(
            f"CSV saved to:\n"
            f"{CSV_OUTPUT}"
        )

        print(
            "CSV output: PASS"
        )

        # ====================================================================
        # 16. SAVE JSON
        # ====================================================================

        print_header(
            "16. SAVE JSON RESULTS"
        )

        report = {
            "phase":
                "9.6",

            "analysis":
                "Land-Cover Relationship Analysis",

            "purpose":
                "Validate whether the final flood "
                "susceptibility surface behaves consistently "
                "with the categorical land-cover factor and "
                "its assigned MCDA susceptibility scores.",

            "methodological_note":
                "Land-cover class codes are categorical and "
                "are not treated as an ordered continuous "
                "variable. The raw land-cover raster is aligned "
                "to the final MCDA grid in memory using "
                "nearest-neighbour resampling. No analysis "
                "raster is written by this validation script.",

            "project_crs":
                EXPECTED_CRS,

            "reference_dimensions": {
                "width":
                    EXPECTED_WIDTH,

                "height":
                    EXPECTED_HEIGHT,
            },

            "inputs": {
                "raw_landcover":
                    str(
                        RAW_LANDCOVER_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "landcover_score":
                    str(
                        LANDCOVER_SCORE_RASTER.relative_to(
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

            "resampling": {
                "method":
                    "nearest_neighbour",

                "performed_in_memory":
                    True,

                "output_raster_written":
                    False,
            },

            "expected_landcover_scores":
                LANDCOVER_SCORES,

            "raw_observed_landcover_classes":
                raw_observed_classes,

            "aligned_observed_landcover_classes":
                aligned_observed_classes,

            "cell_accounting": {
                "reference_grid_cells":
                    total_cells,

                "common_valid_cells":
                    common_cells,

                "common_valid_percentage":
                    safe_percentage(
                        common_cells,
                        total_cells,
                    ),
            },

            "landcover_score_validation": {
                "minimum":
                    score_min,

                "maximum":
                    score_max,

                "mean":
                    score_mean,

                "range_status":
                    "PASS",
            },

            "class_score_consistency":
                class_score_results,

            "landcover_distribution":
                landcover_distribution,

            "susceptibility_class_results":
                class_results,

            "very_high_analysis": {
                "cell_count":
                    very_high_count,

                "mean_landcover_score":
                    very_high_mean_score,

                "mean_continuous_susceptibility":
                    very_high_mean_susceptibility,

                "composition":
                    very_high_composition,
            },

            "landcover_score_vs_continuous_susceptibility": {
                "spearman_correlation":
                    score_susceptibility_correlation,

                "interpretation":
                    correlation_interpretation,
            },

            "overall_status":
                overall_status,

            "model_modified":
                False,

            "classification_modified":
                False,
        }

        with open(
            JSON_OUTPUT,
            "w",
            encoding="utf-8",
        ) as json_file:

            json.dump(
                report,
                json_file,
                indent=4,
            )

        if not JSON_OUTPUT.exists():
            raise RuntimeError(
                "JSON output was not created."
            )

        print(
            f"JSON saved to:\n"
            f"{JSON_OUTPUT}"
        )

        print(
            "JSON output: PASS"
        )

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print("\n" + "=" * 72)
    print(
        "PHASE 9.6 ANALYSIS COMPLETED"
    )
    print("=" * 72)

    print(
        "\nCommon valid cells:"
    )

    print(
        f"{common_cells:,}"
    )

    print(
        "\nLand-cover score vs continuous susceptibility:"
    )

    print(
        f"{score_susceptibility_correlation:.6f}"
    )

    print(
        "\nInterpretation:"
    )

    print(
        correlation_interpretation
    )

    print(
        "\nLand-cover relationship status:"
    )

    print(
        overall_status
    )

    print(
        "\nOutputs:"
    )

    print(
        CSV_OUTPUT
    )

    print(
        JSON_OUTPUT
    )


if __name__ == "__main__":
    main()