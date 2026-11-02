# Phase 10 — Deterministic GeoAI Interpreter Design

## 1. Document Purpose

This document defines the technical design for the deterministic interpretation component of the GeoAI Flood Risk Decision Agent.

The project study area is Nairobi County, Kenya.

The interpreter will build on the existing MCDA flood susceptibility model. Its purpose is to retrieve the model evidence for a selected raster location, calculate individual factor contributions, reconstruct the combined susceptibility score, verify the result against the existing output raster, and provide a scientifically responsible explanation.

This document establishes the intended architecture, processing workflow, validation rules, output structure, error handling, testing requirements, and implementation sequence before development begins.

The interpreter must preserve the project's existing modelling assumptions and Phase 9 findings.

## 2. Relationship to the Existing Model

The existing model combines five standardized and spatially aligned factor rasters using an Analytic Hierarchy Process (AHP)-derived weighted linear combination.

The factor rasters are stored in:

`data/analysis/aligned/`

The continuous susceptibility raster is stored at:

`data/analysis/mcda/flood_susceptibility.tif`

The existing model calculates AHP weights from a pairwise comparison matrix, validates the consistency ratio, checks the compatibility of input rasters, creates a common valid-data mask, calculates the weighted overlay, and records methodological information in the output GeoTIFF metadata.

The interpreter must reuse these established modelling decisions rather than introduce a competing calculation.

### 2.1 Factor inputs

The five aligned factor rasters are:

- `data/analysis/aligned/elevation_score.tif`
- `data/analysis/aligned/slope_score.tif`
- `data/analysis/aligned/distance_to_rivers_score.tif`
- `data/analysis/aligned/landcover_score.tif`
- `data/analysis/aligned/population_score.tif`

The existing continuous susceptibility raster is:

- `data/analysis/mcda/flood_susceptibility.tif`

These paths are project-relative and must remain consistent with the project's existing portability decision.

### 2.2 Factor interpretation

The existing factor-scoring methods establish the following meanings:

| Factor | Existing scoring method | Meaning of a higher score |
|---|---|---|
| Elevation | Inverse min-max normalization | Lower elevation under the model's scoring assumption |
| Slope | Inverse min-max normalization | Gentler slope under the model's scoring assumption |
| Distance to rivers | Inverse min-max normalization | Closer to rivers |
| Land cover | Explicit category-to-score lookup | Depends on the assigned land-cover category score |
| Population | Positive min-max normalization | Higher population score, representing an exposure-related factor |

The land-cover scores are modelling assumptions, not measured flood probabilities.

Population represents an exposure-related factor. A high population score does not, by itself, establish greater physical flood susceptibility.

The interpreter must preserve this distinction in its explanations.

## 3. Objectives

The deterministic interpreter must:

1. Load the existing factor rasters and continuous susceptibility raster.
2. Accept a raster cell as the initial location-selection method.
3. Validate the selected cell against raster dimensions and data validity.
4. Extract all five factor scores at the selected location.
5. obtain the authoritative AHP weights associated with the existing model result.
6. Calculate each factor's weighted contribution.
7. Reconstruct the continuous MCDA score.
8. Compare the reconstructed score with the saved susceptibility raster value.
9. Report numerical verification status.
10. Return structured evidence suitable for testing and later natural-language interpretation.
11. Explain the result without presenting it as a calibrated flood probability.
12. Preserve the documented limitations of the existing model.

## 4. Scope and Boundaries

### 4.1 Included in the first version

The first version will provide:

- Deterministic raster-cell interpretation.
- Validation of required files and raster compatibility.
- Extraction of five factor scores.
- Retrieval and validation of authoritative model weights.
- Calculation of weighted contributions.
- Reconstruction and verification of the stored score.
- Structured results.
- Plain-English interpretation based on verified numerical evidence.
- Clear error handling.
- Automated tests for valid and invalid inputs.

### 4.2 Deferred capabilities

The following capabilities are outside the initial implementation:

- Natural-language query interpretation.
- Language-model-generated explanations.
- Interactive map interfaces.
- Streamlit application development.
- Dynamic flood forecasting.
- Event-specific flood prediction.
- Model retraining or recalibration.
- Changes to the existing AHP matrix or factor weights.
- Regeneration of the existing susceptibility raster.

Geographic-coordinate selection is planned as a subsequent extension after raster-cell interpretation has been implemented and tested.

## 5. Core Calculation

The existing model uses a weighted linear combination:

FS = wE × E + wS × S + wR × R + wL × L + wP × P

Where:

