# GeoAI Flood Risk Decision Agent

A Python-based geospatial analysis project for flood susceptibility modelling in Nairobi County, Kenya.

---

## Project Status — August 2026

> **Current Milestone: Phase 7 — Spatial Alignment and MCDA Preparation**

### Completed

* ✅ Phase 1 — Data Acquisition
* ✅ Phase 2 — Data Validation
* ✅ Phase 3 — Analysis-Ready Data
* ✅ Phase 4 — Terrain and Hydrological Analysis
* ✅ Phase 5 — Flood Conditioning Factors
* ✅ Phase 6 — Factor Standardization / Normalization
* ✅ Phase 7 — Spatial Alignment and MCDA Preparation

### Upcoming

* ⏳ Phase 8 — MCDA Flood Susceptibility Modelling
* ⏳ Phase 9 — Flood Susceptibility Validation
* ⏳ Phase 10 — GeoAI Interpretation and Decision Support

> **Phase 7 is fully completed, validated, visually verified in QGIS, documented, and pushed to GitHub.**
>
> The project is now ready to proceed to **Phase 8 — MCDA Flood Susceptibility Modelling**.

---

# Project Overview

The **GeoAI Flood Risk Decision Agent** is a modular Python-based geospatial analysis and spatial decision-support project for flood susceptibility modelling in Nairobi County, Kenya.

The project integrates GIS, remote sensing, terrain analysis, hydrological modelling, spatial analysis, raster processing, factor standardization, spatial alignment, Multi-Criteria Decision Analysis (MCDA), and GeoAI-assisted interpretation.

The overall workflow is designed to transform raw geospatial datasets into validated flood-conditioning factors, standardize those factors into comparable scores, align them to a common modelling grid, combine them through MCDA, validate the resulting flood susceptibility surface, and ultimately provide an explainable spatial decision-support capability.

The project follows a reproducible, modular, and validation-driven development approach.

Each major phase follows:

```text
Concept
    ↓
Methodology
    ↓
Implementation
    ↓
Execution
    ↓
Validation
    ↓
QGIS Visual Verification
    ↓
Documentation
    ↓
Git Commit
    ↓
Git Push
```

The objective is not simply to produce a flood map, but to build a professional and explainable geospatial workflow that can be inspected, reproduced, validated, and extended.

---

# Project Objectives

The project aims to:

* Build a reproducible GIS workflow using Python.
* Integrate raster and vector geospatial datasets.
* Validate spatial datasets before analysis.
* Prepare analysis-ready geospatial data.
* Perform terrain and hydrological analysis.
* Generate flood-conditioning factors.
* Define explicit relationships between conditioning factors and flood susceptibility.
* Standardize different factors onto a common 0–1 scale.
* Spatially align standardized factors to a common modelling grid.
* Apply Multi-Criteria Decision Analysis (MCDA).
* Generate a flood susceptibility surface.
* Validate the resulting flood susceptibility model.
* Analyse population exposure in relation to flood susceptibility.
* Apply GeoAI methods to interpret spatial results.
* Develop an explainable spatial decision-support workflow.
* Maintain reproducibility through Python scripts, validation scripts, documentation, and Git version control.

---

# Study Area

The study area for this project is:

**Nairobi County, Kenya**

Nairobi provides a suitable environment for developing and demonstrating a flood susceptibility decision-support workflow because of its:

* Urban development
* Changing land-cover patterns
* Complex terrain
* River and drainage networks
* Population concentration
* Potential flood exposure
* Spatial variation in environmental conditions

The project uses spatial datasets representing terrain, hydrology, rivers, land cover, and population exposure.

---

# Project Roadmap

| Phase    | Description                               | Status      |
| -------- | ----------------------------------------- | ----------- |
| Phase 1  | Data Acquisition                          | ✅ Completed |
| Phase 2  | Data Validation                           | ✅ Completed |
| Phase 3  | Analysis-Ready Data                       | ✅ Completed |
| Phase 4  | Terrain and Hydrological Analysis         | ✅ Completed |
| Phase 5  | Flood Conditioning Factors                | ✅ Completed |
| Phase 6  | Factor Standardization / Normalization    | ✅ Completed |
| Phase 7  | Spatial Alignment and MCDA Preparation    | ✅ Completed |
| Phase 8  | MCDA Flood Susceptibility Modelling       | ⏳ Next      |
| Phase 9  | Flood Susceptibility Validation           | ⏳ Planned   |
| Phase 10 | GeoAI Interpretation and Decision Support | ⏳ Planned   |

