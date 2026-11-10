# Phase 10.9 — Integration Testing and Validation

## 1. Overview

Phase 10.9 validates the integration of the six deterministic interpreter components developed during Phase 10.

The objective is to confirm that the components operate together correctly, preserve the integrity of the underlying flood susceptibility model, handle invalid inputs safely, and produce reproducible explanations.

Testing covers both individual component behaviour and the complete interpretation workflow.

The integration tests use controlled synthetic raster inputs. They are designed to validate the interpreter's internal behaviour and numerical safeguards independently of the production raster datasets.

## 2. Testing Objectives

The testing process addresses the following objectives:

1. Run the complete interpreter workflow from raster-cell selection to deterministic explanation generation.
2. Confirm that valid raster cells can be interpreted successfully.
3. Confirm that invalid raster cells are rejected.
4. Verify that the five weighted factor contributions reconstruct the stored susceptibility score.
5. Confirm that failed numerical verification prevents unsupported contribution rankings.
6. Confirm that repeated interpretation of the same cell produces identical explanations.
7. Run the complete regression suite to identify unintended changes to previously validated components.

## 3. Components Under Test

The integration workflow connects six components.

| Component | Module | Responsibility |
|---|---|---|
| Input loading | `input_loader.py` | Loads and validates model inputs |
| Cell selection | `cell_selector.py` | Selects a valid raster cell and retrieves its spatial location |
| Factor evidence | `factor_evidence.py` | Extracts the five factor scores for the selected cell |
| Weighted contributions | `weighted_contributions.py` | Calculates each factor's weighted contribution |
| Score verification | `score_verification.py` | Reconstructs and checks the stored susceptibility score |
| Explanation generation | `explanation_generator.py` | Produces a deterministic, structured explanation |

The integration test invokes the five processing functions after constructing a controlled `ModelInputs` object. Production input loading is tested separately by the input-loader unit tests.

## 4. Integration Test Design

### 4.1 Synthetic raster inputs

The integration tests construct a synthetic raster grid with:

- Height: 3 cells
- Width: 4 cells
- Coordinate reference system: EPSG:32737
- Pixel dimensions: 10 × 10 map units
- Five factor arrays
- Float32 factor values
- A valid-cell mask containing 12 valid cells

Each factor is assigned a value of 0.8 throughout the synthetic grid.

The authoritative AHP weights are obtained through `calculate_ahp_weights()` rather than being independently hardcoded.

The expected susceptibility score is calculated as the weighted sum of the five factor values and converted to float32 to follow the model's numerical convention.

The synthetic inputs allow the integration workflow to be tested under controlled and repeatable conditions.

### 4.2 Complete workflow

The test helper `run_interpreter_workflow()` executes the components in the following order:

1. `select_raster_cell()`
2. `extract_factor_evidence()`
3. `calculate_weighted_contributions()`
4. `verify_susceptibility_score()`
5. `generate_deterministic_explanation()`

The workflow returns the intermediate results and final explanation so that each stage can be inspected by the tests.

## 5. Integration Test Coverage

Five integration tests were implemented in:

`tests/test_interpreter_integration.py`

### Test 1 — Complete workflow passes

`test_complete_workflow_passes`

Confirms that all processing stages execute successfully for a valid synthetic cell.

Assertions verify:

- Numerical verification passes.
- The selected row and column are preserved.
- The coordinate reference system is retained.
- All five factor scores are included.
- The explanation reports verification status as PASS.
- Five factor evidence items and five contribution rankings are returned.

### Test 2 — Weighted contributions reconstruct the stored score

`test_weighted_contributions_reconstruct_stored_score`

Calculates the sum of the five weighted contributions and compares the reconstructed value with the stored susceptibility score.

The comparison uses a tolerance of 1e-5, consistent with the interpreter's numerical verification approach.

### Test 3 — Invalid cell stops the workflow

`test_invalid_cell_stops_workflow`

Attempts to select a row outside the synthetic raster dimensions.

The test confirms that the workflow raises a `ValueError` rather than continuing with an invalid location.

### Test 4 — Failed verification withholds ranking

`test_failed_verification_withholds_ranking`

Introduces an inconsistent stored susceptibility score of 0.70 while retaining the factor values and authoritative weights.

The test confirms that:

- Numerical verification fails.
- The explanation reports verification status as FAIL.
- Contribution ranking is withheld.
- The dominant factor is not reported.

