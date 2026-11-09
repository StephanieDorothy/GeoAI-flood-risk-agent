# Phase 10.8 — Deterministic Explanation Generation

## 1. Overview

Phase 10.8 implements deterministic, structured explanations for individual raster cells in the GeoAI Flood Risk Decision Agent.

The module takes the weighted factor contributions generated in Phase 10.6 and the numerical score-verification result generated in Phase 10.7. It combines these outputs into an explanation that describes the selected cell, its factor evidence, the relative contribution of each factor, and the limitations of the result.

The implementation is designed to interpret existing model outputs. It does not modify the underlying flood-susceptibility model, AHP weights, factor standardisation, or classification thresholds.

**Implementation file:** `src/interpreter/explanation_generator.py`

**Test file:** `tests/test_explanation_generator.py`

## 2. Objectives

The objectives of Phase 10.8 are to:

1. Generate a structured explanation for a selected raster cell.
2. Preserve the location and numerical evidence from earlier interpreter stages.
3. Explain all five model factors using their standardized scores, AHP weights, and weighted contributions.
4. Rank factors according to their weighted contributions.
5. Apply deterministic tie-breaking using the established factor order.
6. Distinguish physical-susceptibility indicators from the population exposure-related factor.
7. Validate consistency between weighted contributions and the reconstructed susceptibility score.
8. Withhold the normal contribution ranking when numerical verification fails.
9. Preserve the model's known limitations and avoid unsupported interpretations.

## 3. Inputs

The explanation generator receives two objects.

### 3.1 WeightedContributions

Produced by Phase 10.6 through `calculate_weighted_contributions()`.

The object contains:

- Raster row and column.
- Projected x and y coordinates.
- Coordinate reference system.
- Stored susceptibility score.
- Five factor contributions.

Each factor contribution contains:

- Standardized factor score.
- AHP weight.
- Weighted contribution.

### 3.2 ScoreVerification

Produced by Phase 10.7 through `verify_susceptibility_score()`.

The object contains:

- Raster row and column.
- Projected x and y coordinates.
- Coordinate reference system.
- Reconstructed susceptibility score.
- Stored susceptibility score.
- Absolute difference.
- Numerical tolerance.
- Verification status.

Both objects must refer to the same raster cell.

## 4. Factor Interpretation

The generator explains the five factors in the existing MCDA model.

| Factor | Interpretation |
|---|---|
| Elevation | Higher standardized scores represent lower elevation under inverse standardisation. |
| Slope | Higher standardized scores represent gentler terrain under inverse standardisation. |
| Distance to rivers | Higher standardized scores represent locations closer to mapped rivers. |
| Land cover | The score is assigned using the existing land-cover lookup table. |
| Population | Higher standardized scores represent higher standardized population values and relate to exposure. |

The generator does not infer the original land-cover category from its standardized score because the current factor-evidence object does not retain the original category.

Population is explicitly distinguished from the four physical-susceptibility indicators. Its contribution must not be interpreted as evidence that population density directly increases physical flood susceptibility.

## 5. Contribution Ranking

The generator ranks the five factors using their weighted contributions.

The calculation is based on:

`Weighted contribution = Standardized factor score × AHP weight`

Factors are ranked from the largest weighted contribution to the smallest.

For equal contributions, the generator uses the established `FACTOR_ORDER` as a deterministic tie-breaker.

This ranking describes each factor's numerical contribution under the existing MCDA model. It does not establish causation, independent predictive importance, or the actual cause of a flood event.

## 6. Numerical Validation

Before generating an explanation, the module validates the input evidence.

The validation checks include:

- Correct top-level input object types.
- Matching raster row and column.
- Matching coordinates and CRS.
- Exactly five expected factor contributions.
- Finite factor scores and weights.
- Factor scores and weights within the range [0, 1].
- Each weighted contribution agrees with its factor score multiplied by its weight.
- AHP weights sum to 1 within the configured tolerance.
- Stored susceptibility score is consistent between the input objects.
- Reported absolute difference agrees with the reconstructed and stored scores.
- Verification status agrees with the reported difference and tolerance.

### 6.1 Independent reconstruction safeguard

An additional consistency check independently sums the five validated weighted contributions.

The sum is converted to `float32` to match the numerical reconstruction convention used in Phase 10.7.

The resulting value is compared with the reconstructed score in the `ScoreVerification` object using `SCORE_MATCH_TOLERANCE`.

If the values disagree, the generator raises a `ValueError`.

This safeguard ensures that the explanation does not rely solely on a verification object whose reconstructed score is inconsistent with the contributions being explained.

