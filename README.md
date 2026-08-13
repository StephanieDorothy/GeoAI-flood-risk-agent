# GeoAI Flood Risk Agent

A Python-based geospatial analysis project for flood susceptibility modelling in Nairobi County, Kenya.

> **Project Status (August 2026)**
>
> **Current Milestone:** Phase 6 – Factor Standardization / Normalization
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
> ✅ Factor Standardization / Normalization Complete
>
> ⏳ Spatial Alignment and MCDA Preparation – Next Stage
>
> ⏳ MCDA Flood Susceptibility Modelling – Planned
>
> ⏳ GeoAI Interpretation and Decision Support – Planned

---

# Project Overview

The **GeoAI Flood Risk Agent** is a modular GIS project that combines Python, geospatial data processing, terrain analysis, hydrological modelling, factor standardization, and Multi-Criteria Decision Analysis (MCDA) to develop a reproducible flood susceptibility modelling workflow for Nairobi County, Kenya.

The project was initiated with the goal of developing a GeoAI-powered spatial decision support system capable of analysing spatial flood-conditioning factors and eventually providing explainable flood-risk information.

The current development stage has completed the preparation and standardization of the major flood-conditioning factors. The next stage will focus on spatially aligning the standardized factors to a common modelling grid before MCDA weighted overlay.

Each stage of the workflow is implemented, validated, documented, and version-controlled before progressing to the next phase. This ensures that the project remains reproducible, modular, testable, and easy to maintain.

---

# Study Area

This project focuses on **Nairobi County, Kenya**, where rapid urbanization, changing land cover, terrain characteristics, drainage conditions, and seasonal rainfall contribute to recurring flood events.

Nairobi provides a practical study area for developing and evaluating a reproducible GIS-based flood susceptibility modelling and decision-support workflow.

---

# Project Objectives

The project aims to:

* Build a reproducible GIS workflow using Python.
* Integrate raster and vector geospatial datasets.
* Validate and prepare spatial datasets for analysis.
* Perform terrain and hydrological preprocessing.
* Generate flood conditioning factors.
* Standardize multiple spatial factors onto a comparable scale.
* Align standardized factors to a common modelling grid.
* Apply Multi-Criteria Decision Analysis (MCDA) for flood susceptibility modelling.
* Produce explainable flood susceptibility information.
* Develop a GeoAI-assisted spatial decision-support workflow.
* Provide reproducible and well-documented geospatial processing methods.

---

# Project Roadmap

## ✅ Phase 1 — Data Acquisition

**Status:** Completed

The following datasets were acquired for the project:

* Digital Elevation Model (DEM)
* Nairobi County Boundary
* Land Cover
* Population
* Rivers

These datasets provide the foundation for terrain analysis, hydrological modelling, flood conditioning factor generation, and exposure assessment.

---

## ✅ Phase 2 — Data Validation

**Status:** Completed

The acquired datasets were individually inspected and validated before analysis.

Validation included:

* Coordinate Reference System (CRS) verification
* Raster metadata inspection
* Raster dimensions and resolution checks
* Vector geometry validation
* NoData inspection
* Dataset integrity checks
* Spatial extent verification

Each major dataset has its own validation workflow.

---

## ✅ Phase 3 — Analysis-Ready Data

**Status:** Completed

The project datasets were prepared for spatial analysis using a common projected coordinate reference system:

**EPSG:32737 — WGS 84 / UTM Zone 37 South**

This projected CRS provides metric units suitable for:

* Distance calculations
* Terrain analysis
* Raster processing
* Spatial overlay
* Flood conditioning factor generation

The analysis-ready datasets were organized within the project data structure before downstream processing.

---

## ✅ Phase 4 — Terrain and Hydrological Analysis

**Status:** Completed

Terrain and hydrological preprocessing were implemented using Python, Rasterio, and WhiteboxTools.

Completed outputs include:

* Filled DEM
* Slope
* Aspect
* D8 Flow Direction
* Flow Accumulation
* Stream Network
* Watershed Delineation

The hydrological workflow was used to understand:

* Terrain characteristics
* Flow direction
* Flow concentration
* Drainage behaviour
* Stream development
* Contributing watershed areas

Each major processing stage included:

* Python processing script
* Validation script
* QGIS visual inspection
* Documentation
* Git version history

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

