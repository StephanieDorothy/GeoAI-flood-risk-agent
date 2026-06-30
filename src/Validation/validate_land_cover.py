import sys
from pathlib import Path

import rasterio
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import PROCESSED_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - LAND COVER VALIDATION ")
print("=" * 60)

landcover_path = (
    PROCESSED_DATA_DIR
    / "Landcover"
    / "Nairobi Landcover.tif"
)

print("\nLooking for Land Cover Raster:")
print(landcover_path)

if not landcover_path.exists():
    raise FileNotFoundError("Land cover raster not found.")

print("\n✅ Land cover file found.")

with rasterio.open(landcover_path) as src:

    print("\nRaster opened successfully.")

    print("\n------------- Raster Information -------------")

    print(f"Filename       : {landcover_path.name}")
    print(f"Coordinate CRS : {src.crs}")
    print(f"Width          : {src.width}")
    print(f"Height         : {src.height}")
    print(f"Bands          : {src.count}")
    print(f"Resolution     : {src.res}")
    print(f"Data Type      : {src.dtypes[0]}")
    print(f"NoData Value   : {src.nodata}")

    band = src.read(1)

    valid_pixels = band[band != src.nodata]

    print("\n---------- Land Cover Statistics ----------")

    print(f"Minimum Class : {valid_pixels.min()}")
    print(f"Maximum Class : {valid_pixels.max()}")

    unique = np.unique(valid_pixels)

    print(f"Unique Classes : {unique}")

print("\n✅ Land Cover validation completed successfully.")