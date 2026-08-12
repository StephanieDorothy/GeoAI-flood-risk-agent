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
> ✅ Analysis-Ready Data Complete
>
> ✅ Terrain and Hydrological Analysis Complete
>
> ✅ Flood Conditioning Factors Complete
>
> 🚧 Factor Standardization / Normalization – Next Phase
>
> ⏳ MCDA Flood Susceptibility Modelling – Planned
>
> ⏳ GeoAI Interpretation and Decision Support – Planned

---

# Project Overview

The **GeoAI Flood Risk Agent** is a modular GIS project that combines Python, geospatial data processing, terrain analysis, hydrological modelling, and Multi-Criteria Decision Analysis (MCDA) to develop a reproducible flood susceptibility modelling workflow for Nairobi County, Kenya.

The project was initiated with the goal of developing a GeoAI-powered spatial decision support system capable of analysing spatial flood-conditioning factors and eventually providing explainable flood-risk information.

The current development stage focuses on building and validating the GIS modelling pipeline that will later support the GeoAI decision-support layer.

Each stage of the workflow is implemented, validated, documented, and version-controlled before progressing to the next phase. This ensures that the project remains reproducible, modular, testable, and easy to maintain.

---

# Study Area

This project focuses on **Nairobi County, Kenya**, where rapid urbanization, changing land cover, terrain characteristics, drainage conditions, and seasonal rainfall contribute to recurring flood events.

Nairobi provides a practical study area for developing and evaluating a reproducible GIS-based flood susceptibility modelling and decision-support workflow.

---

# Project Objectives

The project aims to:

- Build a reproducible GIS workflow using Python.
- Integrate raster and vector geospatial datasets.
- Validate and prepare spatial datasets for analysis.
- Perform terrain and hydrological preprocessing.
- Generate flood conditioning factors.
- Standardize multiple spatial factors onto a comparable scale.
- Apply Multi-Criteria Decision Analysis (MCDA) for flood susceptibility modelling.
- Produce explainable flood susceptibility information.
- Develop a GeoAI-assisted spatial decision-support workflow.
- Provide reproducible and well-documented geospatial processing methods.

---

# Project Roadmap

## ✅ Phase 1 — Data Acquisition

**Status:** Completed

The following datasets were acquired for the project:

- Digital Elevation Model (DEM)
- Nairobi County Boundary
- Land Cover
- Population
- Rivers

These datasets provide the foundation for terrain analysis, hydrological modelling, flood conditioning factor generation, and exposure assessment.

---

## ✅ Phase 2 — Data Validation

**Status:** Completed

The acquired datasets were individually inspected and validated before analysis.

Validation included:

- Coordinate Reference System (CRS) verification
- Raster metadata inspection
- Raster dimensions and resolution checks
- Vector geometry validation
- NoData inspection
- Dataset integrity checks
- Spatial extent verification

Each major dataset has its own validation workflow.

---

## ✅ Phase 3 — Analysis-Ready Data

**Status:** Completed

The project datasets were prepared for spatial analysis using a common projected coordinate reference system:

**EPSG:32737 — WGS 84 / UTM Zone 37 South**

This projected CRS provides metric units suitable for:

- Distance calculations
- Terrain analysis
- Raster processing
- Spatial overlay
- Flood conditioning factor generation

The analysis-ready datasets were organized within the project data structure before downstream processing.

---

## ✅ Phase 4 — Terrain and Hydrological Analysis

**Status:** Completed

Terrain and hydrological preprocessing were implemented using Python, Rasterio, and WhiteboxTools.

Completed outputs include:

- Filled DEM
- Slope
- Aspect
- D8 Flow Direction
- Flow Accumulation
- Stream Network
- Watershed Delineation

The hydrological workflow was used to understand:

- Terrain characteristics
- Flow direction
- Flow concentration
- Drainage behaviour
- Stream development
- Contributing watershed areas

Each major processing stage included:

- Python processing script
- Validation script
- QGIS visual inspection
- Documentation
- Git version history

---

## ✅ Phase 5 — Flood Conditioning Factors

**Status:** Completed

Phase 5 transformed the validated terrain, hydrological, land-cover, river, and population datasets into modelling inputs for the flood susceptibility workflow.

The completed flood conditioning factors are:

### 1. Elevation

**Output:**

