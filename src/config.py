from pathlib import Path

# ==================================================
# PROJECT ROOT
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

print("CONFIG FILE LOADED")

# ==================================================
# DATA DIRECTORIES
# ==================================================

DATA_DIR = PROJECT_ROOT / "data"

# -------------------------------
# Raw Data
# -------------------------------

RAW_DATA_DIR = DATA_DIR / "raw"

# -------------------------------
# Processed Data
# -------------------------------

PROCESSED_DATA_DIR = DATA_DIR / "processed"

# -------------------------------
# Analysis-Ready Data
# -------------------------------

ANALYSIS_DATA_DIR = DATA_DIR / "analysis"

ANALYSIS_DEM_DIR = ANALYSIS_DATA_DIR / "dem"
ANALYSIS_LANDCOVER_DIR = ANALYSIS_DATA_DIR / "landcover"
ANALYSIS_POPULATION_DIR = ANALYSIS_DATA_DIR / "population"
ANALYSIS_RIVERS_DIR = ANALYSIS_DATA_DIR / "rivers"
ANALYSIS_BOUNDARIES_DIR = ANALYSIS_DATA_DIR / "boundaries"

# -------------------------------
# Outputs
# -------------------------------

OUTPUTS_DIR = DATA_DIR / "outputs"

# ==================================================
# DOCUMENTATION
# ==================================================

DOCS_DIR = PROJECT_ROOT / "Docs"

# ==================================================
# SOURCE CODE
# ==================================================

SRC_DIR = PROJECT_ROOT / "src"

# ==================================================
# PROJECT COORDINATE REFERENCE SYSTEMS (CRS)
# ==================================================

# Original geographic CRS used by downloaded datasets
GEOGRAPHIC_CRS = "EPSG:4326"

# Official analysis CRS for the GeoAI Flood Risk Agent
PROJECTED_CRS = "EPSG:32737"