- FS is the combined MCDA susceptibility score.
- E is the elevation score.
- S is the slope score.
- R is the distance-to-rivers score.
- L is the land-cover score.
- P is the population score.
- wE, wS, wR, wL, and wP are the corresponding AHP weights.

For each factor, the interpreter will calculate:

Contribution_i = Score_i × Weight_i

The reconstructed susceptibility score will be:

FS_reconstructed = Sum of all five weighted contributions

The interpreter will compare this reconstructed score with the stored value in `flood_susceptibility.tif`.

### 5.1 Weight authority

The interpreter must not independently invent, manually round, or silently substitute weights.

The implementation must establish a single, traceable source of weights consistent with the existing model. The weights recorded in the susceptibility raster metadata will be used as an important verification reference.

The implementation must verify that:

- All five required factor weights are present.
- All weights are finite and non-negative.
- The weights sum to approximately one.
- The weights are consistent with the model configuration that generated the output.
- Any disagreement between the current configuration and the saved output metadata is detected and reported.

The exact code organization for retrieving and validating these weights will be settled during implementation. Duplicating the AHP matrix or maintaining an independent set of rounded weights should be avoided.

## 6. Proposed Processing Workflow

The interpreter will follow this sequence.

### Step 1 — Initialize

Resolve project-relative paths and identify the required factor rasters and susceptibility raster.

### Step 2 — Validate required inputs

Check that all required files exist and can be opened.

If a required file is missing or unreadable, stop and identify the affected file.

### Step 3 — Validate raster compatibility

Check that the five factor rasters share the required spatial grid, including:

- Coordinate reference system.
- Affine transform.
- Width and height.
- Compatible spatial extent.

Confirm that the continuous susceptibility raster is compatible with the factor rasters.

The existing project uses EPSG:32737 for the aligned model grid. The implementation must verify the actual raster metadata rather than assume that a filename guarantees the correct CRS.

### Step 4 — Validate weights

Retrieve the authoritative weights and validate their completeness, numeric validity, sum, and consistency with the model output metadata.

### Step 5 — Receive a raster cell

The initial interface will accept a zero-based raster row and column.

Both values must be integers within the raster dimensions.

The implementation must document the indexing convention clearly.

### Step 6 — Validate the selected cell

Check that the selected cell is inside the raster and contains valid data in every required factor raster and in the continuous susceptibility raster.

### Step 7 — Extract factor scores

Retrieve the five standardized factor scores for the selected cell.

All extracted values must be finite and within the expected 0–1 range.

### Step 8 — Calculate weighted contributions

Multiply each factor score by its corresponding authoritative weight.

Return both the original score and the weighted contribution for every factor.

### Step 9 — Reconstruct the score

Calculate the sum of the five weighted contributions using a numerically appropriate calculation.

The reconstruction should follow the existing model's calculation as closely as practical, including its use of high-precision intermediate arithmetic.

### Step 10 — Verify against the saved raster

Read the stored continuous susceptibility score for the same cell.

Calculate the absolute difference:

D = abs(FS_reconstructed - FS_stored)

Compare the difference against the documented numerical tolerance.

### Step 11 — Generate the explanation

Produce a structured result and a plain-English explanation using the validated evidence.

### Step 12 — Return the result

Return the location, factor scores, weights, contributions, stored and reconstructed scores, verification status, interpretation, and relevant limitations.

The interpreter must not overwrite or regenerate the original susceptibility raster.

## 7. Location Selection

### 7.1 Initial method: raster row and column

The initial implementation will use raster row and column selection.

This method supports reproducible tests because a particular row and column identifies a specific cell in the validated raster grid.

The interpreter must reject:

- Negative row indices.
- Negative column indices.
- Rows outside the raster dimensions.
- Columns outside the raster dimensions.
- Non-integer indices where integer indices are required.

It must not silently select a neighbouring cell when the requested cell is invalid.

### 7.2 Planned extension: geographic coordinates

Geographic-coordinate selection will be implemented after cell-based extraction and verification are reliable.

The extension must:

1. Validate that coordinates are finite and valid.
2. Require or establish the coordinate reference system of the supplied coordinates.
3. Transform coordinates to the raster CRS when necessary.
4. Identify the corresponding raster cell using the raster transform.
5. Check that the resulting cell lies within the raster.
6. Reuse the same cell-validation and interpretation logic as row-and-column selection.

The coordinate system must never be guessed silently.

## 8. NoData and Data Validation

The existing MCDA model uses a common valid-data mask across all five factors.

The interpreter must preserve this principle.

A complete explanation is permitted only when all five factor scores and the stored susceptibility value are valid.

The interpreter must reject or clearly flag a selected cell if:

