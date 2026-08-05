![Python](https://img.shields.io/badge/Python-3.12-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
# GeoAI Flood Risk Agent

A Python-based geospatial analysis project for flood susceptibility modelling in Nairobi County, Kenya.

> **Project Status (August 2026)**
>
> **Current Milestone:** Phase 5 – Flood Conditioning Factors
>
> ✅ Data Acquisition Complete
>
> ✅ Data Validation Complete
>
> ✅ Terrain and Hydrological Analysis Complete
>
> 🚧 Flood Conditioning Factors In Progress
>
> ⏳ Flood Susceptibility Modelling (Planned)

---

# Project Overview

The GeoAI Flood Risk Agent is a modular GIS project that combines Python, geospatial data processing, and hydrological analysis to build a reproducible flood susceptibility modelling workflow.

The project was initiated with the goal of developing a GeoAI-powered spatial decision support system for assessing flood risk in Nairobi County, Kenya. The current focus is on building the GIS and hydrological modelling pipeline that will later support explainable spatial decision-making.

Each stage of the workflow is implemented, validated, documented, and version-controlled before progressing to the next phase. This ensures the project remains reproducible, modular, and easy to maintain.

---

# Study Area

This project focuses on **Nairobi County, Kenya**, where rapid urbanization, changing land use, and seasonal rainfall contribute to recurring flood events.

The study area provides a practical case for developing and evaluating a reproducible GIS-based flood susceptibility modelling workflow.

---

# Project Objectives

The project aims to:

- Build a reproducible GIS workflow using Python.
- Integrate raster and vector geospatial datasets.
- Perform terrain and hydrological preprocessing.
- Generate flood conditioning factors.
- Compute flood susceptibility indicators using Multi-Criteria Decision Analysis (MCDA).
- Produce explainable flood risk information to support spatial decision-making.

---

# Project Roadmap

## ✅ Phase 1 — Data Acquisition

**Status:** Completed

Datasets acquired:

- Digital Elevation Model (DEM)
- Nairobi County Boundary
- Land Cover
- Population
- Rivers

---

## ✅ Phase 2 — Data Validation

**Status:** Completed

Validation includes:

- Coordinate Reference System (CRS) verification
- Geometry validation
- Raster inspection
- Metadata verification

Each dataset has its own validation script.

---

## ✅ Phase 3 — Analysis-Ready Data

**Status:** Completed

All datasets were successfully prepared for analysis and reprojected to:

**EPSG:32737 — WGS 84 / UTM Zone 37 South**

---

## ✅ Phase 4 — Terrain and Hydrological Analysis

**Status:** Completed

Terrain and hydrological preprocessing were implemented using Python, Rasterio, and WhiteboxTools.

Completed outputs:

- Filled DEM
- Slope
- Aspect
- D8 Flow Direction
- Flow Accumulation
- Stream Network Extraction
- Watershed Delineation

Each processing stage includes:

- Python processing script
- Validation script
- Visual inspection in QGIS
- Documentation
- Git version history

---

## 🚧 Phase 5 — Flood Conditioning Factors

**Status:** In Progress

Completed:

- Elevation factor preparation

Upcoming:

- Distance to Rivers
- Land Cover
- Population
- Factor Normalization
- MCDA Weighted Overlay

---

## ⏳ Phase 6 — Flood Susceptibility Modelling

**Status:** Planned

Future work includes:

- Factor weighting
- Flood susceptibility modelling
- Risk classification
- GeoAI-assisted decision support
- Explainable spatial outputs

---

# Repository Structure

```text
GeoAI-flood-risk-agent/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── analysis/
│       ├── terrain/
│       └── flood_factors/
│
├── src/
│   ├── terrain/
│   ├── validation/
│   ├── flood_factors/
│   └── ...
│
├── Docs/
├── outputs/
└── README.md
```

---

# Technologies

## GIS

- QGIS
- WhiteboxTools

## Python Libraries

- GeoPandas
- Rasterio
- Shapely
- NumPy
- Pandas
- PyProj
- Fiona

## Development Tools

- Python 3.12.10
- Git
- GitHub
- Visual Studio Code

---

# Development Environment

### Python Version

- Python 3.12.10

### Core Libraries

- GeoPandas 1.1.3
- Rasterio 1.5.0
- Shapely 2.1.2
- PyProj 3.7.2
- Fiona 1.10.1
- NumPy 2.5.0
- Pandas 3.0.3

### Environment Status

- Development environment verified
- Dependencies installed successfully
- Project tested within a dedicated virtual environment

---

# Development Workflow

Every processing stage follows the same workflow:

```text
Concept
    ↓
Implementation
    ↓
Validation
    ↓
QGIS Verification
    ↓
Documentation
    ↓
Git Commit
```

This workflow keeps the project reproducible, modular, and easy to extend.

---

# Current Capabilities

The repository currently includes:

- Automated terrain preprocessing
- Hydrological analysis using WhiteboxTools
- Watershed delineation
- Stream network extraction
- Automated validation scripts
- Modular Python project architecture
- Reproducible GIS processing workflow

---

# Current Outputs

The project currently produces:

- Filled Digital Elevation Model (DEM)
- Slope raster
- Aspect raster
- D8 Flow Direction raster
- Flow Accumulation raster
- Stream Network
- Watershed Boundaries
- Validation reports for each processing stage

---

# Getting Started

Clone the repository:

```bash
git clone https://github.com/StephanieDorothy/GeoAI-flood-risk-agent.git
```

Navigate to the project directory:

```bash
cd GeoAI-flood-risk-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

# Future Work

Planned developments include:

- Distance to Rivers analysis
- Land Cover analysis
- Population Exposure analysis
- Raster normalization
- MCDA weighted overlay
- Flood susceptibility mapping
- GeoAI-assisted decision support
- Interactive web dashboard

---

# Author

**Dorothy Stephanie**

GIS | Remote Sensing | Spatial Data Science | Python for Geospatial Analysis

GitHub: https://github.com/StephanieDorothy

---

# License

This project is licensed for educational and portfolio purposes.