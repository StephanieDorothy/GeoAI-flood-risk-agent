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


---

# Phase 11 — Session 3: Multi-Cell Production Integration and Regression Validation

**Session date:** 19 November 2026
**Status:** Session 3 completed; Phase 11 remains in progress.

## 1. Objective

The objective was to extend production-data interpretation beyond the single cell examined in Session 2, exercise the complete deterministic interpreter on low, median, and high susceptibility-score cells, and run the existing regression suite.

The work used the existing production rasters and interpreter modules. No factor raster, AHP weight, MCDA output, or model configuration was changed.

## 2. Repeatable multi-cell production test

A dedicated test module was added:

- `tests/test_phase11_multiple_real_cells.py`

The test loads and validates the production model inputs once, identifies valid cells from the common data mask, and selects three unique cells nearest to the 10th, 50th, and 90th percentiles of the stored susceptibility-score distribution.

Each selected cell is passed through the complete workflow:

1. Production raster cell selection.
2. Extraction of five factor scores.
3. Calculation of five AHP-weighted contributions.
4. Reconstruction and verification of the stored susceptibility score.
5. Deterministic explanation generation.

The test also checks that each explanation contains five factor-evidence entries, five contribution rankings, a dominant factor, and scientific limitations.

## 3. Production-cell results

The production footprint contained **553,860 valid cells**.

| Score range | Selected row | Selected column | Stored score | Reconstructed score | Absolute difference |
|---|---:|---:|---:|---:|---:|
| Low — P10 | 504 | 253 | 0.65325296 | 0.65325296 | 0.000000000000 |
| Median — P50 | 611 | 936 | 0.78351247 | 0.78351247 | 0.000000000000 |
| High — P90 | 435 | 1371 | 0.87177277 | 0.87177277 | 0.000000000000 |

**Result: 3/3 complete production-cell workflows passed.**

For all three selected cells:

- Five factor scores were extracted.
- Five weighted contributions were calculated.
- The reconstructed score matched the stored score at the reported precision.
- Score verification returned PASS.
- The deterministic explanation contained all five factor-evidence and contribution-ranking entries.
- `distance_to_rivers` was the dominant weighted contribution.

The selected cells represent three points in the model's score distribution. They are not a spatially exhaustive sample and do not establish predictive accuracy.

## 4. Regression validation

The following seven existing test modules were run together:

- `tests.test_cell_selector`
- `tests.test_factor_evidence`
- `tests.test_weighted_contributions`
- `tests.test_score_verification`
- `tests.test_explanation_generator`
- `tests.test_input_loader`
- `tests.test_interpreter_integration`

**Result: 92 tests passed; 0 failures; 0 errors.**

The dedicated production integration test was then run separately.

**Result: 1 test passed, covering all three production cells.**

The regression suite covers component-level validation, invalid inputs and cells, numerical reconstruction, deterministic explanation behaviour, failed-verification safeguards, production input validation, and synthetic end-to-end integration.

## 5. Warning deferred for follow-up

The test runs continued to emit a non-fatal NumPy 2.5 deprecation warning associated with the raster-reading path in `src/interpreter/input_loader.py`. It did not cause either test run to fail.

Investigation and any justified compatibility correction are intentionally deferred to the next work session. No warning suppression or unverified code change was made during Session 3.

## 6. Scientific scope and limitations

These tests establish that the deterministic interpreter can process the selected real production cells and numerically reconstruct their stored susceptibility scores. They do not demonstrate that the susceptibility model accurately predicts observed flooding.

The susceptibility output remains a relative MCDA index, not a calibrated flood probability or dynamic forecast. Population remains an exposure-related factor rather than a physical flood-generating process. The Phase 9 external-validation findings and temporal mismatch between 2021 model inputs and the May 2024 UNOSAT reference remain unchanged.

## 7. Session 3 completion assessment

**Session 3 objective: ACHIEVED.**

Completed:

- Added a repeatable three-cell production integration test.
- Passed the complete interpreter workflow for low, median, and high score-range cells.
- Reconstructed all three stored susceptibility scores with zero reported absolute difference.
- Passed all 92 existing regression tests.
- Re-ran the dedicated production integration test successfully.
- Preserved the existing model outputs and scientific limitations.

Deferred:

- Investigating the NumPy 2.5 deprecation warning.
- Any compatibility change, if justified by that investigation.

Phase 11 remains in progress pending the remaining review, documentation, and integration decisions. A successful computational validation must not be presented as evidence of predictive flood accuracy.


$session4 = @'

---

