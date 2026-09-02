# Project Methodology

**Project:**
GeoAI Flood Risk Decision Agent

**Study Area:**
Nairobi County, Kenya

**Objective:**
Develop a GeoAI-powered spatial decision-support system capable of assessing flood susceptibility and supporting flood-risk decision-making using terrain, hydrological, population, and land-cover information.

---

# Phase 6 — Factor Standardization and Normalization

## 1. Purpose

The flood-conditioning factors generated during Phase 5 have different units, value ranges, spatial resolutions, and data structures.

The continuous factors include:

* Elevation
* Slope
* Distance to Rivers
* Population

These factors cannot be directly combined because they are measured using different units and scales.

Land Cover is categorical and therefore requires a separate categorical reclassification approach.

Phase 6 standardizes the five flood-conditioning factors to a common modelling scale of **0–1** before Multi-Criteria Decision Analysis (MCDA).

The standardized score represents the relative contribution of each raster cell to the flood-susceptibility model.

A higher standardized score represents a greater contribution to flood susceptibility or potential exposure, according to the conceptual relationship defined for each factor.

---

## 2. Factor Standardization Methodology

The following factor relationships were established for the flood-susceptibility model:

| Factor             | Data Type           | Relationship    | Standardization Method         |
| ------------------ | ------------------- | --------------- | ------------------------------ |
| Elevation          | Continuous          | Inverse         | Min-Max inverse normalization  |
| Slope              | Continuous          | Inverse         | Min-Max inverse normalization  |
| Distance to Rivers | Continuous          | Inverse         | Min-Max inverse normalization  |
| Population         | Continuous exposure | Positive        | Min-Max positive normalization |
| Land Cover         | Categorical         | Class-dependent | Categorical reclassification   |

The direction of the relationship determines whether increasing source values should increase or decrease the standardized flood contribution.

---

## 3. Positive Min-Max Normalization

For factors where higher source values represent greater flood exposure or susceptibility, the following transformation is used:

$$
S = \frac{x-x_{min}}{x_{max}-x_{min}}
$$

Where:

* `x` = original raster cell value
* `xmin` = minimum valid value
* `xmax` = maximum valid value
* `S` = standardized score

The resulting values range from 0 to 1.

For the current model, **Population** uses the positive relationship because higher population values represent greater potential human exposure in the event of flooding.

---

## 4. Inverse Min-Max Normalization

For factors where lower source values represent greater flood susceptibility, an inverse transformation is used:

$$
S = \frac{x_{max}-x}{x_{max}-x_{min}}
$$

This produces:

* Low source value → high standardized score
* High source value → low standardized score

The following factors use inverse normalization:

* Elevation
* Slope
* Distance to Rivers

This reflects the project's conceptual flood-susceptibility relationships.

---

## 5. Factor Relationships

### 5.1 Elevation

Lower elevation is treated as contributing more strongly to flood susceptibility because lower-lying areas may provide greater potential for water accumulation.

Therefore:

**Lower elevation → higher standardized score**

---

### 5.2 Slope

Lower slopes are treated as contributing more strongly to flood susceptibility because flatter terrain generally provides greater potential for slower surface drainage and local water accumulation.

Therefore:

**Lower slope → higher standardized score**

---

### 5.3 Distance to Rivers

Locations closer to rivers are treated as having greater potential exposure to river-related flooding.

Therefore:

**Shorter distance → higher standardized score**

---

### 5.4 Population

Population is treated as an exposure factor.

Higher population values indicate greater potential human exposure in the event of flooding.

Therefore:

**Higher population → higher standardized score**

Population is standardized using positive Min-Max normalization.

---

# Phase 6 — Land Cover Reclassification

Land Cover is a categorical dataset and its class codes are not continuous measurements.

Therefore, WorldCover class identifiers are not directly normalized.

Instead, each class is assigned a relative flood-susceptibility contribution based on its land-surface characteristics.

## 6.1 Land Cover Reclassification Table

| WorldCover Class | Land Cover               | Standardized Score | Interpretation                                                                              |
| ---------------: | ------------------------ | -----------------: | ------------------------------------------------------------------------------------------- |
|               10 | Tree Cover               |               0.20 | Vegetation promotes interception, infiltration, and surface roughness                       |
|               20 | Shrubland                |               0.30 | Vegetated surface with relatively moderate infiltration                                     |
|               30 | Grassland                |               0.45 | Moderate infiltration and surface roughness                                                 |
|               40 | Cropland                 |               0.60 | Disturbed or seasonal vegetation may produce greater runoff                                 |
|               50 | Built-up                 |               1.00 | Impervious surfaces generally increase runoff generation                                    |
|               60 | Bare / Sparse Vegetation |               0.75 | Limited vegetation and infiltration                                                         |
|               80 | Permanent Water          |               0.00 | Existing water surface is not treated as additional terrestrial susceptibility              |
|               90 | Herbaceous Wetland       |               0.15 | Water-retaining environment and therefore not automatically assigned maximum susceptibility |

These scores represent relative modelling weights for the Land Cover factor.

They are **not flood probabilities**.

The scoring system is therefore interpreted as:

**Higher score = greater contribution of the land-cover class to the susceptibility model.**

Permanent water and wetlands are deliberately not assigned the highest score simply because they contain or retain water.

---

## 7. Treatment of NoData and Invalid Values

NoData cells are preserved during standardization.

They are not converted into zero-risk values.

Invalid numerical values, including non-finite values such as `NaN` or infinity, are excluded from normalization calculations.

The standardized raster preserves the spatial structure of the source raster.

---

## 8. Constant-Value Factors

A factor with identical minimum and maximum valid values cannot be normalized using Min-Max normalization because the denominator would become zero.

Such a condition is treated as a validation error rather than silently assigning an arbitrary score.

---

## 9. Standardized Outputs

The standardized factors are stored separately from the original flood-conditioning factors.

Original factor rasters remain unchanged.

The standardized outputs are generated in:

```text
data/analysis/standardized/
```

The standardized factors produced during Phase 6 are:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

Phase 6 validation confirmed that the standardized factors satisfied the required numerical relationships and score ranges.

