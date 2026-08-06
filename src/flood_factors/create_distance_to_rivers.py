"""
============================================================
GeoAI Flood Risk Agent
Flood Conditioning Factor 2 - Distance to Rivers
============================================================

Generates a Euclidean distance raster from the rasterized
river network.

Input:
    data/analysis/flood_factors/rivers_raster.tif

Output:
    data/analysis/flood_factors/distance_to_rivers.tif

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

from whitebox.whitebox_tools import WhiteboxTools

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - DISTANCE TO RIVERS ")
print("=" * 60)

input_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "rivers_raster.tif"
)

output_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "distance_to_rivers.tif"
)

print(f"\nInput Raster : {input_raster}")
print(f"Output Raster: {output_raster}")

if not input_raster.exists():
    raise FileNotFoundError(f"Input raster not found:\n{input_raster}")

wbt = WhiteboxTools()

print("\nRunning Euclidean Distance...")

wbt.euclidean_distance(
    i=str(input_raster),
    output=str(output_raster)
)

print("\n✅ Distance to Rivers raster created successfully.")

print("\nSaved to:")
print(output_raster)

print("=" * 60)