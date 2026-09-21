"""
Phase 9.11.3 Diagnostic - UNOSAT Reference Rasterization

Purpose
-------
Diagnose the difference between:

1. Vector UNOSAT flood/observation-domain areas
2. Rasterized UNOSAT reference areas

The diagnostic determines whether the apparent area difference is caused by
the MCDA raster's internal NoData footprint or by an actual rasterization/
alignment problem.

This script DOES NOT modify the existing reference raster.

It compares:

    UNOSAT valid observation domain
        -> MCDA raster bounds
        -> MCDA valid-data footprint

and:

    UNOSAT flood
        -> MCDA raster bounds
        -> MCDA valid-data footprint
        -> existing aligned reference raster

Outputs
-------
results/phase9_validation/external_validation/
    unosat_reference_rasterization_diagnostic.json
    unosat_reference_rasterization_diagnostic.csv

Author
------
GeoAI Flood Risk Decision Agent
Phase 9 External Validation
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import box, shape
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

REFERENCE_RASTER = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
    / "unosat_flood_reference_aligned.tif"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "unosat_reference_rasterization_diagnostic.json"
)

REPORT_CSV = (
    OUTPUT_DIR
    / "unosat_reference_rasterization_diagnostic.csv"
)


# ---------------------------------------------------------------------
# Source layers
# ---------------------------------------------------------------------

FLOOD_LAYER_NAME = (
    "PL_20240501_FloodExtent_Nairobi_Kiambu.shp"
)

ANALYSIS_EXTENT_LAYER_NAME = (
    "PL_20240501_AnalysisExtent_Nairobi_Kiambu.shp"
)

CLOUD_LAYER_NAME = (
    "PL_20240501_CloudObstruction_Nairobi_Kiambu.shp"
)


# ---------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------

TARGET_CRS = "EPSG:32737"

REFERENCE_NODATA = -9999

FLOOD_VALUE = 1

NON_FLOOD_VALUE = 0


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------


def json_safe(value: Any) -> Any:
    """Convert values to JSON-safe Python types."""

    if isinstance(value, dict):
        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(v)
            for v in value
        ]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if not np.isfinite(value):
            return None
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, Path):
        return str(value)

    return value


def find_layer(filename: str) -> Path:
    """Locate a required UNOSAT layer."""

    matches = list(
        UNOSAT_ROOT.rglob(filename)
    )

    if not matches:
        raise FileNotFoundError(
            f"Layer not found:\n"
            f"{filename}\n\n"
            f"Search root:\n"
            f"{UNOSAT_ROOT}"
        )

    return matches[0]


def repair_geometries(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Repair invalid geometries in memory."""

    gdf = gdf.copy()

    gdf = gdf.loc[
        gdf.geometry.notna()
    ].copy()

    gdf = gdf.loc[
        ~gdf.geometry.is_empty
    ].copy()

    gdf["geometry"] = gdf.geometry.apply(
        lambda geom: (
            make_valid(geom)
            if not geom.is_valid
            else geom
        )
    )

    gdf = gdf.loc[
        gdf.geometry.notna()
    ].copy()

    gdf = gdf.loc[
        ~gdf.geometry.is_empty
    ].copy()

    return gdf


def union_geometry(
    gdf: gpd.GeoDataFrame,
):
    """Create a valid unary union."""

    geometries = [
        geom
        for geom in gdf.geometry
        if geom is not None
        and not geom.is_empty
        and geom.is_valid
    ]

    if not geometries:
        raise RuntimeError(
            "No valid geometries available."
        )

    result = unary_union(
        geometries
    )

    if not result.is_valid:
        result = make_valid(result)

    if result.is_empty:
        raise RuntimeError(
            "Union geometry is empty."
        )

    return result


def area_km2(geometry) -> float:
    """Return projected geometry area in km²."""

    if geometry is None:
        return 0.0

    if geometry.is_empty:
        return 0.0

    return float(
        geometry.area / 1_000_000.0
    )


def area_difference_pct(
    reference_area: float,
    comparison_area: float,
) -> float | None:
    """
    Calculate percentage difference relative to reference_area.
    """

    if reference_area == 0:
        return None

    return float(
        (
            comparison_area
            - reference_area
        )
        / reference_area
        * 100.0
    )


def mask_area_km2(
    mask: np.ndarray,
    transform,
) -> float:
    """Calculate raster mask area in km²."""

    cell_area_m2 = (
        abs(transform.a)
        * abs(transform.e)
    )

    cell_count = int(
        np.count_nonzero(mask)
    )

    return float(
        cell_count
        * cell_area_m2
        / 1_000_000.0
    )