---

# Phase 1 — Data Acquisition

**Status: ✅ Completed**

The first phase established the project's foundational geospatial datasets.

The following datasets were acquired:

* Digital Elevation Model (DEM)
* Nairobi County Boundary
* Land Cover
* Population
* Rivers

These datasets provide the environmental, hydrological, land-cover, and population information required for the subsequent modelling stages.

The acquired datasets were organized into the project data structure before validation and processing.

---

# Phase 2 — Data Validation

**Status: ✅ Completed**

Before any modelling was performed, the acquired datasets were independently inspected and validated.

Validation included:

* Coordinate Reference System (CRS)
* Raster dimensions
* Raster resolution
* Spatial extent
* Raster data type
* NoData values
* Vector geometry
* Dataset integrity
* Spatial coverage

The purpose of this phase was to ensure that downstream processing was performed using valid and understood datasets.

The project adopts the principle that:

> **Data should be validated before it is analysed.**

---

# Phase 3 — Analysis-Ready Data

**Status: ✅ Completed**

The validated datasets were transformed into an analysis-ready spatial framework.

The primary projected CRS selected for the project is:

```text
EPSG:32737
WGS 84 / UTM Zone 37 South
```

This projected coordinate reference system uses metric units and is therefore appropriate for:

* Distance calculations
* Raster analysis
* Terrain processing
* Hydrological modelling
* Spatial overlays
* Flood-conditioning factor generation
* MCDA processing

The datasets were prepared so that subsequent analysis could be performed within a consistent projected spatial reference.

---

# Phase 4 — Terrain and Hydrological Analysis

**Status: ✅ Completed**

Phase 4 focused on extracting terrain and hydrological information from the Digital Elevation Model.

The project used Python geospatial tools together with WhiteboxTools for terrain and hydrological processing.

Completed terrain products include:

* Digital Elevation Model preparation
* Elevation
* Slope
* Aspect

Completed hydrological products include:

* Flow Direction
* Flow Accumulation
* Stream Network
* Watershed Delineation

The hydrological workflow included DEM preparation and flow-processing operations.

A stream network was generated using a flow-accumulation threshold of:

```text
1000
```

The resulting terrain and hydrological products provided the foundation for the flood-conditioning factor stage.

---

# Phase 5 — Flood Conditioning Factors

**Status: ✅ Completed**

Phase 5 transformed the validated terrain, hydrological, land-cover, river, and population datasets into flood-conditioning factors.

Five major factors were prepared:

1. Elevation
2. Slope
3. Distance to Rivers
4. Land Cover
5. Population

These factors represent different environmental and exposure characteristics that can contribute to the spatial distribution or consequences of flooding.

---

## 5.1 Elevation

Elevation was prepared as a continuous flood-conditioning factor.

Higher and lower terrain positions can influence water accumulation and inundation behaviour.

The elevation factor was subsequently standardized using an inverse relationship for the flood susceptibility model.

---

## 5.2 Slope

Slope was derived from the terrain analysis workflow.

Slope provides information about terrain steepness and can influence:

* Surface runoff
* Water movement
* Drainage
* Potential accumulation

The slope factor was subsequently standardized using the project's defined inverse relationship.

---

## 5.3 Distance to Rivers

A river raster was created from the validated river vector data.

The river rasterization process successfully processed:

```text
655 river features
```

The river raster was then used to calculate Euclidean distance to rivers.

The resulting distance-to-rivers raster had the following validated statistics:

```text
Minimum: 0.0 m
Maximum: 16077.409 m
Mean:    2684.8079 m
```

The distance factor was subsequently standardized using an inverse relationship because areas closer to rivers receive higher susceptibility scores.

---

## 5.4 Land Cover

The land-cover dataset was prepared as a categorical flood-conditioning factor.

The detected land-cover classes included:

```text
10
20
30
40
50
60
80
90
```

The categorical nature of land cover required a reclassification approach rather than continuous min-max normalization.

The land-cover classes were later converted into flood-susceptibility scores during Phase 6.

---

## 5.5 Population

Population was prepared as an exposure-related factor.

The validated population raster had:

```text
CRS:
EPSG:32737

Data Type:
float32

Valid Cells:
61995

Minimum:
0.0

Maximum:
1018.9541

Mean:
83.76664

Median:
37.255993
```

The original population values were preserved in the prepared flood-conditioning raster.

Population is treated as an exposure dimension rather than a direct physical flood-conditioning mechanism.

