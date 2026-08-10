"""
============================================================
GeoAI Flood Risk Agent
Validation - Land Cover Flood Factor
============================================================

Validates the prepared land-cover raster used as a flood
conditioning factor.

This validation checks:
- Raster existence
- CRS
- Resolution
- Dimensions
- Data type
- NoData value
- Unique land-cover classes
- Class cell counts

The original land-cover classes are preserved at this stage.
No flood susceptibility scores are assigned here.

Author: Dorothy Stephanie
"""

from pathlib import Path
import sys

import numpy as np
import rasterio


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import ANALYSIS_DATA_DIR


print("=" * 60)
print(" GEOAI FLOOD RISK AGENT - LAND COVER FACTOR VALIDATION ")
print("=" * 60)


# ------------------------------------------------------------
# Raster Path
# ------------------------------------------------------------

landcover_raster = (
    ANALYSIS_DATA_DIR
    / "flood_factors"
    / "landcover.tif"
)


print(f"\nChecking: {landcover_raster}")


# ------------------------------------------------------------
# Check Raster Exists
# ------------------------------------------------------------

if not landcover_raster.exists():
    raise FileNotFoundError(
        f"\nLand-cover flood factor not found:\n"
        f"{landcover_raster}"
    )


print("\n✅ Raster found.")


# ------------------------------------------------------------
# Read Raster
# ------------------------------------------------------------

with rasterio.open(landcover_raster) as src:

    band = src.read(1)

    print("\n------------- Raster Information -------------")

    print(f"CRS          : {src.crs}")
    print(f"Resolution   : {src.res}")
    print(f"Width        : {src.width}")
    print(f"Height       : {src.height}")
    print(f"Data Type    : {src.dtypes[0]}")
    print(f"NoData Value : {src.nodata}")


    # --------------------------------------------------------
    # Remove NoData Before Class Analysis
    # --------------------------------------------------------

    if src.nodata is not None:
        valid = band[band != src.nodata]
    else:
        valid = band.flatten()


    if valid.size == 0:
        raise ValueError(
            "No valid land-cover cells were found."
        )


    # --------------------------------------------------------
    # Unique Classes
    # --------------------------------------------------------

    unique_values, counts = np.unique(
        valid,
        return_counts=True
    )


    print("\n------------- Land Cover Classes -------------")

    for value, count in zip(unique_values, counts):

        print(
            f"Class {value}: "
            f"{count:,} cells"
        )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n------------- Summary -------------")

    print(
        f"Number of Classes : "
        f"{len(unique_values)}"
    )

    print(
        f"Valid Cells       : "
        f"{valid.size:,}"
    )


print(
    "\n✅ Land Cover flood factor validation "
    "completed successfully."
)

print("=" * 60)