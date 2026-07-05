from pathlib import Path
import sys

import rasterio
from rasterio.warp import calculate_default_transform
from rasterio.warp import reproject
from rasterio.warp import Resampling

# ---------------------------------------------------
# Make config importable
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "src"))

from config import (
    ANALYSIS_POPULATION_DIR,
    PROJECTED_CRS
)

print("=" * 60)
print("REPROJECTING POPULATION")
print("=" * 60)

input_file = PROJECT_ROOT / "data" / "processed" / "population" / "Nairobi population.tif"

output_file = ANALYSIS_POPULATION_DIR / "population_32737.tif"

ANALYSIS_POPULATION_DIR.mkdir(parents=True, exist_ok=True)

with rasterio.open(input_file) as src:

    transform, width, height = calculate_default_transform(
        src.crs,
        PROJECTED_CRS,
        src.width,
        src.height,
        *src.bounds
    )

    metadata = src.meta.copy()

    metadata.update({

        "crs": PROJECTED_CRS,
        "transform": transform,
        "width": width,
        "height": height

    })

    with rasterio.open(output_file, "w", **metadata) as dst:

        for i in range(1, src.count + 1):

            reproject(

                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),

                src_transform=src.transform,
                src_crs=src.crs,

                dst_transform=transform,
                dst_crs=PROJECTED_CRS,

                resampling=Resampling.nearest

            )

print()
print("SUCCESS")
print(output_file)