---

# Phase 5 Validation

**Status: ✅ Completed**

The flood-conditioning factors were subjected to validation before standardization.

Validation included:

* Raster existence
* CRS
* Dimensions
* Resolution
* Spatial extent
* Data type
* NoData values
* Valid-cell statistics
* Spatial inspection
* QGIS verification

The completed factors were therefore considered suitable for the standardization stage.

---

# Phase 6 — Factor Standardization / Normalization

**Status: ✅ Completed**

Phase 6 converted the five flood-conditioning factors into comparable scores suitable for MCDA.

The raw factors had different:

* Units
* Value ranges
* Meanings
* Spatial resolutions
* Data types

They therefore could not be directly combined using weighted overlay.

The purpose of Phase 6 was to convert the factors into a common modelling scale:

```text
0 – 1
```

A score closer to:

```text
1
```

represents a greater contribution to the defined flood susceptibility or exposure relationship.

A score closer to:

```text
0
```

represents a lower contribution.

---

# Factor Standardization Methodology

| Factor             | Type                  | Relationship    | Method                         |
| ------------------ | --------------------- | --------------- | ------------------------------ |
| Elevation          | Continuous            | Inverse         | Min-Max inverse normalization  |
| Slope              | Continuous            | Inverse         | Min-Max inverse normalization  |
| Distance to Rivers | Continuous            | Inverse         | Min-Max inverse normalization  |
| Population         | Continuous / Exposure | Positive        | Min-Max positive normalization |
| Land Cover         | Categorical           | Class-dependent | Categorical reclassification   |

---

# Elevation Standardization

Elevation was standardized using an inverse relationship.

Conceptually:

```text
Lower elevation
      ↓
Higher susceptibility score
```

The resulting standardized raster was:

```text
data/analysis/standardized/elevation_score.tif
```

Validation confirmed the expected inverse relationship:

```text
Correlation:
-1.000000
```

The standardized values were successfully constrained to the expected 0–1 range.

---

# Slope Standardization

Slope was standardized using an inverse relationship.

Conceptually:

```text
Lower slope
      ↓
Higher susceptibility score
```

The resulting standardized raster was:

```text
data/analysis/standardized/slope_score.tif
```

Validation confirmed the expected relationship.

The standardized values were within the expected 0–1 range.

---

# Distance to Rivers Standardization

Distance to rivers was standardized using an inverse relationship.

Conceptually:

```text
Closer to river
      ↓
Higher susceptibility score
```

The resulting standardized raster was:

```text
data/analysis/standardized/distance_to_rivers_score.tif
```

Validation confirmed:

```text
Correlation:
-1.000000
```

The standardized raster successfully represented the intended inverse relationship.

---

# Population Standardization

Population was standardized using a positive relationship.

Conceptually:

```text
Higher population
      ↓
Higher exposure score
```

The resulting standardized raster was:

```text
data/analysis/standardized/population_score.tif
```

Validation confirmed:

```text
Correlation:
1.000000
```

The original population values were preserved separately from the standardized population score.

---

# Land Cover Reclassification

Land Cover required categorical reclassification rather than continuous min-max normalization.

The established mapping was:

| Class | Land Cover               | Score |
| ----: | ------------------------ | ----: |
|    10 | Tree Cover               |  0.20 |
|    20 | Shrubland                |  0.30 |
|    30 | Grassland                |  0.45 |
|    40 | Cropland                 |  0.60 |
|    50 | Built-up                 |  1.00 |
|    60 | Bare / Sparse Vegetation |  0.75 |
|    80 | Permanent Water          |  0.00 |
|    90 | Herbaceous Wetland       |  0.15 |

These values represent relative modelling scores.

They are **not probabilities of flooding**.

The resulting standardized land-cover raster contains the intended score values:

```text
0.00
0.15
0.20
0.30
0.45
0.60
0.75
1.00
```

Validation confirmed that the detected land-cover classes were correctly mapped to their intended scores.

---

# Phase 6 Standardized Outputs

The standardized factors are stored in:

```text
data/analysis/standardized/
```

The outputs include:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

The original flood-conditioning factors were preserved.

Standardization did not overwrite the original factor rasters.

---

# Phase 6 Validation

**Status: ✅ Completed**

The standardized factors were validated using:

```text
src/validation/validate_standardized_factors.py
```

Validation confirmed:

