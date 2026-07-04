"""
============================================================
GeoAI Flood Risk Agent
Dataset: Nairobi County Boundary
Purpose: Reproject boundary to the project analysis CRS
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

from config import (
    PROCESSED_DATA_DIR,
    ANALYSIS_DATA_DIR,
    PROJECTED_CRS
)

import geopandas as gpd

# ----------------------------------------------------------
# Input and Output
# ----------------------------------------------------------

input_file = (
    PROCESSED_DATA_DIR /
    "boundaries" /
    "Nairobi_county_boundary.gpkg"
)

output_folder = ANALYSIS_DATA_DIR / "boundaries"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "Nairobi_boundary_32737.gpkg"

# ----------------------------------------------------------
# Load Dataset
# ----------------------------------------------------------

print("=" * 60)
print("REPROJECTING NAIROBI COUNTY BOUNDARY")
print("=" * 60)

boundary = gpd.read_file(input_file)

print(f"\nOriginal CRS: {boundary.crs}")

# ----------------------------------------------------------
# Reproject
# ----------------------------------------------------------

boundary_projected = boundary.to_crs(PROJECTED_CRS)

print(f"Projected CRS: {boundary_projected.crs}")

# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

boundary_projected.to_file(output_file, driver="GPKG")

print("\nBoundary saved successfully.")

print("\nOutput:")

print(output_file)

print("\nDone.")