"""
GeoAI Flood Risk Decision Agent
--------------------------------
Phase 7 — Spatial Alignment

Script:
    align_standardized_factors.py

Purpose:
    Align the five standardized flood-conditioning factors to a
    common reference grid for subsequent MCDA processing.

Reference grid:
    elevation_score.tif

Reference properties:
    - CRS: EPSG:32737
    - Resolution: approximately 30.8655 m
    - Dimensions: 1603 x 1019
    - Extent: inherited directly from the reference raster
    - Transform: inherited directly from the reference raster

Input directory:
    data/analysis/standardized/

Output directory:
    data/analysis/aligned/

Factors:
    1. Elevation
    2. Slope
    3. Distance to Rivers
    4. Population
    5. Land Cover

Alignment strategy:
    - Elevation: already on reference grid; preserve values.
    - Slope: already on reference grid; preserve values.
    - Distance to Rivers: already on reference grid; preserve values.
    - Population: resample to reference grid using bilinear interpolation.
    - Land Cover: resample to reference grid using nearest neighbour.

IMPORTANT:
    - Original standardized rasters are never overwritten.
    - All aligned outputs are written to a separate directory.
    - NoData is preserved as -9999.
    - Output rasters are stored as float32.
    - This script performs spatial alignment only.
    - MCDA weights are NOT applied here.

Workflow:
    Phase 6 standardized factors
        ↓
    Phase 7 reference-grid selection
        ↓
    This script
        ↓
    Aligned standardized factors
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
from shutil import copyfile

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

STANDARDIZED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "standardized"
)

ALIGNED_DIR = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "aligned"
)


# ============================================================================
# INPUT RASTERS
# ============================================================================

RASTERS = {
    "Elevation": "elevation_score.tif",
    "Slope": "slope_score.tif",
    "Distance to Rivers": "distance_to_rivers_score.tif",
    "Population": "population_score.tif",
    "Land Cover": "landcover_score.tif",
}


# ============================================================================
# RESAMPLING METHODS
# ============================================================================

RESAMPLING_METHODS = {
    "Population": Resampling.bilinear,
    "Land Cover": Resampling.nearest,
}


# ============================================================================
# CONSTANTS
# ============================================================================

OUTPUT_NODATA = -9999.0
OUTPUT_DTYPE = "float32"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section header."""

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_raster_grid(
    label: str,
    crs,
    width: int,
    height: int,
    resolution,
    bounds,
) -> None:
    """Print important raster-grid information."""

    print(f"\n{label}")
    print("-" * 80)

    print(f"CRS: {crs}")
    print(f"Dimensions: {width} columns x {height} rows")

    print(
        f"Resolution: "
        f"{resolution[0]:.12f} x "
        f"{resolution[1]:.12f}"
    )

    print(
        "Bounds: "
        f"left={bounds.left:.6f}, "
        f"bottom={bounds.bottom:.6f}, "
        f"right={bounds.right:.6f}, "
        f"top={bounds.top:.6f}"
    )