The standardized factors therefore became the inputs to Phase 7.

---

# Phase 7 — Spatial Alignment and MCDA Preparation

## 1. Overview

Phase 7 prepares the standardized flood-conditioning factors for cell-by-cell Multi-Criteria Decision Analysis (MCDA).

The preceding Phase 6 standardized the five flood-conditioning factors to a common suitability-score range of **0 to 1**.

However, standardization alone does not guarantee that the rasters share the same spatial grid.

The factors originated from datasets with different spatial resolutions and grid structures.

For MCDA, every factor must represent the same geographic location in the same raster cell.

Phase 7 therefore establishes a common spatial reference grid and aligns all standardized flood-conditioning factors to that grid.

---

## 2. Phase 7 Objective

The objective of Phase 7 is to produce five spatially aligned standardized flood-conditioning rasters that can be combined cell-by-cell during the MCDA stage.

The aligned factors are:

1. Elevation
2. Slope
3. Distance to Rivers
4. Population
5. Land Cover

The resulting rasters are stored separately from the original standardized rasters.

Original Phase 6 standardized rasters are not overwritten.

---

## 3. Why Spatial Alignment Was Necessary

The five standardized factors originated from datasets with different spatial resolutions and grid structures.

Although the factors were standardized to a common 0–1 scale during Phase 6, they were not initially guaranteed to share the same raster grid.

For example:

* Population had a source resolution of approximately **92.60 m**.
* Land Cover had a source resolution of approximately **9.26 m**.
* The selected reference grid has a resolution of approximately **30.87 m**.

A common numerical scale does not make raster cells spatially equivalent.

Without spatial alignment, a mathematical cell-by-cell MCDA operation could combine values that do not represent exactly the same geographic location.

Spatial alignment therefore establishes a common computational framework in which every factor contributes information from corresponding geographic cells.

---

# 4. Reference Grid

The standardized elevation raster was selected as the reference grid:

```text
elevation_score.tif
```

The reference grid uses:

```text
CRS:
EPSG:32737

Coordinate Reference System:
WGS 84 / UTM Zone 37S

Dimensions:
1603 columns × 1019 rows

Pixel size:
30.865516819072 m × 30.865516819072 m

Raster orientation:
North-up

X pixel size:
+30.865516819072 m

Y pixel size:
-30.865516819072 m
```

The negative Y pixel size is expected for a conventional north-up raster because raster rows progress downward while projected Y coordinates decrease toward the south.

The reference transform and spatial extent were inherited directly by the aligned outputs.

Using a single reference raster ensures that all factors share the same:

* CRS
* Raster dimensions
* Pixel size
* Grid origin
* Affine transform
* Spatial extent
* Pixel-to-coordinate relationship

---

# 5. Alignment Strategy

The alignment workflow uses the standardized elevation raster as the reference grid.

Each standardized factor is compared against this reference before any resampling is performed.

This prevents unnecessary modification of factors that are already spatially compatible with the target grid.

The alignment strategy is therefore:

1. Identify the reference grid.
2. Inspect each standardized factor.
3. Determine whether its grid matches the reference.
4. Preserve already-aligned factors without resampling.
5. Resample factors that have incompatible grid structures.
6. Write the aligned factors to a separate output directory.
7. Validate the resulting grids and numerical properties.

---

## 5.1 Elevation

The elevation standardized raster already matched the reference grid.

No resampling was performed.

The raster was copied to the aligned directory while preserving its values and spatial structure.

---

## 5.2 Slope

The slope standardized raster already matched the reference grid.

No resampling was performed.

Its values were preserved exactly.

---

## 5.3 Distance to Rivers

The standardized distance-to-rivers raster already matched the reference grid.

No resampling was performed.

Its values were preserved exactly.

---

## 5.4 Population

The population standardized raster originally had a coarser spatial resolution of approximately **92.60 m**.

It was resampled onto the reference grid using:

```text
Bilinear interpolation
```

Bilinear interpolation was selected because population is represented as a continuous numerical surface.

The operation changes the raster representation onto the common grid; it does not create new population observations.

The resulting population factor can therefore participate in cell-by-cell MCDA on the same spatial grid as the other factors.

---

## 5.5 Land Cover

The standardized land-cover factor originated from a finer-resolution dataset of approximately **9.26 m**.

It was resampled onto the reference grid using:

```text
Nearest neighbour
```

Nearest-neighbour resampling was selected to avoid introducing intermediate values through interpolation.

This is appropriate for land-cover-derived categorical information and preserves the class-derived scores assigned during Phase 6.

---

# 6. Output Directory

Aligned standardized factors are stored in:

```text
data/analysis/aligned/
```

The expected outputs are:

```text
elevation_score.tif
slope_score.tif
distance_to_rivers_score.tif
population_score.tif
landcover_score.tif
```

The Phase 6 standardized rasters remain unchanged in:

```text
data/analysis/standardized/
```

This separation preserves the distinction between:

* standardized source factors, and
* MCDA-ready spatially aligned factors.

---

# 7. Alignment Implementation

The alignment process is implemented by:

```text
src/flood_factors/align_standardized_factors.py
```

The script:

1. Identifies the project root using relative paths.
2. Reads the standardized factor rasters.
3. Selects `elevation_score.tif` as the reference grid.
4. Compares each factor against the reference grid.
5. Preserves factors that are already aligned.
6. Resamples population using bilinear interpolation.
7. Resamples land cover using nearest-neighbour interpolation.
8. Writes all outputs to the dedicated aligned directory.
9. Performs immediate grid validation.

The script does **not** apply MCDA weights.

Its purpose is limited to spatial preparation of the standardized factors.

---

# 8. Output Data Structure

The aligned rasters use:

```text
Data type:
float32

NoData:
-9999
```

All aligned factors use the reference spatial grid:

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

The common grid ensures that corresponding cells across the five rasters refer to corresponding geographic locations.

---

# 9. Dedicated Validation

A separate validation script was developed:

```text
src/validation/validate_aligned_factors.py
```

The validation script independently checks:

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
* Minimum standardized score
* Maximum standardized score
* Valid-cell counts
* NoData counts
* Exact value preservation for factors that were already aligned

