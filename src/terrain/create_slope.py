from pathlib import Path
import sys

import numpy as np
import rasterio

# ==========================================================
# Make config importable
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import (
    DEM_ANALYSIS_FILE,
    ANALYSIS_TERRAIN_DIR,
)

print("=" * 60)
print("CREATING SLOPE RASTER")
print("=" * 60)

# ==========================================================
# Input / Output
# ==========================================================

input_dem = DEM_ANALYSIS_FILE
output_slope = ANALYSIS_TERRAIN_DIR / "slope.tif"

ANALYSIS_TERRAIN_DIR.mkdir(parents=True, exist_ok=True)

print(f"\nInput DEM : {input_dem}")
print(f"Output    : {output_slope}")

# ==========================================================
# Open DEM
# ==========================================================

with rasterio.open(input_dem) as src:

    dem = src.read(1).astype("float32")

    profile = src.profile.copy()

    transform = src.transform

    cellsize_x = transform.a
    cellsize_y = abs(transform.e)

    nodata = src.nodata

# ==========================================================
# Handle NoData
# ==========================================================

if nodata is not None:
    dem[dem == nodata] = np.nan

print("\nCalculating terrain gradients...")

# ==========================================================
# Calculate Gradients
# ==========================================================

gradient_y, gradient_x = np.gradient(
    dem,
    cellsize_y,
    cellsize_x
)

# ==========================================================
# Calculate Slope
# ==========================================================

slope = np.degrees(
    np.arctan(
        np.sqrt(
            gradient_x ** 2 +
            gradient_y ** 2
        )
    )
)

# ==========================================================
# Restore NoData
# ==========================================================

slope = np.where(np.isnan(slope), -9999, slope)

# ==========================================================
# Save Raster
# ==========================================================

profile.update(

    dtype="float32",

    nodata=-9999,

    compress="lzw"

)

with rasterio.open(output_slope, "w", **profile) as dst:

    dst.write(slope.astype("float32"), 1)

print("\nSlope raster successfully created.")

print(f"\nSaved to:\n{output_slope}")

print("\nProcessing complete.")

print("=" * 60)