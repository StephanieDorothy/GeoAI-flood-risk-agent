"""
============================================================
GeoAI Flood Risk Agent
Terrain Derivative 4 - Flow Direction (D8)
============================================================

Generates a D8 Flow Direction raster from the
hydrologically conditioned DEM using WhiteboxTools.

Input:
    data/analysis/terrain/filled_dem.tif

Output:
    data/analysis/terrain/flow_direction.tif

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

# ==========================================================
# Make src importable
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from whitebox.whitebox_tools import WhiteboxTools

from config import ANALYSIS_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - FLOW DIRECTION ")
print("=" * 60)

# ----------------------------------------------------------
# Terrain directory
# ----------------------------------------------------------

terrain_dir = ANALYSIS_DATA_DIR / "terrain"
terrain_dir.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# Input / Output
# ----------------------------------------------------------

input_dem = terrain_dir / "filled_dem.tif"

output_flow = terrain_dir / "flow_direction.tif"

print(f"\nInput DEM : {input_dem}")
print(f"Output    : {output_flow}")

if not input_dem.exists():
    raise FileNotFoundError(
        f"Filled DEM not found:\n{input_dem}"
    )

# ----------------------------------------------------------
# WhiteboxTools
# ----------------------------------------------------------

wbt = WhiteboxTools()
wbt.verbose = True

print("\nRunning D8 Flow Direction...")

wbt.d8_pointer(
    dem=str(input_dem),
    output=str(output_flow),
    esri_pntr=True
)

print("\n✅ Flow Direction raster created successfully.")

print("\nSaved to:")
print(output_flow)

print("=" * 60)