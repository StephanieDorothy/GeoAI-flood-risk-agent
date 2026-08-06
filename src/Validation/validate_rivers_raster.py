"""
============================================================
GeoAI Flood Risk Agent
Validation - Rivers Raster
============================================================

Validates the rasterized river network before generating
the distance-to-rivers factor.

Author: Dorothy Stephanie
"""

from pathlib import Path
import sys

import numpy as np
import rasterio

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - VALIDATE RIVERS RASTER ")
print("=" * 60)

river_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "rivers_raster.tif"
)

if not river_raster.exists():
    raise FileNotFoundError(f"Raster not found:\n{river_raster}")

with rasterio.open(river_raster) as src:

    band = src.read(1)

    unique = np.unique(band)

    print(f"\nCRS          : {src.crs}")
    print(f"Resolution   : {src.res}")
    print(f"Width        : {src.width}")
    print(f"Height       : {src.height}")
    print(f"Data Type    : {src.dtypes[0]}")
    print(f"NoData Value : {src.nodata}")

    print("\nUnique Values:")

    for value in unique:
        count = np.count_nonzero(band == value)
        print(f"Value {value}: {count:,} cells")

print("\n✅ Rivers raster validation completed successfully.")
print("=" * 60)