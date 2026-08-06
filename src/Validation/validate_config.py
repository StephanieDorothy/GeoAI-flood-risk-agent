from pathlib import Path
import sys

# --------------------------------------------------
# Make config importable
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "src"))

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
    ANALYSIS_TERRAIN_DIR,
    OUTPUTS_DIR,
    DOCS_DIR,
    SRC_DIR,
    PROJECTED_CRS
)

print("=" * 60)
print("CONFIGURATION VALIDATION")
print("=" * 60)

print(f"Project Root          : {PROJECT_ROOT}")
print(f"Data Directory        : {DATA_DIR}")
print(f"Raw Data              : {RAW_DATA_DIR}")
print(f"Processed Data        : {PROCESSED_DATA_DIR}")

print("\nAnalysis Directories")
print(f"DEM                   : {ANALYSIS_DEM_DIR}")
print(f"Land Cover            : {ANALYSIS_LANDCOVER_DIR}")
print(f"Population            : {ANALYSIS_POPULATION_DIR}")
print(f"Rivers                : {ANALYSIS_RIVERS_DIR}")
print(f"Boundaries            : {ANALYSIS_BOUNDARIES_DIR}")
print(f"Terrain               : {ANALYSIS_TERRAIN_DIR}")

print(f"\nOutputs               : {OUTPUTS_DIR}")
print(f"Documentation         : {DOCS_DIR}")
print(f"Source Code           : {SRC_DIR}")

print(f"\nProject CRS           : {PROJECTED_CRS}")

print("\n✅ Configuration validation completed successfully.")