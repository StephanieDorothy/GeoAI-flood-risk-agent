"""
GeoAI Flood Risk Decision Agent
--------------------------------
Phase 7 — Spatial Alignment

Script:
    inspect_standardized_rasters.py

Purpose:
    Inspect and compare the spatial metadata of the five standardized
    flood-conditioning factors before spatial alignment.

IMPORTANT:
    This script is READ-ONLY.

    It does NOT:
        - reproject rasters
        - resample rasters
        - modify raster values
        - change CRS
        - create aligned rasters

The results will be used to determine:
    1. Whether the rasters share the same CRS
    2. Which rasters share the same resolution
    3. Which rasters share the same dimensions
    4. Whether their spatial extents match
    5. Whether their raster transforms match
    6. Which raster/grid should potentially become the reference grid
       for MCDA preparation

Validated rasters:
    - Elevation score
    - Slope score
    - Distance to rivers score
    - Population score
    - Land cover score

Project workflow:
    Phase 6
        ↓
    Standardized factors
        ↓
    Python validation
        ↓
    QGIS verification
        ↓
    Phase 7
        ↓
    Spatial alignment inspection
        ↓
    Reference-grid decision
        ↓
    Resampling strategy
        ↓
    Alignment implementation
        ↓
    Alignment validation
        ↓
    QGIS verification
        ↓
    MCDA

Author:
    Dorothy Stephanie
"""

from pathlib import Path

import rasterio


# ============================================================================
# PROJECT PATHS
# ============================================================================

# Project root:
# C:\Users\HP\Documents\GeoAI-flood-risk-agent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Standardized raster directory
STANDARDIZED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "standardized"
)


# ============================================================================
# STANDARDIZED RASTERS
# ============================================================================

