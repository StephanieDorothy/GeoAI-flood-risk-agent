# GeoAI Flood Risk Decision Agent

# Dataset Catalogue

This document records every dataset used in the project to ensure reproducibility, transparency, and proper documentation.

---

## Dataset 001

### Dataset Name

SRTM Digital Elevation Model (DEM)

### Theme

Elevation

### Purpose

Used to derive elevation, slope, terrain characteristics, and support flood risk modelling.

### Source

NASA Shuttle Radar Topography Mission (SRTM)

### Geographic Coverage

Nairobi County, Kenya

### Original Resolution

30 metres

### Format

GeoTIFF (.tif)

### CRS

To be verified after download

### Download Date

(To be completed)

### Licence

Open Data

### Processing History

* Download original DEM
* Verify CRS
* Clip to Nairobi County
* Store clipped raster in `data/processed/`

---

## Dataset 002

### Dataset Name

ESA WorldCover

### Theme

Land Cover

### Purpose

Identify built-up areas, vegetation, water bodies, and bare land for flood susceptibility analysis.

Status: Pending

---

## Dataset 003

### Dataset Name

WorldPop Population

### Theme

Population

### Purpose

Estimate population exposure to flooding.

Status: Pending

---

## Dataset 004

### Dataset Name

OpenStreetMap Roads

### Theme

Infrastructure

### Purpose

Estimate road exposure and accessibility during flooding.

Status: Pending

---

## Dataset 005

### Dataset Name

OpenStreetMap Rivers

### Theme

Hydrology

### Purpose

Measure proximity to rivers and drainage networks.

Status: Pending