The project preserves these categorical classes at the conditioning-factor stage. Their flood-susceptibility influence was later established through an explicit reclassification methodology during Phase 6.

---

### 5. Population Exposure

**Output:**

`data/analysis/flood_factors/population.tif`

Population represents the human exposure dimension of the flood model.

The population raster is based on WorldPop gridded population estimates.

The prepared factor preserves the original population values and raster properties. Population is not treated as a direct physical measure of flood susceptibility; instead, it provides information about where larger numbers of people may potentially be affected by flood hazards.

---

## Phase 5 Validation

**Status:** Completed

All five flood conditioning factors were subjected to the project's validation workflow.

Validation included:

* Raster existence checks
* CRS verification
* Raster dimensions
* Resolution verification
* Spatial extent checks
* NoData inspection
* Data type verification
* Statistical inspection where appropriate
* Spatial comparison
* QGIS visual inspection

The completed factors were therefore ready for standardization.

---

# Phase 6 — Factor Standardization / Normalization

**Status:** Completed

Phase 6 converted the five flood-conditioning factors into comparable flood-susceptibility scores suitable for subsequent MCDA modelling.

The factors originally had different units, value ranges, resolutions, and meanings. Directly combining these raw values would therefore have produced an inappropriate weighted overlay.

The standardization stage established explicit relationships between each factor and flood susceptibility before implementation.

---

## Factor Standardization Methodology

| Factor             | Data Type             | Relationship    | Standardization              |
| ------------------ | --------------------- | --------------- | ---------------------------- |
| Elevation          | Continuous            | Inverse         | Min-Max normalization        |
| Slope              | Continuous            | Inverse         | Min-Max normalization        |
| Distance to Rivers | Continuous            | Inverse         | Min-Max normalization        |
| Population         | Continuous / Exposure | Positive        | Min-Max normalization        |
| Land Cover         | Categorical           | Class-dependent | Categorical reclassification |

Continuous factors were converted to a common **0–1 scale**.

A score closer to **1** represents greater contribution to the modelled flood susceptibility or exposure relationship, while a score closer to **0** represents lower contribution.

---

## 1. Elevation Standardization

**Input:**

`data/analysis/flood_factors/elevation.tif`

**Output:**

`data/analysis/standardized/elevation_score.tif`

Elevation was standardized using an inverse relationship because lower-lying terrain can be more susceptible to water accumulation and inundation.

The transformation produced scores from:

`0.0 → 1.0`

Validation confirmed:

* CRS consistency
* Raster dimensions
* Transform
* Resolution
* Valid cell count
* 0–1 score range
* Expected inverse relationship

The source-score correlation was:

`-1.000000`

---

## 2. Slope Standardization

**Input:**

`data/analysis/flood_factors/slope.tif`

**Output:**

`data/analysis/standardized/slope_score.tif`

Slope was standardized using an inverse relationship because lower slopes generally favour slower drainage and greater potential for surface water accumulation.

The transformation produced scores from:

`0.0 → 1.0`

Validation confirmed the expected inverse relationship.

The source-score correlation was:

`-1.000000`

---

## 3. Distance to Rivers Standardization

**Input:**

`data/analysis/flood_factors/distance_to_rivers.tif`

**Output:**

`data/analysis/standardized/distance_to_rivers_score.tif`

Distance to rivers was standardized using an inverse relationship.

Therefore:

* Areas closer to rivers receive higher scores.
* Areas farther from rivers receive lower scores.

The transformation produced scores from:

`0.0 → 1.0`

Validation confirmed:

`Source-score correlation: -1.000000`

---

## 4. Population Standardization

**Input:**

`data/analysis/flood_factors/population.tif`

**Output:**

`data/analysis/standardized/population_score.tif`

Population was standardized using a positive relationship because higher population values represent greater potential human exposure.

Therefore:

* Lower population → lower exposure score
* Higher population → higher exposure score

The transformation produced scores from:

`0.0 → 1.0`

Validation confirmed:

`Source-score correlation: 1.000000`

The original population values were preserved in the source flood-factor raster.

---

## 5. Land Cover Reclassification

**Input:**

`data/analysis/flood_factors/landcover.tif`

**Output:**

`data/analysis/standardized/landcover_score.tif`

Land Cover was treated differently from the continuous factors because its values represent categorical classes rather than measurements.

