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

# Dataset 005 — OpenStreetMap Rivers (Kenya)

## Purpose

This dataset represents rivers and other mapped waterways extracted from OpenStreetMap (OSM). Within the GeoAI Flood Risk Agent, the river network is used to identify areas that are close to natural drainage channels, which is an important factor when assessing flood susceptibility.

---

## Source

Provider:
OpenStreetMap (Geofabrik Extract)

Dataset:
Kenya Waterways

Website:
https://download.geofabrik.de/africa/kenya.html

---

## Raw Dataset

Filename:

gis_osm_waterways_free_1.shp

Stored in:

data/raw/rivers/

The raw dataset is never modified and serves as the permanent reference copy.

---

## Processed Dataset

Filename:

Nairobi_rivers.gpkg

Stored in:

data/processed/rivers/

The processed dataset contains only waterways located within Nairobi County.

---

## CRS

EPSG:4326 (WGS84)

No reprojection was performed during preprocessing.

---

## Preprocessing Workflow

1. Downloaded Kenya waterways dataset from Geofabrik.
2. Loaded the dataset into QGIS.
3. Loaded the Nairobi County boundary.
4. Clipped the waterways using the Nairobi boundary.
5. Exported the clipped dataset as a GeoPackage (.gpkg).
6. Preserved the original CRS (EPSG:4326).

---

## Validation

Validation was completed using:

src/validation/validate_rivers.py

The validation script confirms:

- Dataset exists.
- CRS is correct.
- Geometry type is valid.
- Attribute fields are present.
- Geometry validity was checked before analysis.

---

## Intended Use

The river dataset will later be used to:

- Calculate distance to rivers.
- Generate river proximity layers.
- Support flood susceptibility modelling.
- Improve spatial reasoning within the GeoAI Flood Risk Agent.

---

## Lessons Learned

- Learned the importance of validating vector datasets before analysis.
- Learned why GeoPackage is preferred over Shapefile for processed vector data.
- Learned how river networks contribute to flood risk assessment.

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
## Analysis Preparation

To prepare the DEM for spatial analysis, the processed DEM was reprojected from its original geographic coordinate system (EPSG:4326) into the project's official analysis coordinate system:

**EPSG:32737 – WGS 84 / UTM Zone 37 South**

The reprojected dataset is stored in:

data/analysis/dem/dem_nairobi_utm37s.tif

The original processed DEM remains unchanged.

This analysis-ready DEM will be used throughout the project for:

- Slope generation
- Aspect calculation
- Flow direction
- Flow accumulation
- Terrain analysis
- Flood susceptibility modelling

Reprojection was performed using:

src/preprocessing/reproject_dem.py

Validation was completed using:

src/validation/validate_analysis_dem.py
# Dataset 002 – Nairobi County Boundary

## Purpose
Administrative boundary used to clip all project datasets and define the official Area of Interest (AOI) for the GeoAI Flood Risk Agent.

## Source Dataset

Dataset Name:
Nairobi County Boundary

Original Source:
geoBoundaries (ADM1 Kenya)

Original CRS:
EPSG:4326 (WGS 84)

Processed Dataset

Location:

data/processed/boundaries/Nairobi_county_boundary.gpkg

Processing Steps

- Downloaded ADM1 boundary.
- Extracted Nairobi County.
- Saved as GeoPackage.
- Preserved original CRS (EPSG:4326).

Analysis Dataset

Location:

data/analysis/boundaries/Nairobi_boundary_32737.gpkg

Analysis CRS

EPSG:32737
WGS 84 / UTM Zone 37 South

Validation

✓ Dataset opens successfully.
✓ CRS verified.
✓ Geometry preserved.
✓ Ready for overlay analysis.

Purpose in GeoAI Model

Used for:

- Dataset clipping
- Spatial masking
- Area of Interest definition
- Overlay analysis

# Dataset 003 – ESA WorldCover Land Cover

## Purpose

Represents land cover classes for Nairobi and provides environmental context for flood-risk modelling.

---

## Source Dataset

Dataset Name:

ESA WorldCover 10 m 2021

Provider:

European Space Agency (ESA)

Original CRS:

