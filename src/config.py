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
# Terrain Analysis
# -------------------------------

ANALYSIS_TERRAIN_DIR = ANALYSIS_DATA_DIR / "terrain"

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
# ==================================================
# ANALYSIS DATASETS
# ==================================================

DEM_ANALYSIS_FILE = (
    ANALYSIS_DEM_DIR / "dem_nairobi_utm37s.tif"
)

LANDCOVER_ANALYSIS_FILE = (
    ANALYSIS_LANDCOVER_DIR / "landcover_32737.tif"
)

POPULATION_ANALYSIS_FILE = (
    ANALYSIS_POPULATION_DIR / "population_32737.tif"
)

RIVERS_ANALYSIS_FILE = (
    ANALYSIS_RIVERS_DIR / "rivers_32737.gpkg"
)

BOUNDARY_ANALYSIS_FILE = (
    ANALYSIS_BOUNDARIES_DIR / "Nairobi_boundary_32737.gpkg"
)