- Any factor contains its declared NoData value.
- Any factor contains a non-finite value.
- Any factor score falls outside the accepted 0–1 range.
- The stored susceptibility value is NoData or non-finite.
- Required raster metadata is inconsistent.
- The selected location cannot be identified unambiguously.

The implementation must use each raster's declared NoData metadata and account for non-finite values. It must not assume that every invalid cell is represented by the same sentinel value.

The interpreter must not replace missing scores with zero, calculate a partial five-factor result, or renormalize the weights for a selected cell.

Such actions would change the existing model's calculation.

## 9. Numerical Verification

The existing MCDA script accumulates weighted values using float64 arithmetic and stores the final susceptibility raster using float32.

Small differences may therefore arise from floating-point representation and storage precision.

The implementation must establish a numerical tolerance appropriate to the existing calculation and verify it through tests.

The tolerance must not be chosen merely to make a failed calculation pass.

For each valid cell, the interpreter will report:

- Reconstructed score.
- Stored score.
- Absolute difference.
- Numerical tolerance.
- Verification status.

Verification succeeds only when the absolute difference is within the accepted tolerance.

If verification fails, the interpreter must report the discrepancy and avoid presenting the result as successfully verified.

Potential causes, such as mismatched factor inputs, inconsistent weights, or an unexpected numerical difference, should be investigated rather than silently corrected.

## 10. Output Structure

The deterministic interpreter should return a structured result with the following components.

### 10.1 Location information

- Raster row.
- Raster column.
- Geographic coordinates when available and correctly derived.
- Raster coordinate reference system.

### 10.2 Overall result

- Stored susceptibility score.
- Reconstructed susceptibility score.
- Absolute difference.
- Numerical tolerance.
- Verification status.

### 10.3 Factor evidence

For each of the five factors:

- Factor name.
- Extracted factor score.
- AHP weight.
- Weighted contribution.

### 10.4 Interpretation

- Plain-English explanation of the combined score.
- Explanation of the individual weighted contributions.
- Identification of the largest numerical contributions.
- Distinction between physical susceptibility indicators and the population exposure indicator.
- Relevant model limitations.

The largest numerical contribution may be described as the factor contributing most to the calculated score at the selected cell. It must not be described as proof of causation or as definitive evidence of the factor's real-world predictive importance.

### 10.5 Verification and limitations

The result must clearly communicate whether numerical verification succeeded.

It must also explain that the continuous MCDA score is a relative susceptibility index and is not a calibrated probability of flooding.

## 11. Plain-English Interpretation Rules

The interpreter must distinguish three concepts.

### 11.1 Factor score

A standardized value describing how a factor was scored under the existing modelling method.

### 11.2 Weighted contribution

The factor score multiplied by its AHP weight. This measures the factor's numerical contribution to the combined MCDA score.

### 11.3 Combined susceptibility score

The sum of the five weighted contributions.

These values must not be confused.

The interpreter must not:

- Interpret a score of 0.80 as an 80% chance of flooding.
- Claim that a factor caused a flood.
- Claim that a location will definitely flood or will never flood.
- Present population exposure as a direct measurement of physical flood susceptibility.
- Claim that successful numerical reconstruction demonstrates predictive accuracy.

The interpretation must reflect the existing model, its input data, its assumptions, and the limitations identified during Phase 9.

## 12. Error Handling

The initial implementation must provide clear, actionable errors for the following conditions.

| Condition | Required behaviour |
|---|---|
| Missing required raster | Stop and identify the missing file |
| Unreadable raster | Stop and identify the affected input |
| Incompatible raster grid | Stop and report the compatibility problem |
| Missing or invalid weights | Stop before producing an explanation |
| Weight/configuration disagreement | Flag the inconsistency rather than silently selecting a value |
| Invalid row or column | Reject the requested cell |
| Out-of-bounds location | Reject the location without substituting another cell |
| NoData in any required input | Do not produce a complete explanation |
| Non-finite factor value | Reject the calculation |
| Factor score outside 0–1 | Reject the calculation |
| Invalid stored susceptibility value | Do not report successful verification |
| Reconstruction mismatch | Report verification failure |
| Invalid geographic coordinates | Reject the request during the coordinate-selection extension |

Error messages should identify the problem without unnecessarily exposing internal implementation details.

## 13. Testing Plan

The interpreter must be tested against actual project data and controlled test cases.

### 13.1 Valid-cell test

Select a known valid cell.

Verify that all five factor scores and the stored susceptibility score can be retrieved.

### 13.2 Contribution test

Calculate the expected contribution for each factor independently:

Contribution_i = Score_i × Weight_i

Compare the expected values with the interpreter's output.

### 13.3 Weight test

Verify that the five weights are complete, finite, non-negative, consistent with the model configuration, and sum to approximately one.

