
# Phase 10.3 — Interpreter Input Reading and Validation

## 1. Purpose

Phase 10.3 implements the input-reading and validation layer for the GeoAI Flood Risk Decision Agent.

The objective is to ensure that the interpreter can safely access the existing MCDA model inputs without modifying or regenerating the original model outputs.

The implementation establishes a reproducible validation process for:

- the five aligned factor rasters;
- the continuous susceptibility raster;
- spatial grid compatibility;
- valid-data coverage;
- factor score ranges;
- AHP weights and consistency ratio;
- saved model metadata; and
- numerical reconstruction of the existing susceptibility output.

## 2. Implementation

The input loader is implemented in:

`src/interpreter/input_loader.py`

The interpreter package is initialized through:

`src/interpreter/__init__.py`

The loader imports the existing AHP configuration and calculation function from:

`src/flood_factors/mcda_flood_susceptibility.py`

It does not introduce a separate set of factor weights or duplicate the AHP weighting configuration.

The loader reads the five existing aligned factor rasters:

1. Elevation score
2. Slope score
3. Distance-to-rivers score
4. Land-cover score
5. Population score

It also reads the existing continuous susceptibility raster:

`data/analysis/mcda/flood_susceptibility.tif`

The classified susceptibility raster is not used as the continuous numerical input.

## 3. Spatial Compatibility

All six input rasters were confirmed to share:

| Property | Verified value |
|---|---|
| CRS | EPSG:32737 |
| Width | 1603 cells |
| Height | 1019 cells |
| Resolution | Approximately 30.8655 m |
| NoData | -9999 |
| Data type | float32 |
| Band count | 1 |

The loader checks the CRS, dimensions, affine transform, resolution, and spatial bounds.

This ensures that corresponding raster cells represent the same spatial locations.

## 4. Valid-Data Mask

The loader constructs a common valid-data mask by combining the valid cells of all five factor rasters.

A cell is considered valid when its factor value is finite and is not equal to the declared NoData value.

The resulting common mask is compared with the valid-data mask of the stored susceptibility raster.

The validation confirmed:

- common valid cells: 553,860;
- stored susceptibility valid cells: 553,860;
- mask agreement: PASS.

This confirms that the existing susceptibility output uses the same common valid-data footprint as the five aligned factors.

## 5. Factor Score Validation

Each factor is checked within the common valid-data footprint.

Valid factor scores must be finite and within the expected 0–1 range, allowing a numerical tolerance of 0.000001.

The loader rejects factor inputs containing values outside the accepted range.

These scores represent standardized modelling inputs. They are not flood probabilities.

## 6. AHP Weight Validation

The loader derives the AHP weights using the existing MCDA implementation.

The derived values are compared with the weights stored in the continuous susceptibility GeoTIFF metadata.

The verified weights are:

| Factor | Weight |
|---|---:|
| Elevation | 0.1868744589 |
| Slope | 0.1868744589 |
| Distance to rivers | 0.4352900433 |
| Land cover | 0.1285887446 |
| Population | 0.0623722944 |
| **Total** | **1.0000000000** |

The calculated AHP consistency ratio is:

**0.0269475117**

The accepted consistency threshold is 0.10.

The calculated weights and consistency ratio agree with the saved GeoTIFF metadata within the configured numerical tolerances.

The loader also checks the model identifier and weighting method recorded in the raster metadata.

## 7. Numerical Reconstruction

The loader independently reconstructs the continuous susceptibility scores using the five factor rasters and the derived AHP weights.

The weighted linear combination is:

\[
S = \sum_{i=1}^{5} w_i x_i
\]

Where:

- \(S\) represents the reconstructed susceptibility score;
- \(w_i\) represents the AHP weight of each factor;
- \(x_i\) represents the standardized factor score.

The reconstructed values are converted to float32 before comparison with the stored susceptibility raster.

The maximum accepted absolute difference is:

**0.00001**

The real-data validation produced:

**Maximum absolute reconstruction error: 0.000000000000**

The reconstruction check therefore passed.

## 8. Error Handling

The loader rejects:

- missing raster files;
- rasters containing multiple bands;
- rasters without a defined CRS;
- rasters without the expected NoData value;
- rasters using an unexpected data type;
- spatially incompatible rasters;
- factor values outside the accepted range;
- empty common valid-data coverage;
- disagreement between the factor and output masks;
- invalid or inconsistent AHP metadata; and
- reconstructed susceptibility values outside the accepted tolerance.

These checks prevent the interpreter from silently proceeding with incompatible or unreliable inputs.

## 9. Automated Testing

Automated tests are implemented in:

`tests/test_input_loader.py`

The tests use small temporary raster datasets rather than modifying the project's real input files.

Six test cases were executed:

| Test | Expected behaviour | Result |
|---|---|---|
| Valid inputs | Accept valid dataset | PASS |
| Missing factor | Reject missing raster | PASS |
| Grid mismatch | Reject incompatible grid | PASS |
| Invalid factor values | Reject values outside 0–1 | PASS |
| Output mask mismatch | Reject inconsistent mask | PASS |
| Weight metadata mismatch | Reject inconsistent AHP weight | PASS |

Test execution:

`python -m unittest discover -s tests -p "test_input_loader.py" -v`

Result:

**Ran 6 tests — OK**

## 10. Numerical and Dependency Notes

The loader uses explicit numerical tolerances:

| Check | Tolerance |
|---|---:|
| Factor score range | 0.000001 |
| AHP weight comparison | 0.000000001 |
| AHP consistency ratio comparison | 0.000000001 |
| Susceptibility reconstruction | 0.00001 |

The terminal also reported a NumPy 2.5 DeprecationWarning associated with Rasterio array reading.

This warning did not interrupt execution or cause any validation test to fail.

It is recorded as a dependency compatibility consideration rather than a model validation failure.

## 11. Data Integrity

Phase 10.3 is read-only.

The implementation does not:

- regenerate the MCDA susceptibility raster;
- modify factor rasters;
- change AHP weights;
- alter classification thresholds;
- overwrite existing model outputs; or
- modify the Phase 9 validation results.

The real-data loader completed successfully and explicitly reported that no model files were modified.

## 12. Phase 10.3 Conclusion

Phase 10.3 successfully established the interpreter's input-reading and validation layer.

The five aligned factor rasters and continuous susceptibility raster were successfully read and validated.

Spatial compatibility, valid-data coverage, factor score ranges, AHP metadata, and numerical reconstruction were all confirmed.

All six automated tests passed, including tests designed to reject missing files, spatial incompatibility, invalid factor values, mask disagreement, and incorrect weight metadata.

The implementation provides a validated foundation for the next stage of Phase 10.

**Phase 10.3 status: COMPLETE.**