The established reclassification methodology was:

| Land Cover Class | Flood Susceptibility Score |
| ---------------: | -------------------------: |
|               10 |                       0.20 |
|               20 |                       0.30 |
|               30 |                       0.45 |
|               40 |                       0.60 |
|               50 |                       1.00 |
|               60 |                       0.75 |
|               80 |                       0.00 |
|               90 |                       0.15 |

The resulting standardized raster contains the expected eight score values:

`0.00, 0.15, 0.20, 0.30, 0.45, 0.60, 0.75, 1.00`

Validation confirmed that every detected land-cover class was correctly mapped to its intended score.

---

## Phase 6 Standardized Outputs

The standardized rasters are stored in:

```text
data/analysis/standardized/
```

Outputs include:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

The original flood-conditioning-factor rasters were not modified during standardization.

No reprojection or resampling was performed during this stage.

This was intentional because the source factors currently exist on different native grids. Spatial alignment will be handled as a separate modelling preparation stage before MCDA.

---

## Phase 6 Validation

**Status:** Completed

The standardized factors were validated using:

`src/validation/validate_standardized_factors.py`

Validation confirmed:

* CRS consistency
* Raster dimensions
* Raster transform
* Raster resolution
* Valid cell counts
* Continuous 0–1 standardization
* Expected direction of continuous relationships
* Land Cover class detection
* Land Cover class-to-score mapping

Validation results:

```text
Elevation              PASS
Slope                  PASS
Distance to Rivers     PASS
Population              PASS
Land Cover              PASS
```

The validation confirmed that all five standardized flood-conditioning factors were correctly generated and are ready for the next modelling preparation stage.

QGIS visual verification is used as an additional spatial inspection step before final phase closure.

---

# Phase 7 — Spatial Alignment and MCDA Preparation

**Status:** Next Stage

The standardized factors currently retain their original raster grids.

For example:

* Elevation, slope, and distance to rivers use approximately 30.87 m resolution.
* Population uses approximately 92.60 m resolution.
* Land Cover uses approximately 9.26 m resolution.

These factors cannot yet be directly combined in an MCDA weighted overlay.

The next stage will therefore establish a common modelling grid.

Spatial alignment will include:

* Selecting the reference grid
* Establishing the target CRS
* Establishing the target extent
* Establishing the target resolution
* Resampling factors where required
* Preserving appropriate resampling methods for continuous and categorical data
* Aligning raster transforms
* Verifying dimensions
* Verifying spatial extent
* Validating NoData handling
* Preparing the standardized factors for MCDA

The original standardized rasters will remain preserved.

---

# Phase 8 — MCDA Flood Susceptibility Model

**Status:** Planned

Once all standardized factors have been spatially aligned to a common modelling grid, they will be combined using **Multi-Criteria Decision Analysis (MCDA)**.

Conceptually:

```text
Elevation Score
       ↓
Slope Score
       ↓
Distance to Rivers Score
       ↓
Land Cover Score
       ↓
Population Score
       ↓
Spatial Alignment
       ↓
Common Modelling Grid
       ↓
Defensible Factor Weights
       ↓
MCDA Weighted Overlay
       ↓
Flood Susceptibility Surface
```

The final weights will be reviewed and documented based on the established factor methodology.

Previously used experimental weights will not automatically be reused without methodological justification.

---

# Phase 9 — Flood Susceptibility Validation

**Status:** Planned

The final flood susceptibility surface will be independently validated.

Validation will examine:

* Raster properties
* Spatial patterns
* High-susceptibility areas
* Relationship to rivers
* Relationship to elevation
* Relationship to slope
* Relationship to land cover
* Relationship to population exposure
* Spatial consistency
* Comparison with available reference information where appropriate

The purpose is to ensure that the final map is analytically defensible rather than simply visually attractive.

---

# Phase 10 — GeoAI Interpretation

**Status:** Planned

After the GIS flood susceptibility model has been validated, the project will introduce the GeoAI interpretation layer.

The GeoAI component will be designed to interpret the spatial outputs and explain:

* Where flood susceptibility is high
* Which factors contribute to the susceptibility
* How different spatial conditions influence the result
* Where exposed populations are concentrated
* What spatial evidence supports a particular risk interpretation

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
│       ├── flood_factors/
│       └── standardized/
│
├── src/
│   ├── terrain/
│   ├── validation/
│   ├── flood_factors/
│   ├── utils/
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

