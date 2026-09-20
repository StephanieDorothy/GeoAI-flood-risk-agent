"""
Phase 9.11.3 - Prepare UNOSAT Flood Reference Data

Purpose
-------
Prepare the official UNOSAT Product 3834 flood extent for external
validation against the Nairobi County MCDA flood-susceptibility model.

The script:

1. Locates the official UNOSAT flood extent shapefile.
2. Loads the original flood geometry without modifying the source.
3. Diagnoses invalid geometry.
4. Repairs invalid geometry in memory using Shapely make_valid().
5. Reprojects the repaired geometry to the MCDA CRS.
6. Determines the spatial overlap between the UNOSAT flood reference
   and the MCDA analysis footprint.
7. Searches the UNOSAT package for a suitable analysis/observation
   extent layer.
8. Prevents unobserved areas from being treated as non-flooded.
9. Creates an MCDA-aligned binary flood reference raster:
       1 = observed flood
       0 = observed non-flood
       NoData = not observed / outside valid reference domain
10. Validates the resulting reference raster.
11. Writes a detailed JSON preparation report.

Important
---------
The original UNOSAT files are NEVER modified.

All geometry repair, reprojection, clipping, and raster creation are
performed on derived/in-memory data.

This script is a preparation step only. It does NOT perform statistical
external validation. That will be Phase 9.11.4 and 9.11.5.
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from shapely.geometry import box
from shapely.validation import explain_validity


# =============================================================================
# PROJECT PATHS
# =============================================================================

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

CLASSIFIED_RASTER = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "mcda"
    / "flood_susceptibility_classified.tif"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_RASTER = OUTPUT_DIR / "unosat_flood_reference_aligned.tif"
PREPARATION_REPORT = OUTPUT_DIR / "unosat_reference_preparation.json"


# =============================================================================
# EXPECTED PRIMARY FLOOD LAYER
# =============================================================================

PRIMARY_FLOOD_FILENAME = "PL_20240501_FloodExtent_Nairobi_Kiambu.shp"


# =============================================================================
# JSON SERIALIZATION
# =============================================================================

def json_safe(value):
    """
    Convert common NumPy, datetime and Path objects into JSON-safe values.
    """

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]

    return value


# =============================================================================
# HELPERS
# =============================================================================

def print_header(title: str):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def find_shapefiles(root: Path) -> list[Path]:
    """Return all shapefiles recursively."""

    return sorted(root.rglob("*.shp"))


def find_primary_flood_layer(root: Path) -> Path:
    """Locate the expected primary UNOSAT flood extent layer."""

    matches = list(root.rglob(PRIMARY_FLOOD_FILENAME))

    if not matches:
        raise FileNotFoundError(
            f"Primary flood layer not found:\n"
            f"  {PRIMARY_FLOOD_FILENAME}\n"
            f"Search root:\n"
            f"  {root}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            "Multiple copies of the primary flood layer were found:\n"
            + "\n".join(str(p) for p in matches)
        )

    return matches[0]


def find_analysis_extent_candidates(root: Path) -> list[Path]:
    """
    Search for likely UNOSAT observation/analysis extent layers.

    We deliberately do not assume a single filename because the package
    may use different naming conventions.
    """

    candidates = []

    keywords = (
        "analysis",
        "analysed",
        "analyzed",
        "cloud",
        "extent",
        "area",
        "study",
    )

    for shp in find_shapefiles(root):

        # The primary flood layer itself is not an observation-domain layer.
        if shp.name.lower() == PRIMARY_FLOOD_FILENAME.lower():
            continue

        name = shp.stem.lower()

        if any(keyword in name for keyword in keywords):
            candidates.append(shp)

    return sorted(set(candidates))


def repair_geometry(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """
    Repair invalid geometries in memory.

    The original source file is never modified.
    """

    original_invalid = int((~gdf.geometry.is_valid).sum())

    invalid_examples = []

    if original_invalid > 0:
        for geom in gdf.loc[~gdf.geometry.is_valid, "geometry"].head(10):
            invalid_examples.append(explain_validity(geom))

    repaired = gdf.copy()

    if original_invalid > 0:
        repaired["geometry"] = repaired.geometry.make_valid()

    remaining_invalid = int((~repaired.geometry.is_valid).sum())

    null_count = int(repaired.geometry.isna().sum())
    empty_count = int(repaired.geometry.is_empty.sum())

    diagnostics = {
        "original_invalid_geometry_count": original_invalid,
        "remaining_invalid_geometry_count": remaining_invalid,
        "null_geometry_count": null_count,
        "empty_geometry_count": empty_count,
        "repair_method": "shapely_make_valid",
        "repair_performed": original_invalid > 0,
        "original_invalid_examples": invalid_examples,
    }

    return repaired, diagnostics


def get_raster_metadata(path: Path) -> dict:
    """Return important raster metadata."""

    with rasterio.open(path) as src:
        return {
            "path": str(path),
            "crs": str(src.crs),
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
            "transform": list(src.transform),
            "resolution_x": src.res[0],
            "resolution_y": src.res[1],
            "bounds": {
                "left": src.bounds.left,
                "bottom": src.bounds.bottom,
                "right": src.bounds.right,
                "top": src.bounds.top,
            },
        }


def geometry_bounds_area_km2(geometry) -> float:
    """Return area in km² for a geometry in a projected CRS."""

    if geometry is None or geometry.is_empty:
        return 0.0

    return float(geometry.area / 1_000_000.0)


# =============================================================================
# MAIN
# =============================================================================

def main():

    print_header("PHASE 9.11.3 - UNOSAT FLOOD REFERENCE DATA PREPARATION")

    report = {
        "phase": "9.11.3",
        "title": "UNOSAT Flood Reference Data Preparation",
        "status": "IN_PROGRESS",
        "project_root": str(PROJECT_ROOT),
        "unosat_root": str(UNOSAT_ROOT),
        "primary_flood_layer": None,
        "mcda_reference": None,
        "classified_reference": None,
        "analysis_extent_candidates": [],
        "geometry_repair": {},
        "reprojection": {},
        "spatial_overlap": {},
        "reference_raster": {},
        "validation": {},
        "scientific_notes": [],
    }

    # -------------------------------------------------------------------------
    # 1. Validate required inputs
    # -------------------------------------------------------------------------

    print_header("1. INPUT VALIDATION")

    if not UNOSAT_ROOT.exists():
        raise FileNotFoundError(
            f"UNOSAT directory does not exist:\n{UNOSAT_ROOT}"
        )

    if not MCDA_RASTER.exists():
        raise FileNotFoundError(
            f"MCDA susceptibility raster does not exist:\n{MCDA_RASTER}"
        )

    if not CLASSIFIED_RASTER.exists():
        raise FileNotFoundError(
            f"Classified susceptibility raster does not exist:\n{CLASSIFIED_RASTER}"
        )

    flood_path = find_primary_flood_layer(UNOSAT_ROOT)

    print(f"UNOSAT package: PASS")
    print(f"MCDA raster: PASS")
    print(f"Classified raster: PASS")
    print()
    print(f"Primary flood layer:")
    print(f"  {flood_path}")

    report["primary_flood_layer"] = str(flood_path)
    report["mcda_reference"] = get_raster_metadata(MCDA_RASTER)
    report["classified_reference"] = get_raster_metadata(CLASSIFIED_RASTER)

    # -------------------------------------------------------------------------
    # 2. Read primary flood layer
    # -------------------------------------------------------------------------

    print_header("2. PRIMARY FLOOD LAYER INSPECTION")

    flood_gdf = gpd.read_file(flood_path)

    if flood_gdf.empty:
        raise RuntimeError("Primary flood layer contains no features.")

    if flood_gdf.crs is None:
        raise RuntimeError(
            "Primary flood layer has no CRS. "
            "Cannot safely prepare the reference."
        )

    print(f"Features: {len(flood_gdf)}")
    print(f"CRS: {flood_gdf.crs}")
    print(f"Geometry types: {flood_gdf.geometry.geom_type.unique().tolist()}")

    print()
    print("Relevant source attributes:")

    for field in [
        "Water_Clas",
        "Water_Stat",
        "Sensor_ID",
        "Sensor_Dat",
        "EventCode",
        "Area_m2",
        "Area_ha",
    ]:
        if field in flood_gdf.columns:
            values = flood_gdf[field].drop_duplicates().tolist()
            print(f"  {field}: {values}")

    report["flood_layer_metadata"] = {
        "feature_count": len(flood_gdf),
        "crs": str(flood_gdf.crs),
        "geometry_types": flood_gdf.geometry.geom_type.unique().tolist(),
        "fields": list(flood_gdf.columns),
    }

    # -------------------------------------------------------------------------
    # 3. Geometry validation and repair
    # -------------------------------------------------------------------------

    print_header("3. GEOMETRY VALIDATION AND REPAIR")

    prepared_flood, geometry_diagnostics = repair_geometry(flood_gdf)

    print(
        "Original invalid geometries: "
        f"{geometry_diagnostics['original_invalid_geometry_count']}"
    )

    print(
        "Remaining invalid geometries: "
        f"{geometry_diagnostics['remaining_invalid_geometry_count']}"
    )

    print(
        "Null geometries: "
        f"{geometry_diagnostics['null_geometry_count']}"
    )

    print(
        "Empty geometries: "
        f"{geometry_diagnostics['empty_geometry_count']}"
    )

    if geometry_diagnostics["remaining_invalid_geometry_count"] > 0:
        raise RuntimeError(
            "Geometry repair did not resolve all invalid geometries."
        )

    if geometry_diagnostics["null_geometry_count"] > 0:
        raise RuntimeError(
            "Null geometries remain after preparation."
        )

    if geometry_diagnostics["empty_geometry_count"] > 0:
        raise RuntimeError(
            "Empty geometries remain after preparation."
        )

    report["geometry_repair"] = geometry_diagnostics

    print("Geometry preparation: PASS")

    # -------------------------------------------------------------------------
    # 4. Reproject to MCDA CRS
    # -------------------------------------------------------------------------

    print_header("4. REPROJECTION TO MCDA CRS")

    with rasterio.open(MCDA_RASTER) as mcda_src:

        mcda_crs = mcda_src.crs
        mcda_bounds = mcda_src.bounds
        mcda_transform = mcda_src.transform
        mcda_width = mcda_src.width
        mcda_height = mcda_src.height
        mcda_nodata = mcda_src.nodata

    print(f"MCDA CRS: {mcda_crs}")
    print(f"Flood source CRS: {prepared_flood.crs}")

    if prepared_flood.crs != mcda_crs:
        flood_projected = prepared_flood.to_crs(mcda_crs)
        print(f"Reprojected flood reference to: {mcda_crs}")
    else:
        flood_projected = prepared_flood.copy()
        print("Flood reference already matches MCDA CRS.")

    print("Reprojection: PASS")

    report["reprojection"] = {
        "source_crs": str(prepared_flood.crs),
        "target_crs": str(mcda_crs),
        "reprojection_performed": str(prepared_flood.crs) != str(mcda_crs),
    }

    # -------------------------------------------------------------------------
    # 5. MCDA footprint intersection
    # -------------------------------------------------------------------------

    print_header("5. MCDA FOOTPRINT OVERLAP")

    mcda_footprint = box(
        mcda_bounds.left,
        mcda_bounds.bottom,
        mcda_bounds.right,
        mcda_bounds.top,
    )

    flood_union = flood_projected.geometry.union_all()

    flood_intersection = flood_union.intersection(mcda_footprint)

    overlap_area_km2 = geometry_bounds_area_km2(flood_intersection)

    print(f"MCDA footprint:")
    print(f"  Width: {mcda_width}")
    print(f"  Height: {mcda_height}")
    print(f"  CRS: {mcda_crs}")

    print()
    print(f"Flood/reference overlap area: {overlap_area_km2:.6f} km²")

    if flood_intersection.is_empty:
        raise RuntimeError(
            "The UNOSAT flood reference has no spatial overlap "
            "with the MCDA analysis footprint."
        )

    print("Spatial overlap: PASS")

    report["spatial_overlap"] = {
        "mcda_crs": str(mcda_crs),
        "mcda_width": mcda_width,
        "mcda_height": mcda_height,
        "flood_overlap_area_km2": overlap_area_km2,
        "overlap_exists": True,
    }

    # -------------------------------------------------------------------------
    # 6. Search for observation / analysis extent layers
    # -------------------------------------------------------------------------

    print_header("6. SEARCH FOR UNOSAT OBSERVATION/ANALYSIS EXTENT")

    analysis_candidates = find_analysis_extent_candidates(UNOSAT_ROOT)

    report["analysis_extent_candidates"] = [
        str(path) for path in analysis_candidates
    ]

    if analysis_candidates:
        print("Potential analysis/observation extent candidates:")

        for candidate in analysis_candidates:
            print(f"  {candidate.name}")

    else:
        print(
            "No clearly named analysis/observation extent layer "
            "was automatically identified."
        )

    # -------------------------------------------------------------------------
    # 7. Safety decision regarding observed domain
    # -------------------------------------------------------------------------

    print_header("7. OBSERVATION-DOMAIN SAFETY CHECK")

    """
    We do NOT automatically create 0 = non-flood from the entire MCDA grid.

    Unless a valid UNOSAT observation/analysis domain is identified, the
    correct scientific action is to stop before producing a binary reference
    raster.

    This protects the validation from incorrectly treating unobserved areas
    as observed non-flooded areas.
    """

    if len(analysis_candidates) == 0:

        report["status"] = "PREPARATION_REQUIRES_OBSERVATION_DOMAIN"

        report["scientific_notes"].append(
            "A valid UNOSAT observation/analysis extent was not "
            "automatically identified. The script therefore does not "
            "create a binary 0/1 reference raster, because unobserved "
            "areas must not be treated as observed non-flooded areas."
        )

        with PREPARATION_REPORT.open("w", encoding="utf-8") as f:
            json.dump(
                json_safe(report),
                f,
                indent=2,
                ensure_ascii=False,
            )

        print()
        print(
            "SAFE STOP: No observation-domain layer was automatically "
            "identified."
        )
        print()
        print(
            "The preparation report has been written, but the reference "
            "raster was NOT created."
        )
        print()
        print(f"Report:")
        print(f"  {PREPARATION_REPORT}")
        print()
        print(
            "This is intentional scientific protection against treating "
            "unobserved areas as non-flooded."
        )

        return

    # -------------------------------------------------------------------------
    # 8. Require exactly one clear observation extent
    # -------------------------------------------------------------------------

    if len(analysis_candidates) > 1:

        report["status"] = "PREPARATION_REQUIRES_ANALYSIS_EXTENT_SELECTION"

        report["scientific_notes"].append(
            "Multiple possible analysis/observation extent layers were "
            "identified. Automatic selection was intentionally avoided "
            "because the correct observation domain must be established "
            "from UNOSAT product semantics rather than filename alone."
        )

        with PREPARATION_REPORT.open("w", encoding="utf-8") as f:
            json.dump(
                json_safe(report),
                f,
                indent=2,
                ensure_ascii=False,
            )

        print()
        print(
            "SAFE STOP: Multiple potential observation-domain layers "
            "were identified."
        )
        print()
        print("They must be evaluated before creating the binary reference.")

        for candidate in analysis_candidates:
            print(f"  {candidate}")

        print()
        print(f"Report:")
        print(f"  {PREPARATION_REPORT}")

        return

    # -------------------------------------------------------------------------
    # 9. Read selected observation extent
    # -------------------------------------------------------------------------

    observation_extent_path = analysis_candidates[0]

    print_header("8. OBSERVATION EXTENT PREPARATION")

    observation_gdf = gpd.read_file(observation_extent_path)

    if observation_gdf.empty:
        raise RuntimeError(
            f"Observation extent layer is empty:\n"
            f"{observation_extent_path}"
        )

    if observation_gdf.crs is None:
        raise RuntimeError(
            f"Observation extent has no CRS:\n"
            f"{observation_extent_path}"
        )

    print(f"Observation extent:")
    print(f"  {observation_extent_path.name}")
    print(f"Features: {len(observation_gdf)}")
    print(f"CRS: {observation_gdf.crs}")

    observation_prepared, observation_geometry_diagnostics = (
        repair_geometry(observation_gdf)
    )

    if (
        observation_geometry_diagnostics[
            "remaining_invalid_geometry_count"
        ]
        > 0
    ):
        raise RuntimeError(
            "Observation extent geometry remains invalid after repair."
        )

    if observation_prepared.crs != mcda_crs:
        observation_projected = observation_prepared.to_crs(mcda_crs)
    else:
        observation_projected = observation_prepared.copy()

    observation_union = observation_projected.geometry.union_all()

    observation_mcda_overlap = observation_union.intersection(
        mcda_footprint
    )

    if observation_mcda_overlap.is_empty:
        raise RuntimeError(
            "UNOSAT observation extent has no overlap with MCDA footprint."
        )

    observed_area_km2 = geometry_bounds_area_km2(
        observation_mcda_overlap
    )

    print(f"Observed/analysis domain overlap: {observed_area_km2:.6f} km²")
    print("Observation extent preparation: PASS")

    # -------------------------------------------------------------------------
    # 10. Restrict flood reference to observation domain
    # -------------------------------------------------------------------------

    print_header("9. FLOOD REFERENCE DOMAIN PREPARATION")

    valid_observation_domain = observation_mcda_overlap

    flood_observed_geometry = flood_union.intersection(
        valid_observation_domain
    )

    flood_observed_area_km2 = geometry_bounds_area_km2(
        flood_observed_geometry
    )

    print(
        "Observed flood area within MCDA + observation domain: "
        f"{flood_observed_area_km2:.6f} km²"
    )

    print("Flood/reference domain intersection: PASS")

    # -------------------------------------------------------------------------
    # 11. Create aligned reference raster
    # -------------------------------------------------------------------------

    print_header("10. CREATE MCDA-ALIGNED REFERENCE RASTER")

    reference_array = rasterize(
        [(valid_observation_domain, 0)],
        out_shape=(mcda_height, mcda_width),
        transform=mcda_transform,
        fill=-9999,
        dtype="int16",
    )

    reference_array = reference_array.astype(np.int16)

    # Flood cells override observed non-flood cells.
    flood_shapes = [
        (geom, 1)
        for geom in flood_projected.geometry
        if geom is not None and not geom.is_empty
    ]

    flood_raster = rasterize(
        flood_shapes,
        out_shape=(mcda_height, mcda_width),
        transform=mcda_transform,
        fill=0,
        dtype="int16",
    )

    observed_mask = reference_array != -9999

    reference_array[
        observed_mask & (flood_raster == 1)
    ] = 1

    # Outside the valid observation domain remains NoData.
    reference_array[
        ~observed_mask
    ] = -9999

    profile = {
        "driver": "GTiff",
        "height": mcda_height,
        "width": mcda_width,
        "count": 1,
        "dtype": "int16",
        "crs": mcda_crs,
        "transform": mcda_transform,
        "nodata": -9999,
        "compress": "lzw",
    }

    with rasterio.open(
        REFERENCE_RASTER,
        "w",
        **profile,
    ) as dst:

        dst.write(reference_array, 1)

        dst.update_tags(
            phase="9.11.3",
            source_product="UNOSAT Product 3834",
            source_event="FL20240426KEN",
            source_sensor="Pleiades",
            source_sensor_date="2024-05-01",
            reference_definition=(
                "1=observed flood; "
                "0=observed non-flood; "
                "-9999=unobserved/outside reference domain"
            ),
            preparation_note=(
                "Derived working reference; original UNOSAT source "
                "data were not modified."
            ),
        )

    print(f"Reference raster created:")
    print(f"  {REFERENCE_RASTER}")

    # -------------------------------------------------------------------------
    # 12. Validate reference raster
    # -------------------------------------------------------------------------

    print_header("11. REFERENCE RASTER VALIDATION")

    with rasterio.open(REFERENCE_RASTER) as src:

        prepared = src.read(1)

        crs_match = src.crs == mcda_crs
        dimensions_match = (
            src.width == mcda_width
            and src.height == mcda_height
        )
        transform_match = np.allclose(
            np.array(src.transform),
            np.array(mcda_transform),
        )
        resolution_match = (
            np.isclose(src.res[0], rasterio.open(MCDA_RASTER).res[0])
            and np.isclose(src.res[1], rasterio.open(MCDA_RASTER).res[1])
        )

        nodata_count = int(np.sum(prepared == -9999))
        nonflood_count = int(np.sum(prepared == 0))
        flood_count = int(np.sum(prepared == 1))

        invalid_values = int(
            np.sum(
                ~np.isin(
                    prepared,
                    [-9999, 0, 1],
                )
            )
        )

    validation = {
        "crs_match": crs_match,
        "dimensions_match": dimensions_match,
        "transform_match": transform_match,
        "resolution_match": resolution_match,
        "nodata_cells": nodata_count,
        "observed_nonflood_cells": nonflood_count,
        "observed_flood_cells": flood_count,
        "invalid_value_cells": invalid_values,
        "valid_observed_cells": nonflood_count + flood_count,
        "reference_raster_created": REFERENCE_RASTER.exists(),
    }

    print(f"CRS match: {'PASS' if crs_match else 'FAIL'}")
    print(
        f"Dimensions match: "
        f"{'PASS' if dimensions_match else 'FAIL'}"
    )
    print(
        f"Transform match: "
        f"{'PASS' if transform_match else 'FAIL'}"
    )
    print(
        f"Resolution match: "
        f"{'PASS' if resolution_match else 'FAIL'}"
    )
    print(f"Observed non-flood cells: {nonflood_count:,}")
    print(f"Observed flood cells: {flood_count:,}")
    print(f"NoData/unobserved cells: {nodata_count:,}")
    print(f"Invalid values: {invalid_values:,}")

    if not all(
        [
            crs_match,
            dimensions_match,
            transform_match,
            resolution_match,
            invalid_values == 0,
            REFERENCE_RASTER.exists(),
        ]
    ):
        raise RuntimeError(
            "Reference raster validation failed."
        )

    print()
    print("Reference raster validation: PASS")

    report["reference_raster"] = {
        "path": str(REFERENCE_RASTER),
        "metadata": get_raster_metadata(REFERENCE_RASTER),
        "observed_flood_area_km2": flood_observed_area_km2,
        "observed_domain_area_km2": observed_area_km2,
    }

    report["validation"] = validation

    report["scientific_notes"].extend(
        [
            "The original UNOSAT source data were not modified.",
            "Invalid flood geometry was repaired only in the derived "
            "working representation.",
            "The UNOSAT flood reference was reprojected to the MCDA CRS "
            "EPSG:32737.",
            "The reference raster uses 1 for observed flood and 0 for "
            "observed non-flood within the valid observation domain.",
            "Cells outside the valid observation domain are NoData and "
            "must not be interpreted as observed non-flood.",
            "External statistical validation has not yet been performed.",
        ]
    )

    report["status"] = "PHASE_9_11_3_DATA_PREPARATION_COMPLETED"

    with PREPARATION_REPORT.open("w", encoding="utf-8") as f:
        json.dump(
            json_safe(report),
            f,
            indent=2,
            ensure_ascii=False,
        )

    # -------------------------------------------------------------------------
    # FINAL
    # -------------------------------------------------------------------------

    print_header("PHASE 9.11.3 COMPLETE")

    print(f"Preparation report:")
    print(f"  {PREPARATION_REPORT}")

    print()
    print(f"Reference raster:")
    print(f"  {REFERENCE_RASTER}")

    print()
    print("Original UNOSAT data were not modified.")

    print()
    print(
        "PHASE_9_11_3_DATA_PREPARATION_COMPLETED"
    )


if __name__ == "__main__":
    main()