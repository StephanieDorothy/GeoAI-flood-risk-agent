"""
============================================================
GeoAI Flood Risk Agent
Fill DEM Depressions (Hydrological Conditioning)
============================================================

Creates a hydrologically conditioned DEM by filling
artificial depressions (sinks).

Input:
    data/analysis/dem/dem_nairobi_utm37s.tif

Output:
    data/analysis/terrain/filled_dem.tif

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

from config import (
    ANALYSIS_DEM_DIR,
    ANALYSIS_DATA_DIR,
)

print("=" * 60)
print("HYDROLOGICAL DEM CONDITIONING")
print("=" * 60)

# ----------------------------------------------------------
# Create terrain directory
# ----------------------------------------------------------

terrain_dir = ANALYSIS_DATA_DIR / "terrain"
terrain_dir.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# Input / Output
# ----------------------------------------------------------

input_dem = ANALYSIS_DEM_DIR / "dem_nairobi_utm37s.tif"

output_dem = terrain_dir / "filled_dem.tif"

print(f"\nInput DEM : {input_dem}")
print(f"Output DEM: {output_dem}")

# ----------------------------------------------------------
# WhiteboxTools
# ----------------------------------------------------------

wbt = WhiteboxTools()

# Optional: display progress
wbt.verbose = True

print("\nRunning Fill Depressions...")

wbt.fill_depressions(
    dem=str(input_dem),
    output=str(output_dem)
)

print("\nHydrologically conditioned DEM created successfully.")

print("\nSaved to:")
print(output_dem)

print("=" * 60)