* CRS consistency
* Raster dimensions
* Raster resolution
* Valid-cell counts
* 0–1 standardization
* Expected continuous-factor relationships
* Land-cover class detection
* Land-cover class-to-score mapping

Validation results:

```text
Elevation              PASS
Slope                  PASS
Distance to Rivers     PASS
Population              PASS
Land Cover              PASS
```

All five standardized flood-conditioning factors passed Phase 6 validation.

---

# Phase 7 — Spatial Alignment and MCDA Preparation

**Status: ✅ Completed**

Phase 7 prepared the five standardized flood-conditioning factors for cell-by-cell Multi-Criteria Decision Analysis.

Although Phase 6 placed the factors on a common numerical scale, the input rasters did not all have the same spatial grid.

For MCDA, corresponding raster cells must represent corresponding geographic locations.

Phase 7 therefore established a common modelling grid and aligned all five standardized factors to that grid.

---

# Phase 7 Objective

The objective of Phase 7 was to produce five spatially aligned standardized factors:

1. Elevation
2. Slope
3. Distance to Rivers
4. Population
5. Land Cover

The resulting rasters can now be combined cell-by-cell during the MCDA stage.

---

# Phase 7 Reference Grid

The standardized elevation raster was selected as the reference grid:

```text
elevation_score.tif
```

The reference grid properties are:

```text
CRS:
EPSG:32737

Coordinate Reference System:
WGS 84 / UTM Zone 37 South

Width:
1603 columns

Height:
1019 rows

Resolution:
30.865516819072 × 30.865516819072 metres
```

The reference grid establishes the common:

* CRS
* Width
* Height
* Pixel size
* Transform
* Grid origin
* Spatial extent
* Pixel-to-coordinate relationship

The negative Y pixel size used by north-up rasters is expected and represents the normal raster row orientation.

---

# Why Spatial Alignment Was Necessary

The standardized factors originated from different source grids.

For example:

```text
Elevation:
approximately 30.87 m

Slope:
approximately 30.87 m

Distance to Rivers:
approximately 30.87 m

Population:
approximately 92.60 m

Land Cover:
approximately 9.26 m
```

Although the factors had already been standardized numerically, their raster cells did not initially correspond spatially.

A common 0–1 scale alone is therefore insufficient for cell-by-cell MCDA.

Spatial alignment ensures that:

```text
Cell [row, column]
```

in one factor represents the same geographic location as:

```text
Cell [row, column]
```

in every other factor.

---

# Phase 7 Alignment Strategy

The alignment workflow was:

```text
1. Select reference grid
        ↓
2. Inspect standardized factors
        ↓
3. Compare CRS and raster grids
        ↓
4. Preserve already-aligned factors
        ↓
5. Resample incompatible factors
        ↓
6. Save aligned outputs separately
        ↓
7. Validate aligned rasters
        ↓
8. Verify visually in QGIS
```

---

# Elevation Alignment

Elevation already matched the reference grid.

Therefore:

```text
No resampling required
```

Its values and spatial structure were preserved.

---

# Slope Alignment

Slope already matched the reference grid.

Therefore:

```text
No resampling required
```

Its values were preserved.

---

# Distance to Rivers Alignment

Distance to Rivers already matched the reference grid.

Therefore:

```text
No resampling required
```

Its values were preserved.

---

# Population Alignment

The population factor originally had a coarser spatial resolution of approximately:

```text
92.60 m
```

It was aligned to the reference grid using:

```text
Bilinear interpolation
```

Bilinear interpolation was selected because population is represented as a continuous numerical surface.

The operation changes the raster representation to the common grid; it does not create new population observations.

---

# Land Cover Alignment

The land-cover factor originated from a finer-resolution raster of approximately:

```text
9.26 m
```

It was aligned to the reference grid using:

```text
Nearest-neighbour resampling
```

Nearest-neighbour resampling was selected because land cover is categorical and the process must avoid creating artificial intermediate class values.

---

# Phase 7 Output Directory

The aligned standardized factors are stored in:

```text
data/analysis/aligned/
```

The outputs are:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

The original Phase 6 standardized factors remain preserved in:

```text
data/analysis/standardized/
```

---

# Phase 7 Implementation

The alignment workflow is implemented in:

```text
src/flood_factors/align_standardized_factors.py
```

The script:

1. Identifies the project root.
2. Uses relative project paths.
3. Reads the standardized factor rasters.
4. Selects `elevation_score.tif` as the reference grid.
5. Compares each factor with the reference grid.
6. Preserves factors that already match.
7. Resamples population using bilinear interpolation.
8. Resamples land cover using nearest-neighbour interpolation.
9. Writes aligned factors into the aligned directory.
10. Performs alignment-related checks.