## 7. Verification Behaviour

The generator handles successful and failed numerical verification differently.

### 7.1 Successful verification

When the reconstructed score agrees with the stored score within the configured tolerance:

- Verification status is reported as `PASS`.
- The contribution ranking is returned.
- The dominant factor is identified.
- The dominant physical-susceptibility factor is identified separately.
- The overall interpretation is generated.

### 7.2 Failed verification

When the difference exceeds the configured tolerance:

- Verification status is reported as `FAIL`.
- Numerical factor evidence is retained for diagnostic review.
- The normal contribution ranking is withheld.
- Dominant-factor fields are set to `None`.
- The interpretation explains why the normal explanation has been withheld.

This prevents an unverified combined score from being presented as a reliable explanation.

## 8. Structured Output

The `generate_deterministic_explanation()` function returns a dictionary containing six top-level sections.

| Output section | Description |
|---|---|
| `location` | Raster row, column, coordinates, and CRS. |
| `susceptibility` | Stored score, reconstructed score, difference, tolerance, and verification result. |
| `factor_evidence` | The five factor scores, AHP weights, weighted contributions, and descriptions. |
| `contribution_ranking` | Factors ranked by weighted contribution, or `None` when verification fails. |
| `interpretation` | Overall explanation, verification interpretation, dominant factors, and population exposure note. |
| `limitations` | Important methodological and validation limitations. |

The structure is intended to support later integration into a user-facing GeoAI decision-support interface.

## 9. Model Limitations Preserved

Phase 10.8 retains the methodological limitations identified in earlier project phases.

1. The susceptibility score is a relative MCDA index, not a calibrated flood probability.
2. The output is not a dynamic flood forecast and does not guarantee that flooding will or will not occur.
3. Population represents an exposure-related indicator, not a direct physical flood-susceptibility process.
4. Numerical score verification confirms consistency between stored and reconstructed values; it does not establish predictive accuracy.
5. The current factor-evidence object does not retain original raw measurements or the original land-cover category.
6. Phase 9 validation against the UNOSAT May 2024 flood extent showed weak and negative agreement with the model's susceptibility ranking. The temporal mismatch between the 2021 model inputs and the 2024 reference data remains an important limitation.

The generator does not modify model weights, thresholds, or factor scores to improve agreement with the validation reference.

## 10. Testing and Validation

Dedicated tests are implemented in:

`tests/test_explanation_generator.py`

The test suite covers:

- Structured output generation.
- Correct cell-location preservation.
- Stored and reconstructed score reporting.
- Successful verification reporting.
- Inclusion of all five factors.
- Factor evidence fields.
- Descending contribution ranking.
- Deterministic tie-breaking.
- Population exposure distinction.
- Separation of physical-susceptibility indicators and population.
- Prevention of unsupported land-cover category inference.
- Inclusion of methodological limitations.
- Deterministic output across repeated calls.
- Failed-verification handling.
- Independent contribution reconstruction.
- Factor contribution consistency.
- Missing factor rejection.
- Invalid AHP weight totals.
- Cell identity mismatch.
- Inconsistent verification status.
- Invalid input object types.

### 10.1 Dedicated test result

Command:

`python -m unittest tests.test_explanation_generator -v`

Result:

**23 tests passed.**

### 10.2 Full regression test result

Command:

`python -m unittest discover -s tests -v`

Result:

**87 tests passed.**

No failures or errors were reported.

The full regression suite confirms that Phase 10.8 did not break the previously implemented Phase 10.3–10.7 interpreter components.

A non-blocking NumPy 2.5 deprecation warning remains in `src/interpreter/input_loader.py:105`. It is recorded as a separate maintenance item.

## 11. Files Created

| File | Purpose |
|---|---|
| `src/interpreter/explanation_generator.py` | Generates validated deterministic explanations. |
| `tests/test_explanation_generator.py` | Tests explanation generation and validation behaviour. |
| `Docs/phase10_deterministic_explanation.md` | Documents the implementation, interpretation rules, limitations, and test results. |

## 12. Phase 10.8 Completion Status

**Status: COMPLETE**

Phase 10.8 successfully implements deterministic explanation generation using the weighted factor contributions and numerical verification evidence from the preceding interpreter stages.

The implementation preserves the existing model methodology, validates the consistency of its inputs, separates population exposure from physical susceptibility, and prevents normal interpretation when score verification fails.

The dedicated and full regression test suites both pass.

**Next stage:** Phase 10.9 — Integration Testing and Validation.