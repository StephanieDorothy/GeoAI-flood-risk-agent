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