This safeguards against presenting an unsupported interpretation when numerical reconstruction fails.

### Test 5 — Repeated workflow produces identical explanations

`test_repeated_workflow_produces_identical_explanations`

Runs the same interpretation twice using identical model inputs and the same selected cell.

The resulting explanation dictionaries must be identical.

This confirms deterministic behaviour for the tested inputs.

## 6. Regression Testing

After the integration tests passed independently, the complete test suite was executed.

Command:

```powershell
python -m unittest discover -s tests -v
```

### Regression test results

| Metric | Result |
|---|---:|
| Total tests executed | 92 |
| Tests passed | 92 |
| Failures | 0 |
| Errors | 0 |
| Execution time | 0.669 seconds |
| Overall result | PASS |

The 92 tests include the five new integration tests and the previously established unit tests for the six interpreter components.

### Regression coverage

The complete suite covers:

- Raster-cell selection and boundary validation.
- Deterministic explanation generation.
- Factor evidence extraction.
- Model input validation.
- Weighted contribution calculations.
- Susceptibility score verification.
- End-to-end interpreter integration.

## 7. Numerical and Model Integrity

The integration tests use the authoritative AHP weights derived from the project's existing pairwise comparison matrix.

The factor weights are:

| Factor | Weight |
|---|---:|
| Elevation | 0.1868744589 |
| Slope | 0.1868744589 |
| Distance to rivers | 0.4352900433 |
| Land cover | 0.1285887446 |
| Population | 0.0623722944 |
| **Total** | **1.0000000000** |

The AHP consistency ratio is approximately 0.0269475117, below the conventional 0.10 threshold.

The integration tests do not modify the weights, susceptibility thresholds, or existing model outputs.

## 8. Error Handling and Interpretation Safeguards

The tests demonstrate that the interpreter:

- Rejects invalid raster-cell selections.
- Checks numerical consistency between factor contributions and the stored score.
- Distinguishes successful verification from failed verification.
- Withholds contribution ranking and dominant-factor identification when verification fails.
- Produces repeatable explanations for identical inputs.

These safeguards ensure that a readable explanation is not treated as sufficient evidence of numerical correctness.

## 9. Testing Limitations

The integration tests use synthetic raster arrays rather than selecting a cell from the full production Nairobi raster datasets.

Consequently, the tests establish that the interpreter components work together under controlled conditions. They do not independently establish the correctness of every production raster value or demonstrate the predictive performance of the flood susceptibility model.

The following limitations remain important:

1. The susceptibility output is a relative MCDA index, not a calibrated flood probability.
2. Population represents an exposure-related factor and should not be interpreted as a direct physical flood-generation mechanism.
3. Numerical reconstruction verifies consistency with the stored MCDA output; it does not establish predictive accuracy.
4. Phase 9 validation identified weak or negative agreement with the available UNOSAT flood reference data, alongside a temporal mismatch between model inputs and the 2024 reference event.
5. The integration tests do not resolve the model's external validation limitations.

These limitations must remain visible in subsequent interpretation and user-facing integration.

## 10. NumPy Deprecation Warning

The full regression run produced a non-fatal NumPy 2.5 deprecation warning at:

`src/interpreter/input_loader.py:105`

The warning concerns setting the shape of a NumPy array.

It did not cause any test failure or error. It is recorded as a maintenance item for a separate, controlled update so that the validated input-loading behaviour is not changed unnecessarily during this testing milestone.

## 11. Phase 10.9 Completion Assessment

The approved Phase 10.9 requirements include:

- Running unit and integration tests.
- Testing valid and invalid cells.
- Testing numerical reconstruction.
- Testing error handling.
- Correcting and retesting failures.

All five integration tests passed, and the complete regression suite passed with 92 tests and zero failures or errors.

**Phase 10.9 testing and validation status: PASS.**

This assessment applies to the implemented interpreter components and the tested synthetic workflow. It does not imply that the entire Phase 10 project is complete.

## 12. Next Phase

The next stage is:

**Phase 10.10 — Document and integrate**

The remaining work includes:

- Completing implementation documentation.
- Recording test evidence.
- Updating appropriate project documentation.
- Verifying the final repository state.
- Confirming that the interpreter documentation, module structure, and tests are consistent.

Natural-language interaction and a user-facing interface remain outside the scope of the initial deterministic interpreter and should follow only after its reliability and documentation have been established.