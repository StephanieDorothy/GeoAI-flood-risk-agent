# Phase 11 — Production Raster Integration and End-to-End Validation

**Project:** GeoAI Flood Risk Decision Agent  
**Study area:** Nairobi County, Kenya  
**Session:** 1 — Production raster audit and readiness assessment  
**Status:** Session 1 completed; Phase 11 remains in progress.

## 1. Session objective

The objective of this session was to inspect the actual production raster inputs configured by the deterministic interpreter, verify their spatial and numerical compatibility, and establish whether the existing Phase 10 input loader accepts the production data.

The work was deliberately limited to read-only inspection and validation. No model raster, AHP weight, or susceptibility output was modified.

## 2. Configured production inputs

The existing model configuration points to these five factor-score rasters:

- `data/analysis/aligned/elevation_score.tif`
- `data/analysis/aligned/slope_score.tif`
- `data/analysis/aligned/distance_to_rivers_score.tif`
- `data/analysis/aligned/landcover_score.tif`
- `data/analysis/aligned/population_score.tif`

The configured susceptibility output is:

- `data/analysis/mcda/flood_susceptibility.tif`

All six configured files were confirmed to exist in the local project environment.

## 3. Spatial metadata audit

All five factor rasters and the susceptibility output reported identical spatial metadata:

| Property | Observed value |
|---|---|
| CRS | EPSG:32737 |
| Width | 1,603 columns |
| Height | 1,019 rows |
| Resolution | 30.86551681907227 × 30.86551681907227 metres |
| Bounds | Identical across all six rasters |
| Data type | float32 |
| NoData | -9999 |

Each raster reported `AREA_OR_POINT=Area`. The susceptibility raster also contains the model metadata tags and AHP weights.

## 4. Valid-data coverage and factor ranges

The observed valid-pixel counts were:

| Raster | Valid pixels |
|---|---:|
| Elevation | 740,186 |
| Slope | 735,043 |
| Distance to rivers | 1,633,457 |
| Land cover | 740,507 |
| Population | 558,306 |
| Susceptibility output | 553,860 |

The intersection of the five factor masks contained exactly **553,860 cells**. The susceptibility output also contained 553,860 valid cells. The masks were exactly equal, with **zero mismatch pixels**.

All five factor-score rasters passed the expected 0–1 range check:

| Factor | Minimum | Maximum | Result |
|---|---:|---:|---|
| Elevation | 0.000000 | 1.000000 | PASS |
| Slope | 0.000000 | 1.000000 | PASS |
| Distance to rivers | 0.000000 | 1.000000 | PASS |
| Land cover | 0.000000 | 1.000000 | PASS |
| Population | 0.000000 | 0.976962 | PASS |

## 5. Existing interpreter input-loader validation

The existing production input loader was executed using:

```powershell
python -m src.interpreter.input_loader
```

**Result: INPUT VALIDATION: PASS**

The loader reported:

- CRS: EPSG:32737
- Raster dimensions: 1603 × 1019
- Common valid cells: 553,860
- Spatial alignment: PASS
- Factor score ranges: PASS
- Output mask agreement: PASS
- AHP metadata agreement: PASS
- Susceptibility reconstruction: PASS
- Maximum reconstruction error: 0.000000000000

The stored AHP metadata was read as:

| Factor | Weight |
|---|---:|
| Elevation | 0.1868744589 |
| Slope | 0.1868744589 |
| Distance to rivers | 0.4352900433 |
| Land cover | 0.1285887446 |
| Population | 0.0623722944 |

The stored AHP consistency ratio was **0.0269475117**.

The loader reported that no model files were modified. A zero reported reconstruction error demonstrates numerical consistency between the weighted factor reconstruction and stored susceptibility raster at the loader's reported precision. It does not demonstrate empirical flood-prediction accuracy.

## 6. First real production-cell selection

