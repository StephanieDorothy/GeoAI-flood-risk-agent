# UNOSAT Reference Data: Source and Limitations

## 1. Purpose

This document records the source, interpretation, processing context, and limitations of the satellite-derived flood reference used to evaluate the GeoAI Flood Risk Decision Agent.

The reference is used for external comparison with the model's MCDA flood-susceptibility surface. It is not treated as complete or error-free ground truth.

## 2. Source Identification

**Organization:** United Nations Satellite Centre (UNOSAT), United Nations Institute for Training and Research (UNITAR).

**Event code:** FL20240426KEN.

**Reference layer:** `PL_20240501_FloodExtent_Nairobi_Kiambu.shp`

**Observation date:** 1 May 2024.

**Satellite sensor:** Pléiades.

**Original coordinate reference system:** EPSG:4326 (WGS 84).

**Water classification:** Flood Water.

**Water status:** New Water / Water Increase.

**Confidence status in source metadata:** To be evaluated.

**Field-validation status in source metadata:** Not yet field validated.

The downloaded source package is stored locally under:

`data/raw/external_validation/_static_unosat_filesystem_3834_FL20240426KEN_SHP/FL20240426KEN_SHP/`

The embedded metadata for `PL_20240501_FloodExtent_Nairobi_Kiambu` identifies the dataset as part of the `FL20240426KEN` event and records the Pléiades sensor, 1 May 2024 observation date, flood-water classification, and Nairobi–Kiambu dataset name. The metadata lineage traces the layer to the UNOSAT `FL20240426KEN` geodatabase.

### Product catalogue identification

The local filesystem directory is labelled with the number `3834`. However, the official UNOSAT catalogue distinguishes between two related products from the same event and acquisition date:

* **Product 3833:** Flood impact analysis in Nairobi and Kiambu County, Kenya as of 1 May 2024.
* **Product 3834:** Flood impact analysis in Nairobi Kenya as of 1 May 2024.

The official Product 3833 record describes the Nairobi–Kiambu analysis and reports approximately 17 km² of detected flood extent.

The official Product 3834 record describes the Nairobi-only analysis and reports approximately 2 km² of detected flood extent.

Because the evaluated layer is explicitly named `PL_20240501_FloodExtent_Nairobi_Kiambu`, the layer's geographic identity corresponds to the Nairobi–Kiambu analysis. The embedded metadata and event code provide direct provenance for the local file, while the local directory name should not by itself be used as the definitive product identifier.

For reproducibility, the reference should therefore be identified primarily by its exact layer name, event code, observation date, and source metadata rather than by the local directory number alone.


## 3. What the Reference Represents

The flood-extent layer represents satellite-detected surface water classified as flood water for the observation period.

The available layer attributes identify the mapped water as:

* `Water_Clas`: Flood Water
* `Water_Stat`: New Water / Water Increase
* `SensorDate`: 2024-05-01
* `EventCode`: FL20240426KEN

These attributes support interpretation of the layer as an event-specific flood observation.

The reference represents observed surface-water extent within the available analysis domain. It does not represent all locations that could flood under different rainfall, river-flow, drainage, or seasonal conditions.

## 4. Observation Domain

The validation domain was derived using the available analysis-extent and cloud-obstruction layers and the valid footprint of the MCDA susceptibility raster.

This distinction is important because the absence of mapped flood water can only be interpreted as observed non-flood within the area treated as observable for this analysis.

Locations outside the observation domain, beneath excluded cloud-obstructed areas, or outside the valid model footprint must not be interpreted as confirmed non-flood locations.

The reference raster uses the following interpretation:

| Raster value | Meaning                                                  |
| ------------ | -------------------------------------------------------- |
| 1            | Observed flood                                           |
| 0            | Observed non-flood within the defined observation domain |
| -9999        | Unobserved or outside the valid comparison domain        |

The value `-9999` must remain excluded from flood/non-flood statistical calculations.

## 5. Processing Context

The source flood polygons were prepared for comparison with the MCDA raster grid.

The preparation process included geometry handling, definition of the observation domain, alignment with the model grid, and rasterization of observed flood and non-flood areas.

The derived reference raster is stored at:

`results/phase9_validation/external_validation/unosat_flood_reference_aligned.tif`

The raster is used alongside:

* `data/analysis/mcda/flood_susceptibility.tif`
* `data/analysis/mcda/flood_susceptibility_classified.tif`

The derived raster is an analytical representation of the source observations. It should not be confused with the original UNOSAT vector dataset.

## 6. Known Reference Limitations

### 6.1 Preliminary assessment

The relevant UNOSAT product documentation describes the analysis as preliminary and not yet validated in the field.

The reference should therefore not be treated as a perfect ground-truth inventory.

### 6.2 Observation timing

The satellite observation represents conditions at the acquisition time. Flood extent can change before and after image acquisition as rainfall, runoff, river discharge, and drainage conditions evolve.

A location not mapped as flooded at the observation time may still have flooded at another time during the event.

### 6.3 Spatial coverage

The validation domain is restricted to the areas represented by the available observation layers and the valid model footprint.

The resulting sample does not represent every valid cell in the MCDA raster.

### 6.4 Cloud obstruction

Cloud-obstructed areas cannot automatically be interpreted as non-flood. Excluded or unobserved locations must remain outside the statistical comparison.

### 6.5 Satellite interpretation and classification

Satellite-derived water delineation may contain classification uncertainty. The mapped extent should be interpreted as an observation produced through image analysis rather than a complete field survey.

### 6.6 Event specificity

The reference represents one event and observation period. Agreement or disagreement with this dataset does not establish performance across other floods, seasons, or geographic areas.

### 6.7 Spatial resolution and rasterization

Converting vector flood boundaries to the model raster grid introduces a representation choice. Boundary cells may be classified differently depending on the rasterization method and cell geometry.

The aligned raster therefore represents the source polygons at the model's spatial resolution rather than reproducing every detail of the original vector boundaries.

## 7. Implications for Validation

The reference is useful for investigating whether the MCDA susceptibility surface corresponds to the observed spatial distribution of flood water during the evaluated event.

However, the comparison must account for the distinction between relative susceptibility and event-specific inundation.

The reference does not, on its own, establish:

* calibrated flood probabilities;
* predictive accuracy for future events;
* complete flood extent throughout the event;
* causal relationships between individual MCDA factors and flooding; or
* generalization to other locations or events.

The observed mismatch between the model's susceptibility ranking and the UNOSAT flood extent must be reported transparently rather than removed through retrospective changes to model weights or classification thresholds.

## 8. Source Attribution and Reproducibility

The official UNOSAT product page is the primary source for product-level metadata and publication details.

The precise product identity associated with the local shapefile package remains to be confirmed.

Once confirmed, the final record should include the exact product identifier, official title, publication date, access date, original download location, and any relevant usage or attribution conditions.

The project should retain the original source files separately from the derived validation outputs and document all transformations required to reproduce the reference raster.

## 9. Status

**Phase 9.12.1 — Source and limitations documentation: Draft prepared.**

The source-product identity discrepancy remains unresolved. This document must not be treated as final source provenance until that discrepancy has been investigated and the product attribution confirmed.