EPSG:4326

Spatial Resolution:

10 metres

Temporal Coverage:

2021

---

## Processed Dataset

Location:

data/processed/Landcover/Nairobi Landcover.tif

Processing Steps

- Downloaded ESA WorldCover 2021.
- Clipped to Nairobi County.
- Preserved original CRS (EPSG:4326).

---

## Analysis Dataset

Location:

data/analysis/landcover/landcover_32737.tif

Analysis CRS

EPSG:32737

Resampling Method

Nearest Neighbour

Reason

Land cover contains categorical classes.
Nearest Neighbour preserves original class values.

---

## Validation

✓ File opens successfully.

✓ CRS verified as EPSG:32737.

✓ Class values preserved.

✓ Ready for spatial overlay analysis.

---

## Purpose in GeoAI Model

Used for:

- Surface characterization
- Urban vs vegetation analysis
- Flood susceptibility modelling
- Environmental feature extraction

# Dataset 004 – Population.

# Analysis-Ready Population Dataset

# Analysis Version

File Name: population_32737.tif
Location: data/analysis/population/
Coordinate Reference System: EPSG:32737 (WGS 84 / UTM Zone 37 South)
Purpose: Analysis-ready population raster for all distance- and area-based GIS operations within the GeoAI Flood Risk Agent.

# Preprocessing Performed

Clipped the Kenya WorldPop 2021 raster to the Nairobi County boundary.
Preserved the original 100 m spatial resolution.
Reprojected the clipped raster from EPSG:4326 to EPSG:32737.
Used Nearest Neighbour resampling to preserve the original population values.

# Validation

Validation confirmed:

Raster opens successfully.
CRS correctly updated to EPSG:32737.
Population statistics remained consistent after reprojection.
NoData values preserved correctly.

# Dataset 005 – Rivers

# Analysis-Ready Rivers Dataset

# Analysis Version

File Name: rivers_32737.gpkg
Location: data/analysis/rivers/
Coordinate Reference System: EPSG:32737 (WGS 84 / UTM Zone 37 South)
Purpose: Analysis-ready river network used for distance-to-river calculations and flood susceptibility modelling.

# Preprocessing Performed

Downloaded the OpenStreetMap waterways dataset for Kenya.
Clipped the dataset to the Nairobi County boundary.
Preserved all river attributes.
Reprojected from EPSG:4326 to EPSG:32737.

# Validation

Validation confirmed:

Dataset opens successfully.
CRS correctly updated to EPSG:32737.
River geometries preserved after reprojection.
Attribute table retained without data loss.
## Derived Dataset 001 — Slope Raster

### Purpose
Represents terrain steepness derived from the analysis-ready Digital Elevation Model (DEM). Slope is used as an input to the GeoAI Flood Risk Agent because it influences surface runoff and water accumulation.

### Source Dataset
Analysis-ready DEM:
`data/analysis/dem/dem_nairobi_utm37s.tif`

### Processing Method
- Reprojected DEM in EPSG:32737.
- Calculated terrain gradients using NumPy.
- Converted gradients to slope in degrees.
- Preserved NoData areas as -9999.
- Saved as GeoTIFF with LZW compression.

### Output Dataset
`data/analysis/terrain/slope.tif`

### Validation Summary
- CRS: EPSG:32737
- Resolution: 30.87 m
- Minimum Slope: 0.00°
- Maximum Slope: 41.72°
- Mean Slope: 3.91°

### Role in the GeoAI Model
Higher slope values indicate faster runoff, while lower slope values highlight flatter terrain where water is more likely to accumulate. This layer will later be combined with elevation, rivers, land cover, and population in the flood susceptibility model.
## Derived Dataset 002 — Aspect Raster

### Purpose
Represents the compass direction that each terrain cell faces, derived from the analysis-ready Digital Elevation Model (DEM). Aspect is a terrain derivative that helps describe terrain orientation and contributes to hydrological and environmental analyses.

### Source Dataset
Analysis-ready DEM:
`data/analysis/dem/dem_nairobi_utm37s.tif`

