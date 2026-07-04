"""
============================================================
GeoAI Flood Risk Agent
Validation Script: Analysis Boundary
Author: Dorothy Stephanie
============================================================
"""

from pathlib import Path
import sys

# ----------------------------------------------------------
# Make project imports work
# ----------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from config import ANALYSIS_BOUNDARIES_DIR

import geopandas as gpd

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - ANALYSIS BOUNDARY VALIDATION ")
print("=" * 60)

boundary_file = ANALYSIS_BOUNDARIES_DIR / "Nairobi_boundary_32737.gpkg"

print("\nLooking for Boundary Dataset:")
print(boundary_file)

if not boundary_file.exists():
    print("\n❌ Boundary dataset not found.")
    raise FileNotFoundError(boundary_file)

print("\n✅ Boundary dataset found.")

boundary = gpd.read_file(boundary_file)

print("\n------------- Dataset Information -------------")
print(f"Features       : {len(boundary)}")
print(f"Geometry Type  : {boundary.geom_type.iloc[0]}")
print(f"CRS            : {boundary.crs}")
print(f"Bounds         : {boundary.total_bounds}")

print("\n✅ Analysis Boundary validation completed successfully.")