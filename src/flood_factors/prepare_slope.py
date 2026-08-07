"""
============================================================
GeoAI Flood Risk Agent
Prepare Flood Factor - Slope
============================================================

Copies the validated slope raster from the terrain module
into the flood_factors directory for flood susceptibility
modelling.

Author: Dorothy Stephanie
"""

from pathlib import Path
import shutil
import sys

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - PREPARE SLOPE ")
print("=" * 60)

input_raster = (
    ANALYSIS_DATA_DIR
    / "terrain"
    / "slope.tif"
)

output_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "slope.tif"
)

if not input_raster.exists():
    raise FileNotFoundError(
        f"Slope raster not found:\n{input_raster}"
    )

output_raster.parent.mkdir(parents=True, exist_ok=True)

shutil.copy2(input_raster, output_raster)

print("\n✅ Slope factor prepared successfully.")

print("\nSaved to:")
print(output_raster)

print("=" * 60)