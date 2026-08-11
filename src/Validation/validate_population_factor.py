"""
============================================================
GeoAI Flood Risk Agent
Validation Script - Population Exposure Flood Factor
============================================================

Validates the prepared population exposure raster used in
the Flood Risk Decision Agent.

The validation compares the original analysis-ready
population raster with the prepared flood-factor raster to
confirm that:

1. The output exists.
2. Raster dimensions are preserved.
3. CRS is preserved.
4. Resolution is preserved.
5. Spatial transform is preserved.
6. Bounds are preserved.
7. Data type is preserved.
8. NoData value is preserved.
9. Population values are preserved.
10. Population statistics remain unchanged.

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Decision Agent
============================================================
"""

from pathlib import Path
import sys

import numpy as np
import rasterio


# ==========================================================
# Make project imports work
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from config import ANALYSIS_DATA_DIR


# ==========================================================
# Input and Output Rasters
# ==========================================================

source_population = (
    ANALYSIS_DATA_DIR
    / "population"
    / "population_32737.tif"
)

population_factor = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "population.tif"
)


# ==========================================================
# Header
# ==========================================================

print("=" * 70)
print(" GEOAI FLOOD RISK AGENT - POPULATION FACTOR VALIDATION ")
print("=" * 70)


# ==========================================================
# Check Files
# ==========================================================

print("\n------------- File Check -------------")

print(f"Source Population : {source_population}")
print(f"Population Factor : {population_factor}")


if not source_population.exists():
    raise FileNotFoundError(
        f"\n❌ Source population raster not found:\n"
        f"{source_population}"
    )

if not population_factor.exists():
    raise FileNotFoundError(
        f"\n❌ Population flood-factor raster not found:\n"
        f"{population_factor}"
    )


print("\n✅ Source population raster found.")
print("✅ Population flood-factor raster found.")


# ==========================================================
# Open Both Rasters
# ==========================================================

with rasterio.open(source_population) as source, \
     rasterio.open(population_factor) as factor:

    # ------------------------------------------------------
    # Raster Information
    # ------------------------------------------------------

    print("\n------------- Source Raster Information -------------")

    print(f"CRS          : {source.crs}")
    print(f"Width        : {source.width}")
    print(f"Height       : {source.height}")
    print(f"Resolution   : {source.res}")
    print(f"Data Type    : {source.dtypes[0]}")
    print(f"NoData Value : {source.nodata}")
    print(f"Bounds       : {source.bounds}")

    print("\n------------- Flood Factor Information -------------")

    print(f"CRS          : {factor.crs}")
    print(f"Width        : {factor.width}")
    print(f"Height       : {factor.height}")
    print(f"Resolution   : {factor.res}")
    print(f"Data Type    : {factor.dtypes[0]}")
    print(f"NoData Value : {factor.nodata}")
    print(f"Bounds       : {factor.bounds}")

    # ------------------------------------------------------
    # Read Data as Masked Arrays
    # ------------------------------------------------------

    source_data = source.read(1, masked=True)
    factor_data = factor.read(1, masked=True)

    source_valid = source_data.compressed()
    factor_valid = factor_data.compressed()

    # ------------------------------------------------------
    # Compare Raster Structure
    # ------------------------------------------------------

    print("\n------------- Structural Validation -------------")

    checks = {
        "CRS": source.crs == factor.crs,
        "Width": source.width == factor.width,
        "Height": source.height == factor.height,
        "Resolution": np.allclose(
            source.res,
            factor.res
        ),
        "Transform": source.transform == factor.transform,
        "Bounds": np.allclose(
            source.bounds,
            factor.bounds
        ),
        "Data Type": source.dtypes[0] == factor.dtypes[0],
        "NoData Value": source.nodata == factor.nodata,
    }

    for name, result in checks.items():
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}: {result}")

    if not all(checks.values()):
        raise ValueError(
            "\n❌ Structural validation failed. "
            "The source and flood-factor rasters do not "
            "have identical raster properties."
        )

    # ------------------------------------------------------
    # Compare Population Values
    # ------------------------------------------------------

    print("\n------------- Population Value Validation -------------")

    values_identical = np.array_equal(
        source_data.data,
        factor_data.data
    )

    masks_identical = np.array_equal(
        source_data.mask,
        factor_data.mask
    )

    print(
        f"{'✅' if values_identical else '❌'} "
        f"Population values preserved: {values_identical}"
    )

    print(
        f"{'✅' if masks_identical else '❌'} "
        f"NoData mask preserved: {masks_identical}"
    )

    if not values_identical or not masks_identical:
        raise ValueError(
            "\n❌ Population values or NoData mask changed "
            "during flood-factor preparation."
        )

    # ------------------------------------------------------
    # Source Statistics
    # ------------------------------------------------------

    print("\n------------- Source Population Statistics -------------")

    source_min = source_valid.min()
    source_max = source_valid.max()
    source_mean = source_valid.mean()
    source_median = np.median(source_valid)

    source_zero = np.count_nonzero(
        source_valid == 0
    )

    source_positive = np.count_nonzero(
        source_valid > 0
    )

    print(f"Valid Cells              : {source_valid.size}")
    print(f"Minimum Population       : {source_min:.6f}")
    print(f"Maximum Population       : {source_max:.6f}")
    print(f"Mean Population          : {source_mean:.6f}")
    print(f"Median Population        : {source_median:.6f}")
    print(f"Zero-Population Cells    : {source_zero}")
    print(f"Positive-Population Cells: {source_positive}")

    # ------------------------------------------------------
    # Flood Factor Statistics
    # ------------------------------------------------------

    print("\n------------- Flood Factor Statistics -------------")

    factor_min = factor_valid.min()
    factor_max = factor_valid.max()
    factor_mean = factor_valid.mean()
    factor_median = np.median(factor_valid)

    factor_zero = np.count_nonzero(
        factor_valid == 0
    )

    factor_positive = np.count_nonzero(
        factor_valid > 0
    )

    print(f"Valid Cells              : {factor_valid.size}")
    print(f"Minimum Population       : {factor_min:.6f}")
    print(f"Maximum Population       : {factor_max:.6f}")
    print(f"Mean Population          : {factor_mean:.6f}")
    print(f"Median Population        : {factor_median:.6f}")
    print(f"Zero-Population Cells    : {factor_zero}")
    print(f"Positive-Population Cells: {factor_positive}")

    # ------------------------------------------------------
    # Compare Statistics
    # ------------------------------------------------------

    print("\n------------- Statistical Validation -------------")

    statistics_match = (
        source_valid.size == factor_valid.size
        and np.isclose(source_min, factor_min)
        and np.isclose(source_max, factor_max)
        and np.isclose(source_mean, factor_mean)
        and np.isclose(source_median, factor_median)
        and source_zero == factor_zero
        and source_positive == factor_positive
    )

    print(
        f"{'✅' if statistics_match else '❌'} "
        f"Population statistics preserved: {statistics_match}"
    )

    if not statistics_match:
        raise ValueError(
            "\n❌ Statistical validation failed."
        )


# ==========================================================
# Final Result
# ==========================================================

print("\n" + "=" * 70)
print("✅ POPULATION EXPOSURE FLOOD FACTOR VALIDATION PASSED")
print("=" * 70)

print("\nConclusion:")
print(
    "The prepared population flood factor preserves the "
    "original raster structure, metadata, NoData mask, "
    "and population values."
)

print("\nThe raster is ready for QGIS inspection and documentation.")

print("=" * 70)