The project separates hydrological terrain products from flood-model inputs and standardized modelling factors.

```text
data/analysis/terrain/
        ↓
Terrain and hydrological products

data/analysis/flood_factors/
        ↓
Flood susceptibility conditioning factors

data/analysis/standardized/
        ↓
Comparable 0–1 modelling scores
```

This separation keeps the modelling architecture modular and makes the later spatial-alignment and MCDA stages easier to maintain.

---

# Technologies

## GIS

* QGIS
* WhiteboxTools

## Python Libraries

* GeoPandas
* Rasterio
* Shapely
* NumPy
* Pandas
* PyProj
* Fiona

## Development Tools

* Python 3.12.10
* Git
* GitHub
* Visual Studio Code

---

# Development Environment

### Python Version

* Python 3.12.10

### Core Libraries

* GeoPandas 1.1.3
* Rasterio 1.5.0
* Shapely 2.1.2
* PyProj 3.7.2
* Fiona 1.10.1
* NumPy 2.5.0
* Pandas 3.0.3

### Environment Status

* Development environment verified
* Dependencies installed successfully
* Project tested within a dedicated virtual environment
* Reproducible dependency configuration maintained through `requirements.txt`

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

* Reproducible
* Testable
* Documented
* Version-controlled
* Easy to troubleshoot
* Easy to explain to other GIS professionals

---

# Data and Reproducibility Policy

The repository tracks reproducible project artifacts rather than large geospatial datasets.

Tracked project artifacts include:

* Python source code
* Validation scripts
* Documentation
* Configuration files
* Project structure
* README
* Git history
* Reproducible processing workflows

Large raster and vector datasets, generated outputs, temporary files, and virtual-environment files are excluded from version control where appropriate.

This keeps the GitHub repository lightweight while preserving the complete methodology required to reproduce the workflow.

---

# Current Capabilities

The repository currently includes:

* Reproducible GIS data preparation
* Raster and vector validation workflows
* CRS verification and spatial preparation
* Terrain preprocessing
* Slope and aspect analysis
* Hydrological analysis using WhiteboxTools
* D8 flow direction analysis
* Flow accumulation analysis
* Stream network extraction
* Watershed delineation
* Flood conditioning factor preparation
* Distance-to-river analysis
* Land-cover factor preparation
* Population exposure factor preparation
* Continuous factor standardization
* Land-cover categorical reclassification
* Population exposure standardization
* Automated standardized-factor validation
* QGIS-based visual verification
* Modular Python project architecture
* Documentation and Git-based version control

---

# Current Outputs

The completed project workflow currently produces:

### Terrain and Hydrological Products

* Filled Digital Elevation Model (DEM)
* Slope raster
* Aspect raster
* D8 Flow Direction raster
* Flow Accumulation raster
* Stream Network raster
* Watershed raster

### Flood Conditioning Factors

* Elevation factor
* Slope factor
* Distance to Rivers factor
* Land Cover factor
* Population Exposure factor

### Standardized Factors

* Elevation score raster
* Slope score raster
* Distance to Rivers score raster
* Population score raster
* Land Cover score raster

### Validation

The project contains validation workflows for the major terrain, hydrological, analysis-ready, flood-conditioning-factor, and standardized-factor datasets.

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

The next major development stage is **Spatial Alignment and MCDA Preparation**.

Planned developments include:

* QGIS verification and final closure of Phase 6
* Spatial alignment of standardized factors
* Selection of the common MCDA modelling grid
* Establishment of target resolution and extent
* Appropriate resampling of continuous and categorical factors
* Spatial metadata validation after alignment
* Preparation of aligned factors for weighted overlay
* Establishing defensible MCDA factor weights
* Generating the flood susceptibility surface
* Validating the final susceptibility model
* Developing GeoAI-assisted spatial interpretation
* Producing explainable flood-risk information
* Developing an interactive decision-support interface
* Preparing final professional visualizations and portfolio documentation

---

# Author

**Dorothy Stephanie**

GIS | Remote Sensing | Spatial Data Science | Python for Geospatial Analysis

GitHub: StephanieDorothy

---

# License

This project is licensed for educational and portfolio purposes.