def raster_mask_to_geometry(
    mask: np.ndarray,
    transform,
):
    """
    Convert a raster mask to a geometry union.

    This is used only for diagnostic comparison with vector
    geometry. It does not modify any project data.
    """

    geometries = []

    for geom, value in shapes(
        mask.astype(np.uint8),
        mask=mask.astype(bool),
        transform=transform,
    ):
        if value == 1:
            geometries.append(
                shape(geom)
            )

    if not geometries:
        return None

    result = unary_union(
        geometries
    )

    if not result.is_valid:
        result = make_valid(result)

    return result


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> None:

    print("=" * 72)
    print(
        "PHASE 9.11.3 - UNOSAT REFERENCE RASTERIZATION DIAGNOSTIC"
    )
    print("=" * 72)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------------
    # 1. Locate inputs
    # ---------------------------------------------------------------

    print("\n[1/8] Locating input data...")

    flood_path = find_layer(
        FLOOD_LAYER_NAME
    )

    analysis_path = find_layer(
        ANALYSIS_EXTENT_LAYER_NAME
    )

    cloud_path = find_layer(
        CLOUD_LAYER_NAME
    )

    if not MCDA_RASTER.exists():
        raise FileNotFoundError(
            f"MCDA raster not found:\n{MCDA_RASTER}"
        )

    if not REFERENCE_RASTER.exists():
        raise FileNotFoundError(
            f"Prepared reference raster not found:\n"
            f"{REFERENCE_RASTER}"
        )

    print(
        f"  Flood: {flood_path}"
    )

    print(
        f"  Analysis extent: {analysis_path}"
    )

    print(
        f"  Cloud obstruction: {cloud_path}"
    )

    print(
        f"  MCDA: {MCDA_RASTER}"
    )

    print(
        f"  Reference raster: {REFERENCE_RASTER}"
    )

    # ---------------------------------------------------------------
    # 2. Read raster grids
    # ---------------------------------------------------------------

    print("\n[2/8] Reading MCDA and reference grids...")

    with rasterio.open(
        MCDA_RASTER
    ) as mcda:

        mcda_data = mcda.read(1)
        mcda_crs = mcda.crs
        mcda_transform = mcda.transform
        mcda_bounds = mcda.bounds
        mcda_width = mcda.width
        mcda_height = mcda.height
        mcda_nodata = mcda.nodata

    with rasterio.open(
        REFERENCE_RASTER
    ) as reference:

        reference_data = reference.read(1)
        reference_crs = reference.crs
        reference_transform = reference.transform
        reference_bounds = reference.bounds
        reference_width = reference.width
        reference_height = reference.height
        reference_nodata = reference.nodata

    if str(mcda_crs) != TARGET_CRS:
        raise RuntimeError(
            f"Unexpected MCDA CRS: {mcda_crs}"
        )

    if str(reference_crs) != TARGET_CRS:
        raise RuntimeError(
            f"Unexpected reference CRS: {reference_crs}"
        )

    mcda_valid = np.isfinite(
        mcda_data
    )

    if mcda_nodata is not None:
        mcda_valid &= (
            mcda_data != mcda_nodata
        )

    reference_observed = (
        reference_data
        != REFERENCE_NODATA
    )

    reference_flood = (
        reference_data
        == FLOOD_VALUE
    )

    reference_non_flood = (
        reference_data
        == NON_FLOOD_VALUE
    )

    reference_unobserved = (
        reference_data
        == REFERENCE_NODATA
    )

    print(
        f"  MCDA dimensions: "
        f"{mcda_width} x {mcda_height}"
    )

    print(
        f"  MCDA valid cells: "
        f"{int(mcda_valid.sum()):,}"
    )

    print(
        f"  Reference observed cells: "
        f"{int(reference_observed.sum()):,}"
    )

    print(
        f"  Reference flood cells: "
        f"{int(reference_flood.sum()):,}"
    )

    # ---------------------------------------------------------------
    # 3. Read and project UNOSAT geometries
    # ---------------------------------------------------------------

    print("\n[3/8] Preparing UNOSAT geometries...")

    flood_gdf = repair_geometries(
        gpd.read_file(
            flood_path
        )
    )

    analysis_gdf = repair_geometries(
        gpd.read_file(
            analysis_path
        )
    )

    cloud_gdf = repair_geometries(
        gpd.read_file(
            cloud_path
        )
    )

    flood_gdf = flood_gdf.to_crs(
        TARGET_CRS
    )

    analysis_gdf = analysis_gdf.to_crs(
        TARGET_CRS
    )

    cloud_gdf = cloud_gdf.to_crs(
        TARGET_CRS
    )

    flood = union_geometry(
        flood_gdf
    )

    analysis_extent = union_geometry(
        analysis_gdf
    )

    cloud = union_geometry(
        cloud_gdf
    )

    valid_observation_domain = (
        analysis_extent.difference(
            cloud
        )
    )

    if not valid_observation_domain.is_valid:
        valid_observation_domain = make_valid(
            valid_observation_domain
        )

    # ---------------------------------------------------------------
    # 4. Construct exact spatial intersections
    # ---------------------------------------------------------------

    print(
        "\n[4/8] Calculating vector intersections..."
    )

    mcda_bounds_geometry = box(
        mcda_bounds.left,
        mcda_bounds.bottom,
        mcda_bounds.right,
        mcda_bounds.top,
    )

    # Valid observation domain inside the rectangular MCDA bounds.
    observation_inside_bounds = (
        valid_observation_domain.intersection(
            mcda_bounds_geometry
        )
    )

    # Flood inside the rectangular MCDA bounds.
    flood_inside_bounds = (
        flood.intersection(
            mcda_bounds_geometry
        )
    )

    # Convert actual valid MCDA raster cells into a polygon geometry.
    mcda_valid_geometry = (
        raster_mask_to_geometry(
            mcda_valid,
            mcda_transform,
        )
    )

    if mcda_valid_geometry is None:
        raise RuntimeError(
            "MCDA valid-data footprint could not be "
            "converted to geometry."
        )

    # Valid observation domain inside actual valid MCDA cells.
    observation_inside_valid_mcda = (
        valid_observation_domain.intersection(
            mcda_valid_geometry
        )
    )

    # Flood inside actual valid MCDA cells.
    flood_inside_valid_mcda = (
        flood.intersection(
            mcda_valid_geometry
        )
    )

    # Flood inside both valid observation domain and
    # actual valid MCDA cells.
    flood_inside_validation_domain = (
        flood.intersection(
            valid_observation_domain
        ).intersection(
            mcda_valid_geometry
        )
    )

    # ---------------------------------------------------------------
    # 5. Calculate vector areas
    # ---------------------------------------------------------------

    print(
        "\n[5/8] Comparing vector areas..."
    )

    vector_results = {
        "analysis_extent_km2": area_km2(
            analysis_extent
        ),
        "cloud_obstruction_km2": area_km2(
            cloud
        ),
        "valid_observation_domain_km2": area_km2(
            valid_observation_domain
        ),
        "valid_observation_inside_mcda_bounds_km2": (
            area_km2(
                observation_inside_bounds
            )
        ),
        "valid_observation_inside_valid_mcda_km2": (
            area_km2(
                observation_inside_valid_mcda
            )
        ),
        "flood_total_km2": area_km2(
            flood
        ),
        "flood_inside_mcda_bounds_km2": (
            area_km2(
                flood_inside_bounds
            )
        ),
        "flood_inside_valid_mcda_km2": (
            area_km2(
                flood_inside_valid_mcda
            )
        ),
        "flood_inside_validation_domain_km2": (
            area_km2(
                flood_inside_validation_domain
            )
        ),
    }

    for key, value in vector_results.items():
        print(
            f"  {key}: {value:.6f}"
        )

    # ---------------------------------------------------------------
    # 6. Calculate raster areas
    # ---------------------------------------------------------------

    print(
        "\n[6/8] Comparing raster areas..."
    )

    reference_flood_area = mask_area_km2(
        reference_flood,
        reference_transform,
    )

    reference_observed_area = mask_area_km2(
        reference_observed,
        reference_transform,
    )

    reference_non_flood_area = mask_area_km2(
        reference_non_flood,
        reference_transform,
    )

    reference_unobserved_area = mask_area_km2(
        reference_unobserved,
        reference_transform,
    )

    raster_results = {
        "reference_flood_km2": (
            reference_flood_area
        ),
        "reference_observed_km2": (
            reference_observed_area
        ),
        "reference_non_flood_km2": (
            reference_non_flood_area
        ),
        "reference_unobserved_km2": (
            reference_unobserved_area
        ),
    }

    for key, value in raster_results.items():
        print(
            f"  {key}: {value:.6f}"
        )

    # ---------------------------------------------------------------
    # 7. Diagnose differences
    # ---------------------------------------------------------------

    print(
        "\n[7/8] Diagnosing area differences..."
    )

    flood_vector_target = vector_results[
        "flood_inside_validation_domain_km2"
    ]

    observed_vector_target = vector_results[
        "valid_observation_inside_valid_mcda_km2"
    ]

    flood_difference_pct = (
        area_difference_pct(
            flood_vector_target,
            reference_flood_area,
        )
    )

    observed_difference_pct = (
        area_difference_pct(
            observed_vector_target,
            reference_observed_area,
        )
    )

    flood_retention_pct = None

    if flood_vector_target > 0:
        flood_retention_pct = (
            reference_flood_area
            / flood_vector_target
            * 100.0
        )

    observed_retention_pct = None

    if observed_vector_target > 0:
        observed_retention_pct = (
            reference_observed_area
            / observed_vector_target
            * 100.0
        )

    print(
        f"  Vector flood in validation domain: "
        f"{flood_vector_target:.6f} km²"
    )

    print(
        f"  Rasterized flood: "
        f"{reference_flood_area:.6f} km²"
    )

    print(
        f"  Flood rasterization difference: "
        f"{flood_difference_pct:.2f}%"
    )

    print(
        f"  Flood area retained: "
        f"{flood_retention_pct:.2f}%"
    )

    print(
        f"  Vector observed domain in valid MCDA: "
        f"{observed_vector_target:.6f} km²"
    )

    print(
        f"  Rasterized observed domain: "
        f"{reference_observed_area:.6f} km²"
    )

    print(
        f"  Observation-domain difference: "
        f"{observed_difference_pct:.2f}%"
    )

    print(
        f"  Observation-domain area retained: "
        f"{observed_retention_pct:.2f}%"
    )

    # ---------------------------------------------------------------
    # Pixel/grid diagnostics
    # ---------------------------------------------------------------

    transform_match = np.allclose(
        mcda_transform,
        reference_transform,
    )

    dimensions_match = (
        mcda_width == reference_width
        and mcda_height == reference_height
    )

    resolution_match = np.allclose(
        mcda_transform.a,
        reference_transform.a,
    ) and np.allclose(
        mcda_transform.e,
        reference_transform.e,
    )

    same_reference_grid = (
        transform_match
        and dimensions_match
        and resolution_match
    )

    print(
        f"\n  Same raster grid: "
        f"{'PASS' if same_reference_grid else 'FAIL'}"
    )

    # ---------------------------------------------------------------
    # Spatial containment diagnostics
    # ---------------------------------------------------------------

    flood_outside_validation = (
        flood_inside_valid_mcda.difference(
            flood_inside_validation_domain
        )
    )

    observation_outside_validation = (
        observation_inside_valid_mcda.difference(
            observation_inside_validation
        )
        if False
        else None
    )

    flood_valid_mcda_area = area_km2(
        flood_inside_valid_mcda
    )

    flood_validation_area = area_km2(
        flood_inside_validation_domain
    )

    flood_excluded_by_observation_domain = (
        max(
            flood_valid_mcda_area
            - flood_validation_area,
            0.0,
        )
    )

    # ---------------------------------------------------------------
    # 8. Final interpretation and report
    # ---------------------------------------------------------------

    print(
        "\n[8/8] Final diagnostic assessment..."
    )

    # A small tolerance is appropriate for raster/vector boundary
    # differences, but not for a discrepancy of tens of percent.
    AREA_TOLERANCE_PERCENT = 5.0

    if (
        abs(flood_difference_pct or 0)
        <= AREA_TOLERANCE_PERCENT
        and abs(observed_difference_pct or 0)
        <= AREA_TOLERANCE_PERCENT
    ):
        diagnostic_status = (
            "RASTERIZATION_AREA_DIFFERENCE_ACCEPTABLE"
        )

    elif (
        flood_retention_pct is not None
        and observed_retention_pct is not None
        and flood_retention_pct < 100
        and observed_retention_pct < 100
    ):
        diagnostic_status = (
            "AREA_DIFFERENCE_REQUIRES_SPATIAL_INTERPRETATION"
        )

    else:
        diagnostic_status = (
            "RASTERIZATION_DIFFERENCE_REQUIRES_INVESTIGATION"
        )

    print(
        f"  Diagnostic status: "
        f"{diagnostic_status}"
    )

    print(
        f"  Flood excluded by observation-domain restriction "
        f"within valid MCDA: "
        f"{flood_excluded_by_observation_domain:.6f} km²"
    )

    report = {
        "phase": "9.11.3",
        "purpose": (
            "Diagnose differences between vector UNOSAT "
            "reference geometry and aligned reference raster."
        ),
        "status": diagnostic_status,
        "inputs": {
            "flood_layer": str(flood_path),
            "analysis_extent_layer": str(analysis_path),
            "cloud_obstruction_layer": str(cloud_path),
            "mcda_raster": str(MCDA_RASTER),
            "reference_raster": str(REFERENCE_RASTER),
        },
        "reference_definition": {
            "valid_observation_domain": (
                "Analysis extent minus cloud obstruction"
            ),
            "validation_domain": (
                "Valid observation domain intersect "
                "actual valid MCDA raster cells"
            ),
            "flood_value": FLOOD_VALUE,
            "non_flood_value": NON_FLOOD_VALUE,
            "nodata_value": REFERENCE_NODATA,
        },
        "mcda_grid": {
            "crs": str(mcda_crs),
            "width": mcda_width,
            "height": mcda_height,
            "valid_cells": int(
                mcda_valid.sum()
            ),
            "same_reference_grid": (
                same_reference_grid
            ),
        },
        "vector_results": vector_results,
        "raster_results": raster_results,
        "comparison": {
            "flood_vector_target_km2": (
                flood_vector_target
            ),
            "flood_raster_km2": (
                reference_flood_area
            ),
            "flood_difference_percent": (
                flood_difference_pct
            ),
            "flood_area_retained_percent": (
                flood_retention_pct
            ),
            "observed_vector_target_km2": (
                observed_vector_target
            ),
            "observed_raster_km2": (
                reference_observed_area
            ),
            "observed_difference_percent": (
                observed_difference_pct
            ),
            "observed_area_retained_percent": (
                observed_retention_pct
            ),
            "flood_excluded_by_observation_domain_within_valid_mcda_km2": (
                flood_excluded_by_observation_domain
            ),
        },
        "interpretation": [
            (
                "The MCDA raster contains a rectangular grid with "
                "a smaller internal valid-data footprint."
            ),
            (
                "External validation must be restricted to cells "
                "where the susceptibility raster contains valid data."
            ),
            (
                "Vector intersections with the MCDA raster bounds "
                "are therefore not equivalent to intersections "
                "with the actual valid MCDA footprint."
            ),
            (
                "Raster/vector area differences can occur because "
                "the reference raster represents the geometry on "
                "the fixed MCDA grid."
            ),
            (
                "The magnitude of the difference must nevertheless "
                "be quantified before spatial validation proceeds."
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

    # CSV summary
    csv_rows = [
        (
            "vector_analysis_extent_km2",
            vector_results[
                "analysis_extent_km2"
            ],
        ),
        (
            "vector_cloud_obstruction_km2",
            vector_results[
                "cloud_obstruction_km2"
            ],
        ),
        (
            "vector_valid_observation_domain_km2",
            vector_results[
                "valid_observation_domain_km2"
            ],
        ),
        (
            "vector_observation_inside_mcda_bounds_km2",
            vector_results[
                "valid_observation_inside_mcda_bounds_km2"
            ],
        ),
        (
            "vector_observation_inside_valid_mcda_km2",
            vector_results[
                "valid_observation_inside_valid_mcda_km2"
            ],
        ),
        (
            "vector_flood_total_km2",
            vector_results[
                "flood_total_km2"
            ],
        ),
        (
            "vector_flood_inside_mcda_bounds_km2",
            vector_results[
                "flood_inside_mcda_bounds_km2"
            ],
        ),
        (
            "vector_flood_inside_valid_mcda_km2",
            vector_results[
                "flood_inside_valid_mcda_km2"
            ],
        ),
        (
            "vector_flood_inside_validation_domain_km2",
            vector_results[
                "flood_inside_validation_domain_km2"
            ],
        ),
        (
            "raster_reference_flood_km2",
            reference_flood_area,
        ),
        (
            "raster_reference_observed_km2",
            reference_observed_area,
        ),
        (
            "raster_reference_non_flood_km2",
            reference_non_flood_area,
        ),
        (
            "raster_reference_unobserved_km2",
            reference_unobserved_area,
        ),
        (
            "flood_difference_percent",
            flood_difference_pct,
        ),
        (
            "flood_area_retained_percent",
            flood_retention_pct,
        ),
        (
            "observed_domain_difference_percent",
            observed_difference_pct,
        ),
        (
            "observed_domain_area_retained_percent",
            observed_retention_pct,
        ),
        (
            "flood_excluded_by_observation_domain_within_valid_mcda_km2",
            flood_excluded_by_observation_domain,
        ),
    ]

    with open(
        REPORT_CSV,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "metric",
                "value",
            ]
        )

        writer.writerows(
            csv_rows
        )

    print(
        f"\nDiagnostic JSON written to:\n"
        f"  {REPORT_JSON}"
    )

    print(
        f"\nDiagnostic CSV written to:\n"
        f"  {REPORT_CSV}"
    )

    print("\n" + "=" * 72)
    print(
        "PHASE_9_11_3_RASTERIZATION_DIAGNOSTIC_COMPLETED"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()