### Processing Method
- Used the analysis-ready DEM in EPSG:32737.
- Calculated terrain gradients using NumPy.
- Converted gradients into aspect values expressed in degrees clockwise from north.
- Assigned NoData value (-9999) to flat terrain and original NoData cells.
- Saved as a compressed GeoTIFF using LZW compression.

### Output Dataset
`data/analysis/terrain/aspect.tif`

### Validation Summary
- CRS: EPSG:32737
- Resolution: 30.87 m
- Data Type: Float32
- NoData Value: -9999

### Role in the GeoAI Model
Aspect describes the orientation of terrain surfaces. While not a primary flood predictor on its own, it complements slope and elevation by providing information about terrain orientation, which influences runoff behaviour, soil moisture, and environmental conditions.

## Derived Dataset 003 — Hydrologically Conditioned DEM (Filled DEM)

### Purpose

A hydrologically conditioned Digital Elevation Model created by filling artificial depressions (sinks) in the analysis-ready DEM. This ensures continuous surface drainage for downstream hydrological analyses.

### Source Dataset

`data/analysis/dem/dem_nairobi_utm37s.tif`

### Processing Method

- Used WhiteboxTools `FillDepressions`.
- Filled artificial depressions while preserving the overall terrain.
- Automatically corrected flat areas to ensure continuous drainage.
- Saved as an analysis-ready GeoTIFF.

### Output Dataset

`data/analysis/terrain/filled_dem.tif`

### Validation Summary

- CRS: EPSG:32737
- Same spatial resolution as the analysis DEM.
- Hydrologically conditioned for flow routing.

### Role in the GeoAI Model

The Filled DEM becomes the primary elevation surface for hydrological modelling. All subsequent analyses—including Flow Direction, Flow Accumulation, watershed delineation, and stream extraction—are derived from this dataset instead of the original DEM.
## Derived Dataset 004 — Flow Direction (D8)

### Purpose

A D8 Flow Direction raster generated from the hydrologically conditioned DEM. Each raster cell stores the direction of surface runoff toward its steepest downslope neighbour using the ESRI D8 pointer convention.

### Source Dataset

`data/analysis/terrain/filled_dem.tif`

### Processing Method

- Used WhiteboxTools `D8Pointer`.
- Generated flow direction using the D8 (Deterministic Eight-Neighbour) algorithm.
- Used ESRI pointer encoding.
- Saved as an analysis-ready GeoTIFF.

### Output Dataset

`data/analysis/terrain/flow_direction.tif`

### Validation Summary

- CRS: EPSG:32737
- Raster successfully generated.
- Verified valid ESRI D8 direction codes.
- Ready for Flow Accumulation.

### Role in the GeoAI Model

The Flow Direction raster defines the downstream path of surface runoff for every raster cell. It is the primary input for Flow Accumulation, watershed analysis, stream extraction, and flood susceptibility modelling.

## Derived Dataset 005 — Flow Accumulation

### Purpose

A D8 Flow Accumulation raster generated from the Flow Direction raster. Each raster cell stores the number of upstream cells contributing flow to that location.

### Source Dataset

`data/analysis/terrain/flow_direction.tif`

### Processing Method

- Used WhiteboxTools `D8FlowAccumulation`.
- Input raster used ESRI D8 pointer encoding.
- Output type: Cell Count.
- Saved as an analysis-ready GeoTIFF.

### Output Dataset

`data/analysis/terrain/flow_accumulation.tif`

### Validation Summary

- CRS: EPSG:32737
- Raster generated successfully.
- Verified valid accumulation values.
- Ready for stream network extraction.

### Role in the GeoAI Model

The Flow Accumulation raster identifies areas where runoff converges. It forms the foundation for extracting stream networks, identifying drainage pathways, and modelling flood-prone locations.

## Lessons Learned

During this stage of the project, the following GIS engineering principles were applied:

- Raw datasets should never be modified.
- Processed datasets preserve the original spatial reference after clipping and cleaning.
- Analysis datasets are stored separately and prepared specifically for modelling.
- A projected CRS (EPSG:32737) is required for accurate distance, area, and terrain analysis.
- Reprojection is performed only after preprocessing to preserve the integrity of the original datasets.

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