RASTERS = {
    "Elevation": "elevation_score.tif",
    "Slope": "slope_score.tif",
    "Distance to Rivers": "distance_to_rivers_score.tif",
    "Population": "population_score.tif",
    "Land Cover": "landcover_score.tif",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section header."""

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def format_bounds(bounds) -> str:
    """Return raster bounds in a readable format."""

    return (
        f"left={bounds.left:.6f}, "
        f"bottom={bounds.bottom:.6f}, "
        f"right={bounds.right:.6f}, "
        f"top={bounds.top:.6f}"
    )


def format_transform(transform) -> str:
    """Return the affine transform in a readable format."""

    return (
        f"({transform.a:.12f}, "
        f"{transform.b:.12f}, "
        f"{transform.c:.12f}, "
        f"{transform.d:.12f}, "
        f"{transform.e:.12f}, "
        f"{transform.f:.12f})"
    )


# ============================================================================
# INSPECT ONE RASTER
# ============================================================================

def inspect_raster(factor_name: str, filename: str) -> dict:
    """
    Inspect the spatial metadata of one standardized raster.

    Returns a dictionary containing the important metadata so that
    the rasters can be compared after inspection.
    """

    raster_path = STANDARDIZED_DIR / filename

    print_header(f"{factor_name.upper()}")

    print(f"File: {filename}")
    print(f"Path: {raster_path}")

    # ------------------------------------------------------------------------
    # FILE EXISTENCE
    # ------------------------------------------------------------------------

    if not raster_path.exists():
        print("\nSTATUS: FAIL")
        print("Reason: Raster file does not exist.")
        return {
            "factor": factor_name,
            "filename": filename,
            "exists": False,
        }

    print("\nFile existence: PASS")

    # ------------------------------------------------------------------------
    # OPEN RASTER READ-ONLY
    # ------------------------------------------------------------------------

    with rasterio.open(raster_path) as src:

        # --------------------------------------------------------------
        # BASIC SPATIAL METADATA
        # --------------------------------------------------------------

        crs = src.crs
        width = src.width
        height = src.height
        resolution = src.res
        bounds = src.bounds
        transform = src.transform
        nodata = src.nodata
        dtype = src.dtypes[0]
        count = src.count

        print("\n--- Raster Metadata ---")

        print(f"CRS: {crs}")
        print(f"Width: {width}")
        print(f"Height: {height}")
        print(
            f"Resolution: "
            f"{resolution[0]:.12f} x {resolution[1]:.12f}"
        )

        print(f"Bounds: {format_bounds(bounds)}")

        print(
            "Transform: "
            f"{format_transform(transform)}"
        )

        print(f"NoData: {nodata}")
        print(f"Data type: {dtype}")
        print(f"Band count: {count}")

        # --------------------------------------------------------------
        # RASTER DIMENSIONS
        # --------------------------------------------------------------

        print("\n--- Grid Information ---")

        print(
            f"Grid dimensions: "
            f"{width} columns x {height} rows"
        )

        # --------------------------------------------------------------
        # PIXEL AREA
        # --------------------------------------------------------------

        pixel_width = abs(resolution[0])
        pixel_height = abs(resolution[1])
        pixel_area = pixel_width * pixel_height

        print(
            f"Approximate pixel area: "
            f"{pixel_area:.6f} square metres"
        )

        # --------------------------------------------------------------
        # DATA RANGE
        # --------------------------------------------------------------
        #
        # We are not modifying the raster.
        # We are only reading its values to provide additional
        # context for Phase 7.
        #
        # The Phase 6 validation already established the
        # standardized 0–1 behaviour. This check simply confirms
        # what is physically present in the current files.
        # --------------------------------------------------------------

        print("\n--- Current Value Information ---")

        band = src.read(1, masked=True)

        if band.count() > 0:
            minimum = float(band.min())
            maximum = float(band.max())

            print(f"Minimum value: {minimum:.6f}")
            print(f"Maximum value: {maximum:.6f}")
            print(f"Valid cells: {band.count()}")
        else:
            minimum = None
            maximum = None

            print("No valid cells detected.")

        print("\nSTATUS: PASS")

        return {
            "factor": factor_name,
            "filename": filename,
            "exists": True,
            "crs": crs,
            "width": width,
            "height": height,
            "resolution": resolution,
            "bounds": bounds,
            "transform": transform,
            "nodata": nodata,
            "dtype": dtype,
            "count": count,
            "pixel_area": pixel_area,
            "minimum": minimum,
            "maximum": maximum,
        }


# ============================================================================
# COMPARE RASTER GRIDS
# ============================================================================

def compare_grids(results: list[dict]) -> None:
    """
    Compare spatial metadata across all successfully inspected rasters.

    This function does not make an alignment decision.

    It only reports whether the properties match.
    """

    valid_results = [
        result
        for result in results
        if result.get("exists") is True
    ]

    if len(valid_results) < 2:
        print("\nNot enough valid rasters available for comparison.")
        return

    print_header("PHASE 7 — SPATIAL GRID COMPARISON")

    # ------------------------------------------------------------------------
    # CRS
    # ------------------------------------------------------------------------

    crs_values = {
        str(result["crs"])
        for result in valid_results
    }

    print("\n1. CRS comparison")
    print("-" * 80)

    if len(crs_values) == 1:
        print("CRS consistency: PASS")
        print(f"Common CRS: {next(iter(crs_values))}")
    else:
        print("CRS consistency: FAIL")
        print("Different CRS values detected:")
        for value in sorted(crs_values):
            print(f"  - {value}")

    # ------------------------------------------------------------------------
    # RESOLUTION
    # ------------------------------------------------------------------------

    resolution_values = {
        (
            round(result["resolution"][0], 12),
            round(result["resolution"][1], 12),
        )
        for result in valid_results
    }

    print("\n2. Resolution comparison")
    print("-" * 80)

    if len(resolution_values) == 1:
        print("Resolution consistency: PASS")
        print(
            f"Common resolution: "
            f"{next(iter(resolution_values))}"
        )
    else:
        print("Resolution consistency: DIFFERENT")
        print("The rasters do not share one common resolution.")

        for result in valid_results:
            print(
                f"  {result['factor']}: "
                f"{result['resolution'][0]:.12f} x "
                f"{result['resolution'][1]:.12f}"
            )

    # ------------------------------------------------------------------------
    # DIMENSIONS
    # ------------------------------------------------------------------------

    dimension_values = {
        (
            result["width"],
            result["height"],
        )
        for result in valid_results
    }

    print("\n3. Raster dimension comparison")
    print("-" * 80)

    if len(dimension_values) == 1:
        print("Dimension consistency: PASS")

        width, height = next(iter(dimension_values))

        print(
            f"Common dimensions: "
            f"{width} columns x {height} rows"
        )
    else:
        print("Dimension consistency: DIFFERENT")

        for result in valid_results:
            print(
                f"  {result['factor']}: "
                f"{result['width']} x "
                f"{result['height']}"
            )

    # ------------------------------------------------------------------------
    # BOUNDS
    # ------------------------------------------------------------------------

    print("\n4. Spatial extent comparison")
    print("-" * 80)

    reference_bounds = valid_results[0]["bounds"]

    all_bounds_match = all(
        result["bounds"] == reference_bounds
        for result in valid_results
    )

    if all_bounds_match:
        print("Bounds consistency: PASS")
        print(
            f"Common bounds: "
            f"{format_bounds(reference_bounds)}"
        )
    else:
        print("Bounds consistency: DIFFERENT")

        for result in valid_results:
            print(
                f"  {result['factor']}: "
                f"{format_bounds(result['bounds'])}"
            )

    # ------------------------------------------------------------------------
    # TRANSFORM
    # ------------------------------------------------------------------------

    print("\n5. Raster transform comparison")
    print("-" * 80)

    reference_transform = valid_results[0]["transform"]

    all_transforms_match = all(
        result["transform"] == reference_transform
        for result in valid_results
    )

    if all_transforms_match:
        print("Transform consistency: PASS")
    else:
        print("Transform consistency: DIFFERENT")

        for result in valid_results:
            print(
                f"  {result['factor']}: "
                f"{format_transform(result['transform'])}"
            )

    # ------------------------------------------------------------------------
    # NODATA
    # ------------------------------------------------------------------------

    print("\n6. NoData comparison")
    print("-" * 80)

    for result in valid_results:
        print(
            f"  {result['factor']}: "
            f"NoData = {result['nodata']}"
        )

    # ------------------------------------------------------------------------
    # DATA TYPES
    # ------------------------------------------------------------------------

    print("\n7. Data type comparison")
    print("-" * 80)

    for result in valid_results:
        print(
            f"  {result['factor']}: "
            f"{result['dtype']}"
        )

    # ------------------------------------------------------------------------
    # FINAL INTERPRETATION
    # ------------------------------------------------------------------------

    print_header("PHASE 7 — INITIAL INTERPRETATION")

    print(
        """
The purpose of this comparison is NOT to decide the reference
grid automatically.

At this stage we are only establishing how the five standardized
rasters differ spatially.

The next decision will consider:

1. Common CRS
2. Native resolution
3. Spatial extent
4. Raster dimensions
5. Pixel alignment
6. Factor characteristics
7. Continuous versus categorical data
8. The information content of each dataset
9. The appropriate modelling scale for the flood susceptibility model

DO NOT resample or reproject any raster based only on this output.

The reference grid will be selected after we interpret these
results together.
"""
    )


# ============================================================================
# SUMMARY TABLE
# ============================================================================

def print_summary(results: list[dict]) -> None:
    """Print a concise metadata summary."""

    print_header("PHASE 7 — STANDARDIZED RASTER SUMMARY")

    print(
        f"{'Factor':<22}"
        f"{'CRS':<15}"
        f"{'Width':>8}"
        f"{'Height':>9}"
        f"{'Resolution':>20}"
    )

    print("-" * 80)

    for result in results:

        if not result.get("exists"):
            print(
                f"{result['factor']:<22}"
                f"{'FILE MISSING':<15}"
            )
            continue

        crs_text = str(result["crs"])

        # Keep CRS readable in the summary.
        if crs_text == "EPSG:32737":
            crs_text = "EPSG:32737"

        resolution_text = (
            f"{result['resolution'][0]:.4f} x "
            f"{result['resolution'][1]:.4f}"
        )

        print(
            f"{result['factor']:<22}"
            f"{crs_text:<15}"
            f"{result['width']:>8}"
            f"{result['height']:>9}"
            f"{resolution_text:>20}"
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run Phase 7 raster inspection."""

    print("\n" + "=" * 80)
    print("GEOAI FLOOD RISK DECISION AGENT")
    print("PHASE 7 — SPATIAL ALIGNMENT")
    print("STANDARDIZED RASTER METADATA INSPECTION")
    print("=" * 80)

    print(f"\nProject root:")
    print(f"  {PROJECT_ROOT}")

    print(f"\nStandardized raster directory:")
    print(f"  {STANDARDIZED_DIR}")

    print(
        """
IMPORTANT:
This is a READ-ONLY inspection.

No raster will be:
    - reprojected
    - resampled
    - modified
    - overwritten
    - aligned

We are inspecting the current files before making the
Phase 7 modelling-grid decision.
"""
    )

    # ------------------------------------------------------------------------
    # INSPECT EACH RASTER
    # ------------------------------------------------------------------------

    results = []

    for factor_name, filename in RASTERS.items():

        result = inspect_raster(
            factor_name=factor_name,
            filename=filename,
        )

        results.append(result)

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------

    print_summary(results)

    # ------------------------------------------------------------------------
    # GRID COMPARISON
    # ------------------------------------------------------------------------

    compare_grids(results)

    # ------------------------------------------------------------------------
    # FINAL STATUS
    # ------------------------------------------------------------------------

    print_header("PHASE 7 INSPECTION COMPLETE")

    missing_files = [
        result["factor"]
        for result in results
        if not result.get("exists")
    ]

    if missing_files:

        print("STATUS: INCOMPLETE")
        print("\nMissing standardized rasters:")

        for factor in missing_files:
            print(f"  - {factor}")

        print(
            "\nDo not proceed with spatial alignment until "
            "the missing files are resolved."
        )

    else:

        print("STATUS: PASS")

        print(
            """
All five standardized rasters were successfully inspected.

No raster was modified.

The next step is to interpret the metadata and determine
the appropriate reference/modelling grid for the MCDA workflow.

DO NOT create aligned rasters yet.
DO NOT start MCDA yet.
"""
        )


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()