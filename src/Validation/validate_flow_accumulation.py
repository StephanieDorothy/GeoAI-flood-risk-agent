"""
============================================================
GeoAI Flood Risk Agent
Validation Script - Flow Accumulation
============================================================

Validates the Flow Accumulation raster generated using
WhiteboxTools.

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
import numpy as np

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - FLOW ACCUMULATION VALIDATION ")
print("=" * 60)

flow_acc = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "flow_accumulation.tif"
)

print(f"\nChecking: {flow_acc}")

if not flow_acc.exists():
    raise FileNotFoundError("Flow Accumulation raster not found.")

print("\n✅ Raster found.")

with rasterio.open(flow_acc) as src:

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

    if np.any(valid < 0):
        print("\n⚠ Negative values detected.")
    else:
        print("\n✅ All accumulation values are valid.")

print("\n✅ Flow Accumulation validation completed successfully.")
print("=" * 60)