The validation is intentionally independent from the alignment implementation so that the output is not considered correct merely because the same script that created it reports success.

---

# 10. Validation Results

The dedicated Phase 7 validation produced:

```text
Total checks: 76
Passed:       76
Failed:       0

Overall status:
PASS
```

This confirms that all five aligned standardized factors satisfy the defined spatial and numerical validation requirements.

---

# 11. Standardized Value Range

The standardized factors are expected to remain within:

```text
0 ≤ score ≤ 1
```

The aligned factors remained within the expected standardized range.

The final aligned statistics were:

| Factor             |  Minimum |  Maximum |     Mean |
| ------------------ | -------: | -------: | -------: |
| Elevation          | 0.000000 | 1.000000 | 0.596241 |
| Slope              | 0.000000 | 1.000000 | 0.906355 |
| Distance to Rivers | 0.000000 | 1.000000 | 0.833007 |
| Population         | 0.000000 | 0.976962 | 0.082178 |
| Land Cover         | 0.000000 | 1.000000 | 0.563188 |

Population does not need to have a maximum of exactly 1.0 after resampling.

Its maximum remained within the required standardized range of 0–1.

Resampling can alter the distribution of values while maintaining the factor's valid standardized range.

---

# 12. Value Preservation

Three factors already matched the reference grid and therefore did not require resampling:

* Elevation
* Slope
* Distance to Rivers

The validation process confirmed exact value preservation for these unchanged factors.

This provides an additional reproducibility and quality-assurance check that the alignment workflow did not modify their pixel values unnecessarily.

Population and Land Cover were intentionally resampled because their original raster grids did not match the reference grid.

---

# 13. QGIS Visual Verification

After numerical validation, all five aligned rasters were loaded into QGIS for visual inspection.

The following checks were performed:

1. Each raster was zoomed to its layer extent.
2. Spatial coverage was compared between all five factors.
3. Raster overlays and transparency were used to inspect spatial consistency.
4. Population was inspected after resampling.
5. Land Cover was inspected after nearest-neighbour resampling.
6. Raster properties were checked to confirm the common target grid.
7. The layers were visually inspected for spatial displacement or unexpected shifts.

The five aligned factors visually overlapped correctly.

Population and Land Cover alignment were also visually confirmed.

No obvious spatial displacement or unexpected grid shift was observed.

---

# 14. Quality Assurance Result

Phase 7 therefore passed two complementary quality-assurance stages.

## 14.1 Numerical Validation

```text
76 / 76 checks passed
```

## 14.2 Visual Validation

```text
All five aligned factors visually overlap correctly in QGIS.
```

The combination of automated numerical validation and visual GIS inspection provides evidence that the aligned factors are spatially and numerically suitable for the next modelling stage.

---

# 15. Phase 7 Outputs

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
docs/methodology.md
```

## Generated Analytical Outputs

```text
data/analysis/aligned/
```

The generated raster outputs are analytical project artifacts and should **not** be committed to Git under the project's established repository tracking policy.

The reproducible source code, validation scripts, documentation, configuration, and project structure are tracked instead.

---

# 16. Reproducibility

Phase 7 is reproducible from the tracked source code and project structure.

The alignment workflow uses relative project paths rather than machine-specific absolute paths.

The alignment process can be reproduced by running:

```bash
python src/flood_factors/align_standardized_factors.py
```

Validation can then be reproduced using:

```bash
python src/validation/validate_aligned_factors.py
```

The expected workflow is therefore:

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
```

---

# 17. Phase 7 Completion Status

```text
Phase 7 — Spatial Alignment
STATUS: COMPLETE
```

Completed components:

* Reference grid selection
* Spatial alignment implementation
* Population resampling
* Land-cover resampling
* Alignment validation
* Numerical quality assurance
* QGIS visual verification
* Phase documentation

The five aligned standardized factors are now prepared for the subsequent MCDA preparation and weighted flood-risk modelling stage.

---

# 18. Transition to MCDA

The output of Phase 7 becomes the input to the MCDA workflow.

The overall modelling progression is:

```text
Phase 5
Flood Conditioning Factors
        ↓
Phase 6
Standardized Factors
        ↓
Phase 7
Spatially Aligned Standardized Factors
        ↓
Phase 8
MCDA Weighting
        ↓
Weighted Flood-Risk Surface
        ↓
Flood-Risk Classification
        ↓
Decision Support
```

Phase 7 therefore establishes the spatial foundation required for a valid cell-by-cell MCDA operation.

In the next phase, the aligned standardized factors will be assigned scientifically justified relative weights and combined into a weighted flood-risk surface.



The MCDA stage will use the aligned factors without altering their standardized values and will apply the selected factor weights explicitly during the weighted overlay operation.

# PHASE 8 — MCDA FLOOD SUSCEPTIBILITY MODELLING

**Status: COMPLETED**

## 8.1 Phase Overview

Phase 8 transforms the five standardized and spatially aligned flood-conditioning factors developed in the preceding phases into a single flood susceptibility model using Multi-Criteria Decision Analysis (MCDA).

The purpose of Phase 8 was to combine:

1. Elevation
2. Slope
3. Distance to rivers
4. Land cover
5. Population

into a spatially explicit flood susceptibility surface for Nairobi County.

At the beginning of Phase 8, all five factors had already been:

* converted into standardized 0–1 susceptibility scores,
* spatially aligned to a common analysis grid,
* assigned a common coordinate reference system,
* prepared for cell-by-cell mathematical combination.

The Phase 8 workflow was:

```text
Aligned Standardized Factors
            ↓
AHP Weighting
            ↓
Pairwise Comparison Matrix
            ↓
Derived Factor Weights
            ↓
AHP Consistency Analysis
            ↓
Weight Validation
            ↓
Cell-by-Cell Weighted Overlay
            ↓
Continuous MCDA Susceptibility Surface
            ↓
Independent MCDA Validation
            ↓
Quantile Classification
            ↓
Independent Classification Validation
            ↓
QGIS Visual Inspection
            ↓
Final Flood Susceptibility Products
```

The methodology was designed to be reproducible through Python scripts rather than relying on manual GIS calculations.

