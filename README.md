# GeoAI Flood Risk Decision Agent

A Python-based geospatial analysis and spatial decision-support project for flood susceptibility modelling in Nairobi County, Kenya.

The project integrates **GIS, remote sensing, terrain analysis, hydrological modelling, raster processing, spatial analysis, factor standardization, spatial alignment, Multi-Criteria Decision Analysis (MCDA), Analytic Hierarchy Process (AHP), independent validation, QGIS visual verification, and GeoAI-oriented interpretation** into a reproducible flood susceptibility workflow.

---

# Table of Contents

1. [Project Overview](#project-overview)
2. [Project Vision](#project-vision)
3. [Project Goal](#project-goal)
4. [Project Objectives](#project-objectives)
5. [Study Area](#study-area)
6. [Project Status](#project-status)
7. [Project Roadmap](#project-roadmap)
8. [Phase 1 — Data Acquisition](#phase-1--data-acquisition)
9. [Phase 2 — Data Validation](#phase-2--data-validation)
10. [Phase 3 — Analysis-Ready Data](#phase-3--analysis-ready-data)
11. [Phase 4 — Terrain and Hydrological Analysis](#phase-4--terrain-and-hydrological-analysis)
12. [Phase 5 — Flood Conditioning Factors](#phase-5--flood-conditioning-factors)
13. [Phase 6 — Factor Standardization](#phase-6--factor-standardization)
14. [Phase 7 — Spatial Alignment and MCDA Preparation](#phase-7--spatial-alignment-and-mcda-preparation)
15. [Phase 8 — MCDA Flood Susceptibility Modelling](#phase-8--mcda-flood-susceptibility-modelling)
16. [Phase 8 Outputs](#phase-8-outputs)
17. [Current Analytical Outputs](#current-analytical-outputs)
18. [Current Capabilities](#current-capabilities)
19. [Interpretation of Current Results](#interpretation-of-current-results)
20. [Important Model Limitations](#important-model-limitations)
21. [Phase 9 — Flood Susceptibility Validation](#phase-9--flood-susceptibility-validation)
22. [Phase 10 — GeoAI Interpretation and Decision Support](#phase-10--geoai-interpretation-and-decision-support)
23. [Validation Philosophy](#validation-philosophy)
24. [Development Workflow](#development-workflow)
25. [Data and Reproducibility Policy](#data-and-reproducibility-policy)
26. [Repository Structure](#repository-structure)
27. [Technologies](#technologies)
28. [Development Environment](#development-environment)
29. [Getting Started](#getting-started)
30. [Reproducing the Workflow](#reproducing-the-workflow)
31. [Project Development Philosophy](#project-development-philosophy)
32. [Future Work](#future-work)
33. [Author](#author)
34. [License](#license)

---

# Project Overview

The **GeoAI Flood Risk Decision Agent** is a modular Python-based geospatial analysis and spatial decision-support project focused on flood susceptibility modelling in Nairobi County, Kenya.

The project is designed as an end-to-end workflow that transforms heterogeneous geospatial datasets into validated flood-conditioning factors, standardizes those factors into comparable modelling scores, aligns them to a common spatial grid, combines them using MCDA, validates the resulting susceptibility surface, and ultimately provides a foundation for GeoAI-assisted interpretation and spatial decision support.

The project combines:

* Digital Elevation Model (DEM)
* Terrain analysis
* Slope analysis
* Aspect analysis
* Hydrological modelling
* River network information
* Distance-to-rivers analysis
* Land-cover information
* Population exposure information
* Raster and vector processing
* Factor standardization
* Spatial alignment
* Multi-Criteria Decision Analysis (MCDA)
* Analytic Hierarchy Process (AHP)
* Flood susceptibility classification
* Independent numerical validation
* QGIS visual verification
* GeoAI-oriented interpretation
* Reproducible Python workflows

The objective is not simply to generate a flood map.

The broader objective is to develop a **professional, transparent, reproducible, explainable, and extensible geospatial decision-support workflow**.

---

# Project Vision

The long-term vision of this project is to demonstrate how conventional GIS and spatial analysis can be combined with **Python, MCDA, reproducible modelling practices, independent validation, and GeoAI interpretation** to create transparent and decision-oriented geospatial systems.

The project is being developed progressively so that every analytical component can be:

* Understood
* Implemented
* Tested
* Independently validated
* Visually verified where appropriate
* Documented
* Reproduced
* Extended

The intended evolution is:

```text
Raw Geospatial Data
        ↓
Data Validation
        ↓
Analysis-Ready Data
        ↓
Terrain & Hydrological Analysis
        ↓
Flood Conditioning Factors
        ↓
Factor Standardization
        ↓
Spatial Alignment
        ↓
MCDA
        ↓
Flood Susceptibility Surface
        ↓
Independent Validation
        ↓
GeoAI Interpretation
        ↓
Spatial Decision Support
```

The ultimate vision is therefore to move from **geospatial data processing** to an **explainable spatial intelligence system** capable of helping users understand where flood susceptibility is relatively higher, what factors contribute to that pattern, and where further investigation or intervention may be appropriate.

---

# Project Goal

The primary goal is to develop a reproducible GeoAI-assisted flood susceptibility and spatial decision-support workflow capable of:

1. Acquiring relevant geospatial datasets.
2. Validating datasets before analysis.
3. Preparing analysis-ready spatial data.
4. Performing terrain and hydrological analysis.
5. Deriving flood-conditioning factors.
6. Standardizing heterogeneous factors to a common 0–1 scale.
7. Spatially aligning the factors to a common modelling grid.
8. Combining factors using defensible MCDA weighting.
9. Producing a continuous flood susceptibility surface.
10. Classifying the susceptibility surface into interpretable categories.
11. Independently validating analytical outputs.
12. Evaluating the spatial behaviour of the susceptibility model.
13. Interpreting susceptibility patterns and contributing factors.
14. Supporting future GeoAI-based spatial queries and decision support.
15. Maintaining reproducibility through code, documentation, validation, and version control.

---

# Project Objectives

The project aims to:

* Build a reproducible GIS workflow using Python.
* Integrate raster and vector geospatial datasets.
* Validate spatial datasets before analysis.
* Prepare analysis-ready geospatial data.
* Perform terrain analysis.
* Perform hydrological analysis.
* Generate flood-conditioning factors.
* Define explicit relationships between factors and susceptibility.
* Standardize heterogeneous factors onto a common 0–1 scale.
* Spatially align standardized factors to a common modelling grid.
* Apply Multi-Criteria Decision Analysis.
* Derive factor weights using AHP.
* Validate AHP consistency.
* Generate a continuous flood susceptibility surface.
* Classify susceptibility into five relative categories.
* Independently reproduce the MCDA calculation.
* Independently reproduce the susceptibility classification.
* Perform complementary QGIS visual verification.
* Prepare the foundation for population exposure analysis.
* Develop an explainable GeoAI interpretation layer.
* Maintain reproducibility through Python scripts, validation scripts, documentation, and Git version control.

---

# Study Area

## Nairobi County, Kenya

The study area for this project is:

**Nairobi County, Kenya**

Nairobi provides a suitable environment for demonstrating a flood susceptibility and spatial decision-support workflow because of its:

* Urban development
* Changing land-cover patterns
* Complex terrain
* River and drainage networks
* Population concentration
* Potential flood exposure
* Spatial variation in environmental conditions

The project uses spatial datasets representing terrain, hydrology, rivers, land cover, and population exposure.

## Analysis Coordinate Reference System

The primary projected CRS used throughout the modelling workflow is:

```text
EPSG:32737
WGS 84 / UTM Zone 37 South
```

A projected CRS provides metric units suitable for:

* Distance calculations
* Raster analysis
* Terrain processing
* Hydrological modelling
* Spatial overlays
* Flood-conditioning factor generation
* MCDA processing

---

# Project Status

## Current Milestone: Phase 8 Completed

The project has successfully completed **Phases 1–8**.

### Completed

* ✅ Phase 1 — Data Acquisition
* ✅ Phase 2 — Data Validation
* ✅ Phase 3 — Analysis-Ready Data
* ✅ Phase 4 — Terrain and Hydrological Analysis
* ✅ Phase 5 — Flood Conditioning Factors
* ✅ Phase 6 — Factor Standardization / Normalization
* ✅ Phase 7 — Spatial Alignment and MCDA Preparation
* ✅ Phase 8 — MCDA Flood Susceptibility Modelling

### Remaining

* ⏳ Phase 9 — Flood Susceptibility Validation
* ⏳ Phase 10 — GeoAI Interpretation and Decision Support

### Current Project Position

```text
Phase 1  ✅ Completed
Phase 2  ✅ Completed
Phase 3  ✅ Completed
Phase 4  ✅ Completed
Phase 5  ✅ Completed
Phase 6  ✅ Completed
Phase 7  ✅ Completed
Phase 8  ✅ Completed
Phase 9  ⏳ Upcoming
Phase 10 ⏳ Upcoming
```

Phase 8 has produced and independently reproduced both the continuous MCDA susceptibility surface and the classified susceptibility raster.

However, the project is **not yet considered fully complete**.

Phase 9 remains responsible for broader analytical validation of the susceptibility model, while Phase 10 will develop the GeoAI interpretation and decision-support layer.

---

# Project Roadmap

The project is organized into ten major phases.

```text
PHASE 1
Data Acquisition
        ↓
PHASE 2
Data Validation
        ↓
PHASE 3
Analysis-Ready Data
        ↓
PHASE 4
Terrain & Hydrological Analysis
        ↓
PHASE 5
Flood Conditioning Factors
        ↓
PHASE 6
Factor Standardization
        ↓
PHASE 7
Spatial Alignment
        ↓
PHASE 8
MCDA Flood Susceptibility Modelling
        ↓
PHASE 9
Flood Susceptibility Validation
        ↓
PHASE 10
GeoAI Interpretation &
Decision Support
```

| Phase    | Description                               | Status      |
| -------- | ----------------------------------------- | ----------- |
| Phase 1  | Data Acquisition                          | ✅ Completed |
| Phase 2  | Data Validation                           | ✅ Completed |
| Phase 3  | Analysis-Ready Data                       | ✅ Completed |
| Phase 4  | Terrain and Hydrological Analysis         | ✅ Completed |
| Phase 5  | Flood Conditioning Factors                | ✅ Completed |
| Phase 6  | Factor Standardization / Normalization    | ✅ Completed |
| Phase 7  | Spatial Alignment and MCDA Preparation    | ✅ Completed |
| Phase 8  | MCDA Flood Susceptibility Modelling       | ✅ Completed |
| Phase 9  | Flood Susceptibility Validation           | ⏳ Upcoming  |
| Phase 10 | GeoAI Interpretation and Decision Support | ⏳ Upcoming  |

---

# Phase 1 — Data Acquisition

**Status: ✅ Completed**

Phase 1 established the project's foundational geospatial datasets.

The project acquired and prepared datasets representing:

* Digital Elevation Model (DEM)
* Nairobi County administrative boundary
* Land Cover
* Population
* Rivers

These datasets provide the environmental, hydrological, land-cover, and population information required for the subsequent modelling stages.

The acquired datasets were organized into the project's data structure before validation and analytical processing.

---

# Phase 2 — Data Validation

**Status: ✅ Completed**

Before analytical modelling was performed, the acquired datasets were inspected and validated.

Validation included examination of:

* File availability
* Raster readability
* Vector readability
* Coordinate Reference Systems
* Raster dimensions
* Raster resolution
* Spatial extents
* Data types
* NoData behaviour
* Vector geometry
* Dataset integrity
* Spatial coverage

The purpose of this stage was to prevent invalid, corrupted, incomplete, or incompatible datasets from propagating into later modelling stages.

The project follows the principle:

> **Data should be validated before it is analysed.**

---

# Phase 3 — Analysis-Ready Data

**Status: ✅ Completed**

The validated datasets were transformed into an analysis-ready spatial framework.

The primary projected CRS is:

```text
EPSG:32737
WGS 84 / UTM Zone 37 South
```

This established a consistent spatial reference framework for:

* Raster analysis
* Distance calculations
* Terrain analysis
* Hydrological analysis
* Spatial overlays
* Flood-conditioning factor generation
* MCDA processing

Using a projected CRS also allows spatial measurements to be expressed in metres.

---

# Phase 4 — Terrain and Hydrological Analysis

**Status: ✅ Completed**

Phase 4 focused on extracting terrain and hydrological information from the DEM and related spatial data.

Python geospatial tools and WhiteboxTools were used for terrain and hydrological processing.

## Terrain Products

Completed terrain products include:

* Analysis-ready DEM
* Elevation
* Slope
* Aspect

## Hydrological Products

Completed hydrological products include:

* Flow Direction
* Flow Accumulation
* Stream Network
* Watershed Delineation

A stream network was generated using a flow-accumulation threshold of:

```text
1000
```

These terrain and hydrological products provided the analytical foundation for subsequent flood-conditioning factor generation.

---

# Phase 5 — Flood Conditioning Factors

**Status: ✅ Completed**

Phase 5 transformed the prepared terrain, hydrological, land-cover, river, and population information into flood-conditioning factors.

Five major factors were established:

1. Elevation
2. Slope
3. Distance to Rivers
4. Land Cover
5. Population

These factors represent different environmental and exposure characteristics relevant to the project's flood susceptibility framework.

---

## 5.1 Elevation

Elevation was prepared as a continuous flood-conditioning factor.

Terrain elevation can influence water accumulation and inundation behaviour.

For the modelling framework, elevation was standardized using an inverse relationship:

```text
Lower elevation
       ↓
Higher susceptibility score
```

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

The river raster was subsequently used to calculate Euclidean distance to rivers.

Validated distance-to-rivers statistics included:

```text
Minimum: 0.0 m
Maximum: 16077.409 m
Mean:    2684.8079 m
```

The distance-to-rivers factor was standardized using an inverse relationship:

```text
Closer to rivers
       ↓
Higher susceptibility score
```

---

## 5.4 Land Cover

Land cover was prepared as a categorical flood-conditioning factor.

Detected land-cover classes included:

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

Because land cover is categorical, it required class-specific reclassification rather than continuous min-max normalization.

The final class-to-score relationship was established during Phase 6.

---

## 5.5 Population

Population was prepared as an exposure-related factor.

The validated population raster included:

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

Population is treated as an **exposure dimension** rather than a direct physical flood-conditioning mechanism.

The original population values were preserved separately from the standardized population score.

---

# Phase 5 Validation

**Status: ✅ Completed**

The flood-conditioning factors were validated before standardization.

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

The five flood-conditioning factors originally existed in different:

* Units
* Value ranges
* Meanings
* Spatial resolutions
* Data types

They therefore could not be directly combined using a weighted overlay.

Phase 6 converted the factors into a common numerical modelling scale:

```text
0 – 1
```

A score closer to `1` represents a greater contribution to the defined susceptibility or exposure relationship.

A score closer to `0` represents a lower contribution.

---

# Factor Standardization Methodology

| Factor             | Type                  | Relationship    | Method                         |
| ------------------ | --------------------- | --------------- | ------------------------------ |
| Elevation          | Continuous            | Inverse         | Min-Max inverse normalization  |
| Slope              | Continuous            | Inverse         | Min-Max inverse normalization  |
| Distance to Rivers | Continuous            | Inverse         | Min-Max inverse normalization  |
| Population         | Continuous / Exposure | Positive        | Min-Max positive normalization |
| Land Cover         | Categorical           | Class-dependent | Categorical reclassification   |

The standardization process did **not** perform spatial reprojection or resampling.

Spatial alignment was deliberately separated into Phase 7.

---

## Elevation Standardization

Elevation was standardized using an inverse relationship:

```text
Lower elevation
       ↓
Higher susceptibility score
```

Output:

```text
data/analysis/standardized/elevation_score.tif
```

Validation confirmed the expected inverse relationship:

```text
Correlation:
-1.000000
```

The standardized values were constrained to the expected 0–1 range.

---

## Slope Standardization

Slope was standardized using an inverse relationship:

```text
Lower slope
       ↓
Higher susceptibility score
```

Output:

```text
data/analysis/standardized/slope_score.tif
```

Validation confirmed the expected relationship and 0–1 value range.

---

## Distance-to-Rivers Standardization

Distance to rivers was standardized using an inverse relationship:

```text
Closer to river
       ↓
Higher susceptibility score
```

Output:

```text
data/analysis/standardized/distance_to_rivers_score.tif
```

Validation confirmed:

```text
Correlation:
-1.000000
```

---

## Population Standardization

Population was standardized using a positive relationship:

```text
Higher population
       ↓
Higher exposure score
```

Output:

```text
data/analysis/standardized/population_score.tif
```

Validation confirmed:

```text
Correlation:
1.000000
```

The original population values were preserved separately.

---

## Land-Cover Reclassification

Land cover required categorical reclassification rather than continuous min-max normalization.

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

These values represent **relative modelling scores**.

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

---

# Phase 6 Standardized Outputs

Standardized factors are stored in:

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

All five standardized factors passed their defined validation checks.

---

# Phase 7 — Spatial Alignment and MCDA Preparation

**Status: ✅ Completed**

Phase 7 prepared the five standardized flood-conditioning factors for cell-by-cell MCDA.

Although Phase 6 placed the factors on a common numerical scale, the source rasters did not initially share the same spatial grid.

For cell-by-cell MCDA, corresponding raster cells must represent corresponding geographic locations.

Phase 7 therefore established a common modelling grid and aligned all five standardized factors to that grid.

---

# Phase 7 Reference Grid

The standardized elevation raster was selected as the reference grid:

```text
elevation_score.tif
```

Reference grid properties:

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

The reference grid established the common:

* CRS
* Width
* Height
* Pixel size
* Transform
* Grid origin
* Spatial extent
* Pixel-to-coordinate relationship

---

# Why Spatial Alignment Was Necessary

The standardized factors originated from different source grids.

Approximate source resolutions included:

```text
Elevation:
30.87 m

Slope:
30.87 m

Distance to Rivers:
30.87 m

Population:
92.60 m

Land Cover:
9.26 m
```

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

## Elevation Alignment

Elevation already matched the reference grid.

Therefore:

```text
No resampling required
```

Its values and spatial structure were preserved.

---

## Slope Alignment

Slope already matched the reference grid.

Therefore:

```text
No resampling required
```

Its values were preserved.

---

## Distance-to-Rivers Alignment

Distance to rivers already matched the reference grid.

Therefore:

```text
No resampling required
```

Its values were preserved.

---

## Population Alignment

Population originally had a coarser spatial resolution of approximately:

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

## Land-Cover Alignment

Land cover originated from a finer-resolution raster of approximately:

```text
9.26 m
```

It was aligned using:

```text
Nearest-neighbour resampling
```

Nearest-neighbour resampling was selected because land cover is categorical and the process must avoid creating artificial intermediate class values.

---

# Phase 7 Outputs

Aligned standardized factors are stored in:

```text
data/analysis/aligned/
```

Outputs:

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
4. Selects the elevation raster as the reference grid.
5. Compares each factor with the reference grid.
6. Preserves factors that already match.
7. Resamples population using bilinear interpolation.
8. Resamples land cover using nearest-neighbour interpolation.
9. Writes aligned factors into the aligned directory.
10. Performs alignment-related checks.

The script does not apply MCDA weights.

Its purpose is to prepare the standardized factors spatially for MCDA.

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

Validation script:

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

## Validation Result

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

The aligned factors were also visually verified in QGIS.

---

# Phase 7 Aligned Factor Statistics

| Factor             |  Minimum |  Maximum |     Mean |
| ------------------ | -------: | -------: | -------: |
| Elevation          | 0.000000 | 1.000000 | 0.596241 |
| Slope              | 0.000000 | 1.000000 | 0.906355 |
| Distance to Rivers | 0.000000 | 1.000000 | 0.833007 |
| Population         | 0.000000 | 0.976962 | 0.082178 |
| Land Cover         | 0.000000 | 1.000000 | 0.563188 |

All aligned factors remained within:

```text
0 ≤ score ≤ 1
```

The population maximum does not need to equal exactly 1.0 after bilinear resampling. Its maximum remained within the required standardized range.

---

# Phase 7 QGIS Visual Verification

After automated numerical validation, the five aligned rasters were loaded into QGIS.

Visual verification included:

* Comparing spatial coverage
* Inspecting layer extents
* Using transparency and overlays
* Inspecting population after bilinear resampling
* Inspecting land cover after nearest-neighbour resampling
* Comparing raster properties
* Checking for spatial displacement
* Checking for unexpected grid shifts

Result:

```text
All five aligned factors visually overlap correctly in QGIS.
```

No obvious spatial displacement or unexpected grid shift was observed.

---

# Phase 8 — MCDA Flood Susceptibility Modelling

**Status: ✅ COMPLETED**

Phase 8 combined the five aligned standardized flood-conditioning factors into a single continuous flood susceptibility surface.

The MCDA workflow uses the **Analytic Hierarchy Process (AHP)** to derive factor weights.

Phase 8 also produced a classified susceptibility raster and independently validated both the continuous MCDA output and the classification.

---

# Purpose of MCDA

Multi-Criteria Decision Analysis allows multiple standardized spatial factors to be combined while accounting for their relative importance.

The conceptual workflow is:

```text
Aligned Elevation Score
        +
Aligned Slope Score
        +
Aligned Distance-to-Rivers Score
        +
Aligned Land-Cover Score
        +
Aligned Population Score
        ↓
AHP Weights
        ↓
Weighted Overlay
        ↓
Continuous Flood Susceptibility Surface
        ↓
Quantile Classification
        ↓
Classified Flood Susceptibility Map
```

The resulting continuous raster provides a susceptibility score for each valid modelling cell.

---

# Phase 8 AHP Weighting

## Weighting Method

The **Analytic Hierarchy Process (AHP)** was selected as the weighting framework.

AHP provides a structured approach for expressing the relative importance of the five factors through pairwise comparisons.

The resulting weights are normalized so that their total equals 1.

---

# AHP Pairwise Comparison Matrix

The project uses the following pairwise comparison matrix:

| Factor     | Elevation |  Slope | Rivers | Land Cover | Population |
| ---------- | --------: | -----: | -----: | ---------: | ---------: |
| Elevation  |    1.0000 | 1.0000 | 0.3333 |     2.0000 |     3.0000 |
| Slope      |    1.0000 | 1.0000 | 0.3333 |     2.0000 |     3.0000 |
| Rivers     |    3.0000 | 3.0000 | 1.0000 |     3.0000 |     5.0000 |
| Land Cover |    0.5000 | 0.5000 | 0.3333 |     1.0000 |     3.0000 |
| Population |    0.3333 | 0.3333 | 0.2000 |     0.3333 |     1.0000 |

The matrix expresses the relative importance assigned to the five modelling factors.

---

# Derived AHP Weights

The final normalized factor weights are:

| Factor             |           Weight | Percentage |
| ------------------ | ---------------: | ---------: |
| Elevation          |     0.1868744589 |   18.6874% |
| Slope              |     0.1868744589 |   18.6874% |
| Distance to Rivers |     0.4352900433 |   43.5290% |
| Land Cover         |     0.1285887446 |   12.8589% |
| Population         |     0.0623722944 |    6.2372% |
| **Total**          | **1.0000000000** |   **100%** |

The largest weight is assigned to **distance to rivers**, followed by **elevation** and **slope**.

The weights are explicitly retained in the MCDA modelling script to support reproducibility.

---

# AHP Consistency Validation

AHP weighting was not accepted solely because the weights summed to 1.

The pairwise comparison matrix was also evaluated for consistency.

Results:

```text
Lambda max:
5.1207248525

Consistency Index (CI):
0.0301812131

Random Index (RI):
1.12

Consistency Ratio (CR):
0.0269475117
```

## Consistency Status

```text
PASS
```

The consistency ratio is below the commonly accepted AHP consistency threshold of `0.10`.

The pairwise comparisons were therefore considered sufficiently consistent for use in the MCDA workflow.

---

# Phase 8 Weighted Overlay

After the AHP weights were established and validated, the five aligned standardized rasters were combined using a cell-by-cell weighted overlay.

The conceptual equation is:

```text
Flood Susceptibility =
    (Elevation Score × Elevation Weight)
  + (Slope Score × Slope Weight)
  + (Distance-to-Rivers Score × Rivers Weight)
  + (Land-Cover Score × Land-Cover Weight)
  + (Population Score × Population Weight)
```

Using the final AHP weights:

```text
Flood Susceptibility =

    (Elevation × 0.1868744589)

  + (Slope × 0.1868744589)

  + (Distance to Rivers × 0.4352900433)

  + (Land Cover × 0.1285887446)

  + (Population × 0.0623722944)
```

Only cells for which the required factor values were valid were included in the final susceptibility calculation.

---

# Continuous Flood Susceptibility Surface

The MCDA produced:

```text
data/analysis/mcda/flood_susceptibility.tif
```

## Output Spatial Properties

```text
CRS:
EPSG:32737

Dimensions:
1603 × 1019

Resolution:
30.86551681907227 m × 30.86551681907227 m

NoData:
-9999

Data Type:
Float32
```

## Output Statistics

```text
Valid cells:
553860

Minimum:
0.483158

5th percentile:
0.632628

25th percentile:
0.711822

Median:
0.783512

75th percentile:
0.839340

95th percentile:
0.884455

Maximum:
0.932311

Mean:
0.772901

Standard deviation:
0.079953
```

The continuous raster represents the underlying numerical susceptibility surface used for subsequent classification and interpretation.

---

# Phase 8 Independent MCDA Validation

A dedicated independent validation script was developed:

```text
src/validation/validate_mcda_output.py
```

The validation does not simply check whether the output file exists.

It independently evaluates the generated MCDA result against the aligned input factors and expected modelling properties.

Validation checks include:

* Output file existence
* GeoTIFF readability
* CRS
* Raster dimensions
* Pixel resolution
* NoData value
* Data type
* Presence of all aligned factors
* Valid-cell mask
* Finite output values
* 0–1 output range
* Independent MCDA reproduction
* Numerical agreement between generated and independently calculated results

## Independent Reproduction Result

```text
Valid cells compared:
553860

Cells within tolerance:
553860

Maximum absolute error:
0.000000029880

Mean absolute error:
0.000000014898

Tolerance:
0.000010000000
```

The independent calculation reproduced the generated MCDA raster within the defined numerical tolerance.

## Validation Status

```text
OVERALL STATUS: PASS
```

This demonstrates that the continuous susceptibility surface is computationally reproducible.

---

# Phase 8 Flood Susceptibility Classification

The continuous MCDA surface was subsequently classified into five susceptibility categories.

A **quantile-based classification** approach was used.

## Classification Classes

| Class | Category  |
| ----: | --------- |
|     1 | Very Low  |
|     2 | Low       |
|     3 | Moderate  |
|     4 | High      |
|     5 | Very High |

The classification thresholds were derived from the distribution of valid MCDA susceptibility values.

## Quantile Thresholds

```text
20th percentile:
0.69158980

40th percentile:
0.76069050

60th percentile:
0.80517520

80th percentile:
0.84985673
```

The classification divides the valid modelling cells into five equal-frequency classes.

---

# Classified Flood Susceptibility Output

The classified raster is:

```text
data/analysis/mcda/flood_susceptibility_classified.tif
```

## Class Distribution

| Class | Category  |  Cells | Percentage |
| ----: | --------- | -----: | ---------: |
|     1 | Very Low  | 110772 |     20.00% |
|     2 | Low       | 110772 |     20.00% |
|     3 | Moderate  | 110772 |     20.00% |
|     4 | High      | 110772 |     20.00% |
|     5 | Very High | 110772 |     20.00% |

Total valid cells:

```text
553860
```

All five classes are present and all valid cells were classified.

---

# Independent Classification Validation

A dedicated validation script was created:

```text
src/validation/validate_classified_susceptibility.py
```

The validation checks:

* File existence
* CRS
* Raster dimensions
* Resolution
* Bounds
* NoData values
* Raster array dimensions
* Valid-cell masks
* Class values
* Presence of all five classes
* Independent classification reproduction
* Class distribution
* Output data type
* Classification metadata

## Independent Reproduction

```text
Valid cells compared:
553860

Differing cells:
0

Independent classification match:
PASS
```

The classification was independently reproduced with **zero differing cells**.

## Overall Validation

```text
OVERALL STATUS: PASS
```

---

# Phase 8 QGIS Visual Verification

The continuous and classified susceptibility rasters were visually inspected in QGIS.

Visual verification was used as a complementary quality-control step rather than a replacement for numerical validation.

The following were inspected:

* Spatial extent
* Overall spatial pattern
* NoData areas
* Unexpected displacement
* Raster alignment
* Classification appearance
* Presence of obvious processing artefacts
* General spatial plausibility

The maps displayed the expected spatial coverage of the modelling domain and retained NoData areas where the underlying valid-cell mask did not support susceptibility calculation.

---

# NoData Handling

NoData areas are intentionally preserved throughout the modelling workflow.

A NoData cell does **not** represent zero susceptibility.

Instead, it represents an area where the required modelling inputs were not simultaneously available or valid.

This distinction is important because assigning zero to missing data would incorrectly imply very low flood susceptibility.

The project therefore preserves NoData areas rather than converting missing information into artificial susceptibility values.

Future improvements may investigate additional data sources or preprocessing methods to reduce legitimate data gaps where appropriate.

---

# Phase 8 Reproducibility

The Phase 8 workflow is designed so that the modelling can be reproduced from the tracked source code and documented methodology.

## MCDA Script

```text
src/flood_factors/mcda_flood_susceptibility.py
```

Run from the repository root:

```bash
python src/flood_factors/mcda_flood_susceptibility.py
```

## MCDA Validation

```bash
python src/validation/validate_mcda_output.py
```

## Classification Script

```text
src/flood_factors/classify_flood_susceptibility.py
```

Run:

```bash
python src/flood_factors/classify_flood_susceptibility.py
```

## Classification Validation

```bash
python src/validation/validate_classified_susceptibility.py
```

The reproducibility workflow is:

```text
Aligned Standardized Factors
            ↓
       AHP Weighting
            ↓
   AHP Consistency Check
            ↓
      Weighted Overlay
            ↓
Continuous Susceptibility Surface
            ↓
Independent MCDA Validation
            ↓
    Quantile Classification
            ↓
Classified Susceptibility Map
            ↓
Independent Classification Validation
            ↓
      QGIS Verification
```

---

# Phase 8 Outputs

## Source Code

```text
src/flood_factors/mcda_flood_susceptibility.py

src/flood_factors/classify_flood_susceptibility.py
```

## Validation Code

```text
src/validation/validate_mcda_output.py

src/validation/validate_classified_susceptibility.py
```

## Analytical Outputs

```text
data/analysis/mcda/flood_susceptibility.tif

data/analysis/mcda/flood_susceptibility_classified.tif
```

The generated analytical raster outputs are not intended to be committed to Git under the project's reproducibility policy.

The repository tracks reproducible artifacts rather than large generated datasets.

---

# Current Analytical Outputs

At the completion of Phase 8, the project has produced the following major analytical products.

## Terrain and Hydrological Outputs

* Analysis-ready DEM
* Elevation raster
* Slope raster
* Aspect raster
* Flow Direction raster
* Flow Accumulation raster
* Stream Network raster
* Watershed outputs

## Flood Conditioning Factors

```text
elevation.tif
slope.tif
distance_to_rivers.tif
land_cover.tif
population.tif
```

## Standardized Factors

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

Stored in:

```text
data/analysis/standardized/
```

## Aligned Standardized Factors

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

Stored in:

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

## MCDA Outputs

Continuous susceptibility:

```text
data/analysis/mcda/flood_susceptibility.tif
```

Classified susceptibility:

```text
data/analysis/mcda/flood_susceptibility_classified.tif
```

---

# Current Capabilities

At the completion of Phase 8, the project can:

* Acquire and organize GIS datasets.
* Validate raster and vector datasets.
* Verify coordinate reference systems.
* Prepare analysis-ready spatial data.
* Process DEM data.
* Perform terrain analysis.
* Generate slope.
* Generate aspect.
* Perform hydrological analysis.
* Generate flow direction.
* Generate flow accumulation.
* Extract stream networks.
* Generate watershed outputs.
* Rasterize river data.
* Calculate distance to rivers.
* Prepare land-cover data.
* Prepare population exposure data.
* Generate flood-conditioning factors.
* Standardize continuous factors.
* Reclassify categorical land-cover data.
* Validate standardized factors.
* Align raster datasets spatially.
* Resample continuous population data using bilinear interpolation.
* Resample categorical land cover using nearest-neighbour interpolation.
* Validate aligned factors.
* Derive AHP-based factor weights.
* Validate AHP consistency.
* Perform cell-by-cell weighted MCDA overlay.
* Generate a continuous flood susceptibility surface.
* Independently reproduce the MCDA calculation.
* Classify susceptibility into five categories.
* Independently reproduce the classification.
* Validate spatial and numerical output properties.
* Visually inspect outputs in QGIS.
* Maintain reproducible Python workflows.
* Maintain a validation-driven development process.
* Maintain Git-based version control.
* Document methodological decisions.

---

# Validation Status

Validation is a central component of the project architecture.

## Phase 6

Standardized-factor validation:

```text
Elevation              PASS
Slope                  PASS
Distance to Rivers     PASS
Population             PASS
Land Cover             PASS
```

## Phase 7

Aligned-factor validation:

```text
Total Checks: 76
Passed:       76
Failed:        0

Status:
PASS
```

## Phase 8 AHP

AHP consistency:

```text
PASS
```

Consistency Ratio:

```text
0.0269475117
```

## Phase 8 MCDA

Independent MCDA reproduction:

```text
PASS
```

Valid cells:

```text
553860
```

Maximum MCDA difference:

```text
0.000000029880
```

## Phase 8 Classification

Independent classification reproduction:

```text
PASS
```

Differing cells:

```text
0
```

## Phase 8 Overall Status

```text
MCDA Modelling:                    PASS
AHP Consistency:                   PASS
MCDA Independent Reproduction:     PASS
Classification:                    PASS
Classification Reproduction:       PASS
QGIS Visual Verification:          PASS

PHASE 8:                           COMPLETED
```

---

# Interpretation of Current Results

The continuous susceptibility raster represents the **relative susceptibility pattern** produced by the selected factors and AHP weights.

The susceptibility values should be interpreted as a **relative susceptibility index**.

They should not be interpreted as direct predictions of:

* Flood depth
* Flood velocity
* Flood discharge
* Flood probability
* Flood return period

The classified map provides a more interpretable representation of the continuous susceptibility surface by dividing valid modelling cells into five relative susceptibility categories:

```text
1 — Very Low
2 — Low
3 — Moderate
4 — High
5 — Very High
```

The model is therefore best understood as a **spatial decision-support product** for identifying areas requiring further investigation, prioritization, or risk-management attention.

---

# Important Model Limitations

The current model should not be interpreted as a complete hydraulic flood model.

The susceptibility surface is dependent on:

* Selected conditioning factors
* Quality of input datasets
* Spatial resolution of input datasets
* Standardization methods
* AHP pairwise comparisons
* Selected factor weights
* Modelling grid
* Treatment of NoData areas
* Classification methodology

The current output represents **relative flood susceptibility** and should not be interpreted as a direct measurement of:

* Flood depth
* Flood velocity
* Flood discharge
* Flood probability
* Flood return period
* Individual property-level flood risk

Further validation against observed flood events and additional hydrological or hydraulic information would strengthen the model.

Population is currently incorporated as an exposure-related factor and should therefore not be interpreted as a direct physical mechanism controlling flood generation.

---

# Phase 9 — Flood Susceptibility Validation

**Status: ⏳ UPCOMING**

Phase 9 will evaluate the flood susceptibility model beyond the computational reproducibility checks already completed during Phase 8.

The existence of a successfully generated and computationally reproduced raster does not by itself establish that the model is environmentally or decision-theoretically appropriate.

Phase 9 will therefore focus on broader analytical validation.

Planned work includes:

* Assessing the spatial distribution of susceptibility classes.
* Examining the spatial pattern of high-susceptibility areas.
* Examining relationships between susceptibility and river proximity.
* Examining relationships between susceptibility and elevation.
* Examining relationships between susceptibility and slope.
* Examining relationships between susceptibility and land cover.
* Examining population exposure within susceptible areas.
* Investigating the influence of individual conditioning factors.
* Assessing model behaviour.
* Assessing robustness of the susceptibility results.
* Identifying uncertainty and potential sources of error.
* Comparing results with suitable reference information where available.
* Documenting the validation methodology.
* Producing evidence-based conclusions about model performance.

Phase 9 will build directly upon the validated continuous and classified susceptibility products produced during Phase 8.

---

# Phase 10 — GeoAI Interpretation and Decision Support

**Status: ⏳ UPCOMING**

Phase 10 will introduce the GeoAI interpretation and spatial decision-support component.

The GeoAI layer will operate on validated spatial outputs.

Its purpose will be to **interpret and explain the GIS results rather than replace the underlying geospatial analysis**.

The intended system should ultimately help answer questions such as:

* Where are the areas of highest flood susceptibility?
* Which factors contribute to the susceptibility?
* Why does a particular area receive a high susceptibility score?
* Where are potentially exposed populations concentrated?
* What spatial evidence supports the interpretation?
* Which areas may require greater attention from planners or decision-makers?
* How does susceptibility vary spatially across Nairobi County?

Potential capabilities include:

* Spatial interpretation
* Factor-based explanation
* Priority-area identification
* Spatial queries
* Human-readable summaries
* Population exposure interpretation
* Map-based reasoning
* GeoAI-assisted explanation
* Decision-oriented flood-risk analysis

The GeoAI layer will be developed only after the underlying geospatial modelling and broader validation stages are sufficiently established.

---

# Validation Philosophy

A major principle of this project is that a processing script should not be considered complete merely because it executes successfully.

A project phase is considered complete when the appropriate combination of:

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

has been completed.

This ensures that the project maintains an auditable and reproducible development history.

---

# Professional Quality-Assurance Philosophy

The project follows several quality-assurance principles.

## 1. Reproducibility

Important analytical processes are implemented through Python scripts rather than undocumented manual processing.

## 2. Independent Validation

Validation scripts independently evaluate analytical outputs.

## 3. Spatial Consistency

Raster datasets are spatially aligned before multi-factor modelling.

## 4. Methodological Transparency

Factor transformations, weights, thresholds, CRS decisions, and processing methods are documented.

## 5. NoData Preservation

Missing data are not silently converted into zero susceptibility.

## 6. Separation of Processing Stages

Data acquisition, validation, standardization, spatial alignment, MCDA, classification, validation, and GeoAI interpretation are treated as distinct stages.

## 7. Progressive Quality Control

Each major phase is validated before the project proceeds to the next major stage.

---

# Development Workflow

The project follows a structured development and quality-assurance workflow.

```text
Concept
   ↓
Why It Matters
   ↓
Methodology
   ↓
Implementation
   ↓
Execution
   ↓
Testing
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

After completing a major phase:

1. The implementation is tested.
2. Validation is performed.
3. QGIS is used for visual verification where appropriate.
4. Documentation is updated.
5. Git status is checked.
6. Changes are reviewed.
7. Changes are committed.
8. Changes are pushed to GitHub.
9. The README is updated to reflect the actual project status.

This workflow prevents downstream modelling from being built on unverified intermediate results.

---

# Data and Reproducibility Policy

The repository follows a reproducibility-focused Git policy.

## Tracked

The repository tracks reproducible project artifacts including:

* Python source code
* Validation scripts
* Documentation
* README
* Configuration
* Reproducible processing workflows
* Project structure

## Not Tracked

The repository does not intentionally track:

* Raw datasets
* Large processed datasets
* Generated analytical rasters
* Temporary files
* Python virtual environments
* Machine-specific files

This keeps the repository manageable while preserving the code and documentation required to reproduce the analytical workflow.

The project uses relative paths rather than machine-specific absolute paths wherever possible.

---

# Reproducibility Principles

## 1. Preserve Source Data

Original datasets are kept separate from derived products.

## 2. Do Not Unnecessarily Overwrite Analytical Products

Original factors and standardized factors are preserved separately.

## 3. Separate Processing Stages

Each major transformation has its own script or module.

## 4. Validate Before Moving Forward

A completed processing script is not considered sufficient without validation.

## 5. Use QGIS for Visual Verification

Automated validation is complemented by visual inspection where spatial interpretation is important.

## 6. Version-Control Reproducible Artifacts

Source code, validation scripts, documentation, and configuration are maintained through Git.

## 7. Document Methodological Decisions

Important choices such as:

* CRS
* Standardization relationships
* Land-cover scores
* Reference grid
* Resampling methods
* MCDA weights
* Classification thresholds

are documented rather than hidden inside the implementation.

---

# Repository Structure

```text
GeoAI-flood-risk-agent/
│
├── README.md
│
├── Docs/
│   └── methodology.md
│
├── src/
│   ├── main.py
│   ├── spatial_engine.py
│   ├── data_loader.py
│   ├── data_loader_osm.py
│   ├── geoai_interpreter.py
│   │
│   ├── flood_factors/
│   │   ├── align_standardized_factors.py
│   │   ├── mcda_flood_susceptibility.py
│   │   └── classify_flood_susceptibility.py
│   │
│   ├── validation/
│   │   ├── validate_aligned_factors.py
│   │   ├── validate_mcda_output.py
│   │   └── validate_classified_susceptibility.py
│   │
│   └── utils/
│       └── normalization.py
│
├── data/
│   ├── raw/
│   └── analysis/
│       ├── standardized/
│       ├── aligned/
│       └── mcda/
│
├── requirements.txt
│
└── .venv/
```

Generated datasets, analytical rasters, temporary files, and the Python virtual environment should not be committed to Git.

---

# Analytical Data Flow

The project's analytical data structure follows:

```text
data/analysis/
       │
       ├── standardized/
       │        ↓
       │   Comparable 0–1 factors
       │
       ├── aligned/
       │        ↓
       │   MCDA-ready spatial factors
       │
       └── mcda/
                ↓
       Continuous susceptibility
                ↓
       Classified susceptibility
```

This separation keeps the workflow modular and prevents different analytical stages from being unnecessarily mixed.

---

# Technologies

## Programming

* Python

## GIS and Spatial Analysis

* QGIS
* WhiteboxTools

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

The project is developed in a dedicated Python virtual environment.

```text
.venv/
```

The virtual environment is intentionally excluded from version control.

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

---

# Getting Started

## 1. Clone the Repository

Clone the project repository using Git.

```bash
git clone <repository-address>
```

## 2. Navigate into the Project

```bash
cd GeoAI-flood-risk-agent
```

## 3. Create the Virtual Environment

```bash
python -m venv .venv
```

## 4. Activate the Environment on Windows

```powershell
.venv\Scripts\Activate.ps1
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

Run scripts from the repository root so that the project's relative paths resolve correctly.

---

# Reproducing the Workflow

The project is designed around reproducible, sequential processing.

The general workflow is:

```text
Raw / Prepared Data
        ↓
Validation
        ↓
Analysis-Ready Data
        ↓
Terrain & Hydrological Analysis
        ↓
Flood Conditioning Factors
        ↓
Standardization
        ↓
Standardized-Factor Validation
        ↓
Spatial Alignment
        ↓
Aligned-Factor Validation
        ↓
AHP Weighting
        ↓
AHP Consistency Validation
        ↓
MCDA Weighted Overlay
        ↓
Independent MCDA Validation
        ↓
Susceptibility Classification
        ↓
Independent Classification Validation
        ↓
QGIS Visual Verification
        ↓
Phase 9 Analytical Validation
        ↓
Phase 10 GeoAI Interpretation
```

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

Expected Phase 7 validation result:

```text
76 / 76 checks passed
```

QGIS can then be used to visually inspect the aligned rasters.

---

# Reproducing Phase 8

## Step 1 — Run MCDA

```bash
python src/flood_factors/mcda_flood_susceptibility.py
```

## Step 2 — Validate MCDA

```bash
python src/validation/validate_mcda_output.py
```

Expected result:

```text
OVERALL STATUS: PASS
```

## Step 3 — Classify Susceptibility

```bash
python src/flood_factors/classify_flood_susceptibility.py
```

## Step 4 — Validate Classification

```bash
python src/validation/validate_classified_susceptibility.py
```

Expected result:

```text
OVERALL STATUS: PASS
```

## Step 5 — Visual Verification

Open the continuous and classified outputs in QGIS for complementary visual inspection.

---

# Phase 8 Reproducibility Summary

The complete Phase 8 processing chain is:

```text
Five Aligned Standardized Factors
              ↓
        AHP Pairwise Matrix
              ↓
         AHP Weights
              ↓
      Consistency Validation
              ↓
        Weighted Overlay
              ↓
Continuous Susceptibility Surface
              ↓
    Independent MCDA Validation
              ↓
      Quantile Classification
              ↓
Classified Susceptibility Surface
              ↓
Independent Classification Validation
              ↓
        QGIS Verification
```

---

# Current Project Progress Summary

```text
Phase 1  — Data Acquisition
           ✅ COMPLETED

Phase 2  — Data Validation
           ✅ COMPLETED

Phase 3  — Analysis-Ready Data
           ✅ COMPLETED

Phase 4  — Terrain & Hydrological Analysis
           ✅ COMPLETED

Phase 5  — Flood Conditioning Factors
           ✅ COMPLETED

Phase 6  — Factor Standardization
           ✅ COMPLETED

Phase 7  — Spatial Alignment
           ✅ COMPLETED

Phase 8  — MCDA Flood Susceptibility Modelling
           ✅ COMPLETED

Phase 9  — Flood Susceptibility Validation
           ⏳ UPCOMING

Phase 10 — GeoAI Interpretation & Decision Support
           ⏳ UPCOMING
```

---

# Final Phase 8 Status

Phase 8 successfully transformed the five aligned standardized flood-conditioning factors into a reproducible flood susceptibility model.

The completed workflow was:

```text
Five Standardized Factors
        ↓
Common Spatial Grid
        ↓
AHP Pairwise Comparison
        ↓
Validated Factor Weights
        ↓
Weighted MCDA Overlay
        ↓
Continuous Flood Susceptibility Surface
        ↓
Independent MCDA Validation
        ↓
Quantile Classification
        ↓
Independent Classification Validation
        ↓
QGIS Visual Verification
```

## Phase 8 Final Results

```text
MCDA Modelling:
PASS

AHP Consistency:
PASS

MCDA Independent Reproduction:
PASS

Classification:
PASS

Classification Independent Reproduction:
PASS

QGIS Visual Verification:
PASS
```

Therefore:

```text
PHASE 8:
COMPLETED
```

The project is now ready to proceed to:

```text
PHASE 9
Flood Susceptibility Validation
```

followed by:

```text
PHASE 10
GeoAI Interpretation and Decision Support
```

---

# Phase 9 Entry Point

The starting point for Phase 9 is the validated Phase 8 output:

```text
data/analysis/mcda/flood_susceptibility.tif
```

and its classified counterpart:

```text
data/analysis/mcda/flood_susceptibility_classified.tif
```

Phase 9 will move beyond computational correctness and investigate the **analytical and spatial behaviour** of the model.

---

# Phase 10 Entry Point

Phase 10 will build on the validated outputs from Phases 8 and 9.

The intended progression is:

```text
Validated Flood Susceptibility
        ↓
Spatial Interpretation
        ↓
Factor Contribution Analysis
        ↓
Population Exposure Analysis
        ↓
GeoAI Explanation
        ↓
Spatial Queries
        ↓
Decision Support
```

---

# Future Work

## Phase 9 — Flood Susceptibility Validation

Planned activities:

* Validate susceptibility spatial patterns.
* Analyse susceptibility-class distribution.
* Investigate high-susceptibility areas.
* Compare susceptibility with river proximity.
* Compare susceptibility with terrain characteristics.
* Compare susceptibility with land-cover patterns.
* Examine population exposure.
* Investigate factor influence.
* Assess model robustness.
* Investigate uncertainty.
* Compare against suitable reference information where available.
* Document validation findings.

## Phase 10 — GeoAI Interpretation and Decision Support

Planned activities:

* Develop explainable spatial interpretation.
* Interpret high-susceptibility areas.
* Identify contributing factors.
* Analyse population exposure.
* Develop decision-support outputs.
* Support spatial queries.
* Generate human-readable explanations.
* Build toward an interactive or query-based spatial decision-support system.
* Produce professional final maps and documentation.

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
Independent Validation
 ↓
Analytical Interpretation
 ↓
GeoAI
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
* Progressive quality assurance

The project deliberately separates **model generation** from **model validation** and **interpretation**.

This ensures that a successful computational result is not automatically treated as a fully validated real-world flood-risk model.

---

# What Has Been Achieved So Far

At the current milestone, the project has progressed from raw geospatial data to a validated, reproducible flood susceptibility modelling framework.

The current pipeline has successfully established:

```text
Raw Geospatial Datasets
        ↓
Validated Datasets
        ↓
Analysis-Ready Spatial Framework
        ↓
Terrain & Hydrological Products
        ↓
Five Flood Conditioning Factors
        ↓
Standardized 0–1 Factors
        ↓
Spatially Aligned Factors
        ↓
AHP Weighting
        ↓
AHP Consistency Validation
        ↓
Continuous MCDA Susceptibility
        ↓
Independent MCDA Reproduction
        ↓
Five-Class Susceptibility Map
        ↓
Independent Classification Reproduction
        ↓
QGIS Visual Verification
```

This represents the completion of the **core flood susceptibility modelling pipeline**.

The remaining work is focused on broader validation, interpretation, and the development of the GeoAI decision-support layer.

---

# Author

**Dorothy Stephanie**

GIS | Remote Sensing | Spatial Data Science | Python for Geospatial Analysis | GeoAI

---

# License

This project is developed for educational, research, portfolio, and professional development purposes.

The project methodology, source code, documentation, and analytical workflow are intended to demonstrate reproducible geospatial analysis, spatial modelling, validation, and spatial decision-support development.

---

# Project Status at a Glance

```text
╔══════════════════════════════════════════════════╗
║       GEOAI FLOOD RISK DECISION AGENT            ║
╠══════════════════════════════════════════════════╣
║ Study Area: Nairobi County, Kenya                ║
║ Analysis CRS: EPSG:32737                         ║
║                                                  ║
║ Phase 1  Data Acquisition                 ✅     ║
║ Phase 2  Data Validation                  ✅     ║
║ Phase 3  Analysis-Ready Data              ✅     ║
║ Phase 4  Terrain & Hydrological Analysis  ✅     ║
║ Phase 5  Flood Conditioning Factors       ✅     ║
║ Phase 6  Standardization                  ✅     ║
║ Phase 7  Spatial Alignment                ✅     ║
║ Phase 8  MCDA Modelling                   ✅     ║
║ Phase 9  Validation                       ⏳     ║
║ Phase 10 GeoAI Decision Support           ⏳     ║
║                                                  ║
║ CURRENT MILESTONE: PHASE 8 COMPLETED             ║
║                                                  ║
║ NEXT: PHASE 9 — FLOOD SUSCEPTIBILITY VALIDATION  ║
╚══════════════════════════════════════════════════╝
```
