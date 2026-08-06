"""
============================================================
GeoAI Flood Risk Agent
Flood Conditioning Factor 2 - Rasterize Rivers
============================================================

Converts the validated river vector into a raster aligned
with the project DEM.

Input:
    data/analysis/rivers/rivers_32737.gpkg
    data/analysis/terrain/filled_dem.tif

Output:
    data/analysis/flood_factors/rivers_raster.tif

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

import geopandas as gpd
import rasterio
from rasterio.features import rasterize

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - RASTERIZE RIVERS ")
print("=" * 60)

# ----------------------------------------------------------
# Paths
# ----------------------------------------------------------

river_vector = (
    ANALYSIS_DATA_DIR
    / "rivers"
    / "rivers_32737.gpkg"
)

reference_dem = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "filled_dem.tif"
)

output_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "rivers_raster.tif"
)

print(f"\nRiver Vector : {river_vector}")
print(f"Reference DEM: {reference_dem}")
print(f"Output Raster: {output_raster}")

# ----------------------------------------------------------
# Check inputs
# ----------------------------------------------------------

if not river_vector.exists():
    raise FileNotFoundError(f"River dataset not found:\n{river_vector}")

if not reference_dem.exists():
    raise FileNotFoundError(f"Reference DEM not found:\n{reference_dem}")

# ----------------------------------------------------------
# Read river data
# ----------------------------------------------------------

print("\nReading river dataset...")

rivers = gpd.read_file(river_vector)

print(f"River Features : {len(rivers)}")

# ----------------------------------------------------------
# Rasterize using DEM geometry
# ----------------------------------------------------------

with rasterio.open(reference_dem) as dem:

    metadata = dem.meta.copy()

    river_raster = rasterize(
        ((geom, 1) for geom in rivers.geometry),
        out_shape=(dem.height, dem.width),
        transform=dem.transform,
        fill=0,
        default_value=1,
        dtype="uint8"
    )

    metadata.update(
        driver="GTiff",
        dtype="uint8",
        count=1,
        nodata=255,
        compress="lzw"
    )

# ----------------------------------------------------------
# Save raster
# ----------------------------------------------------------

print("\nWriting raster...")

with rasterio.open(output_raster, "w", **metadata) as dst:
    dst.write(river_raster, 1)

print("\n✅ Rivers rasterized successfully.")

print("\nSaved to:")
print(output_raster)

print("=" * 60)