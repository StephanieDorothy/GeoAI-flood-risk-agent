"""
Phase 9.11.2 - UNOSAT External Reference Data Inspection

Purpose
-------
Inspect the downloaded UNOSAT Product 3834 GIS data before using it
for external validation of the GeoAI flood susceptibility model.

The script:
1. Discovers all Shapefiles in the UNOSAT directory.
2. Reports geometry type and feature count.
3. Reports CRS and spatial bounds.
4. Reports attribute fields and sample values.
5. Checks geometry validity.
6. Checks spatial overlap with the MCDA reference grid.
7. Produces a reproducible JSON inspection report.

Important
---------
The original UNOSAT source data are never modified.

This inspection is descriptive only. It does not repair geometries,
reproject the original files, or create the final validation raster.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from shapely.geometry import box


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

UNOSAT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "external_validation"
    / "_static_unosat_filesystem_3834_FL20240426KEN_SHP"
    / "FL20240426KEN_SHP"
)

MCDA_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility.tif"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "unosat_reference_data_inspection.json"
)


# ---------------------------------------------------------------------
# JSON SERIALIZATION
# ---------------------------------------------------------------------

def json_safe(value):
    """
    Convert common GIS/Pandas/NumPy/date values into JSON-safe values.
    """

    if value is None:
        return None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if np.isnan(value):
            return None
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except Exception:
            pass

    return value


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def bounds_to_dict(bounds):
    """Convert bounds into a readable dictionary."""

    return {
        "min_x": float(bounds[0]),
        "min_y": float(bounds[1]),
        "max_x": float(bounds[2]),
        "max_y": float(bounds[3]),
    }


def describe_geometry_types(gdf):
    """Return geometry type counts."""

    counts = gdf.geometry.geom_type.value_counts(
        dropna=False
    )

    return {
        str(geometry_type): int(count)
        for geometry_type, count in counts.items()
    }


def describe_columns(gdf):
    """
    Describe the attribute table.

    For each attribute field:
    - data type
    - non-null count
    - null count
    - unique value count
    - sample unique values
    """

    columns = {}

    for column in gdf.columns:

        if column == gdf.geometry.name:
            continue

        series = gdf[column]

        unique_values = series.dropna().unique()

        sample_values = [
            json_safe(value)
            for value in unique_values[:10]
        ]

        columns[column] = {
            "dtype": str(series.dtype),
            "non_null_count": int(series.notna().sum()),
            "null_count": int(series.isna().sum()),
            "unique_count": int(
                series.nunique(dropna=True)
            ),
            "sample_unique_values": sample_values,
        }

    return columns


def check_geometry_validity(gdf):
    """Check null, empty and invalid geometries."""

    null_geometry_count = int(
        gdf.geometry.isna().sum()
    )

    empty_geometry_count = int(
        gdf.geometry.is_empty.sum()
    )

    non_empty = (
        gdf.geometry.notna()
        & (~gdf.geometry.is_empty)
    )

    valid_geometry_count = 0
    invalid_geometry_count = 0

    if non_empty.any():

        valid_geometry_count = int(
            gdf.loc[
                non_empty,
                "geometry"
            ].is_valid.sum()
        )

        invalid_geometry_count = int(
            (
                ~gdf.loc[
                    non_empty,
                    "geometry"
                ].is_valid
            ).sum()
        )

    return {
        "null_geometry_count": null_geometry_count,
        "empty_geometry_count": empty_geometry_count,
        "valid_geometry_count": valid_geometry_count,
        "invalid_geometry_count": invalid_geometry_count,
        "geometry_validity_status": (
            "PASS"
            if invalid_geometry_count == 0
            else "CHECK_REQUIRED"
        ),
    }


def check_mcda_overlap(
    gdf,
    mcda_bounds,
    mcda_crs,
):
    """
    Check whether the dataset overlaps the MCDA reference footprint.

    The dataset is reprojected only in memory for the check.
    The source file is never modified.
    """

    result = {
        "mcda_crs": str(mcda_crs),
        "source_crs": (
            str(gdf.crs)
            if gdf.crs is not None
            else None
        ),
        "crs_match": False,
        "bbox_overlap": False,
        "features_intersecting_mcda_bbox": 0,
        "overlap_status": "NOT_TESTED",
    }

    try:

        if gdf.crs is None:

            result["overlap_status"] = (
                "CANNOT_TEST_MISSING_CRS"
            )

            return result

        result["crs_match"] = bool(
            gdf.crs == mcda_crs
        )

        if gdf.crs != mcda_crs:

            analysis_gdf = gdf.to_crs(mcda_crs)

        else:

            analysis_gdf = gdf.copy()

        if analysis_gdf.empty:

            result["overlap_status"] = (
                "EMPTY_DATASET"
            )

            return result

        reference_bounds = (
            analysis_gdf.total_bounds
        )

        result[
            "reference_bounds_in_mcda_crs"
        ] = bounds_to_dict(
            reference_bounds
        )

        reference_box = box(
            *reference_bounds
        )

        mcda_minx, mcda_miny, mcda_maxx, mcda_maxy = (
            mcda_bounds
        )

        mcda_box = box(
            mcda_minx,
            mcda_miny,
            mcda_maxx,
            mcda_maxy,
        )

        bbox_overlap = bool(
            reference_box.intersects(mcda_box)
        )

        result["bbox_overlap"] = bbox_overlap

        if not bbox_overlap:

            result["overlap_status"] = (
                "NO_BBOX_OVERLAP"
            )

            return result

        non_empty = (
            analysis_gdf.geometry.notna()
            & (~analysis_gdf.geometry.is_empty)
        )

        if non_empty.any():

            intersects = (
                analysis_gdf.loc[
                    non_empty,
                    "geometry"
                ]
                .intersects(mcda_box)
            )

            overlap_feature_count = int(
                intersects.sum()
            )

        else:

            overlap_feature_count = 0

        result[
            "features_intersecting_mcda_bbox"
        ] = overlap_feature_count

        result["overlap_status"] = (
            "OVERLAP_PRESENT"
            if overlap_feature_count > 0
            else "NO_FEATURE_OVERLAP"
        )

    except Exception as exc:

        result["overlap_status"] = (
            "OVERLAP_CHECK_FAILED"
        )

        result["overlap_error"] = str(exc)

    return result


def inspect_shapefile(
    shapefile_path,
    mcda_bounds,
    mcda_crs,
):
    """Inspect one Shapefile."""

    print()
    print("=" * 80)
    print(
        f"INSPECTING: {shapefile_path.name}"
    )
    print("=" * 80)

    result = {
        "file": str(shapefile_path),
        "file_name": shapefile_path.name,
    }

    # -----------------------------------------------------------------
    # READ
    # -----------------------------------------------------------------

    try:

        gdf = gpd.read_file(
            shapefile_path
        )

    except Exception as exc:

        result["read_status"] = "FAILED"
        result["read_error"] = str(exc)

        print("READ STATUS: FAILED")
        print(f"ERROR: {exc}")

        return result

    result["read_status"] = "PASS"

    # -----------------------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------------------

    feature_count = len(gdf)

    geometry_types = (
        describe_geometry_types(gdf)
    )

    result["feature_count"] = int(
        feature_count
    )

    result["geometry_types"] = (
        geometry_types
    )

    result["column_count"] = int(
        len(gdf.columns)
    )

    print(
        f"Feature count: {feature_count}"
    )

    print(
        f"Geometry types: {geometry_types}"
    )

    # -----------------------------------------------------------------
    # CRS
    # -----------------------------------------------------------------

    result["crs"] = (
        str(gdf.crs)
        if gdf.crs is not None
        else None
    )

    print(
        f"CRS: {result['crs']}"
    )

    if gdf.crs is not None:

        try:
            result["epsg"] = (
                gdf.crs.to_epsg()
            )

        except Exception:

            result["epsg"] = None

    else:

        result["epsg"] = None

    # -----------------------------------------------------------------
    # BOUNDS
    # -----------------------------------------------------------------

    if not gdf.empty:

        bounds = gdf.total_bounds

        result["bounds"] = (
            bounds_to_dict(bounds)
        )

        print(
            "Bounds: "
            f"{bounds[0]:.3f}, "
            f"{bounds[1]:.3f}, "
            f"{bounds[2]:.3f}, "
            f"{bounds[3]:.3f}"
        )

    else:

        result["bounds"] = None

        print(
            "Bounds: dataset is empty"
        )

    # -----------------------------------------------------------------
    # ATTRIBUTES
    # -----------------------------------------------------------------

    columns = describe_columns(gdf)

    result["attributes"] = columns

    print()
    print("Attribute fields:")

    for column, information in columns.items():

        print(
            f"  {column} | "
            f"dtype={information['dtype']} | "
            f"unique={information['unique_count']} | "
            f"sample={information['sample_unique_values']}"
        )

    # -----------------------------------------------------------------
    # GEOMETRY VALIDITY
    # -----------------------------------------------------------------

    validity = check_geometry_validity(
        gdf
    )

    result["geometry_validity"] = (
        validity
    )

    print()
    print("Geometry validity:")

    print(
        f"  Null geometries: "
        f"{validity['null_geometry_count']}"
    )

    print(
        f"  Empty geometries: "
        f"{validity['empty_geometry_count']}"
    )

    print(
        f"  Invalid geometries: "
        f"{validity['invalid_geometry_count']}"
    )

    print(
        f"  Status: "
        f"{validity['geometry_validity_status']}"
    )

    # -----------------------------------------------------------------
    # MCDA OVERLAP
    # -----------------------------------------------------------------

    overlap = check_mcda_overlap(
        gdf,
        mcda_bounds,
        mcda_crs,
    )

    result["mcda_overlap"] = overlap

    print()
    print(
        "MCDA spatial compatibility:"
    )

    print(
        f"  CRS match: "
        f"{overlap['crs_match']}"
    )

    print(
        f"  BBox overlap: "
        f"{overlap['bbox_overlap']}"
    )

    print(
        f"  Features intersecting "
        f"MCDA bbox: "
        f"{overlap['features_intersecting_mcda_bbox']}"
    )

    print(
        f"  Status: "
        f"{overlap['overlap_status']}"
    )

    # -----------------------------------------------------------------
    # SAMPLE RECORDS
    # -----------------------------------------------------------------

    sample_records = []

    if not gdf.empty:

        for _, row in gdf.head(5).iterrows():

            record = {}

            for column in gdf.columns:

                if column == gdf.geometry.name:
                    continue

                record[column] = (
                    json_safe(row[column])
                )

            sample_records.append(
                record
            )

    result["sample_records"] = (
        sample_records
    )

    return result


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    print("=" * 80)
    print(
        "PHASE 9.11.2 - "
        "UNOSAT REFERENCE DATA INSPECTION"
    )
    print("=" * 80)

    print()
    print("Project root:")
    print(f"  {PROJECT_ROOT}")

    print()
    print("UNOSAT directory:")
    print(f"  {UNOSAT_DIR}")

    print()
    print("MCDA reference raster:")
    print(f"  {MCDA_RASTER}")

    # -----------------------------------------------------------------
    # INPUT VALIDATION
    # -----------------------------------------------------------------

    if not UNOSAT_DIR.exists():

        raise FileNotFoundError(
            "UNOSAT directory does not exist:\n"
            f"{UNOSAT_DIR}"
        )

    if not UNOSAT_DIR.is_dir():

        raise NotADirectoryError(
            "Expected a directory but found:\n"
            f"{UNOSAT_DIR}"
        )

    if not MCDA_RASTER.exists():

        raise FileNotFoundError(
            "MCDA raster does not exist:\n"
            f"{MCDA_RASTER}"
        )

    # -----------------------------------------------------------------
    # DISCOVER SHAPEFILES
    # -----------------------------------------------------------------

    shapefiles = sorted(
        UNOSAT_DIR.rglob("*.shp")
    )

    print()
    print(
        f"Shapefiles discovered: "
        f"{len(shapefiles)}"
    )

    for shapefile in shapefiles:

        print(
            f"  - {shapefile}"
        )

    if not shapefiles:

        raise FileNotFoundError(
            "No .shp files were found."
        )

    # -----------------------------------------------------------------
    # READ MCDA GRID
    # -----------------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "READING MCDA REFERENCE GRID"
    )
    print("=" * 80)

    with rasterio.open(
        MCDA_RASTER
    ) as src:

        mcda_crs = src.crs

        mcda_bounds = (
            src.bounds.left,
            src.bounds.bottom,
            src.bounds.right,
            src.bounds.top,
        )

        print(
            f"CRS: {mcda_crs}"
        )

        print(
            f"Width: {src.width}"
        )

        print(
            f"Height: {src.height}"
        )

        print(
            f"Resolution: {src.res}"
        )

        print(
            f"Bounds: {src.bounds}"
        )

    # -----------------------------------------------------------------
    # INSPECT DATASETS
    # -----------------------------------------------------------------

    inspection_results = []

    for shapefile in shapefiles:

        result = inspect_shapefile(
            shapefile,
            mcda_bounds,
            mcda_crs,
        )

        inspection_results.append(
            result
        )

    # -----------------------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------------------

    successful_reads = [
        result
        for result in inspection_results
        if result.get("read_status")
        == "PASS"
    ]

    failed_reads = [
        result
        for result in inspection_results
        if result.get("read_status")
        != "PASS"
    ]

    summary = {
        "phase": "9.11.2",
        "analysis": (
            "UNOSAT reference data inspection"
        ),
        "unosat_directory": str(
            UNOSAT_DIR
        ),
        "mcda_reference_raster": str(
            MCDA_RASTER
        ),
        "shapefile_count": len(
            shapefiles
        ),
        "successful_reads": len(
            successful_reads
        ),
        "failed_reads": len(
            failed_reads
        ),
        "mcda_reference_grid": {
            "crs": str(mcda_crs),
            "bounds": bounds_to_dict(
                mcda_bounds
            ),
        },
        "datasets": inspection_results,
    }

    # -----------------------------------------------------------------
    # WRITE REPORT
    # -----------------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            summary,
            f,
            indent=2,
            ensure_ascii=False,
            default=json_safe,
        )

    # -----------------------------------------------------------------
    # FINAL OUTPUT
    # -----------------------------------------------------------------

    print()
    print("=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)

    print()
    print(
        f"Shapefiles discovered: "
        f"{len(shapefiles)}"
    )

    print(
        f"Successfully read: "
        f"{len(successful_reads)}"
    )

    print(
        f"Failed reads: "
        f"{len(failed_reads)}"
    )

    print()
    print("Inspection report:")
    print(
        f"  {OUTPUT_JSON}"
    )

    print()
    print(
        "Primary flood reference candidate:"
    )

    print(
        "  PL_20240501_FloodExtent_Nairobi_Kiambu.shp"
    )

    print()
    print(
        "PHASE_9_11_2_GIS_INSPECTION_COMPLETED"
    )


if __name__ == "__main__":
    main()