The script does not apply MCDA weights.

Its purpose is to prepare the standardized factors spatially for Phase 8.

---

# Phase 7 Data Properties

All aligned factors use:

```text
Data Type:
float32

NoData:
-9999
```

Common grid:

```text
CRS:
EPSG:32737

Width:
1603

Height:
1019

Resolution:
30.865516819072 × 30.865516819072 m
```

---

# Phase 7 Dedicated Validation

A dedicated validation script was created:

```text
src/validation/validate_aligned_factors.py
```

The validation checks:

* File existence
* CRS
* Width
* Height
* Resolution
* Transform
* Bounds
* Data type
* NoData metadata
* Valid-cell presence
* NaN values
* Infinite values
* Minimum score
* Maximum score
* Valid-cell counts
* NoData counts
* Value preservation for factors that did not require resampling

---

# Phase 7 Validation Results

The completed validation produced:

```text
Total Checks: 76
Passed:       76
Failed:        0

Overall Status:
PASS
```

Therefore:

```text
76 / 76 checks passed
```

This confirms that all five aligned standardized factors satisfied the defined spatial and numerical validation requirements.

---

# Phase 7 Aligned Factor Statistics

| Factor             |  Minimum |  Maximum |     Mean |
| ------------------ | -------: | -------: | -------: |
| Elevation          | 0.000000 | 1.000000 | 0.596241 |
| Slope              | 0.000000 | 1.000000 | 0.906355 |
| Distance to Rivers | 0.000000 | 1.000000 | 0.833007 |
| Population         | 0.000000 | 0.976962 | 0.082178 |
| Land Cover         | 0.000000 | 1.000000 | 0.563188 |

All aligned factors remained within the expected standardized range:

```text
0 ≤ score ≤ 1
```

The population maximum does not need to equal exactly 1.0 after bilinear resampling. Its maximum remained within the required standardized range.

---

# Phase 7 Value Preservation

Three factors already matched the reference grid:

* Elevation
* Slope
* Distance to Rivers

These factors therefore did not require resampling.

Validation confirmed that their values were preserved.

Population and Land Cover were intentionally resampled because their original grids did not match the reference grid.

---

# Phase 7 QGIS Visual Verification

After automated numerical validation, the five aligned rasters were loaded into QGIS.

The visual verification included:

* Loading all five aligned factors.
* Comparing their spatial coverage.
* Inspecting layer extents.
* Using transparency and overlays.
* Inspecting the population factor after bilinear resampling.
* Inspecting the land-cover factor after nearest-neighbour resampling.
* Comparing raster properties.
* Checking for spatial displacement.
* Checking for unexpected grid shifts.

### Visual Verification Result

```text
All five aligned factors visually overlap correctly in QGIS.
```

No obvious spatial displacement or unexpected grid shift was observed.

---

# Phase 7 Quality Assurance

Phase 7 passed two complementary quality-assurance stages.

## Numerical Validation

```text
76 / 76 checks passed
0 failures
```

## Visual Validation

```text
All five aligned factors visually overlap correctly in QGIS.
```

The combination of automated validation and QGIS visual inspection confirms that the standardized factors are spatially and numerically prepared for MCDA.

---

# Phase 7 Reproducibility

Phase 7 can be reproduced using the tracked source code and project structure.

The workflow uses relative project paths rather than machine-specific absolute paths.

Run the alignment process from the repository root:

```bash
python src/flood_factors/align_standardized_factors.py
```

Then run validation:

```bash
python src/validation/validate_aligned_factors.py
```

The workflow is:

```text
Standardized Factors
        ↓
Alignment Script
        ↓
Aligned Factors
        ↓
Validation Script
        ↓
Numerical QA
        ↓
QGIS Visual Verification
        ↓
MCDA-Ready Factors
```

---

# Phase 7 Outputs

## Source Code

```text
src/flood_factors/align_standardized_factors.py
```

## Validation Code

```text
src/validation/validate_aligned_factors.py
```

## Documentation

```text
Docs/methodology.md
```

## Aligned Analytical Outputs

```text
data/analysis/aligned/
```

The generated raster outputs are analytical data products and are not tracked in Git under the project's repository policy.

The repository tracks reproducible artifacts including:

* Source code
* Validation scripts
* Documentation
* Configuration
* README
* Project structure
* Reproducible processing workflows

