from pathlib import Path
import sys

import geopandas as gpd

# ---------------------------------------------------
# Make config importable
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "src"))

from config import ANALYSIS_RIVERS_DIR

print("=" * 60)
print("ANALYSIS RIVERS VALIDATION")
print("=" * 60)

river_file = (
    ANALYSIS_RIVERS_DIR
    / "rivers_32737.gpkg"
)

print("\nLooking for:")
print(river_file)

if not river_file.exists():
    raise FileNotFoundError("Analysis rivers dataset not found.")

print("\nDataset found.")

rivers = gpd.read_file(river_file)

print("\nVector opened successfully.\n")

print("------------ River Information ------------")

print(f"CRS            : {rivers.crs}")
print(f"Features       : {len(rivers)}")
print(f"Geometry Type  : {rivers.geom_type.unique()}")
print(f"Bounds         : {rivers.total_bounds}")

print("\nColumns")

for column in rivers.columns:
    print(f" - {column}")

print("\nSUCCESS")
print("Analysis-ready rivers validated.")