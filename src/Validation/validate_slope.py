from pathlib import Path
import sys

import numpy as np
import rasterio

# ==========================================================
# Make config importable
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import ANALYSIS_TERRAIN_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - SLOPE VALIDATION ")
print("=" * 60)

# ==========================================================
# Locate slope raster
# ==========================================================

slope_file = ANALYSIS_TERRAIN_DIR / "slope.tif"

print("\nLooking for slope raster:")
print(slope_file)

if not slope_file.exists():
    raise FileNotFoundError(f"\nSlope raster not found:\n{slope_file}")

print("\n✅ Slope raster found.")

# ==========================================================
# Read raster
# ==========================================================

with rasterio.open(slope_file) as src:

    print("\nRaster opened successfully.")

    print("\n------------- Raster Information -------------")

    print(f"Filename      : {slope_file.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

# ==========================================================
# Ignore NoData
# ==========================================================

band = np.where(band == -9999, np.nan, band)

print("\n------------- Slope Statistics -------------")

print(f"Minimum Slope : {np.nanmin(band):.2f}°")
print(f"Maximum Slope : {np.nanmax(band):.2f}°")
print(f"Mean Slope    : {np.nanmean(band):.2f}°")

print("\n✅ Slope validation completed successfully.")