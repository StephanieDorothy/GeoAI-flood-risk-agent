"""
============================================================
GeoAI Flood Risk Agent
Validation Script - Flow Direction (D8)
============================================================

Validates the D8 Flow Direction raster generated using
WhiteboxTools.

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
print(" GEOAI FLOOD RISK AGENT - FLOW DIRECTION VALIDATION ")
print("=" * 60)

flow_direction = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "flow_direction.tif"
)

print("\nLooking for Flow Direction raster:")
print(flow_direction)

if not flow_direction.exists():
    raise FileNotFoundError("Flow Direction raster not found.")

print("\n✅ Flow Direction raster found.")

with rasterio.open(flow_direction) as src:

    print("\nRaster opened successfully.")

    print("\n------------- Raster Information -------------")
    print(f"Filename      : {flow_direction.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    valid = band[band != src.nodata]

    print("\n------------- Flow Direction Summary -------------")

    unique_values = np.unique(valid)

    print(f"Unique Direction Values : {unique_values}")

    expected = {1, 2, 4, 8, 16, 32, 64, 128}

    unexpected = set(unique_values.tolist()) - expected

    if unexpected:
        print(f"\n⚠ Unexpected direction values detected: {sorted(unexpected)}")
    else:
        print("\n✅ All flow direction values are valid ESRI D8 codes.")

print("\n✅ Flow Direction validation completed successfully.")
print("=" * 60)