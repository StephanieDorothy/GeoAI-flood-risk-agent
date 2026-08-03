"""
============================================================
GeoAI Flood Risk Agent
Validation Script - Stream Network
============================================================

Validates the extracted stream network raster.

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np
import rasterio

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - STREAM NETWORK VALIDATION ")
print("=" * 60)

stream_raster = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "stream_network.tif"
)

print(f"\nChecking: {stream_raster}")

if not stream_raster.exists():
    raise FileNotFoundError("Stream Network raster not found.")

print("\n✅ Stream Network raster found.")

with rasterio.open(stream_raster) as src:

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

    unique = np.unique(valid)

    print("\n------------- Stream Classes -------------")
    print(f"Unique Values : {unique}")

    if set(unique.tolist()).issubset({0, 1}):
        print("\n✅ Valid binary stream raster.")
    else:
        print("\n⚠ Unexpected values detected.")

print("\n✅ Stream Network validation completed successfully.")
print("=" * 60)