---

# Phase 8 — MCDA Flood Susceptibility Modelling

**Status: ⏳ NEXT PHASE**

Phase 8 is the next stage of the project.

With Phase 7 completed, the five standardized flood-conditioning factors are now aligned to the same modelling grid and are ready for weighted overlay.

The purpose of Phase 8 is to combine the aligned standardized factors using **Multi-Criteria Decision Analysis (MCDA)**.

The conceptual workflow will be:

```text
Aligned Elevation Score
          ↓
Aligned Slope Score
          ↓
Aligned Distance-to-Rivers Score
          ↓
Aligned Land-Cover Score
          ↓
Aligned Population Score
          ↓
        MCDA
          ↓
Weighted Overlay
          ↓
Flood Susceptibility Surface
```

The MCDA stage will require defensible factor weights.

The weights will be explicitly documented and justified before implementation.

The project will not automatically reuse experimental weights from earlier development stages without methodological justification.

---

# Phase 8 Planned Tasks

The planned Phase 8 workflow includes:

1. Define the MCDA weighting methodology.
2. Establish defensible factor weights.
3. Confirm that all factor weights are valid.
4. Confirm that the weights sum to 1.
5. Read the five aligned standardized rasters.
6. Apply the selected weights.
7. Perform cell-by-cell weighted overlay.
8. Generate the flood susceptibility surface.
9. Preserve NoData areas appropriately.
10. Save the susceptibility raster.
11. Validate raster properties.
12. Validate numerical range.
13. Inspect susceptibility statistics.
14. Visualize the susceptibility surface in QGIS.
15. Document the methodology.
16. Commit and push the completed Phase 8 work to GitHub.
17. Update this README after Phase 8 completion.

---

# Phase 9 — Flood Susceptibility Validation

**Status: ⏳ PLANNED**

Phase 9 will independently evaluate the flood susceptibility model produced during Phase 8.

Validation will examine:

* Raster integrity
* CRS
* Dimensions
* Resolution
* Spatial extent
* NoData handling
* Minimum and maximum susceptibility values
* Statistical distribution
* Spatial patterns
* High-susceptibility areas
* Relationship to rivers
* Relationship to elevation
* Relationship to slope
* Relationship to land cover
* Population exposure in susceptible areas
* Available reference information where appropriate

The purpose of Phase 9 is to determine whether the resulting susceptibility surface is analytically defensible.

The model will not be considered complete simply because the raster has been successfully generated.

---

# Phase 10 — GeoAI Interpretation and Decision Support

**Status: ⏳ PLANNED**

Phase 10 will introduce the GeoAI interpretation and decision-support component.

The GeoAI layer will operate on validated spatial outputs and will focus on explaining the results rather than replacing the underlying GIS analysis.

The system will ultimately aim to answer questions such as:

* Where are the areas of highest flood susceptibility?
* Which factors contribute to the susceptibility?
* Why does a particular area receive a high susceptibility score?
* Where are potentially exposed populations concentrated?
* What spatial evidence supports the interpretation?
* Which areas may require greater attention from planners or decision-makers?

The final objective is to progress from:

```text
Raw Geospatial Data
        ↓
GIS Processing
        ↓
Flood Conditioning Factors
        ↓
Standardization
        ↓
Spatial Alignment
        ↓
MCDA
        ↓
Validated Flood Susceptibility
        ↓
GeoAI Interpretation
        ↓
Spatial Decision Support
```

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
│       ├── standardized/
│       └── aligned/
│
├── src/
│   ├── terrain/
│   ├── validation/
│   ├── flood_factors/
│   ├── utils/
│   └── ...
│
├── Docs/
│   └── methodology.md
│
├── outputs/
│
├── requirements.txt
│
└── README.md
```

The analytical data workflow is organized as:

```text
data/analysis/terrain/
        ↓
Terrain and hydrological products

data/analysis/flood_factors/
        ↓
Flood-conditioning factors

data/analysis/standardized/
        ↓
Comparable 0–1 modelling scores

data/analysis/aligned/
        ↓