---

# 8.2 MCDA Concept

Multi-Criteria Decision Analysis (MCDA) provides a framework for combining multiple factors that contribute to a decision or spatial suitability problem.

In this project, MCDA is used to combine the five flood-conditioning factors into one relative flood susceptibility score for every valid raster cell.

Each factor contributes differently to flood susceptibility. Therefore, the factors cannot simply be added with equal influence without considering their relative importance.

The general weighted linear combination used is:

```math
S = \sum_{i=1}^{n} w_i x_i
```

where:

* `S` = final flood susceptibility score
* `w_i` = weight assigned to factor `i`
* `x_i` = standardized score of factor `i`
* `n` = number of factors

For this project, five factors were used:

```math
S =
w_EE +
w_SS +
w_{DR}DR +
w_{LC}LC +
w_PP
```

where:

* `E` = elevation score
* `S` = slope score
* `DR` = distance-to-rivers score
* `LC` = land-cover score
* `P` = population score

The weights represent the relative contribution of each factor to the final MCDA susceptibility surface.

---

# 8.3 Why Standardization Was Required

The five flood-conditioning factors originate from different datasets and have different measurement units and value ranges.

For example:

* Elevation is measured in metres.
* Slope is measured in degrees.
* Distance to rivers is measured in metres.
* Population represents population-related values.
* Land cover represents categorical land-cover classes.

These variables cannot be directly combined in their original forms because their numerical scales and meanings differ.

Therefore, Phase 6 converted the factors into standardized susceptibility scores on a common 0–1 scale.

The standardized interpretation is:

```text
0
↓
Lower relative contribution to susceptibility

1
↓
Higher relative contribution to susceptibility
```

This allowed the five factors to be mathematically combined during MCDA.

The standardization step was therefore a prerequisite for the weighted overlay.

---

# 8.4 Input Flood-Conditioning Factors

The MCDA model used five standardized and spatially aligned factors.

## 8.4.1 Elevation

Elevation represents terrain height.

The standardized elevation layer expresses relative susceptibility contribution on a 0–1 scale according to the established project standardization methodology.

Lower relative elevation receives a higher susceptibility score within the adopted standardization framework.

---

## 8.4.2 Slope

Slope represents terrain steepness and was derived from the terrain analysis workflow.

The standardized slope factor represents the relative contribution of slope to flood susceptibility.

Under the established standardization methodology:

* flatter areas receive higher susceptibility scores,
* steeper areas receive lower susceptibility scores.

---

## 8.4.3 Distance to Rivers

Distance to rivers represents proximity to the river network.

The standardized distance-to-rivers factor was transformed so that:

* areas closer to rivers receive higher susceptibility scores,
* areas farther from rivers receive lower susceptibility scores.

This factor received the highest weight in the final AHP model.

---

## 8.4.4 Land Cover

Land cover represents the influence of surface-cover characteristics on flood susceptibility.

The standardized land-cover scores were based on the project methodology established during the flood-conditioning-factor and standardization phases.

The adopted relative scores were:

| Land Cover  | Standardized Score |
| ----------- | -----------------: |
| Built-up    |               1.00 |
| Bare/Sparse |               0.75 |
| Cropland    |               0.60 |
| Grassland   |               0.45 |
| Shrubland   |               0.30 |
| Tree Cover  |               0.20 |
| Wetland     |               0.15 |
| Water       |               0.00 |

These values represent the assumed relative contribution of each land-cover category to the susceptibility model.

---

## 8.4.5 Population

Population was included as an exposure-related conditioning factor.

The population score represents the relative concentration of population across the study area.

It is important to distinguish population exposure from physical flood susceptibility.

Population therefore contributes to the composite decision-support model but should not be interpreted as a direct physical measure of flood probability.

---

# 8.5 Spatial Alignment Before MCDA

Before weighted overlay, all five standardized factors were aligned to a common spatial grid.

This was necessary because raster datasets can have different:

* spatial resolutions,
* dimensions,
* origins,
* extents,
* pixel grids.

Mathematically combining rasters with incompatible grids could result in cells representing different geographic locations being combined incorrectly.

Phase 7 therefore established a common MCDA analysis grid.

The reference grid was the aligned elevation factor.

### Common Analysis Grid

```text
CRS:
EPSG:32737

Dimensions:
1603 × 1019

Pixel size:
30.86551681907227 m × 30.86551681907227 m
```

The five aligned factors used by Phase 8 were:

```text
data/analysis/aligned/elevation_score.tif

data/analysis/aligned/slope_score.tif

data/analysis/aligned/distance_to_rivers_score.tif

data/analysis/aligned/landcover_score.tif

data/analysis/aligned/population_score.tif
```

All five factors therefore occupy the same analytical grid before the weighted overlay operation.

---

# 8.6 AHP Weighting Methodology

Because the five factors do not contribute equally to flood susceptibility, defensible factor weights were required.

The Analytic Hierarchy Process (AHP) was selected to derive the weights.

AHP uses pairwise comparisons to express the relative importance of one factor compared with another.

The process consisted of:

```text
Factor identification
        ↓
Pairwise comparison
        ↓
Pairwise comparison matrix
        ↓
Weight derivation
        ↓
Consistency analysis
        ↓
Consistency Ratio
        ↓
Accept or revise weighting judgments
```

The weights were generated from the pairwise comparison matrix rather than being arbitrarily assigned directly.

---

# 8.7 AHP Pairwise Comparison Matrix

The five factors were ordered as:

1. Elevation
2. Slope
3. Distance to rivers
4. Land cover
5. Population

The pairwise comparison matrix used was:

| Factor             | Elevation |  Slope | Distance to Rivers | Land Cover | Population |
| ------------------ | --------: | -----: | -----------------: | ---------: | ---------: |
| Elevation          |    1.0000 | 1.0000 |             0.3333 |     2.0000 |     3.0000 |
| Slope              |    1.0000 | 1.0000 |             0.3333 |     2.0000 |     3.0000 |
| Distance to Rivers |    3.0000 | 3.0000 |             1.0000 |     3.0000 |     5.0000 |
| Land Cover         |    0.5000 | 0.5000 |             0.3333 |     1.0000 |     3.0000 |
| Population         |    0.3333 | 0.3333 |             0.2000 |     0.3333 |     1.0000 |

