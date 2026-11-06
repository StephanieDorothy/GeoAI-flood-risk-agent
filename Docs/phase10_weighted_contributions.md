# Phase 10.6 — Weighted Factor Contributions

## 1. Purpose

Phase 10.6 implements the calculation of individual weighted contributions for the five standardized factors used in the Nairobi County flood susceptibility MCDA model.

The purpose is to quantify each factor's weighted contribution to the susceptibility index for a previously selected raster cell.

The calculation follows the existing AHP-weighted linear combination approach:

\[
C_i = S_i \times W_i
\]

Where:

- \(C_i\) is the weighted contribution of factor \(i\).
- \(S_i\) is the standardized factor score.
- \(W_i\) is the authoritative AHP weight assigned to that factor.

The implementation is deterministic and read-only. It does not modify the original model inputs or raster outputs.

## 2. Implementation Files

| File | Responsibility |
|---|---|
| `src/interpreter/weighted_contributions.py` | Calculates and structures individual weighted factor contributions. |
| `tests/test_weighted_contributions.py` | Tests contribution calculations and validation behaviour. |
| `src/interpreter/factor_evidence.py` | Supplies the five standardized factor scores and stored susceptibility score. |
| `src/interpreter/input_loader.py` | Supplies validated model inputs and authoritative AHP weights. |

The implementation imports the authoritative factor ordering from:

`src/flood_factors/mcda_flood_susceptibility.py`

This prevents duplication of the model's factor definitions.

## 3. Authoritative AHP Weights

The calculation uses the weights supplied through the validated `ModelInputs` object.

The five factors and their weights are:

| Factor | AHP weight |
|---|---:|
| Elevation | 0.1868744589 |
| Slope | 0.1868744589 |
| Distance to rivers | 0.4352900433 |
| Land cover | 0.1285887446 |
| Population | 0.0623722944 |

The weights are validated to ensure that:

- All five expected factors are present.
- No unexpected factors are supplied.
- Each weight is finite.
- Each weight is within the interval [0, 1].
- The five weights sum to approximately 1.0, using an absolute tolerance of \(10^{-8}\).

The implementation does not independently redefine or modify the AHP weights.

## 4. Contribution Calculation

For each factor, the implementation multiplies its standardized score by its corresponding AHP weight.

The five calculations are:

- Elevation contribution = elevation score × elevation weight.
- Slope contribution = slope score × slope weight.
- River-distance contribution = river-distance score × river-distance weight.
- Land-cover contribution = land-cover score × land-cover weight.
- Population contribution = population score × population weight.

Each factor is processed independently.

The implementation validates that every factor score is finite and falls within the expected interval [0, 1].

## 5. Output Structure

The module defines two dataclasses.

### 5.1 FactorContribution

Stores the three values associated with an individual factor:

- `factor_score`
- `weight`
- `weighted_contribution`

### 5.2 WeightedContributions

Stores the structured output for the selected raster cell:

- `row`
- `column`
- `x`
- `y`
- `crs`
- `susceptibility_score`
- `factor_contributions`

The `factor_contributions` dictionary contains one `FactorContribution` object for each of the five factors.

This structure preserves the relationship between the original standardized score, its AHP weight and the resulting weighted contribution.

## 6. Validation and Error Handling

The implementation rejects invalid or incomplete inputs.

Validation includes:

- Incorrect model input object type.
- Incorrect factor evidence object type.
- Missing factor scores.
- Unexpected factor scores.
- Missing AHP weights.
- Unexpected AHP weights.
- Non-finite factor scores.
- Factor scores outside [0, 1].
- Non-finite AHP weights.
- Negative AHP weights.
- AHP weights greater than 1.
- AHP weights that do not sum to approximately 1.0.

Invalid inputs are rejected rather than silently accepted.

## 7. Relationship with Previous Components

Phase 10.6 builds on the earlier interpreter components.

### Phase 10.3 — Model Input Loading and Validation

Provides validated factor arrays, susceptibility data and authoritative AHP weights.

### Phase 10.4 — Raster Cell Selection

Identifies a valid raster cell and preserves its spatial location.

### Phase 10.5 — Factor Evidence Extraction

Retrieves the five standardized factor scores and stored susceptibility score for the selected cell.

### Phase 10.6 — Weighted Factor Contributions

Calculates the individual weighted contribution of each factor and returns structured factor-level evidence.

These components establish a traceable progression from validated model inputs to individual weighted contributions for a selected spatial location.

## 8. Testing and Verification

The implementation was compiled using:

`python -m py_compile src\interpreter\weighted_contributions.py`

The test module was compiled using:

`python -m py_compile tests\test_weighted_contributions.py`

Both compilation checks completed successfully.

The Phase 10.6 test suite was executed using:

`python -m unittest tests.test_weighted_contributions -v`

**Result: 17 tests passed, 0 failures.**

The earlier components were also retested.

| Test module | Tests passed |
|---|---:|
| `tests.test_weighted_contributions` | 17 |
| `tests.test_factor_evidence` | 13 |
| `tests.test_cell_selector` | 9 |
| **Total** | **39** |

All 39 targeted tests passed.

### 8.1 Test Coverage

The Phase 10.6 tests cover:

1. Successful weighted contribution calculations.
2. Retrieval of all five factor contributions.
3. Preservation of factor scores and weights.
4. Use of authoritative model weights.
5. Preservation of selected-cell information.
6. Rejection of missing factor scores.
7. Rejection of unexpected factor scores.
8. Rejection of missing AHP weights.
9. Rejection of unexpected AHP weights.
10. Rejection of non-finite weights.
11. Rejection of negative weights.
12. Rejection of weights greater than 1.
13. Rejection of weights that do not sum to approximately 1.
14. Rejection of factor scores outside the accepted range.
15. Rejection of non-finite factor scores.
16. Rejection of invalid model input objects.
17. Rejection of invalid evidence objects.

## 9. Scientific and Architectural Boundaries

Phase 10.6 calculates individual factor contributions only.

It does not:

- Sum the five contributions.
- Reconstruct the overall susceptibility score.
- Compare the reconstructed score against the stored raster value.
- Generate a natural-language explanation.
- Modify AHP weights.
- Modify factor scores.
- Change susceptibility classifications.
- Alter the original model rasters.

The weighted contributions are components of the existing MCDA relative susceptibility index. They must not be interpreted as probabilities of flooding.

Population remains a distinct factor. Its contribution must be interpreted in the context of population-related exposure, rather than confused with the physical terrain and hydrological susceptibility represented by the other factors.

The unfavorable findings from the Phase 9 UNOSAT event-level validation remain relevant limitations and are not changed by this calculation.

## 10. Phase Completion

Phase 10.6 — Weighted Factor Contributions is implemented and has passed all 17 dedicated tests.

The previous Phase 10.4 and Phase 10.5 components were retested successfully, bringing the total targeted test count to 39 passing tests.

The component provides structured factor-level weighted evidence for the next stage.

Phase 10.7 — Reconstruct and Verify the Susceptibility Score — remains a separate implementation stage.

No changes were made to the original Nairobi County MCDA model, its AHP weights or its raster outputs.