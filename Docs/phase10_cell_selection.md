# Phase 10.4 — Raster Cell Selection

## 1. Purpose

Phase 10.4 implements the raster cell-selection component of the GeoAI Flood Risk Decision Agent.

The component allows a user or downstream interpreter function to select an individual raster cell using its zero-based row and column indices.

The selector retrieves the selected cell's spatial coordinates, coordinate reference system, and continuous flood-susceptibility score.

It uses the validated `ModelInputs` object produced by Phase 10.3.

## 2. Implementation

Implementation file:

`src/interpreter/cell_selector.py`

The module provides:

- `CellSelection`: an immutable data structure containing the selected cell's information.
- `select_raster_cell()`: the function responsible for validating and selecting a raster cell.

The selector accepts:

- a validated `ModelInputs` object;
- a zero-based row index; and
- a zero-based column index.

## 3. Returned Information

A successful selection returns:

| Field | Description |
|---|---|
| `row` | Selected zero-based raster row |
| `column` | Selected zero-based raster column |
| `x` | Pixel-centre X coordinate |
| `y` | Pixel-centre Y coordinate |
| `crs` | Coordinate reference system |
| `susceptibility_score` | Continuous susceptibility score at the selected cell |

Coordinates are calculated using the raster's affine transform and the pixel-centre convention.

This ensures that the returned coordinates represent the centre of the selected raster cell rather than its upper-left corner.

## 4. Input Validation

The selector performs validation before accessing the selected cell.

### 4.1 Index type validation

Both row and column must be integer indices.

The selector rejects:

- floating-point indices;
- Boolean indices; and
- other non-integer values.

Boolean values are explicitly rejected even though Python treats `bool` as a subclass of `int`.

### 4.2 Raster bounds validation

The selector rejects negative indices and indices outside the raster dimensions.

Valid indices must satisfy:

- `0 <= row < height`
- `0 <= column < width`

### 4.3 Valid-data mask validation

The selected cell must belong to the common valid-data footprint established during Phase 10.3.

Cells outside this footprint, including NoData locations, are rejected.

### 4.4 Susceptibility score validation

The selected susceptibility score must be finite.

Invalid numerical values must not be returned as valid cell-selection results.

## 5. Spatial Coordinate Calculation

The selector uses the affine transform already stored in `ModelInputs`.

The selected cell's centre coordinates are calculated using Rasterio's pixel-coordinate transformation functionality.

The selector does not:

- create a new raster;
- modify the original raster;
- reproject the selected coordinates;
- recalculate susceptibility; or
- alter the model's spatial reference.

The coordinate reference system is returned alongside the coordinates so that downstream components can interpret their spatial meaning correctly.

## 6. Relationship with Phase 10.3

Phase 10.3 established the validated model-input structure.

Phase 10.4 builds directly on that work.

The selector reuses:

- the continuous susceptibility array;
- the common valid-data mask;
- raster height and width;
- the affine transform; and
- the coordinate reference system.

It does not independently reload the six source rasters or reconstruct the MCDA model.

This preserves the separation between input validation and cell selection.

## 7. Automated Testing

Test file:

`tests/test_cell_selector.py`

The tests use a small synthetic raster and a synthetic `ModelInputs` object.

This provides a controlled environment for testing selection behaviour without modifying or regenerating the actual Nairobi County model outputs.

### 7.1 Test results

Command:

```powershell
python -m unittest tests.test_cell_selector -v
```

Result:

**9 tests passed — 0 failures — 0 errors.**

The tests covered:

| Test | Expected behaviour | Result |
|---|---|---|
| Valid cell selection | Returns correct cell information | PASS |
| Negative row | Rejects selection | PASS |
| Negative column | Rejects selection | PASS |
| Row outside bounds | Rejects selection | PASS |
| Column outside bounds | Rejects selection | PASS |
| Non-integer row | Rejects selection | PASS |
| Non-integer column | Rejects selection | PASS |
| Boolean index | Rejects selection | PASS |
| Invalid-mask cell | Rejects selection | PASS |

### 7.2 Coordinate verification

The synthetic test raster uses:

- origin: X = 100, Y = 200;
- pixel width: 10;
- pixel height: 10;
- selected row: 1;
- selected column: 2.

The expected pixel-centre coordinates are:

- X = 125.0
- Y = 185.0

The selector returned these expected coordinates and the corresponding synthetic susceptibility score of 0.75.

This confirms that the pixel-centre coordinate calculation behaves as intended in the test environment.

## 8. Read-Only Design

Phase 10.4 is a read-only operation.

The selector does not modify:

- factor rasters;
- the continuous susceptibility raster;
- the classified susceptibility raster;
- model weights;
- AHP consistency information; or
- previously generated analysis outputs.

It only reads the validated model-input arrays and returns information about the requested cell.

## 9. Limitations and Scope

The current implementation selects raster cells using row and column indices.

It does not yet accept geographic coordinates, perform address-based searches, interpret natural-language requests, or generate recommendations.

Those capabilities belong to subsequent interpreter and decision-support development.

The current automated tests establish correct behaviour for the tested synthetic cases. They do not constitute a separate validation of the entire Nairobi County susceptibility model.

## 10. Phase 10.4 Conclusion

Phase 10.4 successfully implements raster cell selection using the validated model inputs from Phase 10.3.

The implementation validates index types, raster bounds, valid-data membership, and numerical score validity. It returns the selected cell's indices, pixel-centre coordinates, CRS, and continuous susceptibility score.

All nine automated tests passed.

The implementation remains read-only and does not alter the existing MCDA model or its outputs.

**Phase 10.4 — Raster Cell Selection: Implementation and automated tests complete.**