The matrix follows the reciprocal comparison principle of AHP.

For example:

```math
a_{ij} = \frac{1}{a_{ji}}
```

where applicable.

The diagonal elements are equal to 1 because each factor has equal importance relative to itself.

---

# 8.8 Derived AHP Factor Weights

The pairwise comparison matrix produced the following normalized factor weights:

| Factor             |           Weight |    Percentage |
| ------------------ | ---------------: | ------------: |
| Elevation          |     0.1868744589 |      18.6874% |
| Slope              |     0.1868744589 |      18.6874% |
| Distance to Rivers |     0.4352900433 |      43.5290% |
| Land Cover         |     0.1285887446 |      12.8589% |
| Population         |     0.0623722944 |       6.2372% |
| **Total**          | **1.0000000000** | **100.0000%** |

The weights sum to exactly 1:

```math
\sum w_i = 1.0000000000
```

This satisfies the requirement for normalized weighted overlay.

---

# 8.9 Interpretation of Factor Weights

The largest weight was assigned to distance to rivers:

```text
Distance to rivers = 0.4352900433
                    = 43.5290%
```

This means that distance to rivers has the greatest influence on the final MCDA susceptibility score within the adopted weighting framework.

Elevation and slope each received:

```text
0.1868744589
=
18.6874%
```

Land cover received:

```text
0.1285887446
=
12.8589%
```

Population received:

```text
0.0623722944
=
6.2372%
```

The weights should be interpreted as model-specific relative importance values.

They do not represent universal physical laws or direct percentages of actual flooding.

For example:

```text
Distance-to-rivers weight = 43.53%
```

does not mean:

```text
43.53% of flooding is physically caused by distance to rivers.
```

It means that the factor contributes 43.53% of the weighted MCDA score under the adopted model structure.

---

# 8.10 AHP Consistency Analysis

AHP requires assessment of whether the pairwise comparisons are sufficiently consistent.

The following consistency statistics were calculated.

### Maximum Eigenvalue

```text
Lambda max = 5.1207248525
```

### Consistency Index

The consistency index was calculated as:

```math
CI = \frac{\lambda_{\max}-n}{n-1}
```

where:

* `\lambda_{\max}` = maximum eigenvalue
* `n` = number of factors

For five factors:

```math
CI = \frac{5.1207248525 - 5}{5-1}
```

Result:

```text
CI = 0.0301812131
```

### Random Index

For a five-factor AHP matrix:

```text
RI = 1.12
```

### Consistency Ratio

The consistency ratio was calculated as:

```math
CR = \frac{CI}{RI}
```

Result:

```text
CR = 0.0269475117
```

or approximately:

```text
2.69%
```

The commonly used AHP acceptance criterion is:

```text
CR < 0.10
```

The calculated CR of:

```text
0.0269475117
```

is below the acceptance threshold.

Therefore:

```text
AHP consistency status: PASS
```

The weighting judgments were accepted without requiring modification of the pairwise comparison matrix.

---

# 8.11 Weight Validation

The implementation explicitly validated the derived weights before performing the weighted overlay.

The validation confirmed that:

* all five factors were present,
* weights were numerical,
* weights were positive,
* weights were within the expected range,
* the weights summed to 1.

Final validated weights:

```text
elevation                : 0.1868744589
slope                    : 0.1868744589
distance_to_rivers       : 0.4352900433
landcover                : 0.1285887446
population               : 0.0623722944

Weight sum               : 1.0000000000

Status                   : PASS
```

---

# 8.12 MCDA Weighted Overlay

After the AHP weights passed consistency and weight validation, the five aligned standardized rasters were combined cell-by-cell.

For every valid raster cell, the final susceptibility score was calculated as:

```math
S =
(0.1868744589E)
+
(0.1868744589S)
+
(0.4352900433DR)
+
(0.1285887446LC)
+
(0.0623722944P)
```

where each factor value represents its standardized 0–1 score at that geographic cell.

The operation was performed for every cell for which all five input factors contained valid data.

The weighted overlay therefore produced a continuous spatial susceptibility surface.

---

# 8.13 NoData Handling

NoData handling was treated as an explicit part of the MCDA methodology.

A cell was considered valid only when the required five factor values were valid.

The common valid-cell mask was therefore generated from the aligned factor rasters.

NoData cells were not assigned an artificial susceptibility value.

In particular:

```text
NoData ≠ Very Low susceptibility
```

Instead:

```text
NoData = No valid model result
```

This prevents the model from creating artificial information in areas where the complete set of factor inputs is unavailable.

NoData areas were preserved in the final MCDA raster.

---

# 8.14 Continuous MCDA Susceptibility Surface

The continuous MCDA output was written to:

```text
data/analysis/mcda/flood_susceptibility.tif
```

The output uses the project analysis CRS:

```text
EPSG:32737
```

Raster dimensions:

```text
1603 × 1019
```

Pixel resolution:

```text
30.86551681907227 m × 30.86551681907227 m
```

NoData value:

```text
-9999.0
```

Output data type:

```text
Float32
```

---

# 8.15 Continuous MCDA Results

The generated susceptibility surface contained:

```text
Valid cells:
553,860
```

The principal statistics were:

| Statistic          |    Value |
| ------------------ | -------: |
| Minimum            | 0.483158 |
| 5th percentile     | 0.632628 |
| 25th percentile    | 0.711822 |
| Median             | 0.783512 |
| 75th percentile    | 0.839340 |
| 95th percentile    | 0.884455 |
| Maximum            | 0.932311 |
| Mean               | 0.772901 |
| Standard deviation | 0.079953 |

The output values were confirmed to fall within the expected 0–1 susceptibility-score range for valid cells.

---

# 8.16 Interpretation of Continuous Susceptibility Values

The continuous MCDA surface represents a relative susceptibility score.

The values should not be interpreted as probabilities.

For example:

```text
0.90
```

does not mean:

```text
90% probability of flooding.
```

