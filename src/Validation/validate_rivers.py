import geopandas as gpd
from pathlib import Path
import sys

# --------------------------------------------------
# Make project root importable
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import PROCESSED_DATA_DIR

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - RIVERS VALIDATION ")
print("=" * 60)

river_path = (
    PROCESSED_DATA_DIR /
    "rivers" /
    "Nairobi_rivers.gpkg"
)

print("\nLooking for River Dataset:")
print(river_path)

if not river_path.exists():
    print("\n❌ River dataset not found.")
    exit()

print("\n✅ River dataset found.")

gdf = gpd.read_file(river_path)

print("\nDataset opened successfully.")

print("\n------------- Dataset Information -------------")
print(f"CRS           : {gdf.crs}")
print(f"Features      : {len(gdf)}")
print(f"Geometry Type : {gdf.geom_type.unique()}")
print(f"Bounds        : {gdf.total_bounds}")

print("\n------------- Attribute Fields -------------")
print(list(gdf.columns))

print("\n------------- Geometry Check -------------")
invalid = (~gdf.is_valid).sum()

print(f"Invalid Geometries : {invalid}")

if invalid == 0:
    print("✅ All geometries are valid.")
else:
    print("⚠ Invalid geometries detected.")

print("\n✅ Rivers validation completed successfully.")