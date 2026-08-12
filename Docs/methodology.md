# Project Methodology

Project:

GeoAI Flood Risk Decision Agent

Study Area:

Nairobi County, Kenya

Objective:

Develop a GeoAI system capable of assessing flood risk using elevation, population density, river proximity, and land use information.
---

# Phase 6 — Factor Standardization and Normalization

## Purpose

The flood conditioning factors generated during Phase 5 have different units,
value ranges, and data structures.

The continuous factors include:

- Elevation
- Slope
- Distance to Rivers
- Population

These factors cannot be directly combined because they are measured using
different units and scales.

Land Cover is categorical and therefore requires a separate categorical
reclassification approach.

Phase 6 standardizes the flood conditioning factors to a common modelling
scale of 0–1 before Multi-Criteria Decision Analysis (MCDA).

---

## Factor Standardization Methodology

The following factor relationships were established for the flood
susceptibility model:

| Factor | Data Type | Relationship | Standardization Method |
|---|---|---|---|
| Elevation | Continuous | Inverse | Min-Max inverse normalization |
| Slope | Continuous | Inverse | Min-Max inverse normalization |
| Distance to Rivers | Continuous | Inverse | Min-Max inverse normalization |
| Population | Continuous exposure | Positive | Min-Max positive normalization |
| Land Cover | Categorical | Class-dependent | Categorical reclassification |

The direction of the relationship determines whether increasing source
values should increase or decrease the standardized flood contribution.

---

## Positive Min-Max Normalization

For factors where higher source values represent greater flood exposure or
susceptibility, the following transformation is used:

\[
S = \frac{x-x_{min}}{x_{max}-x_{min}}
\]

Where:

- `x` = original raster cell value
- `xmin` = minimum valid value
- `xmax` = maximum valid value
- `S` = standardized score

The resulting values range from 0 to 1.

For the current model, Population uses the positive relationship because
higher population represents greater potential human exposure.

---

## Inverse Min-Max Normalization

For factors where lower source values represent greater flood susceptibility,
an inverse transformation is used:

\[
S = \frac{x_{max}-x}{x_{max}-x_{min}}
\]

This produces:

- Low source value → high standardized score
- High source value → low standardized score

The following factors use inverse normalization:

- Elevation
- Slope
- Distance to Rivers

This reflects the project's conceptual flood-susceptibility relationships.

---

## Factor Relationships

### Elevation

Lower elevation is treated as contributing more strongly to flood
susceptibility because lower-lying areas may provide greater potential for
water accumulation.

Therefore:

**Lower elevation → higher standardized score**

---

### Slope

Lower slopes are treated as contributing more strongly to flood
susceptibility because flatter terrain generally provides greater potential
for slower surface drainage and local water accumulation.

Therefore:

**Lower slope → higher standardized score**

---

### Distance to Rivers

Locations closer to rivers are treated as having greater potential exposure
to river-related flooding.

Therefore:

**Shorter distance → higher standardized score**

---

### Population

Population is treated as an exposure factor.

Higher population values indicate greater potential human exposure in the
event of flooding.

Therefore:

**Higher population → higher standardized score**

Population is standardized using positive Min-Max normalization.

---

# Land Cover Reclassification

Land Cover is a categorical dataset and its class codes are not continuous
measurements.

Therefore, WorldCover class identifiers are not directly normalized.

Instead, each class is assigned a relative flood-susceptibility contribution
based on its land-surface characteristics.

## Land Cover Reclassification Table

| WorldCover Class | Land Cover | Standardized Score | Interpretation |
|---:|---|---:|---|
| 10 | Tree Cover | 0.20 | Vegetation promotes interception, infiltration and surface roughness |
| 20 | Shrubland | 0.30 | Vegetated surface with relatively moderate infiltration |
| 30 | Grassland | 0.45 | Moderate infiltration and surface roughness |
| 40 | Cropland | 0.60 | Disturbed/seasonal vegetation may produce greater runoff |
| 50 | Built-up | 1.00 | Impervious surfaces generally increase runoff generation |
| 60 | Bare / Sparse Vegetation | 0.75 | Limited vegetation and infiltration |
| 80 | Permanent Water | 0.00 | Existing water surface is not treated as additional terrestrial susceptibility |
| 90 | Herbaceous Wetland | 0.15 | Water-retaining environment and therefore not automatically assigned maximum susceptibility |

These scores represent relative modelling weights for the Land Cover factor.
They are not flood probabilities.

The scoring system is therefore interpreted as:

**higher score = greater contribution of the land-cover class to the
susceptibility model.**

Permanent water and wetlands are deliberately not assigned the highest score
simply because they contain or retain water.

---

## Treatment of NoData and Invalid Values

NoData cells are preserved during standardization.

They are not converted into zero-risk values.

Invalid numerical values, including non-finite values such as NaN or infinity,
are excluded from normalization calculations.

The standardized raster preserves the spatial structure of the source raster.

---

## Constant-Value Factors

A factor with identical minimum and maximum valid values cannot be
normalized using Min-Max normalization because the denominator would become
zero.

Such a condition is treated as a validation error rather than silently
assigning an arbitrary score.

---

## Standardized Output

The standardized factors are stored separately from the original flood
conditioning factors.

Original factor rasters remain unchanged.

The standardized outputs are generated in:

```text
data/analysis/standardized/