Instead, a higher MCDA value indicates a higher relative susceptibility score under the adopted factor selection, standardization, and weighting methodology.

Similarly, a lower score indicates lower relative susceptibility within the modeled area.

The continuous surface preserves more numerical information than the classified map and can therefore be used for further quantitative spatial analysis.

---

# 8.17 Independent MCDA Validation

A dedicated independent validation script was developed:

```text
src/validation/validate_mcda_output.py
```

The validation was intentionally separated from the main modelling script.

This ensures that the final product is not considered valid merely because the modelling script executed successfully.

The independent validation checked:

1. Output file existence
2. Raster readability
3. Coordinate reference system
4. Raster dimensions
5. Pixel resolution
6. NoData value
7. Output data type
8. Presence of all aligned input factors
9. Valid-cell mask consistency
10. Finite output values
11. Output numerical range
12. Independent reproduction of the MCDA calculation

---

# 8.18 MCDA Validation Results

The independent validation produced:

```text
Output file exists                         : PASS
GeoTIFF readable                           : PASS
CRS                                        : PASS
Raster dimensions                          : PASS
Pixel resolution                           : PASS
NoData value                               : PASS
Float32 output                             : PASS
All aligned factor rasters                 : PASS
Output mask matches common factor mask     : PASS
All valid cells are finite                 : PASS
Output values within 0-1 range             : PASS
```

The independent calculation compared all:

```text
553,860
```

valid cells.

Results:

```text
Valid cells compared:
553,860

Cells within tolerance:
553,860

Maximum absolute error:
0.000000029880

Mean absolute error:
0.000000014898

Tolerance:
0.000010000000
```

The independent calculation reproduced the generated MCDA surface within the defined numerical tolerance.

Therefore:

```text
Generated MCDA matches independent calculation:
PASS
```

The overall independent MCDA validation status was:

```text
OVERALL STATUS: PASS
```

This provides strong evidence that the implementation is computationally reproducible.

---

# 8.19 Quantile Classification of the Continuous Surface

Although the continuous susceptibility surface is useful for numerical analysis, a classified representation is useful for communication and decision support.

The continuous MCDA surface was therefore classified into five relative susceptibility classes.

The selected classification method was:

```text
Quantile classification
```

Five classes were created:

```text
1 — Very Low
2 — Low
3 — Moderate
4 — High
5 — Very High
```

---

# 8.20 Classification Thresholds

The classification thresholds were derived from the distribution of valid MCDA susceptibility values.

The calculated percentile thresholds were:

```text
20th percentile = 0.69158980
40th percentile = 0.76069050
60th percentile = 0.80517520
80th percentile = 0.84985673
```

The resulting classification structure was:

| Class | Category  | Relative Interpretation              |
| ----: | --------- | ------------------------------------ |
|     1 | Very Low  | Lowest relative susceptibility       |
|     2 | Low       | Relatively low susceptibility        |
|     3 | Moderate  | Intermediate relative susceptibility |
|     4 | High      | Relatively high susceptibility       |
|     5 | Very High | Highest relative susceptibility      |

---

# 8.21 Quantile Class Distribution

The valid MCDA cells were divided into five equal quantile groups.

Total valid cells:

```text
553,860
```

Each class contained:

```text
110,772 cells
```

Distribution:

|     Class | Category  |       Cells |  Percentage |
| --------: | --------- | ----------: | ----------: |
|         1 | Very Low  |     110,772 |      20.00% |
|         2 | Low       |     110,772 |      20.00% |
|         3 | Moderate  |     110,772 |      20.00% |
|         4 | High      |     110,772 |      20.00% |
|         5 | Very High |     110,772 |      20.00% |
| **Total** |           | **553,860** | **100.00%** |

The equal distribution is a consequence of the selected quantile classification method.

It should not be interpreted as meaning that exactly 20% of Nairobi County has an objectively defined level of flood risk.

Instead, it means that the valid modeled cells were divided into five relative susceptibility groups based on their MCDA score distribution.

---

# 8.22 Classified Susceptibility Output

The classified raster was saved as:

```text
data/analysis/mcda/flood_susceptibility_classified.tif
```

The classified raster uses:

```text
CRS:
EPSG:32737

Dimensions:
1603 × 1019

Resolution:
30.86551681907227 m × 30.86551681907227 m

NoData:
0

Data type:
uint8
```

The class values are:

```text
1 = Very Low
2 = Low
3 = Moderate
4 = High
5 = Very High
```

NoData is represented separately as:

```text
0
```

---

# 8.23 Independent Classification Validation

A dedicated validation script was developed:

```text
src/validation/validate_classified_susceptibility.py
```

The validation independently checked the classified susceptibility raster against the continuous MCDA surface.

The validation included:

* file existence,
* CRS,
* dimensions,
* resolution,
* bounds,
* NoData,
* raster array shape,
* valid-cell mask,
* class values,
* presence of all five classes,
* classification thresholds,
* independent classification reproduction,
* class distribution,
* output data type,
* classification metadata.

---

# 8.24 Classification Validation Results

The validation confirmed:

```text
Continuous CRS validation                  : PASS
Classified CRS validation                  : PASS
Continuous dimensions                      : PASS
Classified dimensions                      : PASS
Continuous resolution                      : PASS
Classified resolution                      : PASS
Classified bounds match continuous         : PASS
Continuous NoData                          : PASS
Classified NoData                          : PASS
Raster array shapes match                  : PASS
Valid-cell masks match                     : PASS
Expected valid-cell count                  : PASS
All valid class values finite              : PASS
Class values within 1-5                    : PASS
All five classes present                   : PASS
Independent classification match           : PASS
Equal quantile class distribution          : PASS
Unsigned integer class raster              : PASS
Classification metadata                    : PASS
```

The independent reproduction produced:

```text
Valid cells compared:
553,860

Differing cells:
0
```

Therefore:

```text
Independent classification match:
PASS
```

The overall classification validation status was:

```text
OVERALL STATUS: PASS
```

---

# 8.25 QGIS Visual Verification

Both the continuous and classified susceptibility rasters were visually inspected in QGIS.

The continuous raster:

```text
flood_susceptibility.tif
```

was inspected for:

