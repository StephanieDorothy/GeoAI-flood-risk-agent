"""
============================================================
GeoAI Flood Risk Agent
Terrain Derivative 6 - Stream Network Extraction
============================================================

Extracts a stream network from the Flow Accumulation raster
using WhiteboxTools.

Input:
    data/analysis/terrain/flow_accumulation.tif

Output:
    data/analysis/terrain/stream_network.tif

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
print(" GEOAI FLOOD RISK AGENT - STREAM NETWORK EXTRACTION ")
print("=" * 60)

terrain_dir = ANALYSIS_DATA_DIR / "terrain"
terrain_dir.mkdir(parents=True, exist_ok=True)

input_accumulation = terrain_dir / "flow_accumulation.tif"
output_streams = terrain_dir / "stream_network.tif"

print(f"\nInput Flow Accumulation : {input_accumulation}")
print(f"Output Stream Network   : {output_streams}")

if not input_accumulation.exists():
    raise FileNotFoundError(
        f"Flow Accumulation raster not found:\n{input_accumulation}"
    )

wbt = WhiteboxTools()
wbt.verbose = True

STREAM_THRESHOLD = 1000

print(f"\nUsing stream threshold: {STREAM_THRESHOLD}")

wbt.extract_streams(
    flow_accum=str(input_accumulation),
    output=str(output_streams),
    threshold=STREAM_THRESHOLD
)

print("\n✅ Stream network extracted successfully.")
print(f"\nSaved to:\n{output_streams}")
print("=" * 60)