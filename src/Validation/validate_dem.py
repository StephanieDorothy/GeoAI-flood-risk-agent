"""
validate_dem.py

Purpose:
--------
Validates the processed Nairobi Digital Elevation Model (DEM)
before it is used by the GeoAI Flood Risk Decision Agent.

This script verifies:
- File existence
- CRS
- Dimensions
- Resolution
- Data type
- NoData value
- Bounds
- Elevation statistics
"""

from pathlib import Path
import rasterio

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

DEM_PATH = PROCESSED_DATA_DIR / "dem" / "dem_nairobi.tif"

# --------------------------------------------------
# Validate DEM
# --------------------------------------------------

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - DEM VALIDATION ")
print("=" * 60)

print(f"\nLooking for DEM:\n{DEM_PATH}\n")

# Check if file exists
if not DEM_PATH.exists():
    print("❌ ERROR")
    print("DEM file not found.")
    exit()

print("✅ DEM file found.\n")

try:

    with rasterio.open(DEM_PATH) as src:

        print("Raster opened successfully.\n")

        print("--------------- Raster Information ---------------")

        print(f"Filename       : {DEM_PATH.name}")
        print(f"Coordinate CRS : {src.crs}")
        print(f"Width          : {src.width} pixels")
        print(f"Height         : {src.height} pixels")
        print(f"Bands          : {src.count}")
        print(f"Resolution     : {src.res}")
        print(f"Data Type      : {src.dtypes[0]}")
        print(f"NoData Value   : {src.nodata}")
        print(f"Bounds         : {src.bounds}")

        print("\n------------- Elevation Statistics --------------")

        band = src.read(1)

        print(f"Minimum Elevation : {band.min()} m")
        print(f"Maximum Elevation : {band.max()} m")

        print("\n✅ DEM validation completed successfully.")

except Exception as error:

    print("\n❌ Validation failed.")
    print(error)