* spatial continuity,
* unexpected raster artifacts,
* obvious grid displacement,
* unusual rectangular boundaries,
* extreme isolated pixel patterns,
* consistency of the susceptibility gradient.

The classified raster:

```text
flood_susceptibility_classified.tif
```

was inspected for:

* correct display of the five classes,
* spatial consistency with the continuous raster,
* preservation of NoData,
* reasonable spatial distribution of susceptibility categories.

No obvious:

* raster corruption,
* major grid displacement,
* unexpected spatial shift,
* severe rectangular processing artifacts,
* widespread anomalous pixel patterns

were observed during visual inspection.

The continuous and classified outputs were spatially consistent.

---

# 8.26 NoData Interpretation and Professional Handling

The final susceptibility maps contain areas with NoData.

These areas should remain visually distinct from susceptibility classes.

NoData areas do not represent:

```text
Very Low susceptibility
```

They represent locations where a valid model result was not available under the common factor-data mask.

This is acceptable in professional GIS analysis when the underlying input data do not provide sufficient valid information.

NoData should therefore not be filled simply to make the final map visually complete.

Where NoData areas require future remediation, possible actions include:

1. Investigating the original source datasets.
2. Obtaining more complete or higher-quality source data.
3. Correcting source-data problems where appropriate.
4. Applying a scientifically justified gap-filling method where defensible.
5. Reprocessing the affected factor.
6. Re-running spatial alignment.
7. Re-running MCDA.
8. Re-running independent validation.
9. Documenting the change.

Any gap-filling procedure must therefore be scientifically justified and reproducible.

---

# 8.27 Interpretation of the Final Classified Map

The final classified map provides a relative spatial ranking of flood susceptibility.

The classes should be interpreted as:

### Very Low

Locations falling within the lowest relative susceptibility group of the modeled valid cells.

### Low

Locations with relatively low modeled susceptibility.

### Moderate

Locations occupying the intermediate portion of the susceptibility distribution.

### High

Locations with relatively high modeled susceptibility.

### Very High

Locations occupying the highest relative susceptibility group of the modeled valid cells.

The classification does not represent measured flood probability.

The classification is a decision-support representation of the continuous MCDA susceptibility score.

---

# 8.28 Relationship Between the Five Factors and the Final Surface

The final susceptibility surface is the combined result of all five factors.

The model is therefore not based on a single variable.

Conceptually:

```text
Elevation
    +
Slope
    +
Distance to Rivers
    +
Land Cover
    +
Population
    ↓
AHP-derived weights
    ↓
Weighted overlay
    ↓
Composite susceptibility
```

Because the factors are combined cell-by-cell, the final susceptibility value at a location depends on the combined contribution of all available factors.

Distance to rivers has the largest influence because it has the highest weight.

However, the final result is not determined by distance to rivers alone.

---

# 8.29 Important Interpretation of Population

Population has the smallest weight in the final model:

```text
0.0623722944
=
6.2372%
```

This does not mean that population is unimportant for flood-risk decision making.

Rather, the current project uses population as one component of a susceptibility/exposure-oriented decision-support model, and the AHP weighting framework assigns it the lowest relative contribution among the five selected factors.

Future phases may use the susceptibility surface together with exposure and infrastructure information to support broader flood-risk interpretation.

---

# 8.30 Model Limitations

The Phase 8 MCDA model has several important limitations.

## 8.30.1 Relative susceptibility rather than flood probability

The output is a relative susceptibility score.

It does not represent a statistical probability of flooding.

---

## 8.30.2 MCDA is not a physical flood simulation

The model does not directly simulate:

* flood depth,
* hydraulic flow,
* flood velocity,
* rainfall-runoff processes,
* drainage network capacity,
* inundation extent,
* flood duration.

A hydrodynamic or physically based flood model would be required for those purposes.

---

## 8.30.3 Dependence on factor selection

The final susceptibility pattern depends on the five selected factors.

Adding, removing, or replacing factors could change the results.

---

## 8.30.4 Dependence on weighting assumptions

The final surface depends on the AHP pairwise comparison judgments.

Different defensible weighting assumptions could produce different susceptibility patterns.

---

## 8.30.5 Dependence on source-data quality

The accuracy and spatial completeness of the final model are constrained by the quality, resolution, temporal relevance, and completeness of the input datasets.

---

## 8.30.6 Quantile classification is relative

The five classes are based on the distribution of valid MCDA values.

Therefore, class boundaries should not be interpreted as universal physical thresholds.

---

## 8.30.7 NoData areas

Areas without sufficient valid input data remain outside the modeled valid-cell footprint.

These areas require additional investigation if complete spatial coverage is needed.

---

# 8.31 Phase 8 Reproducibility

The Phase 8 workflow was implemented using reproducible Python scripts.

The primary MCDA modelling script is:

```text
src/flood_factors/mcda_flood_susceptibility.py
```

The susceptibility classification script is:

```text
src/flood_factors/classify_flood_susceptibility.py
```

The independent MCDA validation script is:

```text
src/validation/validate_mcda_output.py
```

The independent classification validation script is:

```text
src/validation/validate_classified_susceptibility.py
```

The scripts use project-relative paths so that the workflow is not dependent on a particular computer's absolute directory structure.

---

# 8.32 Phase 8 Processing Workflow

The complete reproducible workflow is:

```text
Phase 6 Standardized Factors
            ↓
Phase 7 Spatial Alignment
            ↓
data/analysis/aligned/
            ↓
mcda_flood_susceptibility.py
            ↓
AHP weighting
            ↓
Weight validation
            ↓
Raster compatibility validation
            ↓
Factor range validation
            ↓
Weighted overlay
            ↓
data/analysis/mcda/flood_susceptibility.tif
            ↓
validate_mcda_output.py
            ↓
Independent MCDA validation
            ↓
classify_flood_susceptibility.py
            ↓
data/analysis/mcda/flood_susceptibility_classified.tif
            ↓
validate_classified_susceptibility.py
            ↓
Independent classification validation
            ↓
QGIS visual inspection
```

---

# 8.33 Phase 8 Reproducible Commands

From the repository root, the continuous MCDA model can be executed with:

