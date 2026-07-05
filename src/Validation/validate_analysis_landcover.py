"""
============================================================
GeoAI Flood Risk Agent
Validation Script: Analysis Land Cover
Author: Dorothy Stephanie
============================================================
"""

from pathlib import Path
import sys

# ----------------------------------------------------------
# Make project imports work
# ----------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import ANALYSIS_LANDCOVER_DIR

import rasterio
import numpy as np

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - ANALYSIS LAND COVER VALIDATION ")
print("=" * 60)

landcover_file = ANALYSIS_LANDCOVER_DIR / "landcover_32737.tif"

print("\nLooking for Analysis Land Cover:")
print(landcover_file)

if not landcover_file.exists():
    print("\n❌ Land Cover not found.")
    raise FileNotFoundError(landcover_file)

print("\n✅ Land Cover found.")

with rasterio.open(landcover_file) as src:

    print("\n------------- Raster Information -------------")
    print(f"Filename      : {landcover_file.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    if src.nodata is not None:
        valid = band[band != src.nodata]
    else:
        valid = band

    classes = np.unique(valid)

    print("\n----------- Land Cover Classes -----------")
    print(f"Minimum Class : {valid.min()}")
    print(f"Maximum Class : {valid.max()}")
    print(f"Unique Classes: {classes}")

print("\n✅ Analysis Land Cover validation completed successfully.")