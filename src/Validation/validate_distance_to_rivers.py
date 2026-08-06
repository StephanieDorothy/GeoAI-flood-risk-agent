"""
============================================================
GeoAI Flood Risk Agent
Validation - Distance to Rivers
============================================================

Validates the Distance to Rivers flood conditioning factor.

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
print(" GEOAI FLOOD RISK AGENT - DISTANCE TO RIVERS VALIDATION ")
print("=" * 60)

distance_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "distance_to_rivers.tif"
)

if not distance_raster.exists():
    raise FileNotFoundError(f"Raster not found:\n{distance_raster}")

with rasterio.open(distance_raster) as src:

    band = src.read(1)

    print(f"\nCRS          : {src.crs}")
    print(f"Resolution   : {src.res}")
    print(f"Width        : {src.width}")
    print(f"Height       : {src.height}")
    print(f"Data Type    : {src.dtypes[0]}")
    print(f"NoData Value : {src.nodata}")

    print("\n------------- Statistics -------------")

    print(f"Minimum Distance : {np.min(band):.2f} m")
    print(f"Maximum Distance : {np.max(band):.2f} m")
    print(f"Mean Distance    : {np.mean(band):.2f} m")

print("\n✅ Distance to Rivers validation completed successfully.")
print("=" * 60)