```powershell
python src\flood_factors\mcda_flood_susceptibility.py
```

The independent MCDA validation can be executed with:

```powershell
python src\validation\validate_mcda_output.py
```

The classification can be generated with:

```powershell
python src\flood_factors\classify_flood_susceptibility.py
```

The independent classification validation can be executed with:

```powershell
python src\validation\validate_classified_susceptibility.py
```

The expected workflow is therefore:

```text
MCDA modelling
      ↓
MCDA validation
      ↓
Classification
      ↓
Classification validation
      ↓
QGIS visual verification
```

---

# 8.34 Phase 8 Outputs

The principal Phase 8 reproducible source-code artifacts are:

```text
src/
├── flood_factors/
│   ├── mcda_flood_susceptibility.py
│   └── classify_flood_susceptibility.py
│
└── validation/
    ├── validate_mcda_output.py
    └── validate_classified_susceptibility.py
```

The generated analytical outputs are:

```text
data/
└── analysis/
    └── mcda/
        ├── flood_susceptibility.tif
        └── flood_susceptibility_classified.tif
```

The continuous raster represents the numerical MCDA susceptibility surface.

The classified raster represents the five-category relative susceptibility surface.

Generated raster outputs remain analytical data products and are not intended to be committed to GitHub under the project's repository policy.

The repository should instead track:

* source code,
* validation scripts,
* documentation,
* configuration,
* README,
* reproducible processing workflows.

---

# 8.35 Phase 8 Quality Assurance Summary

Phase 8 used multiple levels of quality assurance rather than relying on a single check.

### Level 1 — Weight Validation

Confirmed that:

```text
Weight sum = 1.0000000000
```

Status:

```text
PASS
```

---

### Level 2 — AHP Consistency

Confirmed:

```text
CR = 0.0269475117
```

Status:

```text
PASS
```

---

### Level 3 — Raster Compatibility

Confirmed that all five factors share:

```text
1603 × 1019
EPSG:32737
```

Status:

```text
PASS
```

---

### Level 4 — Factor Range

Confirmed that valid standardized factor values fall within the expected 0–1 range.

Status:

```text
PASS
```

---

### Level 5 — MCDA Output Validation

Confirmed:

* valid raster,
* correct CRS,
* correct dimensions,
* correct resolution,
* correct NoData,
* finite values,
* 0–1 range,
* matching valid-cell mask.

Status:

```text
PASS
```

---

### Level 6 — Independent MCDA Reproduction

Confirmed:

```text
553,860 / 553,860 cells
```

matched the independently calculated result within tolerance.

Status:

```text
PASS
```

---

### Level 7 — Classification Validation

Confirmed:

* five valid classes,
* correct spatial metadata,
* correct valid-cell mask,
* correct quantile thresholds,
* correct class distribution,
* independent classification reproduction.

Status:

```text
PASS
```

---

### Level 8 — QGIS Visual Verification

Confirmed that the continuous and classified products display spatially and are visually consistent.

Status:

```text
PASS
```

---

# 8.36 Phase 8 Final Results

The completed Phase 8 model produced:

```text
Continuous MCDA susceptibility surface
        ↓
flood_susceptibility.tif
```

with:

```text
Valid cells:        553,860
Minimum:            0.483158
Maximum:            0.932311
Mean:               0.772901
Median:             0.783512
Standard deviation: 0.079953
```

The AHP weighting produced:

```text
Elevation              18.6874%
Slope                  18.6874%
Distance to Rivers     43.5290%
Land Cover             12.8589%
Population              6.2372%
```

AHP consistency:

```text
CR = 0.0269475117

Consistency status:
PASS
```

The classified susceptibility product contains:

```text
1 — Very Low
2 — Low
3 — Moderate
4 — High
5 — Very High
```

Each class contains:

```text
110,772 valid cells
```

representing:

```text
20% of valid modeled cells
```

Independent MCDA reproduction:

```text
PASS
```

Independent classification reproduction:

```text
PASS
```

QGIS visual verification:

```text
PASS
```

---

# 8.37 Phase 8 Final Interpretation

Phase 8 successfully transformed five standardized and spatially aligned flood-conditioning factors into a reproducible composite flood susceptibility model.

The final model:

1. Used standardized factor scores on a common 0–1 scale.
2. Applied AHP-derived factor weights.
3. Passed AHP consistency validation.
4. Performed cell-by-cell weighted overlay.
5. Preserved NoData areas.
6. Produced a continuous flood susceptibility surface.
7. Independently reproduced the MCDA calculation.
8. Classified the continuous surface into five relative susceptibility categories.
9. Independently reproduced the classification.
10. Passed spatial and numerical validation.
11. Passed QGIS visual inspection.

The final product should therefore be described as a:

> **Reproducible, spatially explicit, weighted MCDA flood susceptibility model based on five standardized flood-conditioning factors for Nairobi County.**

The output represents relative flood susceptibility within the modeled valid-cell area and is intended as a decision-support layer rather than a direct prediction of flood probability, flood depth, or inundation extent.

---

# 8.38 Phase 8 Completion Status

```text
PHASE 8 — MCDA FLOOD SUSCEPTIBILITY MODELLING
============================================================

AHP weighting                              : COMPLETE
AHP consistency validation                : PASS
Weight validation                         : PASS
Raster compatibility validation           : PASS
Factor range validation                   : PASS
Weighted overlay                          : COMPLETE
Continuous MCDA surface                  : COMPLETE
Independent MCDA validation              : PASS
Quantile classification                   : COMPLETE
Independent classification validation     : PASS
QGIS visual inspection                    : PASS
NoData preservation                       : PASS
Methodology documentation                 : COMPLETE

OVERALL PHASE 8 STATUS:
COMPLETED
```

The Phase 8 analytical chain is therefore:

```text
Five Flood-Conditioning Factors
              ↓
Standardization to 0–1
              ↓
Spatial Alignment
              ↓
AHP Pairwise Comparison
              ↓
Validated Factor Weights
              ↓
AHP Consistency Check
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
              ↓
VALIDATED FLOOD SUSCEPTIBILITY PRODUCTS
```