MCDA-ready spatially aligned factors
```

This structure keeps the project modular and separates source factors, standardized factors, and MCDA-ready factors.

---

# Technologies

## GIS and Spatial Analysis

* QGIS
* WhiteboxTools

## Programming

* Python

## Python Geospatial Libraries

* GeoPandas
* Rasterio
* Shapely
* PyProj
* Fiona

## Scientific and Data Processing Libraries

* NumPy
* Pandas

## Development and Version Control

* Visual Studio Code
* Git
* GitHub
* Python virtual environment

---

# Development Environment

## Python Version

```text
Python 3.12.10
```

## Core Libraries

```text
GeoPandas 1.1.3
Rasterio 1.5.0
Shapely 2.1.2
PyProj 3.7.2
Fiona 1.10.1
NumPy 2.5.0
Pandas 3.0.3
```

## Environment Status

* ✅ Dedicated Python virtual environment
* ✅ Project dependencies installed
* ✅ Development environment tested
* ✅ `requirements.txt` maintained
* ✅ Relative project paths used
* ✅ Git version control implemented

The virtual environment is created using:

```bash
python -m venv .venv
```

It can then be activated on Windows using:

```powershell
.venv\Scripts\Activate.ps1
```

Dependencies can be installed using:

```bash
pip install -r requirements.txt
```

---

# Development Workflow

The project follows a structured lesson and development workflow.

Each major lesson or implementation stage follows:

```text
1. Concept
        ↓
2. Why It Matters
        ↓
3. Methodology
        ↓
4. Implementation
        ↓
5. Execution
        ↓
6. Testing
        ↓
7. Validation
        ↓
8. QGIS Verification
        ↓
9. Documentation
        ↓
10. Git Commit
        ↓
11. Git Push
```

The project is therefore developed incrementally rather than implementing the entire workflow at once.

After completing a major phase:

* The implementation is tested.
* Validation is performed.
* QGIS is used for visual verification where appropriate.
* Documentation is updated.
* Git status is checked.
* Changes are committed.
* Changes are pushed to GitHub.
* The README is updated to reflect the actual project status.

---

# Data and Reproducibility Policy

The repository follows a reproducibility-focused Git policy.

The repository tracks:

* Python source code
* Validation scripts
* Documentation
* Configuration
* README
* Reproducible processing workflows
* Project structure

The repository does **not** intentionally track:

* Raw datasets
* Large processed datasets
* Generated raster outputs
* Temporary files
* Virtual environments
* Machine-specific files

This keeps the repository manageable while preserving the code and documentation required to reproduce the analytical workflow.

The project uses relative paths rather than hard-coded machine-specific paths wherever possible.

---

# Reproducibility Principles

The project follows these principles:

### 1. Preserve Source Data

Original datasets are kept separate from derived products.

### 2. Do Not Overwrite Analytical Products Unnecessarily

Original factors and standardized factors are preserved separately.

### 3. Separate Processing Stages

Each major transformation has its own script or module.

### 4. Validate Before Moving Forward

A completed processing script is not considered sufficient without validation.

### 5. Use QGIS for Visual Verification

Automated validation is complemented by visual inspection where spatial interpretation is important.

### 6. Version Control Reproducible Artifacts

Source code, validation scripts, documentation, and project configuration are maintained through Git.

### 7. Document Methodological Decisions

Important choices such as:

* CRS
* Resampling methods
* Standardization relationships
* Land-cover scores
* Reference grids
* MCDA weights

are documented rather than hidden inside the code.

---

# Current Capabilities

The project currently supports:

* GIS data acquisition
* Raster and vector data validation
* CRS verification
* Analysis-ready spatial preparation
* DEM processing
* Terrain analysis
* Slope generation
* Aspect generation
* Hydrological analysis
* Flow direction analysis
* Flow accumulation analysis
* Stream network extraction
* Watershed analysis
* Flood-conditioning factor preparation
* River rasterization
* Distance-to-river calculation
* Land-cover preparation
* Population exposure preparation
* Continuous factor standardization
* Categorical land-cover reclassification
* Standardized-factor validation
* Spatial alignment
* Raster resampling
* Automated aligned-factor validation
* QGIS visual verification
* Reproducible Python workflows
* Git-based version control
* Phase-based project documentation

---

# Current Outputs

## Terrain and Hydrological Outputs

The project has produced:

* Analysis-ready DEM
* Elevation raster
* Slope raster
* Aspect raster
* Flow Direction raster
* Flow Accumulation raster
* Stream Network raster
* Watershed outputs

---

## Flood Conditioning Factors

The completed flood-conditioning factors include:

```text
elevation.tif
slope.tif
distance_to_rivers.tif
land_cover.tif
population.tif
```

These are stored within:

```text
data/analysis/flood_factors/
```

---

## Standardized Factors

The standardized outputs include:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

These are stored within:

```text
data/analysis/standardized/
```

---

## Aligned Standardized Factors

The Phase 7 outputs include:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

These are stored within:

```text
data/analysis/aligned/
```

All five aligned factors share:

```text
CRS:
EPSG:32737

