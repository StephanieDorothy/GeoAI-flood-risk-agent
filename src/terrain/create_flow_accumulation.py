"""
============================================================
GeoAI Flood Risk Agent
Terrain Derivative 5 - Flow Accumulation
============================================================

Generates a D8 Flow Accumulation raster from the
Flow Direction raster using WhiteboxTools.

Input:
    data/analysis/terrain/flow_direction.tif

Output:
    data/analysis/terrain/flow_accumulation.tif

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
print(" GEOAI FLOOD RISK AGENT - FLOW ACCUMULATION ")
print("=" * 60)

# ----------------------------------------------------------
# Terrain directory
# ----------------------------------------------------------

terrain_dir = ANALYSIS_DATA_DIR / "terrain"
terrain_dir.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# Input / Output
# ----------------------------------------------------------

input_pointer = terrain_dir / "flow_direction.tif"
output_accumulation = terrain_dir / "flow_accumulation.tif"

print(f"\nInput Flow Direction : {input_pointer}")
print(f"Output Raster        : {output_accumulation}")

if not input_pointer.exists():
    raise FileNotFoundError(
        f"Flow Direction raster not found:\n{input_pointer}"
    )

# ----------------------------------------------------------
# WhiteboxTools
# ----------------------------------------------------------

wbt = WhiteboxTools()
wbt.verbose = True

print("\nRunning D8 Flow Accumulation...")

wbt.d8_flow_accumulation(
    i=str(input_pointer),
    output=str(output_accumulation),
    out_type="cells",
    pntr=True,
    esri_pntr=True
)

print("\n✅ Flow Accumulation raster created successfully.")

print("\nSaved to:")
print(output_accumulation)

print("=" * 60)