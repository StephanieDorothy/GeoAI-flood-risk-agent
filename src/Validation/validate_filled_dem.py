"""
============================================================
GeoAI Flood Risk Agent
Validation Script - Filled DEM
============================================================

Validates the hydrologically conditioned DEM generated using
WhiteboxTools Fill Depressions.

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

# ==========================================================
# Make src importable
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import rasterio
import numpy as np

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - FILLED DEM VALIDATION ")
print("=" * 60)

filled_dem = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "filled_dem.tif"
)

print("\nLooking for Filled DEM:")
print(filled_dem)

if not filled_dem.exists():
    raise FileNotFoundError("Filled DEM not found.")

print("\n✅ Filled DEM found.")

with rasterio.open(filled_dem) as src:

    print("\nRaster opened successfully.")

    print("\n------------- Raster Information -------------")
    print(f"Filename      : {filled_dem.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    valid = band[band != src.nodata]

    print("\n------------- Elevation Statistics -------------")
    print(f"Minimum Elevation : {valid.min():.2f} m")
    print(f"Maximum Elevation : {valid.max():.2f} m")
    print(f"Mean Elevation    : {valid.mean():.2f} m")

print("\n✅ Filled DEM validation completed successfully.")