"""
============================================================
GeoAI Flood Risk Agent
Dataset: Land Cover
Purpose: Reproject land cover into the project analysis CRS
Author: Dorothy Stephanie
============================================================
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import (
    PROCESSED_DATA_DIR,
    ANALYSIS_LANDCOVER_DIR,
    PROJECTED_CRS
)

import rasterio
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling
)

# ----------------------------------------------------------
# Input / Output
# ----------------------------------------------------------

input_file = (
    PROCESSED_DATA_DIR /
    "Landcover" /
    "Nairobi Landcover.tif"
)

output_file = (
    ANALYSIS_LANDCOVER_DIR /
    "landcover_32737.tif"
)

ANALYSIS_LANDCOVER_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("REPROJECTING LAND COVER")
print("=" * 60)

with rasterio.open(input_file) as src:

    transform, width, height = calculate_default_transform(
        src.crs,
        PROJECTED_CRS,
        src.width,
        src.height,
        *src.bounds
    )

    metadata = src.meta.copy()

    metadata.update({
        "crs": PROJECTED_CRS,
        "transform": transform,
        "width": width,
        "height": height
    })

    with rasterio.open(output_file, "w", **metadata) as dst:

        reproject(
            source=rasterio.band(src, 1),
            destination=rasterio.band(dst, 1),
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=PROJECTED_CRS,
            resampling=Resampling.nearest
        )

print("\n✅ Land Cover successfully reprojected.")

print(output_file)