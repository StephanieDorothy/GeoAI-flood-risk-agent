"""
============================================================
GeoAI Flood Risk Agent
Prepare Flood Factor - Land Cover
============================================================

Prepares the analysis-ready land cover raster for use as a
flood conditioning factor.

The original land-cover classes are preserved. Reclassification
into flood susceptibility scores will be performed separately
after the dataset has been validated.

Author: Dorothy Stephanie
"""

from pathlib import Path
import shutil
import sys


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import ANALYSIS_DATA_DIR


print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - PREPARE LAND COVER ")
print("=" * 60)


# ------------------------------------------------------------
# Input and Output Paths
# ------------------------------------------------------------

input_raster = (
    ANALYSIS_DATA_DIR
    / "landcover"
    / "landcover_32737.tif"
)

output_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "landcover.tif"
)


print(f"\nInput Land Cover : {input_raster}")
print(f"Output           : {output_raster}")


# ------------------------------------------------------------
# Check Input
# ------------------------------------------------------------

if not input_raster.exists():
    raise FileNotFoundError(
        f"\nLand-cover raster not found:\n{input_raster}"
    )


# ------------------------------------------------------------
# Create Output Directory
# ------------------------------------------------------------

output_raster.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# Prepare Land Cover
# ------------------------------------------------------------

print("\nPreparing land-cover flood factor...")

shutil.copy2(
    input_raster,
    output_raster
)


# ------------------------------------------------------------
# Completion
# ------------------------------------------------------------

print("\n✅ Land Cover flood factor prepared successfully.")

print("\nSaved to:")
print(output_raster)

print("=" * 60)