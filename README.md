# GeoAI Flood Risk Decision Agent

A Python-based geospatial analysis and spatial decision-support project for relative flood-susceptibility mapping in Nairobi County, Kenya.

The project integrates **GIS, remote sensing, terrain analysis, hydrological processing, raster analysis, factor standardization, spatial alignment, Multi-Criteria Decision Analysis (MCDA), Analytic Hierarchy Process (AHP), sensitivity analysis, uncertainty assessment, external validation, QGIS verification, and GeoAI-oriented interpretation** into a reproducible geospatial workflow.

The project deliberately distinguishes between building a technically reproducible model and demonstrating that the model accurately represents real-world flood occurrence.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Vision](#project-vision)
3. [Project Goal and Objectives](#project-goal-and-objectives)
4. [Study Area](#study-area)
5. [Project Status](#project-status)
6. [Project Roadmap](#project-roadmap)
7. [Phases 1–3: Data Acquisition, Validation, and Preparation](#phases-13-data-acquisition-validation-and-preparation)
8. [Phase 4: Terrain and Hydrological Analysis](#phase-4-terrain-and-hydrological-analysis)
9. [Phase 5: Flood-Conditioning Factors](#phase-5-flood-conditioning-factors)
10. [Phase 6: Factor Standardization](#phase-6-factor-standardization)
11. [Phase 7: Spatial Alignment](#phase-7-spatial-alignment)
12. [Phase 8: MCDA Flood-Susceptibility Modelling](#phase-8-mcda-flood-susceptibility-modelling)
13. [Phase 8: Model Outputs and Statistics](#phase-8-model-outputs-and-statistics)
14. [Phase 9: Spatial Diagnostics and Analytical Assessment](#phase-9-spatial-diagnostics-and-analytical-assessment)
15. [Phase 9: Sensitivity and Robustness](#phase-9-sensitivity-and-robustness)
16. [Phase 9: UNOSAT External Validation](#phase-9-unosat-external-validation)
17. [Phase 9: Statistical Evaluation](#phase-9-statistical-evaluation)
18. [Phase 9: Scientific Interpretation](#phase-9-scientific-interpretation)
19. [Model Strengths and Limitations](#model-strengths-and-limitations)
20. [Phase 10: GeoAI Interpretation and Decision Support](#phase-10-geoai-interpretation-and-decision-support)
21. [Technologies](#technologies)
22. [Development Environment](#development-environment)
23. [Repository Structure](#repository-structure)
24. [Analytical Data Flow](#analytical-data-flow)
25. [Getting Started](#getting-started)
26. [Reproducing the Core Workflow](#reproducing-the-core-workflow)
27. [Data and Reproducibility Policy](#data-and-reproducibility-policy)
28. [Validation Philosophy](#validation-philosophy)
29. [Future Research Directions](#future-research-directions)
30. [Project Development Philosophy](#project-development-philosophy)
31. [Author](#author)
32. [License](#license)

---

# Project Overview

The **GeoAI Flood Risk Decision Agent** is a modular Python-based geospatial analysis project focused on flood susceptibility and spatial decision support in Nairobi County, Kenya.

The workflow transforms heterogeneous spatial datasets into standardized and spatially aligned factors, combines those factors using AHP-weighted MCDA, produces a continuous susceptibility surface, classifies the results, and evaluates the model's behaviour using spatial diagnostics, sensitivity analysis, uncertainty assessment, and external reference data.

The project combines:

- Digital Elevation Model (DEM) processing
- Terrain and slope analysis
- Hydrological processing
- River-network and distance-to-rivers analysis
- Land-cover information
- Population-related exposure information
- Raster and vector processing
- Factor standardization and reclassification
- Spatial alignment and resampling
- Analytic Hierarchy Process (AHP)
- Multi-Criteria Decision Analysis (MCDA)
- Relative flood-susceptibility classification
- Independent numerical validation
- Sensitivity and uncertainty assessment
- UNOSAT-based external comparison
- QGIS visual verification
- Scientific interpretation and documentation
- A foundation for future GeoAI-assisted spatial queries

The goal is not simply to produce a flood map. It is to develop a **transparent, reproducible, interpretable, and extensible geospatial decision-support workflow**.

## Project Vision

The long-term vision is to demonstrate how conventional GIS, Python, remote sensing, spatial analysis, and GeoAI-oriented interpretation can be integrated into a decision-support system.

The intended progression is:

```text
Raw Geospatial Data
        |
        v
Data Validation
        |
        v
Analysis-Ready Data
        |
        v
Terrain and Hydrological Analysis
        |
        v
Flood-Conditioning Factors
        |
        v
Factor Standardization
        |
        v
Spatial Alignment
        |
        v
AHP-Weighted MCDA
        |
        v
Relative Susceptibility Surface
        |
        v
Spatial Diagnostics and External Validation
        |
        v
Scientific Interpretation
        |
        v
Future GeoAI Interpretation
        |
        v
Spatial Decision Support
```

The project is developed incrementally so that each stage can be tested, interpreted, documented, and improved independently.

---

# Project Goal and Objectives

The primary goal is to develop a reproducible geospatial modelling and decision-support workflow that can:

1. Acquire and inspect relevant geospatial datasets.
2. Validate source data before analysis.
3. Prepare analysis-ready spatial data.
4. Perform terrain and hydrological processing.
5. Derive flood-conditioning factors.
6. Standardize heterogeneous factors to comparable modelling scores.
7. Align factors to a common spatial grid.
8. Assign and validate MCDA weights using AHP.
9. Produce a continuous relative flood-susceptibility surface.
10. Classify susceptibility scores into five relative categories.
11. Independently validate computational outputs.
12. Investigate spatial patterns and factor influence.
13. Test sensitivity to changes in factor weights.
14. Assess uncertainty and limitations.
15. Compare model outputs with suitable independent reference information.
16. Communicate the scientific meaning and limitations of the results.
17. Establish a foundation for future GeoAI-assisted spatial interpretation.

---

# Study Area

## Nairobi County, Kenya

The project focuses on Nairobi County, Kenya.

The study area provides an opportunity to investigate spatial variation in terrain, river proximity, land cover, and population distribution within an urban environment.

The analysis incorporates spatial factors representing both environmental conditions and population-related exposure. These dimensions must be interpreted carefully because population exposure is not the same as the physical processes that generate flooding.

## Coordinate Reference System

The principal modelling coordinate reference system is:

```text
EPSG:32737
WGS 84 / UTM Zone 37 South
```

A projected coordinate system supports distance calculations, raster processing, terrain analysis, spatial overlays, and cell-based modelling using metric units.

---

# Project Status

## Current milestone: Phase 10 - GeoAI Interpretation and Decision Support

Phases 1–8 established the core geospatial processing and MCDA modelling workflow.

Phase 9 extended the project beyond computational correctness to examine spatial behaviour, factor influence, robustness, uncertainty, and external validation.

Phase 9 analytical work, scientific synthesis, external validation, and documentation are complete. The Phase 9 documentation has been committed to GitHub. The current milestone is Phase 10: GeoAI Interpretation and Decision Support.

### Completed phases

- Phase 1 — Data Acquisition
- Phase 2 — Data Validation
- Phase 3 — Analysis-Ready Data
- Phase 4 — Terrain and Hydrological Analysis
- Phase 5 — Flood-Conditioning Factors
- Phase 6 — Factor Standardization
- Phase 7 — Spatial Alignment and MCDA Preparation
- Phase 8 — MCDA Flood-Susceptibility Modelling

### Phase 9 analytical activities completed

- Susceptibility-class distribution analysis
- Spatial-pattern and cohesion analysis
- River-proximity relationship assessment
- Terrain analysis
- Land-cover analysis
- Population-related exposure assessment
- Factor influence analysis
- Sensitivity and robustness analysis
- Uncertainty assessment
- UNOSAT reference-data inspection and preparation
- External spatial validation
- Statistical evaluation
- Scientific interpretation
- Model strengths and limitations assessment
- Final conclusions and documentation handoff preparation

### Current project position

| Phase | Description | Status |
|---|---|---|
| 1 | Data acquisition | Completed |
| 2 | Data validation | Completed |
| 3 | Analysis-ready data | Completed |
| 4 | Terrain and hydrological analysis | Completed |
| 5 | Flood-conditioning factors | Completed |
| 6 | Factor standardization | Completed |
| 7 | Spatial alignment | Completed |
| 8 | MCDA susceptibility modelling | Completed |
| 9 | Spatial assessment, sensitivity, uncertainty, external validation, and synthesis | Final documentation and handoff |
| 10 | GeoAI interpretation and decision support | Not yet started |

**Important:** The current model is a relative susceptibility framework. The UNOSAT comparison did not demonstrate the expected positive relationship between higher susceptibility scores and observed flooding in the evaluated May 2024 reference sample. The model is not presented as a calibrated or validated, generalizable flood-prediction system.

---

# Project Roadmap

```text
PHASE 1
Data Acquisition
        |
        v
PHASE 2
Data Validation
        |
        v
PHASE 3
Analysis-Ready Data
        |
        v
PHASE 4
Terrain and Hydrological Analysis
        |
        v
PHASE 5
Flood-Conditioning Factors
        |
        v
PHASE 6
Factor Standardization
        |
        v
PHASE 7
Spatial Alignment
        |
        v
PHASE 8
MCDA Flood-Susceptibility Modelling
        |
        v
PHASE 9
Spatial Assessment, Robustness,
Uncertainty and External Validation
        |
        v
PHASE 9
Scientific Synthesis and Documentation
        |
        v
PHASE 10
GeoAI Interpretation and Decision Support
```

Phase 10 will build on the documented evidence and limitations established during Phase 9.

---

# Phases 1–3: Data Acquisition, Validation, and Preparation

## Phase 1 — Data Acquisition

The project established its initial geospatial inputs, including data representing:

- Digital elevation
- Administrative boundaries
- Land cover
- Population
- River networks

These datasets provide the source information for subsequent spatial processing and modelling.

## Phase 2 — Data Validation

The source datasets were inspected before analytical use.

Validation considered relevant properties such as:

- File availability and readability
- Coordinate reference systems
- Spatial extent
- Raster dimensions and resolution
- Data types
- NoData behaviour
- Vector geometry
- Spatial coverage
- Dataset integrity

The governing principle is:

> Data should be validated before it is analysed.

## Phase 3 — Analysis-Ready Data

The validated inputs were organized into a consistent spatial framework suitable for terrain analysis, hydrological processing, factor derivation, and subsequent raster modelling.

The projected modelling CRS is EPSG:32737.

---

# Phase 4: Terrain and Hydrological Analysis

Phase 4 derived terrain and hydrological information from the elevation data and related spatial inputs.

The processing workflow used Python geospatial tools and WhiteboxTools.

## Terrain products

- Elevation
- Slope
- Aspect

## Hydrological products

- Flow direction
- Flow accumulation
- Stream network
- Watershed-related analysis products

A stream network was generated using a flow-accumulation threshold of 1,000.

These outputs provided the terrain and hydrological foundation for the flood-conditioning factors.

---

# Phase 5: Flood-Conditioning Factors

Five factors were established for the MCDA framework.

| Factor | Role in the current model |
|---|---|
| Elevation | Terrain-related susceptibility representation |
| Slope | Terrain steepness representation |
| Distance to rivers | Hydrological-proximity representation |
| Land cover | Surface and land-cover characteristics |
| Population | Population-related exposure consideration |

These factors represent different environmental and exposure dimensions. They do not collectively constitute a complete dynamic simulation of flooding.

## Elevation

Elevation was standardized using the model's defined inverse relationship, under which lower elevation receives a higher score.

This is a modelling assumption and should not be interpreted as a universal rule that every lower-elevation location is more flood-prone.

## Slope

Slope was derived from terrain analysis and standardized using the project's defined inverse relationship, with lower slopes receiving higher scores.

The relationship is an explicit model assumption, not a complete representation of runoff or inundation dynamics.

## Distance to rivers

The river network was rasterized and used to calculate distance to rivers.

The river-processing workflow reported 655 river features.

Distance to rivers was standardized using an inverse relationship, so locations closer to mapped rivers receive higher scores.

## Land cover

Land cover was treated as a categorical factor. Its classes were reclassified to modelling scores rather than processed as though the category codes were continuous measurements.

The assigned scores represent relative modelling assumptions, not observed flood probabilities.

## Population

Population was included as a population-related exposure factor.

Population can help describe where people may be present, but it is not a direct physical mechanism that generates flooding. Its role must remain distinct from physical susceptibility and hazard.

---

# Phase 6: Factor Standardization

The five factors originate from different units, value ranges, and meanings. They therefore required standardization before being combined.

Continuous factors were transformed according to the project's defined relationships, while categorical land-cover data were reclassified using a class-to-score mapping.

The intended modelling scale was 0–1.

| Factor | Standardization approach | Intended relationship |
|---|---|---|
| Elevation | Inverse min-max normalization | Lower elevation receives a higher score |
| Slope | Inverse min-max normalization | Lower slope receives a higher score |
| Distance to rivers | Inverse min-max normalization | Closer river proximity receives a higher score |
| Population | Positive normalization | Higher population receives a higher exposure score |
| Land cover | Categorical reclassification | Class-specific scores |

Standardization was separated from spatial alignment so that numerical transformation and raster-grid compatibility could be validated independently.

The scores express the defined modelling relationships. They are not calibrated probabilities of flooding.

---

# Phase 7: Spatial Alignment

Phase 7 prepared the standardized factors for cell-by-cell MCDA.

All factors needed to represent the same geographic location at corresponding row and column positions. A common numerical scale alone is insufficient for raster overlay.

The reference grid was defined by the standardized elevation raster.

## Reference-grid properties

```text
CRS:
EPSG:32737

Width:
1603 columns

Height:
1019 rows

Pixel resolution:
Approximately 30.8655168 metres
```

The alignment workflow checked:

- CRS
- Dimensions
- Resolution
- Spatial transform
- Grid origin
- Spatial extent
- Pixel-to-coordinate relationship
- Valid-cell coverage

Already aligned factors were preserved, while incompatible factors were resampled using methods appropriate to their data type.

The alignment validation reported 76 of 76 checks passed.

This provided the common spatial framework for Phase 8.

---

# Phase 8: MCDA Flood-Susceptibility Modelling

**Status: Completed**

Phase 8 combined the five aligned standardized factors into a continuous susceptibility surface using AHP-weighted Multi-Criteria Decision Analysis.

## AHP-derived factor weights

The model uses the following approximate weights:

| Factor | Weight |
|---|---:|
| Distance to rivers | 0.4353 |
| Elevation | 0.1869 |
| Slope | 0.1869 |
| Land cover | 0.1286 |
| Population | 0.0624 |

The weights express the relative importance assigned to each factor within the selected MCDA framework.

They should not be interpreted as empirical causal effects or independently measured predictive feature importance.

## MCDA workflow

```text
Five Aligned Standardized Factors
                |
                v
       AHP Pairwise Matrix
                |
                v
          Factor Weights
                |
                v
      AHP Consistency Check
                |
                v
        Weighted MCDA Overlay
                |
                v
 Continuous Susceptibility Surface
                |
                v
     Independent MCDA Validation
                |
                v
      Five-Class Classification
                |
                v
 Independent Classification Validation
                |
                v
        QGIS Visual Verification
```

The MCDA implementation and its principal computational validation checks passed.

## Classification

The continuous susceptibility surface was classified into five quantile-based categories:

1. Very Low
2. Low
3. Moderate
4. High
5. Very High

Each class represents 20% of the valid classified cells.

This quantile classification is useful for relative ranking and spatial interpretation. It does not establish absolute flood probability.

---

# Phase 8: Model Outputs and Statistics

## Continuous susceptibility raster

Primary output:

`data/analysis/mcda/flood_susceptibility.tif`

| Property | Value |
|---|---|
| CRS | EPSG:32737 |
| Width | 1,603 cells |
| Height | 1,019 cells |
| Pixel resolution | Approximately 30.8655168 m |
| Valid cells | 553,860 |
| NoData value | -9999 |
| Minimum | 0.483158 |
| Mean | 0.772901 |
| Median | 0.783512 |
| Maximum | 0.932311 |

## Classified susceptibility raster

Primary output:

`data/analysis/mcda/flood_susceptibility_classified.tif`

The classified raster contains five relative susceptibility classes, with class identifier 0 used for NoData.

## Phase 8 validation

The implemented checks included:

- AHP consistency validation
- MCDA output validation
- Independent reproduction of the MCDA calculation
- Classification validation
- Independent reproduction of the classification
- QGIS visual verification

The successful checks establish computational consistency within the tested workflow. They do not independently establish predictive accuracy against real-world flooding.

---

# Phase 9: Spatial Diagnostics and Analytical Assessment

**Status: Completed — analytical assessment, external validation, scientific synthesis, and documentation.**

Phase 9 investigated how the model behaves spatially and how its assumptions influence its outputs.

The objective was to move beyond producing a susceptibility map and evaluate the characteristics and limitations of the resulting surface.

## Susceptibility-class distribution

The five quantile classes each contained 110,772 valid cells, equivalent to 20% of the classified population of valid cells.

This confirms the expected class balance produced by the quantile classification method. It does not demonstrate that the classes have equal observed flood rates.

## Spatial cohesion

The eight-neighbour cohesion analysis reported:

| Metric | Value |
|---|---:|
| Overall cohesion | 0.716721 |
| Very Low cohesion | 0.831075 |
| Low cohesion | 0.645321 |
| Moderate cohesion | 0.639933 |
| High cohesion | 0.670073 |
| Very High cohesion | 0.795077 |

The maximum isolated-cell share was approximately 3.341%, for the Moderate class. The diagnostic categorized the overall pattern as having minor fragmentation.

These findings indicate that the model produces spatially structured susceptibility patterns. Spatial cohesion is a property of the model's output, not evidence that the output correctly identifies flood locations.

## Factor influence

The factor weights indicate that distance to rivers is the most heavily weighted component of the current MCDA model.

Elevation and slope have equal approximate weights, followed by land cover and population.

The sensitivity analysis further indicates that changes to river-distance weighting can have a substantial effect on class assignments.

The interpretation of factor influence is therefore conditional on the selected factors, transformations, and AHP weighting assumptions.

## Population exposure

Population is included as an exposure-related factor. It should not be treated as a direct physical flood-generation mechanism.

Future decision-support work should distinguish the physical susceptibility of a location from the people and assets potentially exposed there.

---

# Phase 9: Sensitivity and Robustness

The sensitivity analysis tested 11 scenarios: the baseline model and scenarios that perturbed factor weights by approximately ±10%.

The analysis used 553,860 common valid cells, representing approximately 33.907% of the full raster grid.

The maximum absolute difference between the reconstructed and baseline susceptibility surfaces was approximately:

```text
0.000000029880
```

This supports numerical consistency in the reconstruction test.

## Selected sensitivity findings

| Perturbation | Approximate same-class agreement with baseline |
|---|---:|
| Distance-to-rivers weight increased by 10% | 79.77% |
| Slope weight perturbation | Approximately 95% |
| Elevation weight perturbation | Approximately 92% |

The results show that robustness is factor-dependent. In the reported scenarios, the river-distance weight has a greater effect on susceptibility classification than the tested slope or elevation perturbations.

These experiments evaluate sensitivity to selected weighting assumptions. They do not establish predictive accuracy or prove that the baseline weights are optimal.

---

# Phase 9: UNOSAT External Validation

## Purpose

The external validation compared the susceptibility model with prepared UNOSAT flood extent observations associated with satellite imagery acquired on 1 May 2024.

This analysis asked whether locations receiving higher model susceptibility scores also corresponded to observed flood extent within the available reference-data domain.

External validation is different from computational validation: a model can calculate its scores correctly while failing to show the expected relationship with observed flooding.

## Reference data

The primary local flood extent layer is:

`PL_20240501_FloodExtent_Nairobi_Kiambu.shp`

The reference-data workflow included:

1. Inspecting the available reference files and metadata.
2. Preparing the flood geometry.
3. Inspecting the observation domain.
4. Accounting for cloud-obstruction information.
5. Intersecting the reference coverage with the valid model footprint.
6. Rasterizing the flood geometry.
7. Aligning the reference raster with the MCDA grid.
8. Distinguishing flood, non-flood, and unobserved cells.
9. Performing spatial and statistical evaluation.

The prepared reference raster is:

`results/phase9_validation/external_validation/unosat_flood_reference_aligned.tif`

The source metadata indicates that confidence was still to be evaluated and that field validation had not yet been completed. This uncertainty is relevant to the interpretation of the results.

## Raster preparation checks

The prepared flood geometry covered approximately 18.34 km² within the valid MCDA footprint. The rasterized flood area was approximately 18.29 km², with about 99.73% of the flood geometry retained in the rasterization diagnostic.

The reference raster was aligned with the model grid using EPSG:32737, 1,603 columns, 1,019 rows, and a resolution of approximately 30.8655168 metres.

These checks support the technical compatibility of the comparison. They do not establish that the reference dataset is complete or error-free.

## Observation domain

The aligned reference contained:

| Metric | Value |
|---|---:|
| Total grid cells | 1,633,457 |
| Observed validation cells | 228,194 |
| Observation coverage of total grid | 13.970% |
| Observed flood cells | 19,201 |
| Observed non-flood cells | 208,993 |
| Observed flood rate | 8.4143% |

The valid observation domain covers only a subset of the model grid. Results must therefore be interpreted as applying to the observed portion of the study area rather than to every modelled cell.

Coverage also varies across susceptibility classes, which complicates direct comparison between classes.

## Observed flood rate by susceptibility class

| Class | Observed cells | Flood cells | Observed flood rate |
|---|---:|---:|---:|
| Very Low | 242 | 10 | 4.13% |
| Low | 25,800 | 3,366 | 13.05% |
| Moderate | 54,963 | 6,441 | 11.72% |
| High | 53,379 | 5,456 | 10.22% |
| Very High | 93,810 | 3,928 | 4.19% |

The observed flood rates do not increase consistently with susceptibility class. The Very High class has a lower observed flood rate than the Low, Moderate, and High classes.

## Area-normalized comparison

The combined High and Very High classes contained approximately 48.87% of the observed flood cells while representing approximately 64.50% of the observed validation domain.

Their observed flood rate was approximately 6.38%, compared with an overall observed-domain flood rate of approximately 8.41%.

The combined Very Low, Low, and Moderate classes contained approximately 51.13% of the observed flood cells while representing approximately 35.50% of the observed validation domain.

The area-normalized analysis therefore did not show the expected concentration of observed flooding in the combined High and Very High classes.

Differences in observation coverage alone did not explain the mismatch.

---

# Phase 9: Statistical Evaluation

Statistical tests were used to examine the relationship between model scores, susceptibility classes, and the prepared UNOSAT reference.

These tests provide complementary evidence. None should be interpreted in isolation as proof of causal relationships or general predictive performance.

## Categorical association

The chi-square test reported:

| Metric | Result |
|---|---:|
| Chi-square statistic | 3904.254376 |
| Degrees of freedom | 4 |
| Cramér's V | 0.130803 |
| Minimum expected cell count | Approximately 20.36 |

The chi-square result indicates an association between the categorical variables in the observed sample. Cramér's V indicates that the magnitude of the categorical association is modest.

Statistical association does not mean the model correctly ranks flood locations.

## Continuous score comparison

The continuous susceptibility scores were lower on average in observed flood cells than in observed non-flood cells.

| Metric | Result |
|---|---:|
| Mean score in flood cells | 0.806270 |
| Mean score in non-flood cells | 0.828836 |
| Difference in means, flood minus non-flood | -0.022566 |
| Median score in flood cells | 0.802959 |
| Median score in non-flood cells | 0.838924 |
| Difference in medians, flood minus non-flood | -0.035965 |
| Mann–Whitney U statistic | 1,427,526,874.5 |
| Rank-biserial correlation | -0.288527 |

The negative mean and median differences indicate that observed flood cells tended to have lower susceptibility scores in this reference sample.

## Rank correlation and discrimination

| Metric | Result |
|---|---:|
| Spearman rank correlation | -0.138730 |
| ROC AUC | 0.355737 |

The Spearman correlation is negative, indicating a weak negative monotonic relationship in the observed sample.

The ROC AUC is below 0.5, indicating reverse-direction discrimination in this particular reference sample.

This is a material negative validation finding. It does not establish that the MCDA approach is universally unsuitable for flood susceptibility assessment, but it does mean that the current model formulation did not demonstrate the expected positive event-level discrimination against this reference.

## Statistical interpretation limitations

Spatial observations may be dependent because neighbouring raster cells can have similar geographic and environmental characteristics. Conventional statistical tests can overstate the amount of independent evidence when spatial dependence is not addressed.

The results also depend on the event, the observation domain, the reference-data quality, the selected model factors, and the implemented weighting assumptions.

The statistical evaluation should therefore be interpreted together with the effect sizes, relationship directions, coverage diagnostics, and reference-data limitations.

---

# Phase 9: Scientific Interpretation

Phase 9 distinguishes four different dimensions of model evaluation.

| Dimension | Finding |
|---|---|
| Computational consistency | Principal model and raster compatibility checks passed |
| Internal spatial behaviour | The susceptibility surface is spatially structured and interpretable |
| Sensitivity and robustness | Results are sensitive to some factor-weight assumptions, particularly river distance |
| External event-level agreement | The UNOSAT comparison did not demonstrate the expected positive susceptibility–flood relationship |

The distinction is important because a model can be computationally consistent and spatially coherent without accurately representing observed flood occurrence.

## What the current model can support

The current model can be used as an exploratory relative susceptibility mapping and spatial-analysis framework. Its outputs can support investigation of how the selected factor assumptions translate into spatial patterns.

The model can also serve as a foundation for learning, methodological experimentation, and future decision-support development.

## What the current model cannot yet claim

The current evidence does not justify describing the model as:

- A validated flood prediction system
- A calibrated flood-probability model
- A generalizable predictor across flood events
- A dynamic rainfall–runoff or hydraulic simulation
- An empirically proven ranking of causal flood drivers

The UNOSAT comparison is one event-level assessment using a reference product with documented limitations. Additional independent observations and further investigation are needed before broader predictive claims can be supported.

## Plausible areas for further investigation

Future research may examine:

- The relationship between static susceptibility factors and the timing and dynamics of a specific flood event.
- The representation of drainage, runoff, river discharge, and other physical processes.
- The suitability of the current factor transformations and weighting assumptions.
- Reference-data uncertainty, spatial coverage, and acquisition timing.
- The effect of spatial dependence on validation metrics.
- Performance across multiple independent flood events.

These are hypotheses and research directions, not established explanations for the observed mismatch.

The existing validation findings are retained as evidence. The model weights and classification thresholds have not been changed merely to improve agreement with the reference event.

---

# Model Strengths and Limitations

## Strengths

### Reproducible processing

The project uses modular Python workflows, explicit raster alignment, validation scripts, and documented processing decisions.

### Multiple-factor integration

Five factors are integrated through an AHP-weighted MCDA framework, creating an interpretable composite surface.

### Spatial interpretability

The continuous and classified rasters allow spatial patterns to be inspected and investigated in GIS software.

### Sensitivity assessment

The 11-scenario analysis provides evidence about the effects of selected weight perturbations and identifies factor-dependent model stability.

### External comparison

The project goes beyond internal numerical checks by comparing the model against independent flood extent information.

### Transparent interpretation

The project reports the negative-direction validation findings and distinguishes technical correctness from predictive performance.

## Limitations

### Event-level validation mismatch

The evaluated UNOSAT reference sample did not support the expected positive relationship between higher susceptibility scores and observed flooding.

### Limited event coverage

One reference event cannot establish generalization across other floods, seasons, or flood mechanisms.

### Incomplete observation coverage

The valid observation domain covers approximately 13.97% of the full raster grid, and coverage differs by susceptibility class.

### Preliminary reference status

The UNOSAT layer's metadata states that confidence was to be evaluated and that field validation had not yet been completed.

### Static model representation

The current model does not dynamically simulate rainfall, runoff, river discharge, drainage capacity, or floodwater movement.

### Weighting assumptions

AHP weights reflect the chosen MCDA framework and are not proof of empirical causal effects.

### Exposure versus physical susceptibility

Population represents an exposure-related consideration rather than a direct physical flood-generation mechanism.

### No probability calibration

The continuous MCDA scores are relative indices, not calibrated probabilities of flooding.

## Overall model assessment

The current project demonstrates a reproducible and interpretable geospatial MCDA workflow with internal diagnostics, sensitivity analysis, uncertainty assessment, and transparent external validation.

However, the UNOSAT comparison identifies a substantial limitation in the expected event-level relationship between susceptibility and observed flooding.

The most defensible current description is:

> An exploratory AHP-weighted MCDA framework for relative flood-susceptibility mapping and spatial decision support in Nairobi County, with documented internal diagnostics and external validation findings that identify priorities for further development.

---

# Phase 10: GeoAI Interpretation and Decision Support

**Status: In progress — initial project audit and interpretation design.**

Phase 10 will build on the analytical outputs and limitations documented in Phase 9.

The objective is to develop an interpretable layer that helps users understand the model's spatial outputs, explore factor contributions, and formulate spatial questions.

Potential development activities include:

- Explaining susceptibility scores in plain language.
- Interpreting high-scoring locations without treating scores as flood probabilities.
- Exploring the contributions of the five selected factors.
- Separating physical susceptibility from population exposure.
- Supporting natural-language spatial queries.
- Generating structured, evidence-based explanations.
- Exploring QGIS-compatible or GeoJSON outputs.
- Building toward an interactive spatial decision-support interface.
- Communicating uncertainty and validation limitations in user-facing outputs.

Any future GeoAI interface must accurately communicate the limitations established during Phase 9. It should not present the current model as a validated flood predictor.

Phase 9 synthesis and documentation are complete. Phase 10 is the current development milestone and is ready to begin.

---

# Technologies

## Programming and development

- Python
- Visual Studio Code
- Git
- GitHub
- Python virtual environments

## GIS and spatial analysis

- QGIS
- WhiteboxTools

## Python geospatial libraries

- GeoPandas
- Rasterio
- Shapely
- PyProj
- Fiona

## Scientific and data-processing libraries

- NumPy
- Pandas
- SciPy
- scikit-learn

The specific libraries used by each script are defined by its implementation and the project dependency configuration.

---

# Development Environment

The project has been developed in a dedicated Python virtual environment.

```text
Python 3.12.10
```

Recorded core library versions include:

```text
GeoPandas 1.1.3
Rasterio 1.5.0
Shapely 2.1.2
PyProj 3.7.2
Fiona 1.10.1
NumPy 2.5.0
Pandas 3.0.3
```

The installed environment and `requirements.txt` should be checked when reproducing the project because dependency versions can affect geospatial processing behaviour.

The virtual environment is not committed to Git.

---

# Repository Structure

The repository is organized around source code, documentation, validation scripts, configuration, and analytical data directories.

The following is a representative structure; exact filenames and subdirectories may evolve as development continues.

```text
GeoAI-flood-risk-agent/
|
|-- README.md
|-- requirements.txt
|
|-- Docs/
|   |-- methodology.md
|   |-- datasets.md
|   |-- phase9_model_strengths_and_limitations.md
|   |-- phase9_final_conclusions.md
|   |-- unosat_reference_data.md
|
|-- docs/
|   |-- phase9_final_conclusions.md
|   |-- unosat_reference_data.md
|
|-- src/
|   |-- config.py
|   |-- main.py
|   |-- spatial_engine.py
|   |-- data_loader.py
|   |-- data_loader_osm.py
|   |-- geoai_interpreter.py
|   |
|   |-- flood_factors/
|   |   |-- align_standardized_factors.py
|   |   |-- mcda_flood_susceptibility.py
|   |   |-- classify_flood_susceptibility.py
|   |
|   |-- validation/
|   |   |-- validate_aligned_factors.py
|   |   |-- validate_mcda_output.py
|   |   |-- validate_classified_susceptibility.py
|   |   |-- prepare_unosat_flood_reference.py
|   |   |-- validate_susceptibility_against_unosat.py
|   |   |-- evaluate_unosat_statistical_validation.py
|   |
|   |-- utils/
|       |-- normalization.py
|
|-- data/
|   |-- raw/
|   |-- processed/
|   |-- analysis/
|       |-- standardized/
|       |-- aligned/
|       |-- mcda/
|
|-- results/
|   |-- phase9_validation/
|
|-- .venv/
```

This tree is illustrative rather than a guarantee that every listed file exists in precisely that location. The actual repository and local directory structure remain authoritative.

Generated datasets, analytical rasters, temporary files, and the Python virtual environment are excluded from routine source/documentation commits unless there is a specific reason to version a particular artifact.

---

# Analytical Data Flow

The core analytical flow is:

```text
data/analysis/
        |
        |-- standardized/
        |       |
        |       v
        |   Comparable factor scores
        |
        |-- aligned/
        |       |
        |       v
        |   MCDA-ready spatial factors
        |
        |-- mcda/
        |       |
        |       |-- flood_susceptibility.tif
        |       |
        |       |-- flood_susceptibility_classified.tif
        |
        v
Phase 9 diagnostics and external validation
        |
        v
Scientific synthesis and documentation
```

The project separates raw data, standardized factors, aligned factors, MCDA outputs, and validation products to make the workflow easier to inspect and reproduce.

---

# Getting Started

## 1. Clone the repository

```powershell
git clone https://github.com/StephanieDorothy/GeoAI-flood-risk-agent.git
```

## 2. Enter the project directory

```powershell
cd GeoAI-flood-risk-agent
```

## 3. Create a virtual environment

```powershell
python -m venv .venv
```

## 4. Activate the environment on Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, follow the appropriate Python and Windows environment guidance for your machine rather than changing system security settings unnecessarily.

## 5. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Some workflows also require local datasets and external GIS software, including QGIS or WhiteboxTools. Cloning the repository alone does not supply excluded source datasets or generated analytical rasters.

Run project scripts from the repository root so that configured project-relative paths resolve correctly.

---

# Reproducing the Core Workflow

The core processing sequence is:

```text
Prepared Inputs
       |
       v
Input Validation
       |
       v
Terrain and Hydrological Processing
       |
       v
Flood-Conditioning Factors
       |
       v
Standardization
       |
       v
Spatial Alignment
       |
       v
AHP Weighting and Consistency Check
       |
       v
MCDA Susceptibility Surface
       |
       v
Independent MCDA Validation
       |
       v
Quantile Classification
       |
       v
Classification Validation
       |
       v
QGIS Visual Verification
       |
       v
Phase 9 Spatial Diagnostics
       |
       v
Sensitivity and Uncertainty Assessment
       |
       v
External Validation
       |
       v
Scientific Interpretation
```

## Reproducing Phase 7

From the project root:

```powershell
python src/flood_factors/align_standardized_factors.py
```

Then validate the aligned factors:

```powershell
python src/validation/validate_aligned_factors.py
```

The recorded Phase 7 validation result was 76 of 76 checks passed.

## Reproducing Phase 8

Generate the continuous MCDA susceptibility surface:

```powershell
python src/flood_factors/mcda_flood_susceptibility.py
```

Validate the MCDA output:

```powershell
python src/validation/validate_mcda_output.py
```

Generate the classified susceptibility surface:

```powershell
python src/flood_factors/classify_flood_susceptibility.py
```

Validate the classification:

```powershell
python src/validation/validate_classified_susceptibility.py
```

The continuous and classified rasters can then be opened in QGIS for visual inspection.

## Reproducing Phase 9

Phase 9 includes multiple diagnostic and validation scripts under the project's validation directory.

The UNOSAT workflow uses dedicated scripts for reference-data inspection, preparation, rasterization diagnostics, spatial comparison, area-normalized analysis, and statistical evaluation.

The exact execution sequence should follow the existing script dependencies and project documentation. Validation scripts should be run only when their required input data and upstream outputs are available.

**Important:** Reproducing the core MCDA calculation is not the same as reproducing the external validation. The latter also requires the relevant reference data and the prepared observation domain.

---

# Data and Reproducibility Policy

The repository prioritizes reproducible source code and documentation while keeping large or generated data products out of routine commits.

## Normally tracked

- Python source code
- Validation scripts
- Configuration
- Documentation
- README
- Dependency definitions
- Reproducible processing logic

## Normally excluded from Git commits

- `results/`
- Generated analytical rasters
- Large processed datasets
- Temporary processing files
- Local virtual environments
- Machine-specific files

This follows the project's established workflow of pushing source code and documentation while keeping generated results outside the Git commit.

## Reproducibility principles

1. Preserve original data separately from derived products.
2. Avoid unnecessarily overwriting intermediate analytical outputs.
3. Keep processing stages modular.
4. Validate outputs before moving to dependent stages.
5. Use QGIS for visual verification where appropriate.
6. Document methodological decisions.
7. Use version control for source code and documentation.
8. Keep relative paths wherever practical.
9. Preserve negative and inconclusive validation findings.
10. Do not adjust the model merely to obtain a more favourable result against one reference event.

---

# Validation Philosophy

The project separates several kinds of validation because they answer different questions.

| Validation type | Question |
|---|---|
| Input validation | Are the input files readable and suitable for processing? |
| Spatial compatibility | Do rasters share the required spatial grid and alignment? |
| Computational validation | Does the implementation calculate the intended outputs consistently? |
| Internal spatial diagnostics | What spatial patterns does the model produce? |
| Sensitivity analysis | How do selected changes in model assumptions affect outputs? |
| External validation | Do model outputs correspond to independent observations? |
| Scientific interpretation | What conclusions are justified by the evidence? |

Passing computational validation does not guarantee external predictive validity.

Likewise, statistical significance does not automatically demonstrate useful predictive discrimination, causal influence, or generalization to other events.

The project reports these distinctions explicitly.

---

# Future Research Directions

The next development stage is Phase 10, which focuses on GeoAI interpretation and spatial decision support.

Beyond Phase 10, possible research directions include:

- Obtaining independent reference observations for additional flood events.
- Investigating the causes of the observed mismatch between susceptibility scores and the May 2024 flood reference.
- Evaluating alternative factor representations and defensible weighting strategies.
- Incorporating suitable dynamic information, such as rainfall, antecedent wetness, river discharge, and drainage characteristics.
- Separating physical susceptibility, hazard, exposure, and overall risk.
- Evaluating uncertainty and spatial dependence more comprehensively.
- Considering probability calibration only if suitable observations and independent evaluation support it.
- Developing human-readable explanations and spatial queries that communicate uncertainty responsibly.

These are future research directions rather than capabilities already demonstrated by the current model.

Any future model revision should be documented, tested, and evaluated using a defensible validation strategy. A single event should not be used both to tune the model and to claim independent predictive performance.

---

# Project Development Philosophy

This project is being developed as more than a collection of GIS scripts.

It aims to demonstrate an end-to-end professional geospatial workflow involving:

```text
Data Acquisition
       |
       v
Data Validation
       |
       v
Spatial Preparation
       |
       v
Terrain and Hydrological Analysis
       |
       v
Factor Construction
       |
       v
Standardization and Alignment
       |
       v
MCDA Modelling
       |
       v
Independent Validation
       |
       v
Sensitivity and Uncertainty
       |
       v
Scientific Interpretation
       |
       v
GeoAI Development
       |
       v
Decision Support
```

The guiding principles are:

- Reproducibility
- Spatial correctness
- Explicit methodological decisions
- Automated validation
- Visual verification
- Modular code
- Clear documentation
- Version control
- Explainability
- Honest interpretation of negative findings
- Progressive quality assurance

The project deliberately separates model generation, validation, and interpretation so that a successful computational result is never automatically treated as proof of real-world predictive performance.

---

# Author

**Dorothy Stephanie**

GIS | Remote Sensing | Spatial Data Science | Python for Geospatial Analysis | GeoAI

GitHub: [StephanieDorothy](https://github.com/StephanieDorothy)

---

# License

This project is developed for educational, research, portfolio, and professional-development purposes.

The repository's source code, methodology, and documentation demonstrate reproducible geospatial analysis, spatial modelling, validation, and decision-support development. Any formal open-source licensing terms should be defined by the repository's actual license file.

---

# Project Status at a Glance

```text
GEOAI FLOOD RISK DECISION AGENT
Study Area: Nairobi County, Kenya
Analysis CRS: EPSG:32737

Phase 1   Data Acquisition                  COMPLETED
Phase 2   Data Validation                   COMPLETED
Phase 3   Analysis-Ready Data               COMPLETED
Phase 4   Terrain and Hydrological Analysis COMPLETED
Phase 5   Flood-Conditioning Factors        COMPLETED
Phase 6   Factor Standardization            COMPLETED
Phase 7   Spatial Alignment                 COMPLETED
Phase 8   MCDA Susceptibility Modelling     COMPLETED
Phase 9   Diagnostics and External
          Validation                        ANALYSIS COMPLETED
Phase 9   Final Documentation and Handoff   COMPLETED
Phase 10  GeoAI Decision Support            IN PROGRESS

CURRENT MILESTONE:
Phase 10 - GeoAI Interpretation and Decision Support.

NEXT MILESTONE:
Implement and test the Phase 10 GeoAI interpretation and decision-support capabilities.
```

**Scientific qualification:** The current MCDA scores are relative susceptibility indices, not calibrated flood probabilities. The evaluated UNOSAT comparison did not demonstrate the expected positive relationship between higher susceptibility scores and observed flooding. This limitation remains part of the project's documented evidence and guides future development.
