"""
============================================================
GeoAI Flood Risk Agent
Prepare Flood Factor - Population / Exposure
============================================================

Prepares the validated population raster for use as a
flood conditioning and exposure factor.

The original population values are preserved. No population
normalization or flood-risk scoring is performed at this stage.

Normalization and MCDA scoring will be handled later as part
of the factor standardization workflow.

Author: Dorothy Stephanie
============================================================
"""

from pathlib import Path
import shutil
import sys


# ------------------------------------------------------------
# Make project imports work
# ------------------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from config import ANALYSIS_DATA_DIR


# ------------------------------------------------------------
# Input and Output Paths
# ------------------------------------------------------------

input_raster = (
    ANALYSIS_DATA_DIR
    / "population"
    / "population_32737.tif"
)

output_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "population.tif"
)


# ------------------------------------------------------------
# Display Information
# ------------------------------------------------------------

print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - PREPARE POPULATION ")
print("=" * 60)

print("\nInput Population Raster:")
print(input_raster)

print("\nOutput Flood Factor:")
print(output_raster)


# ------------------------------------------------------------
# Check Input Raster
# ------------------------------------------------------------

if not input_raster.exists():
    raise FileNotFoundError(
        f"\nPopulation raster not found:\n{input_raster}"
    )


print("\n✅ Population raster found.")


# ------------------------------------------------------------
# Create Output Directory
# ------------------------------------------------------------

output_raster.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# Prepare Population Flood Factor
# ------------------------------------------------------------

print("\nPreparing population exposure flood factor...")

shutil.copy2(
    input_raster,
    output_raster
)


# ------------------------------------------------------------
# Completion Message
# ------------------------------------------------------------

print("\n✅ Population exposure factor prepared successfully.")

print("\nSaved to:")
print(output_raster)

print("\nImportant:")
print("Original population values have been preserved.")
print("No normalization or flood-risk scoring was applied.")

print("\nNext stage:")
print("Python validation of the prepared population factor.")

print("=" * 60)