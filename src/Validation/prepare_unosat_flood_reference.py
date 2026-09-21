"""
Phase 9.11.3 - Prepare UNOSAT Flood Reference Data

Purpose
-------
Prepare an independent UNOSAT satellite-derived flood observation layer
for external validation of the GeoAI flood susceptibility model.

The validation reference is constructed using:

    UNOSAT Analysis Extent
        MINUS
    Cloud Obstruction
        INTERSECT
    MCDA Footprint

Reference raster values:

    1     = Observed flood
    0     = Observed non-flood
    -9999 = Unobserved / outside valid observation domain

Important scientific principle
------------------------------
Cloud-obstructed areas are NOT treated as observed non-flood.

Only areas within the valid UNOSAT observation domain are assigned
observed flood/non-flood values.

The original UNOSAT source files are never modified.

Outputs
-------
results/phase9_validation/external_validation/
    unosat_flood_reference_aligned.tif
    unosat_reference_preparation.json

Author
------
GeoAI Flood Risk Decision Agent
Phase 9 External Validation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import array_bounds
from shapely.geometry import box
from shapely.ops import unary_union
from shapely.validation import make_valid


# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

UNOSAT_ROOT = (
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

REFERENCE_RASTER = OUTPUT_DIR / "unosat_flood_reference_aligned.tif"
REPORT_JSON = OUTPUT_DIR / "unosat_reference_preparation.json"


# ---------------------------------------------------------------------
# UNOSAT source layers
# ---------------------------------------------------------------------

FLOOD_LAYER_NAME = "PL_20240501_FloodExtent_Nairobi_Kiambu.shp"

ANALYSIS_EXTENT_LAYER_NAME = (
    "PL_20240501_AnalysisExtent_Nairobi_Kiambu.shp"
)

CLOUD_LAYER_NAME = (
    "PL_20240501_CloudObstruction_Nairobi_Kiambu.shp"
)


# ---------------------------------------------------------------------
# Model/reference settings
# ---------------------------------------------------------------------

TARGET_CRS = "EPSG:32737"

REFERENCE_NODATA = -9999

FLOOD_VALUE = 1

NON_FLOOD_VALUE = 0

RASTERIZATION_ALL_TOUCHED = False


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------


def json_safe(value: Any) -> Any:
    """
    Convert NumPy/Shapely-related values into JSON-safe Python values.
    """
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, Path):
        return str(value)

    if value is None:
        return None

    if isinstance(value, float) and not np.isfinite(value):
        return None

    return value


def find_required_layer(filename: str) -> Path:
    """
    Locate a required UNOSAT Shapefile.
    """
    matches = list(UNOSAT_ROOT.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Required UNOSAT layer was not found:\n"
            f"  {filename}\n"
            f"Search root:\n"
            f"  {UNOSAT_ROOT}"
        )

    if len(matches) > 1:
        print(
            f"WARNING: Multiple matches found for {filename}. "
            f"Using the first match:"
        )

        for match in matches:
            print(f"  {match}")

    return matches[0]


def repair_geometries(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """
    Repair invalid geometries in memory using make_valid().

    The source file is never modified.
    """
    gdf = gdf.copy()

    initial_invalid = int((~gdf.geometry.is_valid).sum())
    initial_null = int(gdf.geometry.isna().sum())
    initial_empty = int(gdf.geometry.is_empty.sum())

    gdf = gdf.loc[gdf.geometry.notna()].copy()
    gdf = gdf.loc[~gdf.geometry.is_empty].copy()

    if len(gdf) > 0:
        gdf["geometry"] = gdf.geometry.apply(
            lambda geom: make_valid(geom) if not geom.is_valid else geom
        )

    final_invalid = int((~gdf.geometry.is_valid).sum())
    final_null = int(gdf.geometry.isna().sum())
    final_empty = int(gdf.geometry.is_empty.sum())

    diagnostics = {
        "initial_feature_count": initial_invalid + len(gdf),
        "initial_invalid_geometries": initial_invalid,
        "initial_null_geometries": initial_null,
        "initial_empty_geometries": initial_empty,
        "final_feature_count": len(gdf),
        "final_invalid_geometries": final_invalid,
        "final_null_geometries": final_null,
        "final_empty_geometries": final_empty,
        "geometry_repair_pass": (
            final_invalid == 0
            and final_null == 0
            and final_empty == 0
        ),
    }

    return gdf, diagnostics


def project_geometries(
    gdf: gpd.GeoDataFrame,
    target_crs: str,
) -> gpd.GeoDataFrame:
    """
    Reproject a GeoDataFrame to the target CRS.
    """
    if gdf.crs is None:
        raise ValueError("Input layer has no CRS.")

    return gdf.to_crs(target_crs)


def union_geometry(gdf: gpd.GeoDataFrame):
    """
    Create a unary union from valid geometries.
    """
    geometries = [
        geom
        for geom in gdf.geometry
        if geom is not None
        and not geom.is_empty
        and geom.is_valid
    ]

    if not geometries:
        raise ValueError("No valid geometries available for union.")

    result = unary_union(geometries)

    if result.is_empty:
        raise ValueError("Union geometry is empty.")

    if not result.is_valid:
        result = make_valid(result)

    if result.is_empty:
        raise ValueError("Repaired union geometry is empty.")

    return result


def area_km2(geometry) -> float:
    """
    Calculate projected geometry area in square kilometres.
    """
    if geometry is None or geometry.is_empty:
        return 0.0

    return float(geometry.area / 1_000_000.0)


def geometry_bounds_overlap(
    geometry,
    raster_bounds,
) -> bool:
    """
    Quickly determine whether geometry bounds overlap raster bounds.
    """
    geometry_box = box(*geometry.bounds)

    raster_box = box(
        raster_bounds.left,
        raster_bounds.bottom,
        raster_bounds.right,
        raster_bounds.top,
    )

    return geometry_box.intersects(raster_box)


# ---------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------


def main() -> None:

    print("=" * 72)
    print("PHASE 9.11.3 - UNOSAT FLOOD REFERENCE PREPARATION")
    print("=" * 72)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # 1. Locate source layers
    # ---------------------------------------------------------------

    print("\n[1/10] Locating UNOSAT source layers...")

    flood_path = find_required_layer(FLOOD_LAYER_NAME)

    analysis_extent_path = find_required_layer(
        ANALYSIS_EXTENT_LAYER_NAME
    )

    cloud_path = find_required_layer(
        CLOUD_LAYER_NAME
    )

    print(f"  Flood extent:")
    print(f"    {flood_path}")

    print(f"  Analysis extent:")
    print(f"    {analysis_extent_path}")

    print(f"  Cloud obstruction:")
    print(f"    {cloud_path}")

    if not MCDA_RASTER.exists():
        raise FileNotFoundError(
            f"MCDA raster not found:\n{MCDA_RASTER}"
        )

    print(f"  MCDA raster:")
    print(f"    {MCDA_RASTER}")

    # ---------------------------------------------------------------
    # 2. Read MCDA reference grid
    # ---------------------------------------------------------------

    print("\n[2/10] Reading MCDA reference grid...")

    with rasterio.open(MCDA_RASTER) as mcda:

        mcda_crs = mcda.crs
        mcda_width = mcda.width
        mcda_height = mcda.height
        mcda_transform = mcda.transform
        mcda_resolution = mcda.res
        mcda_bounds = mcda.bounds

        mcda_data = mcda.read(1)
        mcda_nodata = mcda.nodata

    if mcda_crs is None:
        raise ValueError("MCDA raster has no CRS.")

    if str(mcda_crs) != TARGET_CRS:
        raise ValueError(
            f"MCDA CRS mismatch.\n"
            f"Expected: {TARGET_CRS}\n"
            f"Found: {mcda_crs}"
        )

    mcda_valid = np.isfinite(mcda_data)

    if mcda_nodata is not None:
        mcda_valid &= mcda_data != mcda_nodata

    print(f"  CRS: {mcda_crs}")
    print(f"  Dimensions: {mcda_width} x {mcda_height}")
    print(
        f"  Resolution: "
        f"{mcda_resolution[0]:.9f} x "
        f"{mcda_resolution[1]:.9f} m"
    )
    print(f"  NoData: {mcda_nodata}")
    print(f"  Valid MCDA cells: {int(mcda_valid.sum()):,}")

    # ---------------------------------------------------------------
    # 3. Read UNOSAT layers
    # ---------------------------------------------------------------

    print("\n[3/10] Reading UNOSAT layers...")

    flood_gdf = gpd.read_file(flood_path)
    analysis_gdf = gpd.read_file(analysis_extent_path)
    cloud_gdf = gpd.read_file(cloud_path)

    print(
        f"  Flood features: "
        f"{len(flood_gdf):,}"
    )

    print(
        f"  Analysis extent features: "
        f"{len(analysis_gdf):,}"
    )

    print(
        f"  Cloud obstruction features: "
        f"{len(cloud_gdf):,}"
    )

    print(
        f"  Flood CRS: "
        f"{flood_gdf.crs}"
    )

    print(
        f"  Analysis extent CRS: "
        f"{analysis_gdf.crs}"
    )

    print(
        f"  Cloud CRS: "
        f"{cloud_gdf.crs}"
    )

    # ---------------------------------------------------------------
    # 4. Repair geometries in memory
    # ---------------------------------------------------------------

    print("\n[4/10] Validating and repairing geometries...")

    flood_gdf, flood_geometry_report = repair_geometries(
        flood_gdf
    )

    analysis_gdf, analysis_geometry_report = repair_geometries(
        analysis_gdf
    )

    cloud_gdf, cloud_geometry_report = repair_geometries(
        cloud_gdf
    )

    print(
        f"  Flood invalid before repair: "
        f"{flood_geometry_report['initial_invalid_geometries']}"
    )

    print(
        f"  Flood invalid after repair: "
        f"{flood_geometry_report['final_invalid_geometries']}"
    )

    print(
        f"  Analysis extent invalid after repair: "
        f"{analysis_geometry_report['final_invalid_geometries']}"
    )

    print(
        f"  Cloud invalid after repair: "
        f"{cloud_geometry_report['final_invalid_geometries']}"
    )

    if not (
        flood_geometry_report["geometry_repair_pass"]
        and analysis_geometry_report["geometry_repair_pass"]
        and cloud_geometry_report["geometry_repair_pass"]
    ):
        raise RuntimeError(
            "Geometry preparation failed."
        )

    print("  Geometry preparation: PASS")

    # ---------------------------------------------------------------
    # 5. Reproject to MCDA CRS
    # ---------------------------------------------------------------

    print("\n[5/10] Reprojecting UNOSAT layers to EPSG:32737...")

    flood_projected = project_geometries(
        flood_gdf,
        TARGET_CRS,
    )

    analysis_projected = project_geometries(
        analysis_gdf,
        TARGET_CRS,
    )

    cloud_projected = project_geometries(
        cloud_gdf,
        TARGET_CRS,
    )

    print(
        f"  Flood CRS after reprojection: "
        f"{flood_projected.crs}"
    )

    print(
        f"  Analysis extent CRS after reprojection: "
        f"{analysis_projected.crs}"
    )

    print(
        f"  Cloud CRS after reprojection: "
        f"{cloud_projected.crs}"
    )

    if (
        str(flood_projected.crs) != TARGET_CRS
        or str(analysis_projected.crs) != TARGET_CRS
        or str(cloud_projected.crs) != TARGET_CRS
    ):
        raise RuntimeError(
            "One or more UNOSAT layers failed CRS transformation."
        )

    print("  CRS transformation: PASS")

    # ---------------------------------------------------------------
    # 6. Build valid observation domain
    # ---------------------------------------------------------------

    print("\n[6/10] Building valid observation domain...")

    analysis_union = union_geometry(
        analysis_projected
    )

    cloud_union = union_geometry(
        cloud_projected
    )

    flood_union = union_geometry(
        flood_projected
    )

    valid_observation_domain = analysis_union.difference(
        cloud_union
    )

    if not valid_observation_domain.is_valid:
        valid_observation_domain = make_valid(
            valid_observation_domain
        )

    if valid_observation_domain.is_empty:
        raise RuntimeError(
            "Valid observation domain is empty."
        )

    mcda_polygon = box(
        mcda_bounds.left,
        mcda_bounds.bottom,
        mcda_bounds.right,
        mcda_bounds.top,
    )

    valid_observation_mcda = (
        valid_observation_domain.intersection(
            mcda_polygon
        )
    )

    if not valid_observation_mcda.is_valid:
        valid_observation_mcda = make_valid(
            valid_observation_mcda
        )

    if valid_observation_mcda.is_empty:
        raise RuntimeError(
            "Valid observation domain has no overlap "
            "with the MCDA footprint."
        )

    # Flood observations are restricted to the valid observation domain.
    observed_flood_geometry = flood_union.intersection(
        valid_observation_mcda
    )

    if not observed_flood_geometry.is_valid:
        observed_flood_geometry = make_valid(
            observed_flood_geometry
        )

    # ---------------------------------------------------------------
    # 7. Spatial diagnostics
    # ---------------------------------------------------------------

    print("\n[7/10] Calculating spatial diagnostics...")

    analysis_area_km2 = area_km2(
        analysis_union
    )

    cloud_area_km2 = area_km2(
        cloud_union
    )

    valid_observation_area_km2 = area_km2(
        valid_observation_domain
    )

    valid_observation_mcda_area_km2 = area_km2(
        valid_observation_mcda
    )

    flood_total_area_km2 = area_km2(
        flood_union
    )

    flood_valid_area_km2 = area_km2(
        observed_flood_geometry
    )

    flood_mcda_area_km2 = area_km2(
        flood_union.intersection(mcda_polygon)
    )

    flood_cloud_intersection_km2 = area_km2(
        flood_union.intersection(cloud_union)
    )

    flood_analysis_intersection_km2 = area_km2(
        flood_union.intersection(analysis_union)
    )

    print(
        f"  Analysis extent area: "
        f"{analysis_area_km2:.6f} km²"
    )

    print(
        f"  Cloud obstruction area: "
        f"{cloud_area_km2:.6f} km²"
    )

    print(
        f"  Valid observation domain: "
        f"{valid_observation_area_km2:.6f} km²"
    )

    print(
        f"  Valid observation domain within MCDA: "
        f"{valid_observation_mcda_area_km2:.6f} km²"
    )

    print(
        f"  Flood extent total: "
        f"{flood_total_area_km2:.6f} km²"
    )

    print(
        f"  Flood within analysis extent: "
        f"{flood_analysis_intersection_km2:.6f} km²"
    )

    print(
        f"  Flood within MCDA footprint: "
        f"{flood_mcda_area_km2:.6f} km²"
    )

    print(
        f"  Flood overlapping cloud obstruction: "
        f"{flood_cloud_intersection_km2:.6f} km²"
    )

    print(
        f"  Flood within valid observation domain: "
        f"{flood_valid_area_km2:.6f} km²"
    )

    # ---------------------------------------------------------------
    # 8. Rasterize onto exact MCDA grid
    # ---------------------------------------------------------------

    print("\n[8/10] Rasterizing reference data to MCDA grid...")

    valid_domain_mask = rasterize(
        [(valid_observation_mcda, 1)],
        out_shape=(mcda_height, mcda_width),
        transform=mcda_transform,
        fill=0,
        dtype="uint8",
        all_touched=RASTERIZATION_ALL_TOUCHED,
    )

    flood_mask = rasterize(
        [(observed_flood_geometry, 1)],
        out_shape=(mcda_height, mcda_width),
        transform=mcda_transform,
        fill=0,
        dtype="uint8",
        all_touched=RASTERIZATION_ALL_TOUCHED,
    )

    # Ensure flood cells can only occur within the valid observation
    # domain.
    flood_mask = flood_mask & valid_domain_mask

    reference_array = np.full(
        (mcda_height, mcda_width),
        REFERENCE_NODATA,
        dtype=np.int16,
    )

    reference_array[
        valid_domain_mask == 1
    ] = NON_FLOOD_VALUE

    reference_array[
        flood_mask == 1
    ] = FLOOD_VALUE

    # Never allow cells outside the MCDA valid-data footprint to become
    # reference observations.
    reference_array[
        ~mcda_valid
    ] = REFERENCE_NODATA

    observed_mask = (
        reference_array != REFERENCE_NODATA
    )

    observed_flood_mask = (
        reference_array == FLOOD_VALUE
    )

    observed_non_flood_mask = (
        reference_array == NON_FLOOD_VALUE
    )

    unobserved_mask = (
        reference_array == REFERENCE_NODATA
    )

    flood_cell_count = int(
        observed_flood_mask.sum()
    )

    non_flood_cell_count = int(
        observed_non_flood_mask.sum()
    )

    unobserved_cell_count = int(
        unobserved_mask.sum()
    )

    observed_cell_count = int(
        observed_mask.sum()
    )

    pixel_area_m2 = (
        abs(mcda_transform.a)
        * abs(mcda_transform.e)
    )

    rasterized_flood_area_km2 = (
        flood_cell_count
        * pixel_area_m2
        / 1_000_000.0
    )

    rasterized_observed_area_km2 = (
        observed_cell_count
        * pixel_area_m2
        / 1_000_000.0
    )

    rasterized_unobserved_area_km2 = (
        unobserved_cell_count
        * pixel_area_m2
        / 1_000_000.0
    )

    print(
        f"  Observed flood cells: "
        f"{flood_cell_count:,}"
    )

    print(
        f"  Observed non-flood cells: "
        f"{non_flood_cell_count:,}"
    )

    print(
        f"  Unobserved cells: "
        f"{unobserved_cell_count:,}"
    )

    print(
        f"  Rasterized observed area: "
        f"{rasterized_observed_area_km2:.6f} km²"
    )

    print(
        f"  Rasterized flood area: "
        f"{rasterized_flood_area_km2:.6f} km²"
    )

    print(
        f"  Rasterized unobserved area: "
        f"{rasterized_unobserved_area_km2:.6f} km²"
    )

    # ---------------------------------------------------------------
    # 9. Validate raster geometry and reference logic
    # ---------------------------------------------------------------

    print("\n[9/10] Validating prepared reference raster...")

    unique_values = np.unique(reference_array)

    print(
        f"  Reference values present: "
        f"{unique_values.tolist()}"
    )

    allowed_values = {
        REFERENCE_NODATA,
        NON_FLOOD_VALUE,
        FLOOD_VALUE,
    }

    if not set(unique_values.tolist()).issubset(
        allowed_values
    ):
        raise RuntimeError(
            "Reference raster contains unexpected values."
        )

    if flood_cell_count == 0:
        raise RuntimeError(
            "No observed flood cells were produced."
        )

    if non_flood_cell_count == 0:
        raise RuntimeError(
            "No observed non-flood cells were produced."
        )

    if observed_cell_count == 0:
        raise RuntimeError(
            "No observed cells were produced."
        )

    if not geometry_bounds_overlap(
        valid_observation_mcda,
        mcda_bounds,
    ):
        raise RuntimeError(
            "Valid observation domain does not overlap "
            "the MCDA raster bounds."
        )

    print("  Allowed reference values: PASS")
    print("  Observed flood cells: PASS")
    print("  Observed non-flood cells: PASS")
    print("  Observed domain: PASS")
    print("  MCDA spatial overlap: PASS")

    # ---------------------------------------------------------------
    # 10. Write raster and report
    # ---------------------------------------------------------------

    print("\n[10/10] Writing aligned reference raster and report...")

    with rasterio.open(
        MCDA_RASTER
    ) as mcda:

        profile = mcda.profile.copy()

    profile.update(
        driver="GTiff",
        dtype="int16",
        count=1,
        nodata=REFERENCE_NODATA,
        compress="deflate",
        predictor=2,
    )

    with rasterio.open(
        REFERENCE_RASTER,
        "w",
        **profile,
    ) as dst:

        dst.write(
            reference_array,
            1,
        )

        dst.set_band_description(
            1,
            "UNOSAT observed flood reference",
        )

        dst.update_tags(
            phase="9.11.3",
            reference_source="UNOSAT Product 3834",
            event_code="FL20240426KEN",
            sensor="Pleiades",
            acquisition_date="2024-05-01",
            flood_value="1",
            non_flood_value="0",
            nodata_value="-9999",
            observation_domain=(
                "AnalysisExtent_Nairobi_Kiambu "
                "minus CloudObstruction_Nairobi_Kiambu "
                "intersect MCDA footprint"
            ),
            cloud_obstruction_treatment=(
                "Excluded from observed domain; "
                "not classified as non-flood"
            ),
            rasterization_method=(
                "center-based rasterization; all_touched=False"
            ),
            validation_role=(
                "Independent satellite-derived flood observation "
                "for external validation"
            ),
        )

    # Final raster validation by reopening output.
    with rasterio.open(
        REFERENCE_RASTER
    ) as reference:

        output_crs = reference.crs
        output_width = reference.width
        output_height = reference.height
        output_transform = reference.transform
        output_resolution = reference.res
        output_nodata = reference.nodata
        output_array = reference.read(1)

    geometry_match = (
        output_width == mcda_width
        and output_height == mcda_height
        and np.allclose(
            output_transform,
            mcda_transform,
        )
    )

    resolution_match = (
        np.allclose(
            output_resolution,
            mcda_resolution,
        )
    )

    crs_match = (
        str(output_crs) == TARGET_CRS
    )

    nodata_match = (
        output_nodata == REFERENCE_NODATA
    )

    values_match = np.array_equal(
        output_array,
        reference_array,
    )

    print(
        f"  CRS match: "
        f"{'PASS' if crs_match else 'FAIL'}"
    )

    print(
        f"  Dimensions match: "
        f"{'PASS' if geometry_match else 'FAIL'}"
    )

    print(
        f"  Resolution match: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )

    print(
        f"  NoData match: "
        f"{'PASS' if nodata_match else 'FAIL'}"
    )

    print(
        f"  Written values match source array: "
        f"{'PASS' if values_match else 'FAIL'}"
    )

    if not all(
        [
            crs_match,
            geometry_match,
            resolution_match,
            nodata_match,
            values_match,
        ]
    ):
        raise RuntimeError(
            "Final reference raster validation failed."
        )

    # ---------------------------------------------------------------
    # Build provenance/validation report
    # ---------------------------------------------------------------

    report = {
        "phase": "9.11.3",
        "status": "COMPLETED",
        "purpose": (
            "Preparation of independent UNOSAT satellite-derived "
            "flood observations for external validation."
        ),
        "source": {
            "product": "UNOSAT Product 3834",
            "event_code": "FL20240426KEN",
            "sensor": "Pleiades",
            "acquisition_date": "2024-05-01",
            "flood_layer": str(flood_path),
            "analysis_extent_layer": str(
                analysis_extent_path
            ),
            "cloud_obstruction_layer": str(
                cloud_path
            ),
        },
        "reference_definition": {
            "flood_value": FLOOD_VALUE,
            "non_flood_value": NON_FLOOD_VALUE,
            "nodata_value": REFERENCE_NODATA,
            "valid_observation_domain": (
                "Analysis Extent minus Cloud Obstruction"
            ),
            "validation_domain": (
                "Valid observation domain intersect MCDA footprint"
            ),
            "cloud_obstruction_treatment": (
                "Cloud-obstructed areas are unobserved and "
                "are not assigned non-flood values."
            ),
            "rasterization_all_touched": RASTERIZATION_ALL_TOUCHED,
        },
        "mcda_reference_grid": {
            "crs": str(mcda_crs),
            "width": mcda_width,
            "height": mcda_height,
            "resolution_x_m": float(mcda_resolution[0]),
            "resolution_y_m": float(mcda_resolution[1]),
            "pixel_area_m2": float(pixel_area_m2),
            "valid_cells": int(mcda_valid.sum()),
        },
        "geometry_diagnostics": {
            "flood": flood_geometry_report,
            "analysis_extent": analysis_geometry_report,
            "cloud_obstruction": cloud_geometry_report,
        },
        "spatial_diagnostics": {
            "analysis_extent_area_km2": analysis_area_km2,
            "cloud_obstruction_area_km2": cloud_area_km2,
            "valid_observation_domain_area_km2": (
                valid_observation_area_km2
            ),
            "valid_observation_domain_mcda_area_km2": (
                valid_observation_mcda_area_km2
            ),
            "flood_total_area_km2": flood_total_area_km2,
            "flood_inside_analysis_extent_km2": (
                flood_analysis_intersection_km2
            ),
            "flood_inside_mcda_footprint_km2": (
                flood_mcda_area_km2
            ),
            "flood_overlapping_cloud_km2": (
                flood_cloud_intersection_km2
            ),
            "flood_inside_valid_observation_domain_km2": (
                flood_valid_area_km2
            ),
        },
        "raster_reference_statistics": {
            "flood_cells": flood_cell_count,
            "non_flood_cells": non_flood_cell_count,
            "observed_cells": observed_cell_count,
            "unobserved_cells": unobserved_cell_count,
            "rasterized_flood_area_km2": (
                rasterized_flood_area_km2
            ),
            "rasterized_observed_area_km2": (
                rasterized_observed_area_km2
            ),
            "rasterized_unobserved_area_km2": (
                rasterized_unobserved_area_km2
            ),
            "unique_values": [
                int(value)
                for value in unique_values
            ],
        },
        "output_validation": {
            "output_raster": str(REFERENCE_RASTER),
            "crs_match": crs_match,
            "dimensions_match": geometry_match,
            "resolution_match": resolution_match,
            "nodata_match": nodata_match,
            "values_match": values_match,
            "validation_pass": all(
                [
                    crs_match,
                    geometry_match,
                    resolution_match,
                    nodata_match,
                    values_match,
                ]
            ),
        },
        "scientific_notes": [
            (
                "The UNOSAT flood polygon was restricted to the "
                "valid observation domain before rasterization."
            ),
            (
                "Cloud-obstructed areas were excluded from the "
                "reference domain rather than being classified "
                "as observed non-flood."
            ),
            (
                "The reference raster is aligned exactly to the "
                "MCDA grid to enable cell-by-cell external validation."
            ),
            (
                "The reference represents observed flood extent "
                "for the 1 May 2024 satellite acquisition and "
                "does not represent flood probability."
            ),
            (
                "Preparation of the reference raster does not by "
                "itself establish predictive validity; spatial and "
                "statistical validation are performed in subsequent "
                "Phase 9.11 steps."
            ),
        ],
    }

    with open(
        REPORT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            json_safe(report),
            f,
            indent=2,
        )

    print(
        f"\nReference raster written to:\n"
        f"  {REFERENCE_RASTER}"
    )

    print(
        f"\nPreparation report written to:\n"
        f"  {REPORT_JSON}"
    )

    print("\n" + "=" * 72)
    print("PHASE_9_11_3_REFERENCE_PREPARATION_COMPLETED")
    print("=" * 72)


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()