# Phase 11 — Session 4: NumPy Compatibility Investigation and Rasterio Upgrade

**Session date:** 20 November 2026
**Status:** Session 4 completed; Phase 11 remains in progress.

## 1. Objective

Investigate and resolve the NumPy 2.5 deprecation warning observed during Session 3, verify the compatibility correction, and establish a reproducible dependency configuration.

The investigation was intended to correct the underlying compatibility issue rather than suppress the warning or modify the interpreter's raster-processing logic.

## 2. Warning reproduction and diagnosis

The warning was reproduced by treating deprecation warnings as errors during raster reading.

The traceback identified the source as Rasterio's compiled raster-reading implementation:

`DatasetReaderBase.read`

The reported operation involved assigning a new shape to a NumPy array. This behaviour is deprecated in NumPy 2.5.

Inspection of `src/interpreter/input_loader.py` found that the project used the ordinary Rasterio `dataset.read(1)` operation. No explicit array-shape mutation in the project code was identified as the cause.

The evidence therefore pointed to a Rasterio and NumPy compatibility issue rather than a defect in the project's input-loader implementation.

## 3. Dependency correction

The environment before the correction included:

| Package | Previous version |
|---|---:|
| Python | 3.12.10 |
| NumPy | 2.5.0 |
| Rasterio | 1.5.0 |
| GDAL | 3.12.1 |

Rasterio was upgraded without downgrading NumPy:

```powershell
python -m pip install --upgrade rasterio==1.5.2
```

The resulting environment reported:

| Package | Verified version |
|---|---:|
| Python | 3.12.10 |
| NumPy | 2.5.0 |
| Rasterio | 1.5.2 |
| GDAL | 3.12.2 |

The project dependency declaration was updated from `rasterio==1.5.0` to `rasterio==1.5.2`.

The existing 26 dependency entries were retained. The dependency snapshot `requirements_before_rasterio_upgrade.txt` was preserved separately and was not included in the intended source commit.

The original committed requirements file was UTF-16 encoded. The local requirements file was converted to UTF-8 so that it uses a conventional plain-text encoding.

A normalized text comparison confirmed that the only dependency-version change was:

```diff
-rasterio==1.5.0
+rasterio==1.5.2
```

## 4. Compatibility verification

The production raster-reading operation was repeated with deprecation warnings treated as errors.

The raster was read successfully with:

- Dimensions: 1603 × 1019
- Array shape: (1019, 1603)
- Data type: float32
- Rasterio version: 1.5.2

The previously observed NumPy deprecation warning did not recur.

**Result: Raster-reading compatibility verification PASS.**

## 5. Regression testing

The following eight test modules were executed with deprecation warnings treated as errors:

- `tests.test_cell_selector`
- `tests.test_factor_evidence`
- `tests.test_weighted_contributions`
- `tests.test_score_verification`
- `tests.test_explanation_generator`
- `tests.test_input_loader`
- `tests.test_interpreter_integration`
- `tests.test_phase11_multiple_real_cells`

Command:

```powershell
python -W error::DeprecationWarning -m unittest `
    tests.test_cell_selector `
    tests.test_factor_evidence `
    tests.test_weighted_contributions `
    tests.test_score_verification `
    tests.test_explanation_generator `
    tests.test_input_loader `
    tests.test_interpreter_integration `
    tests.test_phase11_multiple_real_cells -v
```

**Result: 93 tests passed; 0 failures; 0 errors.**

The dedicated production integration test again validated three real cells representing low, median, and high susceptibility-score ranges. All three completed the interpretation workflow and reconstructed their stored scores with zero reported absolute difference.

No deprecation warning was raised during the regression run.

## 6. Dependency integrity

The installed Rasterio version was checked against the updated dependency declaration.

The package integrity check was executed:

```powershell
python -m pip check
```

**Result: No broken requirements found.**

The requirements-file comparison also confirmed that all 26 dependency entries were retained and only the Rasterio version changed.

## 7. Session 4 completion assessment

**Session 4 objective: ACHIEVED.**

Completed:

- Reproduced the NumPy 2.5 deprecation warning.
- Identified Rasterio's raster-reading implementation as the source.
- Confirmed that the project code did not explicitly perform the reported shape mutation.
- Upgraded Rasterio from 1.5.0 to 1.5.2.
- Retained NumPy 2.5.0.
- Verified production raster reading with deprecation warnings treated as errors.
- Passed all 93 regression tests with deprecation warnings treated as errors.
- Confirmed that the three real production-cell workflows still pass.
- Confirmed that `pip check` reports no broken requirements.
- Updated the dependency pin and corrected the requirements file encoding.

