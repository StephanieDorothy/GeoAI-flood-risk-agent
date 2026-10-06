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

# UNOSAT Reference Preparation and Rasterization Workflow

## Phase 9.12.2 — External Reference Preparation

### 1. Purpose

The GeoAI Flood Risk Decision Agent was externally evaluated against an independent satellite-derived flood reference from UNOSAT.

The purpose of this processing stage was to transform the original UNOSAT vector flood data into a spatially aligned raster reference that could be compared consistently with the model's flood-susceptibility raster.

The workflow was:

**UNOSAT flood shapefile**
→ **geometry preparation**
→ **observation-domain preparation**
→ **cloud-obstruction handling**
→ **intersection with the valid MCDA footprint**
→ **rasterization**
→ **alignment to the MCDA grid**
→ **flood / non-flood / unobserved coding**
→ **validation against MCDA susceptibility**

This processing was performed before the statistical evaluation and did not modify the MCDA model, its factors, weights, or classification thresholds.

---

## 2. Independent Reference Dataset

The primary reference layer was:

`PL_20240501_FloodExtent_Nairobi_Kiambu.shp`

The layer represents satellite-observed flood extent associated with the April 2024 Kenya flood event and uses imagery acquired on **1 May 2024** from the **Pléiades** satellite.

The original vector layer was provided in geographic coordinates (EPSG:4326) and was subsequently transformed into the same projected coordinate reference system used by the MCDA analysis:

**EPSG:32737 — WGS 84 / UTM zone 37S**

The source metadata identifies the event as:

`FL20240426KEN`

The metadata also identifies the water classification as flood water and describes the mapped water as new water / water increase.

The source metadata indicates that the reference was preliminary, with confidence listed as **"To be evaluated"** and field validation listed as **"Not yet field validated"**. These characteristics were retained as limitations when interpreting the external validation.

---

## 3. Why the Original Shapefile Could Not Be Compared Directly

The MCDA model produces a raster covering a fixed analytical grid.

The UNOSAT reference, however, is a vector polygon representing observed flood extent.

The two datasets therefore differed in several important ways:

* data format: vector versus raster;
* coordinate reference system;
* spatial extent;
* spatial resolution;
* observation coverage;
* areas affected by cloud obstruction or unavailable observation;
* and the meaning of the data.

The MCDA raster represents a continuous susceptibility score across its valid modelling area.

The UNOSAT layer represents an observation of flood water during a particular event and at a particular observation time.

Therefore, the UNOSAT layer first had to be converted into a spatial reference that could be compared fairly with the model.

---

# 4. Geometry Preparation

The first stage was to inspect and prepare the UNOSAT flood geometry.

The primary flood layer was read as a vector dataset and its geometry, coordinate reference system, attributes, and spatial extent were checked.

The geometry was then transformed from its original geographic coordinate system into the projected CRS used by the MCDA analysis:

**EPSG:32737**

Using the same projected CRS was necessary because subsequent operations depended on consistent spatial coordinates and distances.

The resulting flood geometry was then evaluated against the actual valid footprint of the MCDA model rather than simply against the rectangular bounding box of the raster.

This distinction is important because the MCDA raster contains cells that are not necessarily valid modelling locations.

---

# 5. Observation Domain

A major consideration in external validation was that the UNOSAT satellite reference does not necessarily provide an observation for every cell in the MCDA raster.

Therefore, the validation process distinguished between:

1. locations where UNOSAT provided an observable non-flood condition;
2. locations where UNOSAT identified observed flood;
3. locations where the reference did not provide a valid observation.

The third category was not treated as non-flood.

This is important.

An area without a valid UNOSAT observation does **not** mean:

> "UNOSAT observed that this location did not flood."

It means:

> "This location was not included in the valid observation domain used for the comparison."

This distinction prevents unobserved areas from being incorrectly converted into negative flood observations.

---

# 6. Cloud-Obstruction and Observation Constraints

The UNOSAT package included information describing the observation extent and areas affected by cloud obstruction.

These constraints were incorporated into the definition of the valid observation domain.

The purpose was to ensure that the validation only treated locations as observed where the satellite reference provided an appropriate basis for comparison.

Conceptually:

**Full study area**

minus

**areas without valid observation**

minus

**cloud-obstructed / excluded areas**

→

**valid UNOSAT observation domain**

This produced the spatial area within which flood and non-flood comparisons could legitimately be made.

---

# 7. Intersection with the Valid MCDA Footprint

The next step was to restrict the external reference to locations that were simultaneously:

* valid locations in the MCDA model, and
* valid locations in the UNOSAT observation domain.

The comparison domain can therefore be represented as:

**Valid MCDA footprint ∩ Valid UNOSAT observation domain**

This was important because simply rasterizing the entire UNOSAT polygon over the MCDA raster bounding box could produce misleading statistics.

The actual MCDA footprint was therefore used rather than the rectangular raster extent.

During the preparation diagnostics, the primary UNOSAT flood geometry within the valid MCDA footprint was approximately:

**18.34 km²**

After rasterization, the corresponding flood area was approximately:

**18.29 km²**

