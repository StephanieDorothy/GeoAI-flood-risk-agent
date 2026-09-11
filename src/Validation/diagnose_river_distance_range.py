
"""
GeoAI Flood Risk Decision Agent
Phase 9.4 - River Distance Range Diagnostic

Purpose
-------
Investigate the river-distance range used by the flood susceptibility
MCDA model.

This diagnostic compares:

1. Raw river-distance raster
2. Aligned/standardized river-distance score
3. Continuous MCDA susceptibility raster
4. Classified susceptibility raster

The purpose is to determine whether the apparently high standardized
river scores are consistent with the actual distance range present
within the common MCDA analysis footprint.

This is a diagnostic only.

It does NOT:
- modify any raster
- modify MCDA weights
- modify classification thresholds
- regenerate susceptibility outputs

Expected project CRS
--------------------
EPSG:32737
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DISTANCE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "flood_factors"
    / "distance_to_rivers.tif"
)

RIVER_SCORE_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
    / "distance_to_rivers_score.tif"
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
    / "river_relationship"
)

DIAGNOSTIC_JSON = (
    RESULTS_DIR
    / "river_distance_range_diagnostic.json"
)


# ============================================================================
# EXPECTED PROJECT SPECIFICATION
# ============================================================================

EXPECTED_CRS = "EPSG:32737"

EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019


# ============================================================================
# HELPERS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section heading."""

    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def open_raster(path: Path):
    """
    Open a raster and return the dataset and first-band array.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required raster does not exist:\n{path}"
        )

    src = rasterio.open(path)

    array = src.read(1)

    return src, array


def valid_mask(
    array: np.ndarray,
    nodata,
) -> np.ndarray:
    """
    Return a mask identifying valid finite raster cells.
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


def raster_metadata(src) -> dict:
    """Return important spatial metadata."""

    return {
        "crs": (
            src.crs.to_string()
            if src.crs is not None
            else None
        ),
        "width": src.width,
        "height": src.height,
        "resolution": [
            float(src.res[0]),
            float(src.res[1]),
        ],
        "transform": [
            float(value)
            for value in src.transform
        ],
        "nodata": (
            float(src.nodata)
            if src.nodata is not None
            else None
        ),
    }


