# Phase 10.7 — Susceptibility Score Reconstruction and Verification

## 1. Overview

Phase 10.7 implements the reconstruction and numerical verification of the flood susceptibility score for a selected raster cell.

It uses the five weighted factor contributions calculated in Phase 10.6 to reconstruct the susceptibility score and compare the reconstructed value against the original stored susceptibility score.

The purpose is to establish whether the selected cell's stored score is consistent with the underlying weighted factor contributions.

This is a deterministic verification step. It does not modify the original susceptibility raster, factor rasters, AHP weights, or model parameters.

## 2. Objectives

The implementation is designed to:

- Reconstruct the susceptibility score from all five weighted factor contributions.
- Follow the factor order used by the original MCDA model.
- Use float64 arithmetic for accumulation.
- Convert the reconstructed result to float32 to match the original MCDA output precision.
- Compare the reconstructed score against the stored susceptibility score.
- Apply the established reconstruction tolerance.
- Return a structured verification result.
- Distinguish a numerical verification failure from an invalid input or software error.

## 3. Implementation

**Source module:**

`src/interpreter/score_verification.py`

**Test module:**

`tests/test_score_verification.py`

**Main function:**

`verify_susceptibility_score(contributions)`

The function accepts a `WeightedContributions` object produced by Phase 10.6.

## 4. Reconstruction methodology

The original MCDA model calculates the susceptibility score as a weighted sum of the five standardized factor scores.

For a selected raster cell:

\[
S = \sum_{i=1}^{5} (F_i \times W_i)
\]

Where:

- \(S\) is the reconstructed susceptibility score.
- \(F_i\) is the standardized score of factor \(i\).
- \(W_i\) is the corresponding AHP weight.

The five factors are processed in the established model order:

1. Elevation
2. Slope
3. Distance to rivers
4. Land cover
5. Population

Phase 10.7 sums the weighted contributions produced by Phase 10.6. It does not independently recalculate the individual factor contributions.

## 5. Numerical precision

The original MCDA implementation accumulates weighted factor values using float64 arithmetic and converts the final susceptibility array to float32.

The Phase 10.7 implementation follows the same numerical procedure:

1. Accumulate the five weighted contributions using float64 arithmetic.
2. Convert the reconstructed score to float32.
3. Compare the reconstructed value with the stored susceptibility score.

This approach maintains consistency with the original model's output precision.

## 6. Reconstruction tolerance

The implementation reuses the existing tolerance defined in:

`src/interpreter/input_loader.py`

The shared constant is:

`RECONSTRUCTION_TOLERANCE = 1e-5`

The absolute difference is calculated as:

\[
D = |S_r - S_s|
\]

Where:

- \(D\) is the absolute difference.
- \(S_r\) is the reconstructed score.
- \(S_s\) is the stored susceptibility score.

Verification passes when:

\[
D \leq 10^{-5}
\]

The tolerance is imported from the input loader rather than duplicated in the score-verification module.

## 7. Verification outcomes

The function returns a structured `ScoreVerification` object.

The result contains:

- Raster row and column.
- Selected cell coordinates.
- Coordinate reference system.
- Reconstructed susceptibility score.
- Stored susceptibility score.
- Absolute difference.
- Applied tolerance.
- Boolean verification status.

The `verification_passed` field communicates the numerical outcome.

**Successful verification**

When the absolute difference is within the established tolerance, `verification_passed` is `True`.

**Failed verification**

When the absolute difference exceeds the tolerance, `verification_passed` is `False`.

A numerical mismatch does not automatically raise an exception. It is returned as a verification result so that subsequent interpretation can distinguish an unsuccessful reconstruction from invalid input.

## 8. Input validation

Before reconstruction, the implementation checks:

- The supplied object is a `WeightedContributions` instance.
- All five expected factor contributions are present.
- No unexpected factors are supplied.
- Each factor contribution is a `FactorContribution` instance.
- Factor scores are finite and within the accepted 0–1 range.
- AHP weights are finite and within the accepted 0–1 range.
- Weighted contributions are finite and within the accepted 0–1 range.
- The stored susceptibility score is finite and within the accepted 0–1 range.

Invalid inputs raise an appropriate `TypeError` or `ValueError`.

## 9. Relationship with previous phases

Phase 10.7 depends on the outputs of earlier interpreter components.

| Phase | Responsibility |
|---|---|
| 10.3 | Load and validate model inputs |
| 10.4 | Select a valid raster cell |
| 10.5 | Extract factor evidence |
| 10.6 | Calculate individual weighted contributions |
| 10.7 | Reconstruct and verify the stored susceptibility score |

The separation of responsibilities keeps the interpretation workflow modular and testable.

## 10. Testing and validation

The dedicated test module contains 19 tests.

The tests cover:

- Successful score reconstruction.
- Inclusion of all five weighted contributions.
- Preservation of the stored score.
- Preservation of selected-cell metadata.
- Use of the shared reconstruction tolerance.
- Verification within tolerance.
- Verification failure beyond tolerance without raising an exception.
- Missing and unexpected factor contributions.
- Invalid contribution object types.
- Non-finite and out-of-range factor scores.
- Non-finite and out-of-range AHP weights.
- Non-finite and out-of-range weighted contributions.
- Invalid stored susceptibility scores.
- Invalid top-level input objects.

### Test execution

```powershell
python -m py_compile src\interpreter\score_verification.py
python -m py_compile tests\test_score_verification.py
python -m unittest tests.test_score_verification -v
```

### Dedicated test result

**19 tests passed.**

The complete interpreter regression suite was also executed:

```powershell
python -m unittest discover -s tests -v
```

**Full regression result: 64 tests passed.**

No test failures were reported.

## 11. Scientific and analytical safeguards

Phase 10.7 verifies numerical consistency between the weighted contributions and the stored susceptibility score.

It does not establish that the susceptibility model accurately predicts real-world flood events.

The susceptibility score remains a relative model index, not a calibrated flood probability.

The limitations identified during Phase 9 validation remain applicable. Score reconstruction must not be presented as independent evidence of predictive accuracy.

The implementation does not modify AHP weights, factor standardization, classification thresholds, or the original MCDA outputs.

## 12. Output and modification policy

The module produces an in-memory `ScoreVerification` result for the selected cell.

It does not:

- Rewrite the susceptibility raster.
- Modify factor rasters.
- Recalculate or adjust AHP weights.
- Change susceptibility classification thresholds.
- Modify Phase 9 validation results.

This preserves the integrity and reproducibility of the original analytical model.

## 13. Phase 10.7 completion status

**Status: Implementation and testing complete.**

Deliverables:

- `src/interpreter/score_verification.py`
- `tests/test_score_verification.py`
- `Docs/phase10_score_verification.md`

Validation:

- Python compilation checks passed.
- Dedicated tests: 19/19 passed.
- Full interpreter regression suite: 64/64 passed.

Phase 10.7 establishes a numerical verification step between weighted factor contribution analysis and deterministic interpretation in Phase 10.8.