`data/analysis/flood_factors/elevation.tif`

Elevation represents the vertical position of the terrain and provides information relevant to potential water accumulation and flood susceptibility.

---

### 2. Slope

**Output:**

`data/analysis/flood_factors/slope.tif`

Slope represents terrain steepness and provides information about surface runoff behaviour and potential water accumulation.

The slope raster was prepared from the validated terrain analysis workflow rather than unnecessarily recalculating an existing validated product.

---

### 3. Distance to Rivers

**Output:**

`data/analysis/flood_factors/distance_to_rivers.tif`

Distance to rivers represents the Euclidean distance from each raster cell to the nearest mapped river feature.

Areas closer to rivers generally have greater potential exposure to river-related flooding, although distance to rivers is interpreted together with the other conditioning factors.

---

### 4. Land Cover

**Output:**

`data/analysis/flood_factors/land_cover.tif`

Land cover represents the physical characteristics of the Earth's surface.

The land-cover dataset contains categorical classes representing different surface-cover types.

The project preserves these categorical classes at the conditioning-factor stage. Their flood-susceptibility influence will be determined through an explicit reclassification methodology during the standardization stage rather than treating class identifiers as risk scores.

---

### 5. Population Exposure

**Output:**

`data/analysis/flood_factors/population.tif`

Population represents the human exposure dimension of the flood model.

The population raster is based on WorldPop gridded population estimates.

The prepared factor preserves the original population values and raster properties. Population is not treated as a direct physical measure of flood susceptibility; instead, it provides information about where larger numbers of people may potentially be affected by flood hazards.

---

## Phase 5 Validation

All five flood conditioning factors were subjected to the project's validation workflow.

Validation included:

- Raster existence checks
- CRS verification
- Raster dimensions
- Resolution verification
- Spatial extent checks
- NoData inspection
- Data type verification
- Statistical inspection where appropriate
- Spatial comparison
- QGIS visual inspection

The completed factors are now ready for the next modelling stage.

---

# Phase 6 — Factor Standardization / Normalization

**Status:** Next Phase

The five flood conditioning factors currently have different units, value ranges, and meanings.

For example:

| Factor | Data Type | Measurement / Meaning |
|---|---|---|
| Elevation | Continuous | Metres |
| Slope | Continuous | Degrees |
| Distance to Rivers | Continuous | Metres |
| Land Cover | Categorical | Surface-cover classes |
| Population | Continuous / Exposure | Estimated population |

These factors cannot be directly combined in their current form.

The next phase will therefore establish a defensible factor standardization methodology.

The standardization stage will consider:

- Factor type
- Relationship to flood susceptibility
- Direction of influence
- Value ranges
- Appropriate transformation method
- Land-cover reclassification
- Population exposure scaling
- Comparable modelling scale

A factor methodology table will be established before implementing the final normalization workflow.

The planned relationships include:

- **Elevation:** relationship to flood susceptibility to be justified
- **Slope:** generally lower slopes can favour inundation
- **Distance to Rivers:** inverse relationship
- **Land Cover:** class-dependent relationship
- **Population:** positive exposure relationship

The exact scoring methodology will be documented and justified before implementation.

---

# Phase 7 — MCDA Flood Susceptibility Model

**Status:** Planned

Once all flood conditioning factors have been standardized to a common scale, they will be combined using **Multi-Criteria Decision Analysis (MCDA)**.

Conceptually:

```text
Elevation
     ↓
Slope
     ↓
Distance to Rivers
     ↓
Land Cover
     ↓
Population
     ↓
Normalization / Standardization
     ↓
Common Modelling Scale
     ↓
Defensible Factor Weights
     ↓
MCDA Weighted Overlay
     ↓
Flood Susceptibility Surface
```

The final weights will be reviewed and documented based on the factor methodology.

Previously used experimental weights will not automatically be reused without methodological justification.

---

# Phase 8 — Flood Susceptibility Validation

**Status:** Planned

The final flood susceptibility surface will be independently validated.

Validation will examine:

- Raster properties
- Spatial patterns
- High-susceptibility areas
- Relationship to rivers
- Relationship to elevation
- Relationship to slope
- Relationship to land cover
- Relationship to population exposure
- Spatial consistency
- Comparison with available reference information where appropriate

The purpose is to ensure that the final map is analytically defensible rather than simply visually attractive.

