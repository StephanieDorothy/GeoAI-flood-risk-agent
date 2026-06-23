from pathlib import Path

# --------------------------------------------------
# Project Root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Data Directories
# --------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = DATA_DIR / "outputs"

# --------------------------------------------------
# Documentation
# --------------------------------------------------

DOCS_DIR = PROJECT_ROOT / "docs"

# --------------------------------------------------
# Source Code
# --------------------------------------------------

SRC_DIR = PROJECT_ROOT / "src"
print("CONFIG FILE LOADED")