Width:
1603

Height:
1019

Resolution:
30.865516819072 × 30.865516819072 m
```

---

# Validation

Validation is an important component of the project architecture.

The project currently includes validation workflows for:

* Data acquisition
* Analysis-ready data
* Terrain products
* Hydrological products
* Flood-conditioning factors
* Standardized factors
* Spatially aligned factors

The Phase 6 standardized-factor validation confirmed that all five standardized factors passed their defined checks.

The Phase 7 aligned-factor validation achieved:

```text
Total Checks: 76
Passed:       76
Failed:        0

Result:
PASS
```

The aligned factors were also visually verified in QGIS.

---

# Phase Completion Philosophy

A project phase is considered complete only when:

```text
Implementation
      +
Testing
      +
Validation
      +
Visual Verification where appropriate
      +
Documentation
      +
Git Version Control
```

have been completed.

This ensures that the project does not simply contain working scripts, but maintains an auditable and reproducible development history.

---

# Getting Started

Clone the repository:

```bash
git clone https://github.com/StephanieDorothy/GeoAI-flood-risk-agent.git
```

Navigate into the project:

```bash
cd GeoAI-flood-risk-agent
```

Create the virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run scripts from the repository root so that the project's relative paths resolve correctly.

---

# Reproducing Phase 7

From the project root:

```bash
python src/flood_factors/align_standardized_factors.py
```

Then run:

```bash
python src/validation/validate_aligned_factors.py
```

The expected validation outcome is:

```text
76 / 76 checks passed
```

QGIS can then be used to visually inspect the aligned rasters.

---

# Phase 8 Entry Point

The project is now ready to begin:

```text
PHASE 8
MCDA FLOOD SUSCEPTIBILITY MODELLING
```

The starting inputs for Phase 8 are the five validated aligned standardized factors:

```text
data/analysis/aligned/
```

The next implementation should therefore begin with:

```text
1. MCDA methodology
2. Factor weighting
3. Weight validation
4. Weighted overlay implementation
5. Flood susceptibility raster generation
6. Numerical validation
7. QGIS verification
8. Documentation
9. Git commit and push
10. README update
```

Phase 8 will build directly on the validated outputs of Phases 1–7.

---

# Future Work

## Phase 8

**MCDA Flood Susceptibility Modelling**

* Establish defensible factor weights
* Implement weighted overlay
* Generate flood susceptibility surface
* Validate the numerical output
* Inspect susceptibility distribution
* Visualize the susceptibility surface

## Phase 9

**Flood Susceptibility Validation**

* Validate the final susceptibility raster
* Analyse spatial patterns
* Compare susceptibility with conditioning factors
* Examine relationship with river proximity
* Examine relationship with terrain
* Examine relationship with population exposure
* Compare against suitable reference information where available

## Phase 10

**GeoAI Interpretation and Decision Support**

* Develop explainable spatial interpretation
* Interpret high-susceptibility areas
* Identify contributing factors
* Analyse population exposure
* Develop decision-support outputs
* Build toward an interactive or query-based spatial decision-support system
* Produce professional final maps and project documentation

---

# Project Development Philosophy

This project is being developed as more than a collection of GIS scripts.

It is intended to demonstrate an end-to-end professional geospatial workflow involving:

```text
Data
 ↓
Validation
 ↓
Spatial Preparation
 ↓
Terrain Analysis
 ↓
Hydrological Analysis
 ↓
Flood Factors
 ↓
Standardization
 ↓
Spatial Alignment
 ↓
MCDA
 ↓
Validation
 ↓
GeoAI Interpretation
 ↓
Decision Support
```

The emphasis throughout the project is on:

* Reproducibility
* Spatial correctness
* Explicit methodology
* Automated validation
* Visual verification
* Modular code
* Clear documentation
* Version control
* Explainability

---

# Author

**Dorothy Stephanie**

GIS | Remote Sensing | Spatial Data Science | Python for Geospatial Analysis

GitHub:

```text
https://github.com/StephanieDorothy/GeoAI-flood-risk-agent
```

---

# License

This project is developed for educational, research, portfolio, and professional development purposes.

The project methodology, source code, documentation, and generated analytical workflow are intended to demonstrate reproducible geospatial analysis and spatial decision-support development.

---
