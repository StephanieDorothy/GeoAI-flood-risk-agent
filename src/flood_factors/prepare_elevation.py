"""
============================================================
GeoAI Flood Risk Agent
Flood Conditioning Factor 1 - Elevation
============================================================

Prepares the analysis-ready DEM as the Elevation factor
for the flood susceptibility model.

Input:
    data/analysis/terrain/filled_dem.tif

Output:
    data/analysis/flood_factors/elevation.tif

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
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
print(" GEOAI FLOOD RISK AGENT - PREPARE ELEVATION ")
print("=" * 60)

terrain_dir = ANALYSIS_DATA_DIR / "terrain"
flood_dir = ANALYSIS_DATA_DIR / "flood_factors"

flood_dir.mkdir(parents=True, exist_ok=True)

input_dem = terrain_dir / "filled_dem.tif"
output_dem = flood_dir / "elevation.tif"

print(f"\nInput DEM : {input_dem}")
print(f"Output    : {output_dem}")

if not input_dem.exists():
    raise FileNotFoundError(
        f"Filled DEM not found:\n{input_dem}"
    )

shutil.copy2(input_dem, output_dem)

print("\n✅ Elevation factor prepared successfully.")

print("\nSaved to:")
print(output_dem)

print("=" * 60)