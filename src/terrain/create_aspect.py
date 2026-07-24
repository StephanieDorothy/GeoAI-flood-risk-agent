from pathlib import Path
import sys

# ==========================================================
# Make src importable
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np
import rasterio

from config import (
    ANALYSIS_DEM_DIR,
    ANALYSIS_DATA_DIR,
)

print("CONFIG FILE LOADED")

print("=" * 60)
print("CREATING ASPECT RASTER")
print("=" * 60)

terrain_dir = ANALYSIS_DATA_DIR / "terrain"
terrain_dir.mkdir(parents=True, exist_ok=True)

input_dem = ANALYSIS_DEM_DIR / "dem_nairobi_utm37s.tif"
output_aspect = terrain_dir / "aspect.tif"

print(f"\nInput DEM : {input_dem}")
print(f"Output    : {output_aspect}")

with rasterio.open(input_dem) as src:

    dem = src.read(1).astype("float32")

    profile = src.profile.copy()

    nodata = src.nodata

    print("\nCalculating terrain gradients...")

    dz_dy, dz_dx = np.gradient(
        dem,
        src.res[1],
        src.res[0]
    )

    aspect = np.degrees(np.arctan2(dz_dx, -dz_dy))

    aspect = np.where(aspect < 0, 90.0 - aspect, aspect)

    aspect = np.where(aspect > 360, aspect - 360, aspect)

    flat = (dz_dx == 0) & (dz_dy == 0)
    aspect[flat] = -9999

    if nodata is not None:
        aspect[dem == nodata] = -9999

    profile.update(
        dtype="float32",
        nodata=-9999,
        compress="lzw"
    )

    with rasterio.open(output_aspect, "w", **profile) as dst:
        dst.write(aspect.astype("float32"), 1)

print("\nAspect raster successfully created.")

print("\nSaved to:")
print(output_aspect)

print("\nProcessing complete.")
print("=" * 60)