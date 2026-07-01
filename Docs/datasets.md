# GeoAI Flood Risk Agent - Dataset Documentation

This document records every dataset used in the GeoAI Flood Risk Agent project.

For each dataset we document:

- Purpose
- Source
- Download date
- Coordinate Reference System (CRS)
- Resolution
- Preprocessing steps
- Validation
- Notes

---

# Dataset 001 — Digital Elevation Model (DEM)

## Purpose
Provides terrain elevation for flood risk modelling. It will later be used to derive:

- Slope
- Flow Direction
- Flow Accumulation
- Terrain Analysis

## Source

Provider:
NASA Shuttle Radar Topography Mission (SRTM)

Resolution:
30 metres

Download Date:
29 June 2026

Original CRS:
EPSG:4326 (WGS84)

## Raw Dataset

Stored locally:

```
data/raw/dem/output_SRTMGL1.tif
```

## Preprocessing

Completed in QGIS.

Steps:

1. Loaded the raw DEM.
2. Loaded the Nairobi County boundary.
3. Clipped the raster using the Nairobi boundary.
4. Saved the clipped raster as:

```
data/processed/dem/dem_nairobi.tif
```

The original raster remains unchanged.

## Validation

Validation script:

```
src/validation/validate_dem.py
```

Checks performed:

- File exists
- CRS
- Resolution
- Raster dimensions
- Elevation statistics
- NoData value
- Raster integrity

Validation completed successfully.

## Notes

The DEM remains in EPSG:4326 for consistency with the other datasets. Reprojection will be performed later during the modelling stage if required.

---

# Dataset 002 — Nairobi County Boundary

## Purpose

Defines the Area of Interest (AOI) for the project.

The boundary is used to:

- Clip raster datasets
- Standardize study extent
- Limit spatial analyses to Nairobi County

## Source

Provider:
geoBoundaries

Country:
Kenya

Administrative Level:
ADM1 (County)

Download Date:
29 June 2026

Original CRS:
EPSG:4326 (WGS84)

## Raw Dataset

Stored locally:

```
data/raw/boundaries/geoBoundaries-KEN-ADM1.geojson
```

## Processed Dataset

The Nairobi County boundary was extracted and saved as:

```
data/processed/vectors/Nairobi_county_boundary.gpkg
```

## Validation

Validated in QGIS by confirming:

- Correct county selection
- Geometry integrity
- CRS
- Extent

## Notes

This boundary will be reused throughout the project for clipping and spatial masking.

---

# Dataset 003 — ESA WorldCover Land Cover

## Purpose

Represents land cover classes across Nairobi.

This dataset will later support:

- Surface runoff estimation
- Impervious surface identification
- Land cover weighting within the flood risk model

## Source

Provider:
European Space Agency (ESA)

Dataset:
WorldCover 2021

Resolution:
10 metres

Download Date:
30 June 2026

Original CRS:
EPSG:4326 (WGS84)

## Raw Dataset

Stored locally:

```
data/raw/landcover/
```

## Preprocessing

Completed in QGIS.

Steps:

1. Loaded the WorldCover raster.
2. Clipped using the Nairobi County boundary.
3. Saved as:

```
data/processed/Landcover/Nairobi Landcover.tif
```

## Validation

Validation script:

```
src/validation/validate_land_cover.py
```

Checks performed:

- File exists
- CRS
- Raster dimensions
- Resolution
- Land cover class values
- Unique class identification
- NoData value

Validation completed successfully.

## Notes

Only the Nairobi subset is used during modelling.

---

# Dataset 004 — WorldPop Population Raster

## Purpose

Represents the spatial distribution of population across Nairobi.

This dataset will later support:

- Exposure analysis
- Population-at-risk estimation
- Risk scoring

## Source

Provider:
WorldPop

Dataset:
Kenya Population Count 2021 (100m)

Temporal Coverage:
2021

Resolution:
100 metres

Download Date:
1 July 2026

Original CRS:
EPSG:4326 (WGS84)

License:
CC BY 4.0

## Raw Dataset

Stored locally:

```
data/raw/population/ken_pop_2021_CN_100m_R2025A_v1.tif
```

## Preprocessing

Completed in QGIS.

Steps:

1. Loaded the national Kenya population raster.
2. Clipped using the Nairobi County boundary.
3. Saved as:

```
data/processed/population/Nairobi population.tif
```

## Validation

Validation script:

```
src/validation/validate_population.py
```

Checks performed:

- File exists
- CRS
- Resolution
- Raster dimensions
- Population statistics
- NoData value
- Raster integrity

Validation completed successfully.

## Notes

The project intentionally uses the 2021 WorldPop dataset to maintain temporal consistency with the 2021 ESA WorldCover dataset.

---

# Dataset Acquisition Workflow

Every dataset used in this project follows the same professional workflow:

1. Understand the dataset
2. Download the raw data
3. Verify metadata
4. Inspect in QGIS
5. Preprocess the data
6. Validate the output
7. Document the dataset
8. Use it in Python
9. Integrate it into the GeoAI model

This workflow ensures reproducibility, transparency, and professional GIS project management.

---

# Repository Philosophy

The GitHub repository contains:

- Source code
- Documentation
- Validation scripts
- Configuration files
- Project structure

The repository does **not** contain:

- Raw datasets
- Processed datasets
- Generated outputs

Anyone reproducing the project can download the datasets from their original sources and follow the documented preprocessing workflow.