No model weights, factor rasters, susceptibility outputs, or analytical results were changed.

## 8. Remaining Phase 11 work

Phase 11 remains in progress. Resolving the dependency warning and passing the current regression suite do not complete all production-integration objectives.

Remaining work includes reviewing additional production-data failure cases, assessing missing-input behaviour, and deciding whether further end-to-end validation is needed before developing a user-facing interface.

The scientific limitations recorded in Phase 9 remain unchanged. Computational consistency must not be presented as proof of predictive flood accuracy.


## 9. Session 5 - Production-data failure-case validation

**Date:** 24 November 2026

### 9.1 Objective

Expand the production input-loader test suite to verify that invalid, incomplete, inconsistent, or unreadable raster inputs are rejected safely. Confirm that the interpreter regression suite remains stable and document the resulting test coverage.

No production raster, susceptibility output, AHP weight, or analytical result was modified during this session.

### 9.2 Input-loader failure-case tests

The input-loader test module now contains 31 tests.

The expanded tests cover:

- Missing factor rasters and missing susceptibility output.
- Rasters without a CRS or required NoData metadata.
- Incorrect NoData values.
- Multiband rasters and unsupported data types.
- Unreadable raster inputs.
- Grid inconsistencies and absence of common valid cells.
- Factor and susceptibility values outside the permitted range.
- Non-finite valid factor values and empty valid selections.
- Susceptibility reconstruction mismatches.
- Missing, malformed, inconsistent, negative, or non-finite AHP weight metadata and calculated values.
- Invalid consistency-ratio metadata and consistency ratios exceeding the accepted threshold.
- Missing or incorrect model and weighting-method metadata.

**Result: 31 input-loader tests passed.**

### 9.3 Input-loader coverage

Coverage.py was used to measure statement and branch coverage for `src/interpreter/input_loader.py`.

| Measurement | Result |
|---|---:|
| Statements | 178 |
| Missed statements | 29 |
| Branches | 70 |
| Partial branches | 2 |
| Coverage | 86% |

The 86% figure applies to the input-loader module only; it is not a whole-project coverage result.

The remaining uncovered paths include non-finite susceptibility output validation and portions of the command-line reporting and execution path. These are documented coverage gaps, not evidence that the production loader has passed every possible execution path.

### 9.4 Complete interpreter regression suite

The complete Phase 11 interpreter suite was executed with Python deprecation warnings treated as errors.

**Result: 118 tests passed.**

The tested modules included cell selection, factor evidence, weighted contributions, score verification, deterministic explanation generation, input loading, interpreter integration, and multiple real production cells.

### 9.5 Multi-cell production validation

Three real cells from the production susceptibility raster were tested.

| Production cell | Row | Column | Stored score | Reconstructed score | Absolute difference |
|---|---:|---:|---:|---:|---:|
| Low - P10 | 504 | 253 | 0.65325296 | 0.65325296 | 0.000000000000 |
| Median - P50 | 611 | 936 | 0.78351247 | 0.78351247 | 0.000000000000 |
| High - P90 | 435 | 1371 | 0.87177277 | 0.87177277 | 0.000000000000 |

All three production-cell workflows passed score reconstruction verification. The dominant weighted contribution in each selected cell was `distance_to_rivers`.

These results demonstrate computational consistency between the production factor scores, AHP weights, and stored susceptibility values. They do not independently establish predictive flood accuracy.

### 9.6 Session 5 completion assessment

**Session 5 objective: ACHIEVED.**

Completed:

- Expanded the input-loader test module to 31 tests.
- Tested additional missing-input, raster-metadata, grid, value-range, reconstruction, and AHP failure cases.
- Measured 86% statement and branch coverage for the input-loader module.
- Passed all 118 interpreter regression tests with deprecation warnings treated as errors.
- Reconfirmed successful interpretation and score reconstruction for the P10, P50, and P90 production cells.
- Confirmed that no production analytical data or model weights were changed.

### 9.7 Remaining Phase 11 work and scientific limitations

Phase 11 remains in progress. Session 5 strengthens the evidence that the production input loader rejects a broad range of invalid inputs safely. The remaining uncovered code paths and any additional end-to-end integration requirements should be reviewed before the phase is closed.

The model remains a relative MCDA flood susceptibility index, not a calibrated flood probability or operational flood forecast. Successful software tests and exact score reconstruction demonstrate computational consistency, not independent predictive validity. The temporal mismatch and limitations of the UNOSAT reference comparison documented in earlier phases remain applicable.
