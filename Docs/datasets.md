# GeoAI Flood Risk Decision Agent

# Dataset Catalogue

This document records every dataset used in the project to ensure reproducibility, transparency, and proper documentation.

---

# Dataset 001: SRTM Digital Elevation Model (DEM)

## 1. Dataset Overview

**Dataset Name:** SRTM Global 1 Arc-Second Digital Elevation Model (SRTMGL1)

**Theme:** Elevation

**Purpose in Project:**
This dataset provides terrain elevation information for Nairobi County. It forms the foundation of the flood risk model by supporting the derivation of terrain characteristics such as slope and elevation, which influence how surface water flows and accumulates.

---

## 2. Data Source

**Source:** NASA Shuttle Radar Topography Mission (SRTM)

**Download Platform:** OpenTopography

**Download Date:** 29 June 2026 *(Update if different)*

**Data Licence:** Open Data

---

## 3. Storage Location

**Raw Dataset**

`data/raw/dem/output_SRTMGL1.tif`

**Processed Dataset**

`data/processed/dem/`

---

## 4. Metadata Verification

| Property           | Value                                          |
| ------------------ | ---------------------------------------------- |
| File Format        | GeoTIFF (.tif)                                 |
| CRS                | EPSG:4326 (WGS84 Geographic Coordinate System) |
| Coordinate Units   | Degrees                                        |
| Raster Type        | Single-band raster                             |
| Width              | 2136 pixels                                    |
| Height             | 1102 pixels                                    |
| Pixel Size         | 0.000277777° (~30 m)                           |
| Data Type          | Int16                                          |
| NoData Value       | -32768                                         |
| Compression        | LZW                                            |
| Minimum Elevation  | 1466 m                                         |
| Maximum Elevation  | 2200 m                                         |
| Mean Elevation     | 1695.50 m                                      |
| Standard Deviation | 166.79 m                                       |
| Valid Pixels       | 100%                                           |

---

## 5. Spatial Coverage

**Study Area:** Nairobi County and surrounding region

**Extent**

* West: 36.531250°
* East: 37.124583°
* South: -1.457083°
* North: -1.150972°

---

## 6. Quality Assurance (QA)

### Metadata Verification

* ✓ File successfully opened in QGIS.
* ✓ CRS verified.
* ✓ Resolution verified.
* ✓ Raster dimensions verified.
* ✓ Single raster band confirmed.
* ✓ NoData value confirmed.
* ✓ Elevation statistics reviewed.
* ✓ Raster contains 100% valid pixels.

### Visual Inspection

* ✓ Raster displays correctly in QGIS.
* ✓ Terrain appears realistic.
* ✓ No obvious missing tiles or corrupted regions observed.

**QA Status:** Approved for preprocessing.

---

## 7. Preprocessing History

| Step                      | Status     |
| ------------------------- | ---------- |
| Download raw DEM          | ✓ Complete |
| Verify metadata           | ✓ Complete |
| Visual inspection in QGIS | ✓ Complete |
| Clip to Nairobi County    | ✓ Complete  |
| Reproject to EPSG:32737   | ☐ Pending  |
| Validate processed raster | ✓ Complete  |

---

## 8. Why This Dataset Was Selected

The SRTM Digital Elevation Model was selected because it is a globally recognised, freely available elevation dataset with an approximate spatial resolution of 30 metres. It provides sufficient detail for county-scale flood risk assessment while remaining computationally efficient for a reproducible GeoAI workflow.

---

## 9. Contribution to the GeoAI Flood Risk Decision Agent

This dataset contributes the terrain component of the flood model. It will be used to:

* Calculate terrain elevation.
* Generate slope maps.
* Support future flow direction and drainage analyses.
* Identify areas where water is likely to accumulate.
* Contribute to the overall flood risk score used by the GeoAI Decision Agent.

---

## 10. Lessons Learned

This dataset demonstrated the importance of validating spatial metadata before analysis. Although the DEM is distributed in EPSG:4326, flood modelling requires measurements in metres. Therefore, the raster will be reprojected to a projected CRS (EPSG:32737) before spatial analysis.

# Dataset 003 — ESA WorldCover 2021 (Land Cover)

## Purpose

Provides land cover classification for Nairobi County. This dataset represents the physical surface cover (e.g., vegetation, built-up areas, water bodies) and will be used in the GeoAI Flood Risk Decision Agent to model surface runoff and infiltration characteristics.

---

## Source

Provider: European Space Agency (ESA)

Dataset: ESA WorldCover 2021 Version 2.0

Resolution: 10 metres

License: CC BY 4.0

CRS: EPSG:4326 (WGS84)

---

## Raw Dataset

Location:

data/raw/landcover/

Original filename:

ESA_WorldCover_10m_2021_v200_S03E036_Map.tif

Status:

Read-only

---

## Preprocessing

Steps performed:

- Verified raster metadata
- Inspected in QGIS
- Clipped using Nairobi County boundary
- Saved processed raster separately
- Preserved raw raster unchanged

Processed Output:

data/processed/Landcover/Nairobi Landcover.tif

---

## Validation

Validation script:

src/validation/validate_land_cover.py

Validation Status:

Passed

Raster Type:

Categorical Raster

Classes detected:

10

20

30

40

50

60

80

90

---

## Notes

This raster will later be converted into flood susceptibility weights during the multi-layer flood risk modelling stage.