This represented approximately **99.73% retention of the flood geometry**, indicating that the rasterization and footprint restriction preserved almost all of the relevant flood geometry.

---

# 8. Rasterization

After the observation domain and valid comparison footprint had been established, the UNOSAT vector flood geometry was rasterized.

Rasterization means converting the vector polygon into cells on a raster grid.

The rasterization was performed using the same spatial framework as the MCDA analysis.

The target grid was:

* CRS: **EPSG:32737**
* width: **1603 cells**
* height: **1019 cells**
* pixel size: approximately **30.8655 m**
* same spatial transform as the MCDA raster

This ensured that each UNOSAT reference cell corresponded spatially to the same location as a cell in the MCDA susceptibility raster.

---

# 9. Flood / Non-Flood / Unobserved Coding

The resulting reference raster used three important states.

### Code 1 — Observed Flood

A cell received the value:

`1`

when it fell within the prepared UNOSAT flood extent and was part of the valid comparison domain.

This represents:

> UNOSAT observed flood water at this location.

---

### Code 0 — Observed Non-Flood

A cell received the value:

`0`

when it was inside the valid UNOSAT observation domain but was not classified as flood.

This represents:

> The location was observed by the reference dataset and was not classified as flood.

This is fundamentally different from an unobserved location.

---

### Code -9999 — Unobserved / Invalid Comparison Area

A cell received:

`-9999`

when it was outside the valid UNOSAT observation domain or otherwise excluded from the comparison.

This represents:

> No valid UNOSAT observation was available for this cell for the purposes of this validation.

These cells were excluded from the statistical comparison.

---

# 10. Final Aligned Reference Raster

The final prepared reference raster was:

`results\phase9_validation\external_validation\unosat_flood_reference_aligned.tif`

The raster was aligned to the MCDA grid so that the two datasets could be compared cell-by-cell.

The alignment checks confirmed compatibility in:

* coordinate reference system;
* raster dimensions;
* spatial transform;
* and resolution.

The resulting comparison therefore used a common raster grid rather than attempting to compare the original vector geometry directly with the model.

---

# 11. Validation Domain

The final comparison contained:

* total MCDA raster cells: **1,633,457**
* valid MCDA model cells: **553,860**
* valid UNOSAT observation cells: **228,194**
* observed flood cells: **19,201**
* observed non-flood cells: **208,993**

Therefore, only the cells satisfying the required model and observation conditions were included in the external validation.

The observed flood rate within the valid UNOSAT observation domain was approximately:

**8.41%**

This does not mean that 8.41% of Nairobi flooded.

It means that approximately 8.41% of the cells within the specific valid UNOSAT comparison domain were classified as observed flood.

---

# 12. Why the Observation Domain Matters

The valid UNOSAT observation domain did not cover the MCDA classes equally.

For example, the proportion of each MCDA class represented inside the observation domain was approximately:

| MCDA Class | Observation-domain coverage |
| ---------- | --------------------------: |
| Very Low   |                       0.22% |
| Low        |                      23.29% |
| Moderate   |                      49.62% |
| High       |                      48.19% |
| Very High  |                      84.69% |

This means that the external reference was not a simple random sample of the entire MCDA study area.

The Very High class was much more heavily represented in the observed domain than the Very Low class.

This unequal representation was therefore considered during interpretation of the validation results.

An additional area-normalized analysis was performed to determine whether unequal observation coverage alone could explain the observed mismatch.

It did not.

---

# 13. Area-Normalized Reference Check

The observed flood distribution was compared with the distribution that would be expected if flood observations were proportional to the amount of each MCDA class represented in the observation domain.

The resulting enrichment values were:

| MCDA Class | Enrichment | Interpretation |
| ---------- | ---------: | -------------- |
| Very Low   |      0.491 | Below expected |
| Low        |      1.551 | Above expected |
| Moderate   |      1.393 | Above expected |
| High       |      1.215 | Above expected |
| Very High  |      0.498 | Below expected |

The grouped comparison showed:

| Group                     | Flood share | Expected/normalized interpretation |
| ------------------------- | ----------: | ---------------------------------- |
| Very Low + Low + Moderate |      51.13% | Above expected                     |
| High + Very High          |      48.87% | Below expected                     |

This showed that unequal observation coverage was an important consideration, but it did not explain the entire disagreement between the MCDA susceptibility ranking and the UNOSAT flood observation.

---

# 14. Quality-Control Checks

Several checks were performed before statistical validation.

### Input validation

The following were confirmed:

* MCDA continuous susceptibility raster available;
* MCDA classified susceptibility raster available;
* UNOSAT reference raster available;
* expected CRS present;
* expected raster dimensions present;
* expected resolution present;
* expected spatial transform present.

### Raster compatibility

The MCDA and UNOSAT reference rasters were confirmed to have compatible:

* CRS;
* dimensions;
* transforms;
* resolutions.

### Reference rasterization

The flood geometry was compared before and after rasterization.

Approximately **99.73%** of the relevant flood geometry was retained within the valid MCDA footprint.