def compare_spatial_grid(
    reference,
    candidate,
    candidate_name: str,
) -> None:
    """
    Confirm that the candidate raster matches the reference
    raster spatial grid.
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
            f"{candidate_name} does not share the "
            "same spatial grid as the reference raster."
        )


def describe_values(
    name: str,
    values: np.ndarray,
) -> dict:
    """
    Calculate descriptive statistics for a valid numeric array.
    """

    if values.size == 0:
        raise ValueError(
            f"No valid values available for {name}."
        )

    percentiles = np.percentile(
        values,
        [5, 25, 50, 75, 95],
    )

    result = {
        "count": int(values.size),
        "minimum": float(np.min(values)),
        "p05": float(percentiles[0]),
        "p25": float(percentiles[1]),
        "median": float(percentiles[2]),
        "p75": float(percentiles[3]),
        "p95": float(percentiles[4]),
        "maximum": float(np.max(values)),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
    }

    print(f"\n{name}")

    print(
        f"  Count   : {result['count']:,}"
    )

    print(
        f"  Minimum : {result['minimum']:.6f}"
    )

    print(
        f"  P05     : {result['p05']:.6f}"
    )

    print(
        f"  P25     : {result['p25']:.6f}"
    )

    print(
        f"  Median  : {result['median']:.6f}"
    )

    print(
        f"  P75     : {result['p75']:.6f}"
    )

    print(
        f"  P95     : {result['p95']:.6f}"
    )

    print(
        f"  Maximum : {result['maximum']:.6f}"
    )

    print(
        f"  Mean    : {result['mean']:.6f}"
    )

    print(
        f"  Std     : {result['std']:.6f}"
    )

    return result


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run the river-distance range diagnostic."""

    print("=" * 72)
    print(
        "PHASE 9.4 - RIVER DISTANCE RANGE DIAGNOSTIC"
    )
    print("=" * 72)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nRaw distance raster:")
    print(RAW_DISTANCE_RASTER)

    print("\nRiver score raster:")
    print(RIVER_SCORE_RASTER)

    print("\nContinuous susceptibility raster:")
    print(CONTINUOUS_SUSCEPTIBILITY_RASTER)

    print("\nClassified susceptibility raster:")
    print(CLASSIFIED_SUSCEPTIBILITY_RASTER)

    print("\nDiagnostic output:")
    print(DIAGNOSTIC_JSON)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================================
    # 1. INPUT VALIDATION
    # ========================================================================

    print_header(
        "1. INPUT RASTER VALIDATION"
    )

    paths = {
        "Raw distance":
            RAW_DISTANCE_RASTER,
        "River score":
            RIVER_SCORE_RASTER,
        "Continuous susceptibility":
            CONTINUOUS_SUSCEPTIBILITY_RASTER,
        "Classified susceptibility":
            CLASSIFIED_SUSCEPTIBILITY_RASTER,
    }

    for name, path in paths.items():

        print(f"\n{name}:")
        print(path)

        if not path.exists():
            raise FileNotFoundError(
                f"{name} raster was not found."
            )

        print("Exists: PASS")

    # ========================================================================
    # 2. OPEN RASTERS
    # ========================================================================

    raw_src = None
    score_src = None
    continuous_src = None
    classified_src = None

    try:

        raw_src, raw_distance = open_raster(
            RAW_DISTANCE_RASTER
        )

        score_src, river_score = open_raster(
            RIVER_SCORE_RASTER
        )

        continuous_src, continuous_susceptibility = (
            open_raster(
                CONTINUOUS_SUSCEPTIBILITY_RASTER
            )
        )

        classified_src, classified_susceptibility = (
            open_raster(
                CLASSIFIED_SUSCEPTIBILITY_RASTER
            )
        )

        # ====================================================================
        # 3. REFERENCE GRID VALIDATION
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
            continuous_src.width
            != EXPECTED_WIDTH
            or
            continuous_src.height
            != EXPECTED_HEIGHT
        ):
            raise ValueError(
                "Continuous susceptibility dimensions "
                "do not match the expected analysis grid."
            )

        print("Dimensions: PASS")

        # ====================================================================
        # 4. COMPARE SPATIAL GRIDS
        # ====================================================================

        print_header(
            "3. SPATIAL GRID COMPATIBILITY"
        )

        compare_spatial_grid(
            continuous_src,
            raw_src,
            "Raw distance",
        )

        compare_spatial_grid(
            continuous_src,
            score_src,
            "River score",
        )

        compare_spatial_grid(
            continuous_src,
            classified_src,
            "Classified susceptibility",
        )

        print(
            "Spatial grid compatibility: PASS"
        )

        # ====================================================================
        # 5. VALID MASKS
        # ====================================================================

        print_header(
            "4. VALID-CELL MASK ANALYSIS"
        )

        raw_valid = valid_mask(
            raw_distance,
            raw_src.nodata,
        )

        score_valid = valid_mask(
            river_score,
            score_src.nodata,
        )

        continuous_valid = valid_mask(
            continuous_susceptibility,
            continuous_src.nodata,
        )

        classified_valid = valid_mask(
            classified_susceptibility,
            classified_src.nodata,
        )

        print(
            f"Raw distance valid cells: "
            f"{np.count_nonzero(raw_valid):,}"
        )

        print(
            f"River score valid cells: "
            f"{np.count_nonzero(score_valid):,}"
        )

        print(
            f"Continuous susceptibility valid cells: "
            f"{np.count_nonzero(continuous_valid):,}"
        )

        print(
            f"Classified susceptibility valid cells: "
            f"{np.count_nonzero(classified_valid):,}"
        )

        # ====================================================================
        # 6. COMMON MCDA FOOTPRINT
        # ====================================================================

        print_header(
            "5. COMMON MCDA ANALYSIS FOOTPRINT"
        )

        common_mask = (
            raw_valid
            &
            score_valid
            &
            continuous_valid
            &
            classified_valid
        )

        common_count = int(
            np.count_nonzero(common_mask)
        )

        total_cells = int(
            common_mask.size
        )

        print(
            f"Total raster cells: "
            f"{total_cells:,}"
        )

        print(
            f"Common valid cells: "
            f"{common_count:,}"
        )

        print(
            f"Common valid percentage: "
            f"{common_count / total_cells * 100:.3f}%"
        )

        if common_count == 0:
            raise ValueError(
                "No common valid cells were found."
            )

        print(
            "Common MCDA footprint: PASS"
        )

        # ====================================================================
        # 7. EXTRACT COMMON VALUES
        # ====================================================================

        common_distance = (
            raw_distance[common_mask]
            .astype(np.float64)
        )

        common_score = (
            river_score[common_mask]
            .astype(np.float64)
        )

        common_continuous = (
            continuous_susceptibility[common_mask]
            .astype(np.float64)
        )

        common_classified = (
            classified_susceptibility[common_mask]
            .astype(np.int16)
        )

        # ====================================================================
        # 8. RAW RASTER RANGE
        # ====================================================================

        print_header(
            "6. RAW RIVER-DISTANCE RANGE"
        )

        raw_all_valid = (
            raw_distance[raw_valid]
            .astype(np.float64)
        )

        raw_statistics = describe_values(
            "Entire raw-distance raster",
            raw_all_valid,
        )

        # ====================================================================
        # 9. MCDA FOOTPRINT RANGE
        # ====================================================================

        print_header(
            "7. RIVER-DISTANCE RANGE WITHIN MCDA FOOTPRINT"
        )

        mcda_statistics = describe_values(
            "Common MCDA footprint",
            common_distance,
        )

        # ====================================================================
        # 10. RIVER SCORE RANGE
        # ====================================================================

        print_header(
            "8. STANDARDIZED RIVER-SCORE RANGE"
        )

        score_statistics = describe_values(
            "Standardized river score",
            common_score,
        )

        # ====================================================================
        # 11. CONTINUOUS SUSCEPTIBILITY RANGE
        # ========================================================================

        print_header(
            "9. CONTINUOUS SUSCEPTIBILITY RANGE"
        )

        susceptibility_statistics = describe_values(
            "Continuous susceptibility",
            common_continuous,
        )

        # ====================================================================
        # 12. CLASS COUNTS
        # ========================================================================

        print_header(
            "10. SUSCEPTIBILITY CLASS COUNTS"
        )

        class_counts = {}

        for class_code in range(1, 6):

            count = int(
                np.count_nonzero(
                    common_classified == class_code
                )
            )

            class_counts[str(class_code)] = count

            print(
                f"Class {class_code}: "
                f"{count:,} cells"
            )

        # ====================================================================
        # 13. RANGE COMPARISON
        # ========================================================================

        print_header(
            "11. RANGE COMPARISON"
        )

        raw_max = raw_statistics[
            "maximum"
        ]

        mcda_max = mcda_statistics[
            "maximum"
        ]

        raw_median = raw_statistics[
            "median"
        ]

        mcda_median = mcda_statistics[
            "median"
        ]

        print(
            f"Entire raw raster maximum: "
            f"{raw_max:.6f} m"
        )

        print(
            f"MCDA footprint maximum: "
            f"{mcda_max:.6f} m"
        )

        print(
            f"Entire raw raster median: "
            f"{raw_median:.6f} m"
        )

        print(
            f"MCDA footprint median: "
            f"{mcda_median:.6f} m"
        )

        if raw_max > 0:

            max_difference_percent = (
                (
                    raw_max - mcda_max
                )
                /
                raw_max
                *
                100
            )

        else:

            max_difference_percent = 0.0

        print(
            "Reduction in maximum distance "
            "within MCDA footprint: "
            f"{max_difference_percent:.3f}%"
        )

        # ====================================================================
        # 14. RIVER SCORE / DISTANCE CONSISTENCY
        # ========================================================================

        print_header(
            "12. RIVER SCORE / DISTANCE CONSISTENCY"
        )

        # Because the river score was designed as an inverse distance
        # relationship, a strong negative rank relationship is expected.

        distance_order = np.argsort(
            common_distance
        )

        score_order = np.argsort(
            common_score
        )

        # Calculate Spearman correlation using rank arrays.
        distance_ranks = np.empty_like(
            distance_order,
            dtype=np.float64,
        )

        distance_ranks[
            distance_order
        ] = np.arange(
            len(distance_order)
        )

        score_ranks = np.empty_like(
            score_order,
            dtype=np.float64,
        )

        score_ranks[
            score_order
        ] = np.arange(
            len(score_order)
        )

        distance_centered = (
            distance_ranks
            -
            np.mean(distance_ranks)
        )

        score_centered = (
            score_ranks
            -
            np.mean(score_ranks)
        )

        denominator = (
            np.sqrt(
                np.sum(
                    distance_centered ** 2
                )
                *
                np.sum(
                    score_centered ** 2
                )
            )
        )

        if denominator == 0:

            distance_score_spearman = (
                float("nan")
            )

        else:

            distance_score_spearman = float(
                np.sum(
                    distance_centered
                    *
                    score_centered
                )
                /
                denominator
            )

        print(
            "Spearman correlation:"
        )

        print(
            "Raw river distance vs "
            "standardized river score: "
            f"{distance_score_spearman:.6f}"
        )

        if (
            not np.isnan(
                distance_score_spearman
            )
            and
            distance_score_spearman < 0
        ):

            score_direction_status = (
                "CONSISTENT_WITH_INVERSE_DISTANCE_SCORING"
            )

        else:

            score_direction_status = (
                "INVESTIGATE_SCORING_DIRECTION"
            )

        print(
            "Score direction status:"
        )

        print(
            score_direction_status
        )

        # ====================================================================
        # 15. RANGE DIAGNOSTIC CONCLUSION
        # ====================================================================

        print_header(
            "13. DIAGNOSTIC CONCLUSION"
        )

        if (
            mcda_max < raw_max
            and
            score_direction_status
            == "CONSISTENT_WITH_INVERSE_DISTANCE_SCORING"
        ):

            diagnostic_status = (
                "MCDA_FOOTPRINT_RANGE_DIFFERS_FROM_FULL_RAW_RANGE"
            )

        else:

            diagnostic_status = (
                "REQUIRES_FURTHER_INVESTIGATION"
            )

        print(
            "Diagnostic status:"
        )

        print(
            diagnostic_status
        )

        print(
            "\nImportant:"
        )

        print(
            "This diagnostic does not modify the MCDA model."
        )

        print(
            "This diagnostic does not modify the "
            "classification."
        )

        # ====================================================================
        # 16. SAVE JSON
        # ====================================================================

        print_header(
            "14. SAVE DIAGNOSTIC JSON"
        )

        report = {
            "phase": "9.4",
            "analysis":
                "River Distance Range Diagnostic",

            "purpose":
                "Compare the full raw river-distance range "
                "with the range present in the common MCDA "
                "analysis footprint.",

            "project_crs":
                EXPECTED_CRS,

            "expected_dimensions": {
                "width": EXPECTED_WIDTH,
                "height": EXPECTED_HEIGHT,
            },

            "inputs": {
                "raw_distance":
                    str(
                        RAW_DISTANCE_RASTER.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                "river_score":
                    str(
                        RIVER_SCORE_RASTER.relative_to(
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

            "cell_accounting": {
                "total_cells":
                    total_cells,

                "common_valid_cells":
                    common_count,

                "common_valid_percentage":
                    float(
                        common_count
                        /
                        total_cells
                        *
                        100
                    ),
            },

            "raw_distance_statistics":
                raw_statistics,

            "mcda_footprint_distance_statistics":
                mcda_statistics,

            "river_score_statistics":
                score_statistics,

            "continuous_susceptibility_statistics":
                susceptibility_statistics,

            "class_counts":
                class_counts,

            "range_comparison": {
                "raw_maximum_m":
                    raw_max,

                "mcda_footprint_maximum_m":
                    mcda_max,

                "raw_median_m":
                    raw_median,

                "mcda_footprint_median_m":
                    mcda_median,

                "maximum_reduction_percent":
                    float(
                        max_difference_percent
                    ),
            },

            "distance_score_relationship": {
                "spearman_correlation":
                    distance_score_spearman,

                "status":
                    score_direction_status,
            },

            "diagnostic_status":
                diagnostic_status,

            "model_modified":
                False,

            "classification_modified":
                False,
        }

        with open(
            DIAGNOSTIC_JSON,
            "w",
            encoding="utf-8",
        ) as json_file:

            json.dump(
                report,
                json_file,
                indent=4,
            )

        if not DIAGNOSTIC_JSON.exists():
            raise RuntimeError(
                "Diagnostic JSON was not created."
            )

        print(
            f"Diagnostic JSON saved to:\n"
            f"{DIAGNOSTIC_JSON}"
        )

        print(
            "JSON output: PASS"
        )

    finally:

        if raw_src is not None:
            raw_src.close()

        if score_src is not None:
            score_src.close()

        if continuous_src is not None:
            continuous_src.close()

        if classified_src is not None:
            classified_src.close()

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print("\n" + "=" * 72)
    print(
        "PHASE 9.4 DISTANCE RANGE DIAGNOSTIC COMPLETED"
    )
    print("=" * 72)

    print(
        "\nRaw distance maximum:"
    )

    print(
        f"{raw_max:.6f} m"
    )

    print(
        "\nMCDA footprint distance maximum:"
    )

    print(
        f"{mcda_max:.6f} m"
    )

    print(
        "\nRaw distance median:"
    )

    print(
        f"{raw_median:.6f} m"
    )

    print(
        "\nMCDA footprint distance median:"
    )

    print(
        f"{mcda_median:.6f} m"
    )

    print(
        "\nDistance vs river-score Spearman correlation:"
    )

    print(
        f"{distance_score_spearman:.6f}"
    )

    print(
        "\nScore direction:"
    )

    print(
        score_direction_status
    )

    print(
        "\nDiagnostic status:"
    )

    print(
        diagnostic_status
    )

    print(
        "\nOutput:"
    )

    print(
        DIAGNOSTIC_JSON
    )


if __name__ == "__main__":
    main()