def ensure_input_exists(path: Path, factor_name: str) -> None:
    """
    Stop execution if an expected input raster does not exist.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"{factor_name} raster was not found:\n"
            f"{path}"
        )


# ============================================================================
# REFERENCE GRID
# ============================================================================

def get_reference_grid(reference_path: Path) -> dict:
    """
    Read and return the complete spatial grid definition
    from the reference raster.
    """

    print_header("REFERENCE GRID")

    ensure_input_exists(
        reference_path,
        "Reference elevation",
    )

    with rasterio.open(reference_path) as src:

        reference = {
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
            "bounds": src.bounds,
            "resolution": src.res,
            "nodata": src.nodata,
            "dtype": src.dtypes[0],
        }

    print_raster_grid(
        label="Reference raster: elevation_score.tif",
        crs=reference["crs"],
        width=reference["width"],
        height=reference["height"],
        resolution=reference["resolution"],
        bounds=reference["bounds"],
    )

    print(
        f"\nReference NoData: "
        f"{reference['nodata']}"
    )

    print(
        f"Reference data type: "
        f"{reference['dtype']}"
    )

    return reference


# ============================================================================
# CHECK WHETHER A RASTER ALREADY MATCHES THE REFERENCE GRID
# ============================================================================

def matches_reference_grid(
    src,
    reference: dict,
) -> bool:
    """
    Determine whether an input raster already has exactly the
    same spatial grid as the reference raster.
    """

    return (
        src.crs == reference["crs"]
        and src.transform == reference["transform"]
        and src.width == reference["width"]
        and src.height == reference["height"]
    )


# ============================================================================
# COPY AN ALREADY-ALIGNED RASTER
# ============================================================================

def copy_aligned_raster(
    source_path: Path,
    output_path: Path,
    factor_name: str,
) -> None:
    """
    Copy a raster that already matches the reference grid.

    No resampling is performed.
    """

    print_header(f"{factor_name.upper()} — ALREADY ALIGNED")

    print(f"Input:  {source_path}")
    print(f"Output: {output_path}")

    copyfile(
        source_path,
        output_path,
    )

    print("\nAction: File copied without resampling.")
    print("Spatial grid: Preserved exactly.")
    print("STATUS: PASS")


# ============================================================================
# RESAMPLE A RASTER TO THE REFERENCE GRID
# ============================================================================

def resample_to_reference(
    source_path: Path,
    output_path: Path,
    factor_name: str,
    reference: dict,
    resampling_method: Resampling,
) -> None:
    """
    Resample an input raster onto the exact reference grid.
    """

    print_header(
        f"{factor_name.upper()} — RESAMPLING"
    )

    print(f"Input:  {source_path}")
    print(f"Output: {output_path}")
    print(
        f"Resampling method: "
        f"{resampling_method.name}"
    )

    with rasterio.open(source_path) as src:

        print_raster_grid(
            label="Source grid",
            crs=src.crs,
            width=src.width,
            height=src.height,
            resolution=src.res,
            bounds=src.bounds,
        )

        # --------------------------------------------------------------------
        # Create output profile based on the reference grid.
        # --------------------------------------------------------------------

        profile = src.profile.copy()

        profile.update(
            {
                "driver": "GTiff",
                "dtype": OUTPUT_DTYPE,
                "nodata": OUTPUT_NODATA,
                "width": reference["width"],
                "height": reference["height"],
                "crs": reference["crs"],
                "transform": reference["transform"],
                "count": 1,
                "compress": "lzw",
                "predictor": 3,
            }
        )

        # --------------------------------------------------------------------
        # Allocate target array.
        # --------------------------------------------------------------------

        destination = np.full(
            (
                reference["height"],
                reference["width"],
            ),
            OUTPUT_NODATA,
            dtype=np.float32,
        )

        # --------------------------------------------------------------------
        # Perform spatial transformation/resampling.
        #
        # Even though all factors currently use EPSG:32737,
        # reproject() is used because it allows us to explicitly
        # define the exact target transform, dimensions and CRS.
        # --------------------------------------------------------------------

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=reference["transform"],
            dst_crs=reference["crs"],
            dst_nodata=OUTPUT_NODATA,
            resampling=resampling_method,
        )

    # ------------------------------------------------------------------------
    # Write aligned raster.
    # ------------------------------------------------------------------------

    with rasterio.open(
        output_path,
        "w",
        **profile,
    ) as dst:

        dst.write(
            destination,
            1,
        )

    print("\nTarget grid:")

    print_raster_grid(
        label="Reference target grid",
        crs=reference["crs"],
        width=reference["width"],
        height=reference["height"],
        resolution=reference["resolution"],
        bounds=reference["bounds"],
    )

    print("\nOutput NoData:", OUTPUT_NODATA)
    print("Output data type:", OUTPUT_DTYPE)
    print("STATUS: PASS")


# ============================================================================
# VALIDATE OUTPUT GRID IMMEDIATELY
# ============================================================================

def validate_output_grid(
    output_path: Path,
    reference: dict,
    factor_name: str,
) -> None:
    """
    Perform a basic immediate validation of the output raster.

    Full Phase 7 validation will be performed by a dedicated
    validation script later.
    """

    print_header(
        f"{factor_name.upper()} — IMMEDIATE GRID CHECK"
    )

    with rasterio.open(output_path) as src:

        checks = {
            "CRS": src.crs == reference["crs"],
            "Width": src.width == reference["width"],
            "Height": src.height == reference["height"],
            "Transform": src.transform == reference["transform"],
            "Resolution": src.res == reference["resolution"],
            "Bounds": src.bounds == reference["bounds"],
            "NoData": src.nodata == OUTPUT_NODATA,
            "Data type": src.dtypes[0] == OUTPUT_DTYPE,
        }

        for check_name, passed in checks.items():

            status = "PASS" if passed else "FAIL"

            print(
                f"{check_name:<15}: {status}"
            )

        if not all(checks.values()):
            raise RuntimeError(
                f"Immediate grid validation failed for "
                f"{factor_name}."
            )

    print("Immediate validation: PASS")


# ============================================================================
# PROCESS ONE FACTOR
# ============================================================================

def process_factor(
    factor_name: str,
    filename: str,
    reference: dict,
) -> None:
    """
    Process one standardized factor.
    """

    source_path = STANDARDIZED_DIR / filename
    output_path = ALIGNED_DIR / filename

    ensure_input_exists(
        source_path,
        factor_name,
    )

    # ------------------------------------------------------------------------
    # If this factor already matches the reference grid, preserve it.
    # ------------------------------------------------------------------------

    with rasterio.open(source_path) as src:

        already_aligned = matches_reference_grid(
            src,
            reference,
        )

    if already_aligned:

        copy_aligned_raster(
            source_path=source_path,
            output_path=output_path,
            factor_name=factor_name,
        )

    # ------------------------------------------------------------------------
    # Otherwise, resample according to the factor-specific method.
    # ------------------------------------------------------------------------

    else:

        if factor_name not in RESAMPLING_METHODS:
            raise ValueError(
                f"No resampling method has been defined for "
                f"{factor_name}."
            )

        resample_to_reference(
            source_path=source_path,
            output_path=output_path,
            factor_name=factor_name,
            reference=reference,
            resampling_method=RESAMPLING_METHODS[
                factor_name
            ],
        )

    # ------------------------------------------------------------------------
    # Immediate validation.
    # ------------------------------------------------------------------------

    validate_output_grid(
        output_path=output_path,
        reference=reference,
        factor_name=factor_name,
    )


# ============================================================================
# SUMMARY
# ============================================================================

def print_final_summary(
    reference: dict,
) -> None:
    """
    Print the final Phase 7 processing summary.
    """

    print_header(
        "PHASE 7 — ALIGNMENT PROCESSING SUMMARY"
    )

    print(
        "Reference grid:"
    )

    print(
        f"  CRS: {reference['crs']}"
    )

    print(
        f"  Resolution: "
        f"{reference['resolution'][0]:.12f} x "
        f"{reference['resolution'][1]:.12f} m"
    )

    print(
        f"  Dimensions: "
        f"{reference['width']} columns x "
        f"{reference['height']} rows"
    )

    print(
        "  Bounds: "
        f"left={reference['bounds'].left:.6f}, "
        f"bottom={reference['bounds'].bottom:.6f}, "
        f"right={reference['bounds'].right:.6f}, "
        f"top={reference['bounds'].top:.6f}"
    )

    print(
        "\nAligned output directory:"
    )

    print(
        f"  {ALIGNED_DIR}"
    )

    print(
        "\nExpected outputs:"
    )

    for filename in RASTERS.values():
        output_path = ALIGNED_DIR / filename

        status = (
            "PASS"
            if output_path.exists()
            else "MISSING"
        )

        print(
            f"  {filename:<35} {status}"
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run the complete Phase 7 spatial alignment workflow."""

    print_header(
        "GEOAI FLOOD RISK DECISION AGENT"
    )

    print(
        "PHASE 7 — SPATIAL ALIGNMENT"
    )

    print(
        "STANDARDIZED FACTOR ALIGNMENT"
    )

    print(
        "\nThis process will:"
    )

    print(
        "  1. Read the standardized factors."
    )

    print(
        "  2. Use elevation_score.tif as the reference grid."
    )

    print(
        "  3. Preserve factors already on the reference grid."
    )

    print(
        "  4. Resample population using bilinear interpolation."
    )

    print(
        "  5. Resample land cover using nearest neighbour."
    )

    print(
        "  6. Write outputs to data/analysis/aligned/."
    )

    print(
        "  7. Perform immediate grid validation."
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "  Original standardized rasters will NOT be overwritten."
    )

    print(
        "  MCDA weights will NOT be applied."
    )

    print(
        "  This script performs spatial alignment only."
    )

    # ------------------------------------------------------------------------
    # Create output directory.
    # ------------------------------------------------------------------------

    ALIGNED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"\nOutput directory ready:"
    )

    print(
        f"  {ALIGNED_DIR}"
    )

    # ------------------------------------------------------------------------
    # Reference raster.
    # ------------------------------------------------------------------------

    reference_path = (
        STANDARDIZED_DIR
        / RASTERS["Elevation"]
    )

    reference = get_reference_grid(
        reference_path
    )

    # ------------------------------------------------------------------------
    # Process all five factors.
    # ------------------------------------------------------------------------

    for factor_name, filename in RASTERS.items():

        process_factor(
            factor_name=factor_name,
            filename=filename,
            reference=reference,
        )

    # ------------------------------------------------------------------------
    # Final summary.
    # ------------------------------------------------------------------------

    print_final_summary(
        reference=reference
    )

    # ------------------------------------------------------------------------
    # Completion message.
    # ------------------------------------------------------------------------

    print_header(
        "PHASE 7 — ALIGNMENT COMPLETE"
    )

    print(
        "STATUS: PASS"
    )

    print(
        """
All five standardized factors have been processed against
the selected reference grid.

IMPORTANT:
This does NOT yet mean that Phase 7 is complete.

Next steps:
    1. Run dedicated alignment validation.
    2. Compare every aligned raster against the reference grid.
    3. Validate value ranges.
    4. Validate NoData behaviour.
    5. Confirm that alignment did not introduce invalid values.
    6. Open the aligned rasters in QGIS.
    7. Visually verify spatial overlap.
    8. Document the methodology.
    9. Update README.md.
    10. Commit and push the reproducible Phase 7 artifacts.

Do not proceed to MCDA until these validation steps pass.
"""
    )


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()