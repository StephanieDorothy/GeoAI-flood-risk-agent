"""
============================================================
GeoAI Flood Risk Agent
Raster Preprocessing Module
============================================================

Purpose
-------
Reusable preprocessing functions for raster datasets.

Author: Dorothy Stephanie
Project: GeoAI Flood Risk Agent
"""

from pathlib import Path
import sys

import rasterio
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling,
)

# ------------------------------------------------------------
# Allow importing config.py
# ------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parent.parent
sys.path.append(str(SRC_DIR))

from config import ANALYSIS_DEM_DIR


def reproject_raster(
    input_raster,
    output_raster,
    target_crs="EPSG:32737"
):
    """
    Reprojects a raster into the desired CRS.

    Parameters
    ----------
    input_raster : str or Path
        Path to the source raster.

    output_raster : str or Path
        Path where the reprojected raster
        will be saved.

    target_crs : str
        CRS to project into.

    Returns
    -------
    None
    """

    input_raster = Path(input_raster)
    output_raster = Path(output_raster)

    print("=" * 60)
    print("REPROJECTING RASTER")
    print("=" * 60)

    print(f"\nInput:")
    print(input_raster)

    print(f"\nOutput:")
    print(output_raster)

    with rasterio.open(input_raster) as src:

        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds
        )

        kwargs = src.meta.copy()

        kwargs.update({
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height
        })

        output_raster.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with rasterio.open(output_raster, "w", **kwargs) as dst:

            for band in range(1, src.count + 1):

                reproject(
                    source=rasterio.band(src, band),
                    destination=rasterio.band(dst, band),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest
                )

    print("\n✅ Reprojection completed successfully.")