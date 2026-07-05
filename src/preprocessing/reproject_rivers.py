from pathlib import Path
import sys

import geopandas as gpd

# ---------------------------------------------------
# Make config importable
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "src"))

from config import (
    ANALYSIS_RIVERS_DIR,
    PROJECTED_CRS
)

print("=" * 60)
print("REPROJECTING NAIROBI RIVERS")
print("=" * 60)

input_file = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rivers"
    / "Nairobi_rivers.gpkg"
)

output_file = (
    ANALYSIS_RIVERS_DIR
    / "rivers_32737.gpkg"
)

ANALYSIS_RIVERS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("\nReading rivers...")

rivers = gpd.read_file(input_file)

print("Original CRS:")
print(rivers.crs)

print("\nReprojecting...")

rivers = rivers.to_crs(PROJECTED_CRS)

print("New CRS:")
print(rivers.crs)

print("\nSaving analysis-ready dataset...")

rivers.to_file(
    output_file,
    driver="GPKG"
)

print("\nSUCCESS")
print(output_file)