The existing selector in `src/interpreter/cell_selector.py` was inspected. It accepts zero-based raster row and column indices, validates their types and bounds, rejects cells outside the common valid-data footprint, checks the selected score is finite, and returns cell-centre coordinates in the raster CRS.

A reproducible test selected the valid cell closest to the centre of the raster and passed it through `select_raster_cell()`.

| Property | Selected value |
|---|---:|
| Row | 509 |
| Column | 801 |
| CRS | EPSG:32737 |
| Cell-centre X | 264350.952 m |
| Cell-centre Y | 9855972.966 m |
| Stored susceptibility score | 0.84615213 |

This confirms that the existing selector can select a valid cell from the actual production inputs. The score is a relative susceptibility index, not an 84.6% probability of flooding.

## 7. Warnings and maintenance notes

The inspection and input-loading commands emitted a non-fatal NumPy 2.5 deprecation warning associated with array shape handling in the raster-reading path. The commands completed successfully and the validation checks passed. The warning is recorded for a separate compatibility review; no code was changed to suppress or work around it during this session.

## 8. Session 1 completion assessment

**Session 1 objective: ACHIEVED.**

Completed:

- Confirmed all six configured production raster files exist.
- Audited CRS, dimensions, resolution, bounds, data type, and NoData metadata.
- Verified the common factor mask exactly matches the susceptibility output mask.
- Verified all five factor-score ranges.
- Ran the existing interpreter input loader successfully against production rasters.
- Verified AHP metadata and susceptibility reconstruction.
- Selected one valid real production cell using the existing cell selector.

Not yet completed:

- Extracting all five factor values for the selected cell.
- Calculating and verifying the five weighted contributions for that cell.
- Generating and reviewing its deterministic explanation.
- Testing real-data NoData, invalid-index, boundary, and missing-input cases.
- Completing end-to-end production integration documentation and validation.

## 9. Next session

The next session will continue with the same selected production cell (row 509, column 801):

1. Inspect and use the existing factor-evidence extraction function.
2. Extract the five production factor values.
3. Calculate their weighted contributions using the stored AHP weights.
4. Verify that the contributions reconstruct the selected cell's stored susceptibility score.
5. Pass the verified evidence through the deterministic explanation generator.
6. Begin the real-data edge-case checks.

The existing MCDA model, factor weights, and stored susceptibility raster must remain unchanged.

## 10. Scientific scope

This phase validates production-data integration and deterministic computational consistency. It does not resolve the Phase 9 external-validation limitations, calibrate flood probabilities, establish causal relationships, or demonstrate generalizable predictive performance. The existing UNOSAT comparison findings and the temporal mismatch between the 2021 model inputs and May 2024 reference data remain important limitations.


---

# Phase 11 — Session 2: Real-Cell Interpretation and Production Rejection Testing

**Session date:** 14 November 2026  
**Status:** Session 2 completed; Phase 11 remains in progress.

## 1. Objective

The objective was to trace one selected cell from the actual production rasters through factor-evidence extraction, weighted-contribution calculation, numerical score verification, and deterministic explanation generation. The session also tested regression behaviour and safe rejection of invalid production-data locations.

The work was read-only. The MCDA model, AHP weights, factor rasters, and stored susceptibility raster were not modified.

## 2. Selected production cell

The same reproducible valid cell selected in Session 1 was used:

| Property | Value |
|---|---:|
| Row | 509 |
| Column | 801 |
| CRS | EPSG:32737 |
| Cell-centre X | 264350.95249378704 m |
| Cell-centre Y | 9855972.965717278 m |
| Stored susceptibility score | 0.846152126789093 |

## 3. Extracted factor evidence

All five standardized factor scores were successfully extracted from the production rasters:

| Factor | Standardized score |
|---|---:|
| Elevation | 0.65120870 |
| Slope | 0.93330878 |
| Distance to rivers | 0.95277900 |
| Land cover | 1.00000000 |
| Population | 0.10777754 |

**Result: Factor evidence extraction PASS.**

These are standardized factor scores, not raw elevation, slope, distance, population, or original land-cover category measurements.

