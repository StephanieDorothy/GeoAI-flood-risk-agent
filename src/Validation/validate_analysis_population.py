from pathlib import Path
import sys

import rasterio
import numpy as np

# --------------------------------------------------
# Make config importable
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "src"))

from config import ANALYSIS_POPULATION_DIR

print("=" * 60)
print(" ANALYSIS POPULATION VALIDATION ")
print("=" * 60)

population_file = ANALYSIS_POPULATION_DIR / "population_32737.tif"

print()
print("Looking for:")
print(population_file)

if not population_file.exists():
    raise FileNotFoundError("Analysis-ready population raster not found.")

print("\n✅ Population raster found.")

with rasterio.open(population_file) as src:

    print("\nRaster opened successfully.\n")

    print("------------ Raster Information ------------")
    print(f"Filename      : {population_file.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    valid = band[band != src.nodata]

    print("\n-------- Population Statistics --------")
    print(f"Minimum Population : {valid.min():.2f}")
    print(f"Maximum Population : {valid.max():.2f}")
    print(f"Mean Population    : {valid.mean():.2f}")

print("\n✅ Analysis-ready population validation completed successfully.")