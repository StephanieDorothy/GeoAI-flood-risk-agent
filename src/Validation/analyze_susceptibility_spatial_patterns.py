"""
Phase 9.3 - Spatial Pattern Analysis of Flood Susceptibility Classes

Purpose
-------
Evaluate the spatial organization and coherence of the classified
flood susceptibility raster produced during Phase 8.

The analysis examines:

1. Class area and spatial extent
2. Neighbouring-cell relationships
3. Same-class spatial cohesion
4. Isolated cells
5. NoData distribution
6. Overall spatial coherence

This is an internal/model-consistency validation step.

It does NOT establish predictive accuracy against observed flood events.

Input
-----
data/analysis/mcda/flood_susceptibility_classified.tif

Outputs
-------
results/phase9_validation/spatial_patterns/
    susceptibility_spatial_pattern_summary.csv
    susceptibility_spatial_pattern_summary.json
    susceptibility_adjacency_matrix.csv

Coordinate Reference System
---------------------------
EPSG:32737

Classification
--------------
0 = NoData
1 = Very Low
2 = Low
3 = Moderate
4 = High
5 = Very High

Connectivity
------------
8-neighbour connectivity is used for spatial neighbourhood analysis.

Author
------
GeoAI Flood Risk Decision Agent
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


# ---------------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_RASTER = (
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
    / "spatial_patterns"
)

SUMMARY_CSV = RESULTS_DIR / "susceptibility_spatial_pattern_summary.csv"
SUMMARY_JSON = RESULTS_DIR / "susceptibility_spatial_pattern_summary.json"
ADJACENCY_CSV = RESULTS_DIR / "susceptibility_adjacency_matrix.csv"


# ---------------------------------------------------------------------------
# EXPECTED RASTER SPECIFICATION
# ---------------------------------------------------------------------------

EXPECTED_CRS = "EPSG:32737"
EXPECTED_WIDTH = 1603
EXPECTED_HEIGHT = 1019
EXPECTED_NODATA = 0

VALID_CLASSES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# ---------------------------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------------------------

def validate_input_raster(src: rasterio.io.DatasetReader) -> None:
    """
    Validate the basic spatial specification of the input raster.
    """

    print("\n1. INPUT RASTER VALIDATION")

    actual_crs = src.crs.to_string() if src.crs else None
    actual_width = src.width
    actual_height = src.height
    actual_nodata = src.nodata

    print(f"Expected CRS: {EXPECTED_CRS}")
    print(f"Actual CRS:   {actual_crs}")

    if actual_crs != EXPECTED_CRS:
        raise ValueError(
            f"CRS mismatch. Expected {EXPECTED_CRS}, got {actual_crs}."
        )

    print("CRS PASS")

    print(
        f"Expected dimensions: "
        f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT}"
    )

    print(
        f"Actual dimensions:   "
        f"{actual_width} x {actual_height}"
    )

    if (
        actual_width != EXPECTED_WIDTH
        or actual_height != EXPECTED_HEIGHT
    ):
        raise ValueError(
            "Raster dimensions do not match the expected project grid."
        )

    print("Dimensions PASS")

    print(f"Expected NoData: {EXPECTED_NODATA}")
    print(f"Actual NoData:   {actual_nodata}")

    if actual_nodata != EXPECTED_NODATA:
        raise ValueError(
            f"NoData mismatch. Expected {EXPECTED_NODATA}, "
            f"got {actual_nodata}."
        )

    print("NoData PASS")


# ---------------------------------------------------------------------------
# NEIGHBOUR ANALYSIS
# ---------------------------------------------------------------------------

def calculate_neighbour_statistics(
    array: np.ndarray,
    valid_mask: np.ndarray,
) -> tuple[dict[int, dict[str, float]], np.ndarray]:
    """
    Calculate spatial cohesion statistics using 8-neighbour relationships.

    For each valid cell, neighbouring cells are examined in the eight
    surrounding directions.

    Returns
    -------
    class_statistics:
        Dictionary containing per-class neighbourhood statistics.

    adjacency_matrix:
        Matrix counting valid neighbouring cell pairs by class.
    """

    print("\n4. SPATIAL NEIGHBOUR ANALYSIS")

    height, width = array.shape

    # -----------------------------------------------------------------------
    # Store neighbour offsets for 8-connectivity.
    # -----------------------------------------------------------------------

    neighbour_offsets = [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]

    # -----------------------------------------------------------------------
    # Adjacency matrix
    #
    # Rows = source class
    # Columns = neighbouring class
    #
    # Classes 1-5 are represented by matrix indices 0-4.
    # -----------------------------------------------------------------------

    adjacency_matrix = np.zeros((5, 5), dtype=np.int64)

    # Per-class neighbour totals.
    total_neighbours = {
        class_code: 0
        for class_code in VALID_CLASSES
    }

    same_class_neighbours = {
        class_code: 0
        for class_code in VALID_CLASSES
    }

    isolated_cells = {
        class_code: 0
        for class_code in VALID_CLASSES
    }

    # -----------------------------------------------------------------------
    # Iterate through the raster.
    #
    # The raster is approximately 1.6 million cells, so we use NumPy
    # operations for the neighbourhood calculations rather than nested
    # Python loops over every cell.
    # -----------------------------------------------------------------------

    for row_offset, col_offset in neighbour_offsets:

        source_rows = slice(
            max(0, -row_offset),
            min(height, height - row_offset),
        )

        source_cols = slice(
            max(0, -col_offset),
            min(width, width - col_offset),
        )

        neighbour_rows = slice(
            max(0, row_offset),
            min(height, height + row_offset),
        )

        neighbour_cols = slice(
            max(0, col_offset),
            min(width, width + col_offset),
        )

        source_values = array[source_rows, source_cols]
        neighbour_values = array[neighbour_rows, neighbour_cols]

        source_valid = valid_mask[source_rows, source_cols]
        neighbour_valid = valid_mask[neighbour_rows, neighbour_cols]

        pair_valid = source_valid & neighbour_valid

        if not np.any(pair_valid):
            continue

        source_values = source_values[pair_valid]
        neighbour_values = neighbour_values[pair_valid]

        # ---------------------------------------------------------------
        # Count class-to-class neighbouring relationships.
        # ---------------------------------------------------------------

        for source_class in VALID_CLASSES:
            source_class_mask = source_values == source_class

            if not np.any(source_class_mask):
                continue

            neighbour_for_source = neighbour_values[source_class_mask]

            for neighbour_class in VALID_CLASSES:
                count = np.count_nonzero(
                    neighbour_for_source == neighbour_class
                )

                if count:
                    adjacency_matrix[
                        source_class - 1,
                        neighbour_class - 1,
                    ] += count

    # -----------------------------------------------------------------------
    # Calculate per-class cohesion.
    #
    # The adjacency matrix is directed because each cell is considered as
    # the source cell. This makes the class-level neighbourhood calculations
    # straightforward.
    # -----------------------------------------------------------------------

    for class_code in VALID_CLASSES:

        row = adjacency_matrix[class_code - 1]

        total = int(row.sum())
        same = int(row[class_code - 1])

        total_neighbours[class_code] = total
        same_class_neighbours[class_code] = same

        # ---------------------------------------------------------------
        # Isolated cells
        #
        # We identify cells with zero same-class neighbours.
        # This requires calculating same-class neighbour counts per cell.
        # ---------------------------------------------------------------

        same_neighbour_count = np.zeros(
            array.shape,
            dtype=np.uint8,
        )

        class_mask = valid_mask & (array == class_code)

        for row_offset, col_offset in neighbour_offsets:

            shifted_class_mask = np.zeros_like(class_mask)

            source_rows = slice(
                max(0, -row_offset),
                min(height, height - row_offset),
            )

            source_cols = slice(
                max(0, -col_offset),
                min(width, width - col_offset),
            )

            neighbour_rows = slice(
                max(0, row_offset),
                min(height, height + row_offset),
            )

            neighbour_cols = slice(
                max(0, col_offset),
                min(width, width + col_offset),
            )

            shifted_class_mask[
                source_rows,
                source_cols,
            ] = class_mask[
                neighbour_rows,
                neighbour_cols,
            ]

            same_neighbour_count += shifted_class_mask

        isolated = class_mask & (same_neighbour_count == 0)

        isolated_cells[class_code] = int(
            np.count_nonzero(isolated)
        )

    # -----------------------------------------------------------------------
    # Convert statistics into a clean result structure.
    # -----------------------------------------------------------------------

    class_statistics = {}

    for class_code, class_name in VALID_CLASSES.items():

        total = total_neighbours[class_code]
        same = same_class_neighbours[class_code]
        isolated = isolated_cells[class_code]

        if total > 0:
            cohesion = same / total
        else:
            cohesion = np.nan

        class_statistics[class_code] = {
            "class_name": class_name,
            "neighbour_relationships": total,
            "same_class_relationships": same,
            "spatial_cohesion": float(cohesion),
            "isolated_cells": isolated,
        }

    return class_statistics, adjacency_matrix


# ---------------------------------------------------------------------------
# MAIN ANALYSIS
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Execute Phase 9.3 spatial pattern analysis.
    """

    print("=" * 72)
    print("PHASE 9.3 - SPATIAL PATTERN ANALYSIS")
    print("=" * 72)

    print(f"\nProject root:")
    print(PROJECT_ROOT)

    print("\nInput raster:")
    print(INPUT_RASTER)

    print("\nResults directory:")
    print(RESULTS_DIR)

    # -----------------------------------------------------------------------
    # Create output directory.
    # -----------------------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------------------------
    # Confirm input exists.
    # -----------------------------------------------------------------------

    if not INPUT_RASTER.exists():
        raise FileNotFoundError(
            f"Input raster not found:\n{INPUT_RASTER}"
        )

    print("\nInput raster exists: PASS")

    # -----------------------------------------------------------------------
    # Open raster.
    # -----------------------------------------------------------------------

    with rasterio.open(INPUT_RASTER) as src:

        validate_input_raster(src)

        # ---------------------------------------------------------------
        # Read classified raster.
        # ---------------------------------------------------------------

        array = src.read(1)

        transform = src.transform

        pixel_width = abs(transform.a)
        pixel_height = abs(transform.e)

        pixel_area_m2 = pixel_width * pixel_height

        print("\n2. RASTER GEOMETRY")

        print(
            f"Pixel width:  {pixel_width:.10f} m"
        )

        print(
            f"Pixel height: {pixel_height:.10f} m"
        )

        print(
            f"Pixel area:   {pixel_area_m2:.4f} m²"
        )

        # ---------------------------------------------------------------
        # Valid/NoData masks.
        # ---------------------------------------------------------------

        valid_mask = array != EXPECTED_NODATA
        nodata_mask = ~valid_mask

        total_cells = int(array.size)
        valid_cells = int(np.count_nonzero(valid_mask))
        nodata_cells = int(np.count_nonzero(nodata_mask))

        print("\n3. VALID AND NODATA CELLS")

        print(f"Total cells:  {total_cells}")
        print(f"Valid cells:  {valid_cells}")
        print(f"NoData cells: {nodata_cells}")

        if valid_cells == 0:
            raise ValueError(
                "No valid susceptibility cells were found."
            )

        if valid_cells + nodata_cells != total_cells:
            raise ValueError(
                "Valid and NoData cells do not account for the "
                "entire raster."
            )

        print("Cell accounting PASS")

        # ---------------------------------------------------------------
        # Validate class values.
        # ---------------------------------------------------------------

        observed_values = np.unique(array[valid_mask])

        print("\nCLASS VALUE VALIDATION")

        print(
            "Observed valid classes:",
            observed_values.tolist(),
        )

        observed_set = set(
            int(value)
            for value in observed_values
        )

        expected_set = set(VALID_CLASSES.keys())

        if not observed_set.issubset(expected_set):
            unexpected = sorted(
                observed_set - expected_set
            )

            raise ValueError(
                f"Unexpected class values found: {unexpected}"
            )

        print("Class values PASS")

        # ---------------------------------------------------------------
        # Class area statistics.
        # ---------------------------------------------------------------

        print("\n5. CLASS AREA ANALYSIS")

        summary_records = []

        for class_code, class_name in VALID_CLASSES.items():

            class_mask = array == class_code

            cell_count = int(
                np.count_nonzero(class_mask)
            )

            percentage = (
                cell_count / valid_cells * 100
            )

            area_m2 = (
                cell_count * pixel_area_m2
            )

            area_ha = area_m2 / 10_000

            area_km2 = area_m2 / 1_000_000

            summary_records.append(
                {
                    "class_code": class_code,
                    "class_name": class_name,
                    "cell_count": cell_count,
                    "percentage_valid_cells": percentage,
                    "area_m2": area_m2,
                    "area_hectares": area_ha,
                    "area_km2": area_km2,
                }
            )

            print(
                f"{class_code} - {class_name}: "
                f"{cell_count:,} cells | "
                f"{percentage:.3f}% | "
                f"{area_ha:.3f} ha | "
                f"{area_km2:.6f} km²"
            )

        # ---------------------------------------------------------------
        # Validate class completeness.
        # ---------------------------------------------------------------

        class_cell_sum = sum(
            record["cell_count"]
            for record in summary_records
        )

        print("\n6. CLASS COMPLETENESS")

        print(
            f"Valid cells:       {valid_cells:,}"
        )

        print(
            f"Class cell total:  {class_cell_sum:,}"
        )

        if class_cell_sum != valid_cells:
            raise ValueError(
                "Class counts do not account for all valid cells."
            )

        print("Class completeness PASS")

        # ---------------------------------------------------------------
        # NoData statistics.
        # ---------------------------------------------------------------

        nodata_percentage_total = (
            nodata_cells / total_cells * 100
        )

        nodata_area_m2 = (
            nodata_cells * pixel_area_m2
        )

        nodata_area_ha = (
            nodata_area_m2 / 10_000
        )

        nodata_area_km2 = (
            nodata_area_m2 / 1_000_000
        )

        print("\n7. NODATA ANALYSIS")

        print(
            f"NoData percentage of raster: "
            f"{nodata_percentage_total:.3f}%"
        )

        print(
            f"NoData area: "
            f"{nodata_area_ha:.3f} ha "
            f"({nodata_area_km2:.6f} km²)"
        )

        # ---------------------------------------------------------------
        # Spatial neighbourhood analysis.
        # ---------------------------------------------------------------

        class_statistics, adjacency_matrix = (
            calculate_neighbour_statistics(
                array=array,
                valid_mask=valid_mask,
            )
        )

        # ---------------------------------------------------------------
        # Add neighbourhood statistics to summary.
        # ---------------------------------------------------------------

        for record in summary_records:

            class_code = record["class_code"]

            statistics = class_statistics[class_code]

            record[
                "neighbour_relationships"
            ] = statistics[
                "neighbour_relationships"
            ]

            record[
                "same_class_relationships"
            ] = statistics[
                "same_class_relationships"
            ]

            record[
                "spatial_cohesion"
            ] = statistics[
                "spatial_cohesion"
            ]

            record[
                "isolated_cells"
            ] = statistics[
                "isolated_cells"
            ]

            if record["cell_count"] > 0:

                record[
                    "isolated_cell_percentage"
                ] = (
                    record["isolated_cells"]
                    / record["cell_count"]
                    * 100
                )

            else:

                record[
                    "isolated_cell_percentage"
                ] = 0.0

        # ---------------------------------------------------------------
        # Overall spatial cohesion.
        # ---------------------------------------------------------------

        total_neighbour_relationships = int(
            adjacency_matrix.sum()
        )

        diagonal_relationships = int(
            np.trace(adjacency_matrix)
        )

        if total_neighbour_relationships > 0:

            overall_cohesion = (
                diagonal_relationships
                / total_neighbour_relationships
            )

        else:

            overall_cohesion = np.nan

        print("\n8. SPATIAL COHESION")

        print(
            "Overall same-class neighbour ratio: "
            f"{overall_cohesion:.6f}"
        )

        for record in summary_records:

            print(
                f"{record['class_name']}: "
                f"cohesion="
                f"{record['spatial_cohesion']:.6f}, "
                f"isolated="
                f"{record['isolated_cells']:,} "
                f"("
                f"{record['isolated_cell_percentage']:.3f}%"
                f")"
            )

        # ---------------------------------------------------------------
        # Create summary dataframe.
        # ---------------------------------------------------------------

        summary_df = pd.DataFrame(summary_records)

        # ---------------------------------------------------------------
        # Save class-level summary.
        # ---------------------------------------------------------------

        summary_df.to_csv(
            SUMMARY_CSV,
            index=False,
        )

        print("\n9. SUMMARY OUTPUT")

        print(
            f"CSV saved: {SUMMARY_CSV}"
        )

        if not SUMMARY_CSV.exists():
            raise RuntimeError(
                "Summary CSV was not created."
            )

        print("CSV output PASS")

        # ---------------------------------------------------------------
        # Save adjacency matrix.
        # ---------------------------------------------------------------

        adjacency_df = pd.DataFrame(
            adjacency_matrix,
            index=[
                VALID_CLASSES[code]
                for code in VALID_CLASSES
            ],
            columns=[
                VALID_CLASSES[code]
                for code in VALID_CLASSES
            ],
        )

        adjacency_df.index.name = "source_class"

        adjacency_df.to_csv(
            ADJACENCY_CSV
        )

        print(
            f"Adjacency matrix saved: "
            f"{ADJACENCY_CSV}"
        )

        if not ADJACENCY_CSV.exists():
            raise RuntimeError(
                "Adjacency matrix CSV was not created."
            )

        print("Adjacency matrix output PASS")

        # ---------------------------------------------------------------
        # Determine interpretation status.
        #
        # This is deliberately conservative. We do not declare the model
        # "accurate". We only flag obvious structural concerns.
        # ---------------------------------------------------------------

        maximum_isolated_percentage = max(
            record["isolated_cell_percentage"]
            for record in summary_records
        )

        if maximum_isolated_percentage <= 1:
            spatial_pattern_status = "COHERENT"

        elif maximum_isolated_percentage <= 5:
            spatial_pattern_status = "MINOR_FRAGMENTATION"

        else:
            spatial_pattern_status = "INVESTIGATE_FRAGMENTATION"

        # ---------------------------------------------------------------
        # Prepare JSON report.
        # ---------------------------------------------------------------

        json_report = {
            "phase": "9.3",
            "analysis": "Spatial Pattern Analysis",
            "input_raster": str(
                INPUT_RASTER.relative_to(PROJECT_ROOT)
            ),
            "crs": EXPECTED_CRS,
            "dimensions": {
                "width": EXPECTED_WIDTH,
                "height": EXPECTED_HEIGHT,
            },
            "nodata_value": EXPECTED_NODATA,
            "total_cells": total_cells,
            "valid_cells": valid_cells,
            "nodata_cells": nodata_cells,
            "nodata_percentage_total": (
                nodata_percentage_total
            ),
            "pixel_width_m": pixel_width,
            "pixel_height_m": pixel_height,
            "pixel_area_m2": pixel_area_m2,
            "nodata_area_m2": nodata_area_m2,
            "nodata_area_hectares": nodata_area_ha,
            "nodata_area_km2": nodata_area_km2,
            "overall_spatial_cohesion": (
                float(overall_cohesion)
            ),
            "maximum_isolated_cell_percentage": (
                float(maximum_isolated_percentage)
            ),
            "spatial_pattern_status": (
                spatial_pattern_status
            ),
            "connectivity": "8-neighbour",
            "classes": summary_records,
        }

        with open(
            SUMMARY_JSON,
            "w",
            encoding="utf-8",
        ) as json_file:

            json.dump(
                json_report,
                json_file,
                indent=4,
            )

        print(
            f"JSON saved: {SUMMARY_JSON}"
        )

        if not SUMMARY_JSON.exists():
            raise RuntimeError(
                "Summary JSON was not created."
            )

        print("JSON output PASS")

    # -----------------------------------------------------------------------
    # Final report.
    # -----------------------------------------------------------------------

    print("\n" + "=" * 72)
    print("PHASE 9.3 ANALYSIS COMPLETED")
    print("=" * 72)

    print(
        f"\nSpatial pattern status: "
        f"{spatial_pattern_status}"
    )

    print(
        f"Overall spatial cohesion: "
        f"{overall_cohesion:.6f}"
    )

    print(
        f"Maximum isolated-cell percentage: "
        f"{maximum_isolated_percentage:.3f}%"
    )

    print("\nOutputs:")

    print(SUMMARY_CSV)
    print(SUMMARY_JSON)
    print(ADJACENCY_CSV)


if __name__ == "__main__":
    main()