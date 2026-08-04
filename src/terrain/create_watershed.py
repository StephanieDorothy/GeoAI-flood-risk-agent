"""
============================================================
GeoAI Flood Risk Agent
Terrain Derivative 7 - Watershed Delineation
============================================================

Creates a watershed raster from the Flow Direction raster
and a user-defined pour point.

Input:
    data/analysis/terrain/flow_direction.tif
    data/analysis/terrain/pour_point.shp

Output:
    data/analysis/terrain/watershed.tif

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from whitebox.whitebox_tools import WhiteboxTools
from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - WATERSHED DELINEATION ")
print("=" * 60)

terrain_dir = ANALYSIS_DATA_DIR / "terrain"

flow_direction = terrain_dir / "flow_direction.tif"
pour_point = terrain_dir / "pour_point.shp"
watershed = terrain_dir / "watershed.tif"

print(f"\nFlow Direction : {flow_direction}")
print(f"Pour Point     : {pour_point}")
print(f"Output         : {watershed}")

if not flow_direction.exists():
    raise FileNotFoundError(flow_direction)

if not pour_point.exists():
    raise FileNotFoundError(pour_point)

wbt = WhiteboxTools()
wbt.verbose = True

print("\nRunning Watershed Delineation...")

wbt.watershed(
    d8_pntr=str(flow_direction),
    pour_pts=str(pour_point),
    output=str(watershed),
    esri_pntr=True
)

print("\n✅ Watershed generated successfully.")

print("\nSaved to:")
print(watershed)

print("=" * 60)