"""
============================================================
GeoAI Flood Risk Agent
Configuration Validation Script
============================================================
"""

from pathlib import Path
import sys

# ------------------------------------------------------------
# Add src directory to Python path
# ------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()

SRC_DIR = CURRENT_FILE.parents[1]

sys.path.append(str(SRC_DIR))

# ------------------------------------------------------------
# Import configuration
# ------------------------------------------------------------

from config import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    ANALYSIS_DATA_DIR,
    ANALYSIS_DEM_DIR,
    ANALYSIS_LANDCOVER_DIR,
    ANALYSIS_POPULATION_DIR,
    ANALYSIS_RIVERS_DIR,
    ANALYSIS_BOUNDARIES_DIR,
    OUTPUTS_DIR,
    DOCS_DIR,
    SRC_DIR,
)


def check_directory(directory):
    """Checks whether a directory exists."""

    if directory.exists():
        print(f"✅ {directory}")
    else:
        print(f"❌ {directory} (Missing)")


print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - CONFIGURATION VALIDATION ")
print("=" * 60)

print("\nProject Root")
check_directory(PROJECT_ROOT)

print("\nData")
check_directory(DATA_DIR)

print("\nRaw Data")
check_directory(RAW_DATA_DIR)

print("\nProcessed Data")
check_directory(PROCESSED_DATA_DIR)

print("\nAnalysis Data")
check_directory(ANALYSIS_DATA_DIR)

print("\nAnalysis Subdirectories")
check_directory(ANALYSIS_DEM_DIR)
check_directory(ANALYSIS_LANDCOVER_DIR)
check_directory(ANALYSIS_POPULATION_DIR)
check_directory(ANALYSIS_RIVERS_DIR)
check_directory(ANALYSIS_BOUNDARIES_DIR)

print("\nOutputs")
check_directory(OUTPUTS_DIR)

print("\nDocumentation")
check_directory(DOCS_DIR)

print("\nSource Code")
check_directory(SRC_DIR)

print("\n✅ Configuration validation completed successfully.")