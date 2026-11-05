# Phase 10.5 — Factor Evidence Extraction

## 1. Purpose

Phase 10.5 implements the extraction of factor evidence for a previously selected raster cell.

The objective is to retrieve the five standardized factor scores and the stored continuous susceptibility score associated with that cell.

This functionality provides the evidence required by subsequent interpretation stages.

The implementation is deterministic and read-only. It does not modify the original MCDA model, its factor rasters, AHP weights, classification thresholds or susceptibility output.

## 2. Implementation Files

The implementation consists of:

| File | Purpose |
|---|---|
| `src/interpreter/factor_evidence.py` | Extracts and validates factor evidence for a selected cell. |
| `tests/test_factor_evidence.py` | Tests the factor evidence extraction functionality. |
| `src/interpreter/cell_selector.py` | Supplies the selected raster cell. |
| `src/interpreter/input_loader.py` | Supplies validated model inputs. |

The implementation uses the authoritative factor ordering defined in:

`src/flood_factors/mcda_flood_susceptibility.py`

This avoids independently redefining the model's factor names.

## 3. Extracted Evidence

For each selected cell, the module retrieves:

1. Elevation factor score.
2. Slope factor score.
3. Distance-to-rivers factor score.
4. Land-cover factor score.
5. Population factor score.
6. Stored continuous susceptibility score.

It also preserves the selected cell's:

- raster row;
- raster column;
- projected X coordinate;
- projected Y coordinate; and
- coordinate reference system.

The extracted factor scores represent the standardized inputs already used by the existing MCDA model.

They are not raw elevation, slope, distance, land-cover or population measurements.

## 4. Data Validation

Before returning evidence, the extraction function checks the integrity of the requested cell and its associated data.

The checks include:

- model input object type;
- cell selection object type;
- raster dimensions;
- availability of all five required factors;
- compatibility of factor-array dimensions;
- selected row and column validity;
- selected cell membership in the valid-data mask;
- finite factor values;
- factor scores within the expected interval [0, 1];
- finite stored susceptibility score; and
- consistency between the selected cell's susceptibility score and the stored raster value.

Invalid or incomplete evidence is rejected rather than silently accepted.

## 5. Output Structure

The extraction function returns a `FactorEvidence` dataclass.

The structure contains:

- `row`
- `column`
- `x`
- `y`
- `crs`
- `factor_scores`
- `susceptibility_score`

The `factor_scores` field contains the five standardized factor values, keyed by their authoritative factor names.

The returned object is immutable at the dataclass level.

## 6. Relationship with Previous Components

Phase 10.5 builds on the earlier Phase 10 components.

### Phase 10.3 — Input Validation

The input loader reads and validates the existing factor rasters and continuous susceptibility raster.

### Phase 10.4 — Cell Selection

The cell selector identifies a valid raster cell and preserves its spatial location and stored susceptibility score.

### Phase 10.5 — Factor Evidence Extraction

The evidence extractor retrieves the five factor scores and stored susceptibility score for that selected cell.

Together, these components establish a controlled process for moving from validated model inputs to a spatially identified cell with traceable factor evidence.

## 7. Testing and Verification

The implementation was tested using:

`python -m unittest tests.test_factor_evidence -v`

Result:

- 13 tests executed.
- 13 tests passed.
- 0 failures.

The existing cell-selection functionality was also tested again using:

`python -m unittest tests.test_cell_selector -v`

Result:

- 9 tests executed.
- 9 tests passed.
- 0 failures.

Python compilation was checked using:

`python -m py_compile tests\test_factor_evidence.py`

Compilation completed successfully.

### 7.1 Test Coverage

The factor evidence tests cover:

1. Successful factor evidence extraction.
2. Retrieval of all five factors.
3. Preservation of spatial location information.
4. Rejection of missing factors.
5. Rejection of incompatible factor dimensions.
6. Rejection of non-finite factor scores.
7. Rejection of factor scores above 1.
8. Rejection of negative factor scores.
9. Rejection of invalid-mask cells.
10. Rejection of non-finite susceptibility values.
11. Rejection of mismatched susceptibility scores.
12. Rejection of invalid model input objects.
13. Rejection of invalid cell selection objects.

All 22 targeted tests passed.

## 8. Scientific and Architectural Boundaries

Phase 10.5 extracts existing model evidence. It does not independently determine whether the selected location will flood.

The extracted susceptibility score remains a relative MCDA index, not a calibrated flood probability.

Population is retained as a separate factor score. Its interpretation should distinguish population-related exposure considerations from the physical susceptibility characteristics represented by the other factors.

The implementation does not:

- calculate weighted factor contributions;
- reconstruct the susceptibility score;
- generate a natural-language explanation;
- modify AHP weights;
- modify factor scores;
- change susceptibility classifications; or
- alter the original model rasters.

These responsibilities remain outside the scope of Phase 10.5.

## 9. Phase Completion

Phase 10.5 — Factor Evidence Extraction is complete.

The implementation successfully retrieves the five standardized factor scores and stored susceptibility score for a validated raster cell.

All 13 factor evidence tests and all 9 cell-selection regression tests passed.

The component provides the evidence foundation for Phase 10.6 — Weighted Factor Contributions.

No changes were made to the original Nairobi County MCDA model or its raster outputs.