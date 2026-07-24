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
print(" GEOAI FLOOD RISK AGENT - ASPECT VALIDATION ")
print("=" * 60)

aspect_file = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "aspect.tif"
)

print("\nLooking for aspect raster:")
print(aspect_file)

if not aspect_file.exists():
    raise FileNotFoundError("Aspect raster not found.")

print("\n✅ Aspect raster found.")

with rasterio.open(aspect_file) as src:

    print("\nRaster opened successfully.")

    print("\n------------- Raster Information -------------")
    print(f"Filename      : {aspect_file.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    valid = band[band != src.nodata]

    print("\n------------- Aspect Statistics -------------")
    print(f"Minimum Aspect : {valid.min():.2f}°")
    print(f"Maximum Aspect : {valid.max():.2f}°")
    print(f"Mean Aspect    : {valid.mean():.2f}°")

print("\n✅ Aspect validation completed successfully.")