## 4. Weighted contributions

The existing AHP weights were applied without modification:

| Factor | Factor score | AHP weight | Weighted contribution |
|---|---:|---:|---:|
| Elevation | 0.65120870 | 0.18687446 | 0.12169427 |
| Slope | 0.93330878 | 0.18687446 | 0.17441157 |
| Distance to rivers | 0.95277900 | 0.43529004 | 0.41473521 |
| Land cover | 1.00000000 | 0.12858874 | 0.12858874 |
| Population | 0.10777754 | 0.06237229 | 0.00672233 |

**Result: Weighted contribution calculation PASS.**

Distance to rivers produced the largest weighted contribution for this cell. Population is correctly identified as an exposure-related factor and should not be interpreted as a physical flood-generating process.

## 5. Stored-score reconstruction

The five weighted contributions reconstructed the stored susceptibility score:

| Verification item | Result |
|---|---:|
| Stored score | 0.846152126789093 |
| Reconstructed score | 0.846152126789093 |
| Absolute difference | 0.000000000000 |
| Accepted tolerance | 0.000010000000 |
| Verification | PASS |

The reconstruction confirms numerical consistency for this selected cell. It does not establish predictive accuracy, causation, or flood probability calibration.

## 6. Deterministic explanation

The explanation generator returned the selected cell's location, verification details, factor evidence, contribution ranking, interpretation, and scientific limitations.

Contribution ranking for this cell:

1. Distance to rivers — 0.41473521
2. Slope — 0.17441157
3. Land cover — 0.12858874
4. Elevation — 0.12169427
5. Population — 0.00672233

The explanation explicitly states that the score is a relative MCDA susceptibility index, not a calibrated flood probability or dynamic forecast. It also preserves the Phase 9 limitation: the UNOSAT May 2024 event comparison showed weak and negative agreement with the susceptibility ranking, with a temporal mismatch between the 2021 model inputs and 2024 reference data.

**Result: Deterministic explanation generation PASS.**

## 7. Automated regression tests

The following five unit-test modules were executed:

- `tests.test_cell_selector`
- `tests.test_factor_evidence`
- `tests.test_weighted_contributions`
- `tests.test_score_verification`
- `tests.test_explanation_generator`

**Result: 81 tests passed; 0 failures; 0 errors.**

Coverage includes valid selection, invalid indices, NoData masks, invalid types, missing or unexpected factors, invalid score and weight ranges, non-finite values, reconstruction tolerance, inconsistent verification states, deterministic ranking, and scientific limitations.

## 8. Real production-data rejection tests

The production rasters were loaded and the selector was tested against five invalid locations:

| Rejection case | Result |
|---|---|
| Negative row | PASS |
| Row beyond raster bounds | PASS |
| Negative column | PASS |
| Column beyond raster bounds | PASS |
| NoData cell at row 0, column 0 | PASS |

**Result: 5/5 production-data rejection checks passed.**

The invalid cell at row 0, column 0 was rejected because it lies outside the common valid-data footprint.

## 9. Session 2 completion assessment

**Session 2 objective: ACHIEVED.**

Completed:

- Extracted all five factor scores from the real production rasters for the selected cell.
- Calculated the five weighted contributions using the existing AHP weights.
- Reconstructed the stored susceptibility score with zero reported absolute difference.
- Generated and reviewed the deterministic explanation.
- Passed all 81 regression unit tests across the five interpreter components.
- Passed all five real production-data rejection checks.

No model weights, factor rasters, or susceptibility outputs were changed.

## 10. Scope and next work

Phase 11 remains in progress. This session validates one selected production cell and several real-data rejection cases; it does not by itself establish exhaustive end-to-end coverage across the full raster or predictive validity.

Further Phase 11 work should broaden production integration and validation, including relevant missing-input and additional edge-case behaviour, before any user-facing interface is considered complete. The scientific limitations documented in Phase 9 remain unchanged.