### 13.4 Reconstruction test

Reconstruct the combined score and compare it with the saved raster value using the documented tolerance.

### 13.5 NoData test

Select a cell with NoData in at least one required factor.

Verify that the interpreter does not return a complete explanation.

### 13.6 Bounds test

Test negative indices and row or column indices beyond the raster dimensions.

Verify that invalid selections are rejected.

### 13.7 Input-integrity test

Test missing files, unreadable inputs, incompatible grids, and invalid numerical values.

Verify that each problem is detected and reported.

### 13.8 Numerical-failure test

Use a controlled test case to demonstrate that a reconstruction discrepancy exceeding the tolerance is reported as a failure.

Do not alter the original model output to create this test.

### 13.9 Interpretation-integrity test

Verify that the explanation:

- Uses the actual extracted scores and weights.
- Reports the correct numerical contributions.
- Does not describe susceptibility as a calibrated probability.
- Distinguishes population exposure from physical susceptibility.
- Does not claim that numerical verification proves predictive accuracy.

### 13.10 Coordinate-selection tests

After geographic-coordinate selection is implemented, test coordinate transformation, valid cell selection, out-of-bounds coordinates, invalid coordinate values, and consistency with known raster cells.

## 14. Scientific Limitations

The interpreter explains the existing model. It does not independently establish whether the model accurately predicts flooding.

The continuous susceptibility surface is a relative MCDA index derived from five conditioning factors and AHP-derived weights.

It is not a calibrated probability, a dynamic flood forecast, or a guarantee of flood occurrence.

The project has documented limitations from its Phase 9 analyses and independent UNOSAT reference evaluation. These findings must remain visible in the interpretation and documentation.

Successful numerical reconstruction establishes that the interpreter reproduces the stored model calculation within tolerance. It does not establish that the model has strong predictive performance.

The interpreter must not alter the weights, classifications, or explanation language to obscure unfavourable validation results.

## 15. Proposed Implementation Sequence

Implementation will proceed in manageable stages.

### Phase 10.3 — Read and validate model inputs

- Establish project-relative paths.
- Open the five factor rasters and continuous susceptibility raster.
- Validate raster compatibility.
- Validate the authoritative weights.
- Confirm NoData and finite-value handling.

### Phase 10.4 — Select a raster cell

- Accept row and column indices.
- Validate index types and bounds.
- Establish reproducible cell selection.

### Phase 10.5 — Extract factor evidence

- Retrieve all five factor scores.
- Read the stored susceptibility value.
- Reject invalid or incomplete cells.

### Phase 10.6 — Calculate weighted contributions

- Retrieve the correct weights.
- Calculate each contribution.
- Produce structured factor-level evidence.

### Phase 10.7 — Reconstruct and verify the score

- Calculate the weighted sum.
- Compare it with the saved raster value.
- Apply the documented numerical tolerance.
- Report verification status.

### Phase 10.8 — Generate the deterministic explanation

- Produce the structured result.
- Explain the factor contributions.
- Distinguish susceptibility from exposure.
- Include the relevant scientific limitations.

### Phase 10.9 — Test and validate

- Run unit tests and integration tests.
- Test valid and invalid cells.
- Test numerical reconstruction.
- Test error handling.
- Correct and retest any failures.

### Phase 10.10 — Document and integrate

- Document the implementation.
- Record test evidence.
- Update the project documentation where appropriate.
- Verify the final repository state.

Natural-language interaction and a user-facing interface will follow only after the deterministic interpreter is reliable.

## 16. Completion Criteria

The initial deterministic interpreter will be considered ready when:

1. Required model inputs are loaded and validated.
2. Raster-cell selection is reliable.
3. All five factor scores are extracted correctly.
4. Authoritative weights are retrieved and validated.
5. Individual weighted contributions are calculated correctly.
6. The combined score is reconstructed and checked against the saved raster.
7. Numerical verification succeeds within the documented tolerance for valid test cells.
8. NoData and invalid locations are handled correctly.
9. Error conditions are tested.
10. The output is structured and traceable to the underlying evidence.
11. The explanation does not make unsupported probability or prediction claims.
12. The implementation and its limitations are documented.

The implementation must not be considered complete merely because it runs without an exception or generates a readable explanation.

## 17. Design Status

**Phase 10.2 — Interpreter Design**

The design establishes the interpreter's purpose, inputs, calculations, location-selection approach, validation requirements, output structure, error handling, testing strategy, and implementation sequence.

The next stage is Phase 10.3: reading and validating the existing model inputs.

No interpreter implementation or changes to the existing MCDA model are authorized by this design document alone.