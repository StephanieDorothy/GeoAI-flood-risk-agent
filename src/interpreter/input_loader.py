
"""
Phase 10.3 — Read and validate existing MCDA model inputs.

This module is read-only. It does not modify or regenerate any model raster.
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from src.flood_factors.mcda_flood_susceptibility import (
    CR_THRESHOLD,
    FACTOR_FILES,
    FACTOR_ORDER,
    OUTPUT_FILE,
    calculate_ahp_weights,
)


# Numerical tolerances
VALUE_TOLERANCE = 1e-6
WEIGHT_TOLERANCE = 1e-9
CR_TOLERANCE = 1e-9
RECONSTRUCTION_TOLERANCE = 1e-5

EXPECTED_NODATA = -9999.0


@dataclass
class ModelInputs:
    """Validated inputs required by the GeoAI interpreter."""

    factor_arrays: dict[str, np.ndarray]
    susceptibility: np.ndarray
    valid_mask: np.ndarray
    weights: dict[str, float]
    consistency_ratio: float

    crs: Any
    transform: Any
    width: int
    height: int
    resolution: tuple[float, float]
    nodata: float

    valid_cell_count: int
    factor_paths: dict[str, Path]
    susceptibility_path: Path
    metadata: dict[str, str]

    max_reconstruction_error: float


def _read_raster(path: Path, label: str) -> tuple[np.ndarray, dict]:
    """Read one single-band raster and return its array and metadata."""

    if not path.exists():
        raise FileNotFoundError(
            f"Missing {label} raster: {path}"
        )

    try:
        with rasterio.open(path) as dataset:
            if dataset.count != 1:
                raise ValueError(
                    f"{label} must contain exactly one band; "
                    f"found {dataset.count}."
                )

            if dataset.crs is None:
                raise ValueError(
                    f"{label} has no defined CRS."
                )

            if dataset.nodata is None:
                raise ValueError(
                    f"{label} has no declared NoData value."
                )

            if not np.isclose(
                dataset.nodata,
                EXPECTED_NODATA,
                atol=0,
                rtol=0,
            ):
                raise ValueError(
                    f"{label} has unexpected NoData value "
                    f"{dataset.nodata}; expected {EXPECTED_NODATA}."
                )

            if dataset.dtypes[0] != "float32":
                raise ValueError(
                    f"{label} must use float32; "
                    f"found {dataset.dtypes[0]}."
                )

            array = dataset.read(1)

            metadata = {
                "crs": dataset.crs,
                "transform": dataset.transform,
                "width": dataset.width,
                "height": dataset.height,
                "resolution": dataset.res,
                "nodata": dataset.nodata,
                "bounds": dataset.bounds,
                "dtype": dataset.dtypes[0],
                "tags": dataset.tags(),
            }

    except rasterio.errors.RasterioError as error:
        raise ValueError(
            f"Could not read {label} raster at {path}: {error}"
        ) from error

    return array, metadata


def _validate_grid(
    reference_metadata: dict,
    candidate_metadata: dict,
    label: str,
) -> None:
    """Ensure that a raster uses the same spatial grid as the reference."""

    checks = {
        "CRS": (
            candidate_metadata["crs"]
            == reference_metadata["crs"]
        ),
        "dimensions": (
            candidate_metadata["width"]
            == reference_metadata["width"]
            and candidate_metadata["height"]
            == reference_metadata["height"]
        ),
        "affine transform": (
            candidate_metadata["transform"]
            == reference_metadata["transform"]
        ),
        "resolution": (
            candidate_metadata["resolution"]
            == reference_metadata["resolution"]
        ),
        "bounds": (
            candidate_metadata["bounds"]
            == reference_metadata["bounds"]
        ),
    }

    failed = [
        name for name, passed in checks.items()
        if not passed
    ]

    if failed:
        raise ValueError(
            f"{label} is not spatially aligned with the "
            f"reference grid. Failed checks: {', '.join(failed)}."
        )


def _valid_data_mask(
    array: np.ndarray,
    nodata: float,
) -> np.ndarray:
    """Return cells containing finite, non-NoData values."""

    return (
        np.isfinite(array)
        & (array != nodata)
    )


def _validate_factor_values(
    factor_name: str,
    array: np.ndarray,
    valid_mask: np.ndarray,
) -> None:
    """Check that valid factor scores are within the 0–1 range."""

    values = array[valid_mask]

    if values.size == 0:
        raise ValueError(
            f"{factor_name} contains no valid cells."
        )

    if not np.all(np.isfinite(values)):
        raise ValueError(
            f"{factor_name} contains non-finite valid values."
        )

    minimum = float(np.min(values))
    maximum = float(np.max(values))

    if (
        minimum < -VALUE_TOLERANCE
        or maximum > 1.0 + VALUE_TOLERANCE
    ):
        raise ValueError(
            f"{factor_name} contains values outside the "
            f"expected 0–1 range. Minimum={minimum}, "
            f"maximum={maximum}."
        )


def _load_and_validate_weights(
    metadata: dict[str, str],
) -> tuple[dict[str, float], float]:
    """Derive AHP weights and compare them with saved raster metadata."""

    # The existing AHP function prints diagnostics.
    # Suppress those prints when it is used internally.
    with contextlib.redirect_stdout(io.StringIO()):
        weights, calculated_cr, _, _ = calculate_ahp_weights()

    weights = {
        name: float(weights[name])
        for name in FACTOR_ORDER
    }

    if not all(np.isfinite(value) for value in weights.values()):
        raise ValueError("Calculated AHP weights contain non-finite values.")

    if any(value < 0 for value in weights.values()):
        raise ValueError("Calculated AHP weights cannot be negative.")

    if not np.isclose(
        sum(weights.values()),
        1.0,
        atol=WEIGHT_TOLERANCE,
        rtol=0,
    ):
        raise ValueError("Calculated AHP weights do not sum to 1.")

    if not np.isfinite(calculated_cr):
        raise ValueError("Calculated AHP consistency ratio is not finite.")

    if calculated_cr > CR_THRESHOLD:
        raise ValueError(
            f"AHP consistency ratio {calculated_cr:.10f} "
            f"exceeds the accepted threshold {CR_THRESHOLD:.10f}."
        )

    for factor in FACTOR_ORDER:
        tag_name = f"{factor}_weight"

        if tag_name not in metadata:
            raise ValueError(
                f"Susceptibility raster is missing metadata tag "
                f"'{tag_name}'."
            )

        try:
            stored_weight = float(metadata[tag_name])
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid stored weight in metadata tag '{tag_name}'."
            ) from error

        if not np.isclose(
            weights[factor],
            stored_weight,
            atol=WEIGHT_TOLERANCE,
            rtol=0,
        ):
            raise ValueError(
                f"AHP weight mismatch for {factor}: "
                f"calculated={weights[factor]:.10f}, "
                f"stored={stored_weight:.10f}."
            )

    if "consistency_ratio" not in metadata:
        raise ValueError(
            "Susceptibility raster is missing the "
            "'consistency_ratio' metadata tag."
        )

    try:
        stored_cr = float(metadata["consistency_ratio"])
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Invalid stored AHP consistency ratio."
        ) from error

    if not np.isclose(
        calculated_cr,
        stored_cr,
        atol=CR_TOLERANCE,
        rtol=0,
    ):
        raise ValueError(
            f"AHP consistency ratio mismatch: "
            f"calculated={calculated_cr:.10f}, "
            f"stored={stored_cr:.10f}."
        )

    return weights, float(calculated_cr)


def load_model_inputs() -> ModelInputs:
    """
    Load and validate the existing MCDA inputs.

    No source raster is modified or regenerated.
    """

    factor_arrays: dict[str, np.ndarray] = {}
    factor_metadata: dict[str, dict] = {}
    factor_paths = {
        name: Path(FACTOR_FILES[name])
        for name in FACTOR_ORDER
    }

    # 1. Read the five aligned factor rasters.
    for factor in FACTOR_ORDER:
        array, metadata = _read_raster(
            factor_paths[factor],
            f"{factor} factor",
        )

        factor_arrays[factor] = array
        factor_metadata[factor] = metadata

    # 2. Use elevation as the reference grid.
    reference_metadata = factor_metadata["elevation"]

    for factor in FACTOR_ORDER:
        _validate_grid(
            reference_metadata,
            factor_metadata[factor],
            f"{factor} factor",
        )

    # 3. Read the existing continuous susceptibility raster.
    susceptibility_path = Path(OUTPUT_FILE)

    susceptibility, susceptibility_metadata = _read_raster(
        susceptibility_path,
        "continuous susceptibility",
    )

    _validate_grid(
        reference_metadata,
        susceptibility_metadata,
        "Continuous susceptibility raster",
    )

    # 4. Construct the common valid-data mask.
    valid_mask = np.ones(
        susceptibility.shape,
        dtype=bool,
    )

    for factor in FACTOR_ORDER:
        factor_mask = _valid_data_mask(
            factor_arrays[factor],
            EXPECTED_NODATA,
        )

        valid_mask &= factor_mask

    if not np.any(valid_mask):
        raise ValueError(
            "The five factor rasters have no common valid cells."
        )

    # 5. Validate factor values.
    for factor in FACTOR_ORDER:
        _validate_factor_values(
            factor,
            factor_arrays[factor],
            valid_mask,
        )

    # 6. Confirm that the stored output has the same valid-data mask.
    output_mask = _valid_data_mask(
        susceptibility,
        EXPECTED_NODATA,
    )

    if not np.array_equal(valid_mask, output_mask):
        mismatch_count = int(
            np.count_nonzero(valid_mask != output_mask)
        )

        raise ValueError(
            "The common factor mask does not match the stored "
            f"susceptibility mask. Mismatched cells: {mismatch_count}."
        )

    output_values = susceptibility[output_mask]

    if not np.all(np.isfinite(output_values)):
        raise ValueError(
            "The susceptibility raster contains non-finite valid values."
        )

    if (
        float(np.min(output_values)) < -VALUE_TOLERANCE
        or float(np.max(output_values)) > 1.0 + VALUE_TOLERANCE
    ):
        raise ValueError(
            "The susceptibility raster contains values outside 0–1."
        )

    # 7. Validate model identity and weighting metadata.
    tags = susceptibility_metadata["tags"]

    if tags.get("model") != "MCDA Flood Susceptibility":
        raise ValueError(
            "Unexpected or missing model identifier in susceptibility metadata."
        )

    if tags.get("weighting_method") != "AHP":
        raise ValueError(
            "Unexpected or missing weighting method in susceptibility metadata."
        )

    weights, consistency_ratio = _load_and_validate_weights(tags)

    # 8. Reconstruct the stored susceptibility values.
    reconstructed = np.zeros(
        susceptibility.shape,
        dtype=np.float64,
    )

    for factor in FACTOR_ORDER:
        reconstructed[valid_mask] += (
            factor_arrays[factor][valid_mask].astype(np.float64)
            * weights[factor]
        )

    reconstructed = reconstructed.astype(np.float32)

    absolute_errors = np.abs(
        reconstructed[valid_mask]
        - susceptibility[valid_mask]
    )

    max_error = float(np.max(absolute_errors))

    if max_error > RECONSTRUCTION_TOLERANCE:
        raise ValueError(
            "The reconstructed susceptibility does not match "
            "the stored model output. "
            f"Maximum absolute error={max_error:.12f}; "
            f"tolerance={RECONSTRUCTION_TOLERANCE:.12f}."
        )

    # 9. Return the validated inputs.
    return ModelInputs(
        factor_arrays=factor_arrays,
        susceptibility=susceptibility,
        valid_mask=valid_mask,
        weights=weights,
        consistency_ratio=consistency_ratio,
        crs=reference_metadata["crs"],
        transform=reference_metadata["transform"],
        width=reference_metadata["width"],
        height=reference_metadata["height"],
        resolution=reference_metadata["resolution"],
        nodata=reference_metadata["nodata"],
        valid_cell_count=int(np.count_nonzero(valid_mask)),
        factor_paths=factor_paths,
        susceptibility_path=susceptibility_path,
        metadata=tags,
        max_reconstruction_error=max_error,
    )


def main() -> None:
    """Run the Phase 10.3 input validation independently."""

    print("=" * 72)
    print("PHASE 10.3 — INTERPRETER INPUT VALIDATION")
    print("=" * 72)

    inputs = load_model_inputs()

    print("\nINPUT VALIDATION: PASS")
    print("-" * 72)

    print(f"CRS: {inputs.crs}")
    print(f"Raster dimensions: {inputs.width} × {inputs.height}")
    print(f"Resolution: {inputs.resolution}")
    print(f"NoData: {inputs.nodata}")

    print("\nFactor rasters:")
    for factor in FACTOR_ORDER:
        print(f"  {factor}: PASS")

    print("\nModel metadata:")
    for factor in FACTOR_ORDER:
        print(
            f"  {factor} weight: "
            f"{inputs.weights[factor]:.10f}"
        )

    print(
        f"  AHP consistency ratio: "
        f"{inputs.consistency_ratio:.10f}"
    )

    print("\nValidation checks:")
    print(f"  Common valid cells: {inputs.valid_cell_count:,}")
    print("  Spatial alignment: PASS")
    print("  Factor score ranges: PASS")
    print("  Output mask agreement: PASS")
    print("  AHP metadata agreement: PASS")
    print("  Susceptibility reconstruction: PASS")
    print(
        f"  Maximum reconstruction error: "
        f"{inputs.max_reconstruction_error:.12f}"
    )

    print("\nNo model files were modified.")
    print("=" * 72)


if __name__ == "__main__":
    main()
