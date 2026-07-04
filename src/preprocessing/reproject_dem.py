"""
============================================================
GeoAI Flood Risk Agent
DEM Reprojection Script
============================================================

Purpose:
Reproject the processed DEM from EPSG:4326
to the project's analysis CRS:

EPSG:32737
(WGS 84 / UTM Zone 37 South)

Author:
Dorothy Stephanie

============================================================
"""

from pathlib import Path
import sys

# --------------------------------------------------
# Make project root importable
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

# --------------------------------------------------
# Imports
# --------------------------------------------------

from config import (
    PROCESSED_DATA_DIR,
    ANALYSIS_DATA_DIR,
)

import rasterio
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling,
)

# --------------------------------------------------
# Input DEM
# --------------------------------------------------

input_dem = (
    PROCESSED_DATA_DIR
    / "dem"
    / "dem_nairobi.tif"
)

# --------------------------------------------------
# Output DEM
# --------------------------------------------------

output_folder = (
    ANALYSIS_DATA_DIR
    / "dem"
)

output_folder.mkdir(
    parents=True,
    exist_ok=True
)

output_dem = (
    output_folder
    / "dem_nairobi_utm37s.tif"
)

# --------------------------------------------------
# Target CRS
# --------------------------------------------------

target_crs = "EPSG:32737"

print("=" * 60)
print(" DEM REPROJECTION ")
print("=" * 60)

print(f"\nInput DEM:\n{input_dem}")

print(f"\nOutput DEM:\n{output_dem}")

# --------------------------------------------------
# Reproject
# --------------------------------------------------

with rasterio.open(input_dem) as src:

    transform, width, height = calculate_default_transform(
        src.crs,
        target_crs,
        src.width,
        src.height,
        *src.bounds,
    )

    kwargs = src.meta.copy()

    kwargs.update(
        {
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height,
        }
    )

    with rasterio.open(output_dem, "w", **kwargs) as dst:

        for band in range(1, src.count + 1):

            reproject(
                source=rasterio.band(src, band),
                destination=rasterio.band(dst, band),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=target_crs,
                resampling=Resampling.bilinear,
            )

print("\n✅ DEM successfully reprojected.")

print(f"\nSaved to:\n{output_dem}")