These checks reduced the possibility that the later statistical findings were caused simply by incompatible raster grids or a failed rasterization process.

---

# 15. Relationship to Statistical Validation

Once the reference raster had been prepared, it became the independent reference used by the Phase 9.11 statistical evaluation.

The prepared raster was compared against:

1. the continuous MCDA susceptibility raster; and
2. the five-class susceptibility raster.

The statistical analysis included:

* class-level flood rates;
* area-normalized enrichment;
* chi-square association;
* Cramer's V;
* Mann-Whitney U;
* rank-biserial correlation;
* Spearman correlation;
* ROC analysis and AUC.

The reference preparation therefore formed the bridge between the original UNOSAT vector data and the statistical validation.

---

# 16. Important Scientific Distinction

The UNOSAT reference represents **observed flood extent during a particular satellite observation/event**.

The MCDA model represents **relative spatial susceptibility based on static spatial factors**.

These are not identical quantities.

The comparison therefore asks whether locations ranked as more susceptible by the MCDA model corresponded spatially to locations observed as flooded during the UNOSAT event.

It does not constitute a direct test of whether the MCDA model can predict future floods under arbitrary rainfall or hydrological conditions.

This distinction is central to interpreting the external validation results.

---

# 17. Reproducibility Chain

The complete processing chain can be summarized as:

```text
UNOSAT Flood Extent Shapefile
        │
        ▼
Geometry inspection and preparation
        │
        ▼
Reprojection to EPSG:32737
        │
        ▼
UNOSAT observation-domain preparation
        │
        ▼
Cloud-obstruction / unavailable-observation exclusion
        │
        ▼
Intersection with valid MCDA footprint
        │
        ▼
Flood geometry rasterization
        │
        ▼
Alignment to MCDA raster grid
        │
        ▼
Reference coding
        │
        ├── 1     = observed flood
        ├── 0     = observed non-flood
        └── -9999 = unobserved / excluded
        │
        ▼
Aligned UNOSAT reference raster
        │
        ▼
Cell-by-cell comparison with MCDA
        │
        ▼
Spatial + statistical validation
```

---

# 18. Processing Scripts

The reference preparation and diagnostic workflow was implemented through dedicated scripts rather than manually editing the final validation raster.

Key scripts included:

* `prepare_unosat_flood_reference.py`
* `inspect_unosat_observation_domain.py`
* `diagnose_unosat_reference_rasterization.py`
* `validate_susceptibility_against_unosat.py`
* `diagnose_unosat_spatial_validation.py`
* `analyze_unosat_area_normalized_validation.py`
* `evaluate_unosat_statistical_validation.py`

The scripts separate reference preparation, diagnostics, spatial comparison, area-normalized analysis, and statistical evaluation.

This makes the external validation workflow reproducible and auditable.

---

# 19. Interpretation of the Preparation Stage

The preparation workflow successfully produced a spatially aligned independent reference suitable for comparison with the MCDA model.

The important outcome of this stage is not that the model performed well or poorly.

Rather, the important outcome is that the comparison was performed using a clearly defined and quality-controlled validation domain.

The external validation therefore did not treat:

* unobserved locations as non-flood;
* the entire MCDA bounding box as valid;
* incompatible raster grids as directly comparable;
* or the original vector polygon as if it were already a cell-based reference.

Instead, the reference was explicitly transformed into a common spatial framework.

The subsequent disagreement between the model susceptibility ranking and the UNOSAT flood observations is therefore interpreted as a **scientific validation finding**, rather than simply being attributed to an obvious rasterization or spatial-alignment error.

---

## 20. Final Reference Product

The principal prepared reference used in Phase 9.11 was:

`results\phase9_validation\external_validation\unosat_flood_reference_aligned.tif`

This raster represents the final independent observation framework used for the external validation of the GeoAI Flood Risk Decision Agent.

It should be interpreted as an **event-specific observed flood reference**, not as a complete historical flood inventory or a calibrated ground-truth probability surface.

---

## 21. Limitations Carried Forward

The following limitations remain relevant to the interpretation of the validation:

1. The reference represents a particular flood event rather than multiple independent flood events.
2. The observation domain is spatially restricted.
3. Satellite observation conditions can limit where flood water can be reliably identified.
4. The source metadata indicates that the reference was preliminary and not yet field validated.
5. The reference represents observed inundation, whereas the MCDA model represents static susceptibility.
6. The MCDA model does not explicitly simulate rainfall, runoff, drainage, river discharge, or hydraulic processes.
7. Spatial dependence between neighboring raster cells means that conventional statistical significance values should not be interpreted as if every cell were an independent observation.
8. The validation therefore provides evidence about the model's performance against this particular independent reference, but does not establish general predictive performance across future flood events.

---

## 22. Conclusion

The UNOSAT reference was systematically transformed from its original vector flood extent into an aligned raster observation framework before external validation.

The final comparison therefore followed a controlled workflow:

**independent observation → controlled preparation → common spatial grid → explicit observation coding → validation.**

This provides a transparent basis for interpreting the Phase 9.11 external validation results and establishes the reference-data processing lineage required for the final Phase 9 synthesis.
