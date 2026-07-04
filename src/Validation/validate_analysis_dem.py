"""
============================================================
GeoAI Flood Risk Agent
Analysis DEM Validation
============================================================

Validates the analysis-ready DEM stored in the analysis folder.

Author:
Dorothy Stephanie
============================================================
"""

from pathlib import Path
import sys

# --------------------------------------------------
# Allow importing config.py
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import ANALYSIS_DATA_DIR

import rasterio

print("=" * 60)
print(" ANALYSIS DEM VALIDATION ")
print("=" * 60)

dem_path = (
    ANALYSIS_DATA_DIR
    / "dem"
    / "dem_nairobi_utm37s.tif"
)

print(f"\nLooking for DEM:\n{dem_path}")

if not dem_path.exists():
    raise FileNotFoundError("Analysis DEM not found.")

print("\n✅ Analysis DEM found.")

with rasterio.open(dem_path) as src:

    print("\nRaster opened successfully.")

    print("\n------------- Raster Information -------------")
    print(f"Filename      : {dem_path.name}")
    print(f"CRS           : {src.crs}")
    print(f"Width         : {src.width}")
    print(f"Height        : {src.height}")
    print(f"Bands         : {src.count}")
    print(f"Resolution    : {src.res}")
    print(f"Data Type     : {src.dtypes[0]}")
    print(f"NoData Value  : {src.nodata}")

    band = src.read(1)

    valid = band[band != src.nodata]

    print("\n------------- Elevation Statistics -------------")
    print(f"Minimum Elevation : {valid.min():.2f} m")
    print(f"Maximum Elevation : {valid.max():.2f} m")
    print(f"Mean Elevation    : {valid.mean():.2f} m")

print("\n✅ Analysis DEM validation completed successfully.")