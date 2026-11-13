import rasterio
from src.flood_factors.mcda_flood_susceptibility import (
    FACTOR_FILES,
    FACTOR_ORDER,
    OUTPUT_FILE,
)

files = [(name, FACTOR_FILES[name]) for name in FACTOR_ORDER]
files.append(("susceptibility", OUTPUT_FILE))

for name, path in files:
    with rasterio.open(path) as src:
        valid_pixels = int(src.read_masks(1).astype(bool).sum())

        print(f"\n--- {name.upper()} ---")
        print(f"Path: {path}")
        print(f"CRS: {src.crs}")
        print(f"Dimensions: {src.width} x {src.height}")
        print(f"Resolution: {src.res}")
        print(f"Bounds: {src.bounds}")
        print(f"Data type: {src.dtypes[0]}")
        print(f"NoData: {src.nodata}")
        print(f"Valid pixels: {valid_pixels:,}")
        print(f"Tags: {src.tags()}")
