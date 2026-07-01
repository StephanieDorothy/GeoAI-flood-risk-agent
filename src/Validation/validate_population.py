import rasterio
from pathlib import Path
import sys

# --------------------------------------------------
# Make project root importable
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import PROCESSED_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - POPULATION VALIDATION ")
print("=" * 60)

population_path = (
    PROCESSED_DATA_DIR /
    "population" /
    "Nairobi population.tif"
)

print("\nLooking for Population Raster:")
print(population_path)

if not population_path.exists():
    print("\n❌ Population raster not found.")
    exit()

print("\n✅ Population raster found.")

with rasterio.open(population_path) as src:

    print("\nRaster opened successfully.\n")

    print("------------- Raster Information -------------")
    print(f"Filename      : {population_path.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    valid_pixels = band[band != src.nodata]

    print("\n----------- Population Statistics -----------")
    print(f"Minimum Population : {valid_pixels.min():.2f}")
    print(f"Maximum Population : {valid_pixels.max():.2f}")
    print(f"Mean Population    : {valid_pixels.mean():.2f}")

print("\n✅ Population validation completed successfully.")