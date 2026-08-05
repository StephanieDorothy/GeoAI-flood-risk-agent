"""
============================================================
GeoAI Flood Risk Agent
Validation Script - Elevation Factor
============================================================

Validates the prepared elevation raster used in the
Flood Susceptibility Model.

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import rasterio

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - ELEVATION VALIDATION ")
print("=" * 60)

elevation = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "elevation.tif"
)

print(f"\nChecking: {elevation}")

if not elevation.exists():
    raise FileNotFoundError("Elevation raster not found.")

print("\n✅ Elevation raster found.")

with rasterio.open(elevation) as src:

    band = src.read(1)

    if src.nodata is not None:
        valid = band[band != src.nodata]
    else:
        valid = band.flatten()

    print("\n------------- Raster Information -------------")
    print(f"CRS          : {src.crs}")
    print(f"Width        : {src.width}")
    print(f"Height       : {src.height}")
    print(f"Resolution   : {src.res}")
    print(f"Data Type    : {src.dtypes[0]}")
    print(f"NoData Value : {src.nodata}")

    print("\n------------- Statistics -------------")
    print(f"Minimum      : {valid.min():.2f}")
    print(f"Maximum      : {valid.max():.2f}")
    print(f"Mean         : {valid.mean():.2f}")

print("\n✅ Elevation validation completed successfully.")
print("=" * 60)