---

# Phase 9 — GeoAI Interpretation

**Status:** Planned

After the GIS flood susceptibility model has been validated, the project will introduce the GeoAI interpretation layer.

The GeoAI component will be designed to interpret the spatial outputs and explain:

- Where flood susceptibility is high
- Which factors contribute to the susceptibility
- How different spatial conditions influence the result
- Where exposed populations are concentrated
- What spatial evidence supports a particular risk interpretation

The objective is to move from a static flood map toward an **explainable spatial decision-support system**.

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
│       ├── population/
│       └── flood_factors/
│
├── src/
│   ├── terrain/
│   ├── validation/
│   ├── flood_factors/
│   └── ...
│
├── Docs/
│
├── outputs/
│
├── requirements.txt
│
└── README.md
```

The project separates hydrological terrain products from flood-model inputs.

```text
data/analysis/terrain/
        ↓
Terrain and hydrological products

data/analysis/flood_factors/
        ↓
Flood susceptibility modelling inputs
```

This separation keeps the modelling architecture modular and makes the later normalization and MCDA stages easier to maintain.

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
- Reproducible dependency configuration maintained through `requirements.txt`

---

# Development Workflow

Every major processing stage follows the same engineering workflow:

```text
Concept
    ↓
Understand the methodology
    ↓
Implementation
    ↓
Run
    ↓
Python Validation
    ↓
QGIS Verification
    ↓
Documentation
    ↓
Git Status Check
    ↓
Git Commit
    ↓
Git Push
```

This workflow ensures that each project stage is:

- Reproducible
- Testable
- Documented
- Version-controlled
- Easy to troubleshoot
- Easy to explain to other GIS professionals

---

# Data and Reproducibility Policy

The repository tracks reproducible project artifacts rather than large geospatial datasets.

Tracked project artifacts include:

- Python source code
- Validation scripts
- Documentation
- Configuration files
- Project structure
- README
- Git history
- Reproducible processing workflows

Large raster and vector datasets, generated outputs, temporary files, and virtual-environment files are excluded from version control where appropriate.

This keeps the GitHub repository lightweight while preserving the complete methodology required to reproduce the workflow.

---

# Current Capabilities

The repository currently includes:

- Reproducible GIS data preparation
- Raster and vector validation workflows
- CRS verification and spatial preparation
- Terrain preprocessing
- Slope and aspect analysis
- Hydrological analysis using WhiteboxTools
- D8 flow direction analysis
- Flow accumulation analysis
- Stream network extraction
- Watershed delineation
- Flood conditioning factor preparation
- Distance-to-river analysis
- Land-cover factor preparation
- Population exposure factor preparation
- Automated raster validation
- QGIS-based visual verification
- Modular Python project architecture
- Documentation and Git-based version control

---

# Current Outputs

The completed project workflow currently produces:

### Terrain and Hydrological Products

- Filled Digital Elevation Model (DEM)
- Slope raster
- Aspect raster
- D8 Flow Direction raster
- Flow Accumulation raster
- Stream Network raster
- Watershed raster

### Flood Conditioning Factors

- Elevation factor
- Slope factor
- Distance to Rivers factor
- Land Cover factor
- Population Exposure factor

### Validation

The project contains validation workflows for the major terrain, hydrological, analysis-ready, and flood-conditioning-factor datasets.

---

# Getting Started

Clone the repository using Git.

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

The project should then be run from the repository root so that the configured relative project paths resolve correctly.

---

# Future Work

The next major development stage is **Factor Standardization / Normalization**.

Planned developments include:

- Establishing the factor methodology table
- Defining the relationship of each factor to flood susceptibility
- Standardizing continuous factors
- Reclassifying land-cover classes
- Standardizing population exposure
- Creating the normalization module
- Validating standardized factors
- Applying defensible MCDA weights
- Generating the flood susceptibility surface
- Validating the final susceptibility model
- Developing GeoAI-assisted spatial interpretation
- Producing explainable flood-risk information
- Developing an interactive decision-support interface
- Preparing final professional visualizations and portfolio documentation

---

# Author

**Dorothy Stephanie**

GIS | Remote Sensing | Spatial Data Science | Python for Geospatial Analysis

GitHub: StephanieDorothy

---

# License

This project is licensed for educational and portfolio purposes.