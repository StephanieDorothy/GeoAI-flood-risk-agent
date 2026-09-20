"""
Phase 9.11.3 - UNOSAT Observation Domain Investigation

Purpose
-------
Investigate the Nairobi/Kiambu Pléiades reference-domain layers from
UNOSAT Product 3834 to determine which layer represents the valid
observation/analysis domain for external flood validation.

Layers investigated:

1. PL_20240501_AnalysisExtent_Nairobi_Kiambu.shp
2. PL_20240501_AnalysisExtent_CropLand_Nairobi_Kiambu.shp
3. PL_20240501_CloudObstruction_Nairobi_Kiambu.shp

The script does NOT:

- modify original UNOSAT data
- repair source files on disk
- create the final validation raster
- perform statistical validation
- classify unobserved areas as non-flooded

The script only investigates the spatial meaning and compatibility
of the candidate observation-domain layers.

Outputs
-------
results/phase9_validation/external_validation/
    unosat_observation_domain_investigation.json
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "external_validation"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = (
    OUTPUT_DIR
    / "unosat_observation_domain_investigation.json"
)


# =============================================================================
# EXPECTED LAYERS
# =============================================================================

CANDIDATE_LAYERS = {
    "analysis_extent": (
        "PL_20240501_AnalysisExtent_Nairobi_Kiambu.shp"
    ),
    "crop_land_analysis_extent": (
        "PL_20240501_AnalysisExtent_CropLand_Nairobi_Kiambu.shp"
    ),
    "cloud_obstruction": (
        "PL_20240501_CloudObstruction_Nairobi_Kiambu.shp"
    ),
}


# =============================================================================
# JSON SERIALIZATION
# =============================================================================

def json_safe(value):
    """Convert common NumPy, datetime and Path values to JSON-safe values."""

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
        return {
            str(key): json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(item)
            for item in value
        ]

    return value


# =============================================================================
# HELPERS
# =============================================================================

def print_header(title: str):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def locate_layer(filename: str) -> Path:
    """Locate one expected UNOSAT shapefile."""

    matches = list(UNOSAT_ROOT.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Could not find:\n"
            f"  {filename}\n"
            f"within:\n"
            f"  {UNOSAT_ROOT}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple copies found for {filename}:\n"
            + "\n".join(str(path) for path in matches)
        )

    return matches[0]


def geometry_area_km2(geometry) -> float:
    """Calculate area in km² for geometry in a projected CRS."""

    if geometry is None or geometry.is_empty:
        return 0.0

    return float(geometry.area / 1_000_000.0)


def geometry_bounds(geometry) -> dict:
    """Return geometry bounds."""

    if geometry is None or geometry.is_empty:
        return {
            "left": None,
            "bottom": None,
            "right": None,
            "top": None,
        }

    left, bottom, right, top = geometry.bounds

    return {
        "left": float(left),
        "bottom": float(bottom),
        "right": float(right),
        "top": float(top),
    }


def geometry_diagnostics(gdf: gpd.GeoDataFrame) -> dict:
    """Return basic geometry diagnostics."""

    invalid_mask = ~gdf.geometry.is_valid

    invalid_examples = []

    for geometry in gdf.loc[invalid_mask, "geometry"].head(5):
        invalid_examples.append(
            explain_validity(geometry)
        )

    return {
        "feature_count": int(len(gdf)),
        "null_geometry_count": int(gdf.geometry.isna().sum()),
        "empty_geometry_count": int(gdf.geometry.is_empty.sum()),
        "invalid_geometry_count": int(invalid_mask.sum()),
        "invalid_examples": invalid_examples,
        "geometry_types": (
            gdf.geometry.geom_type
            .value_counts()
            .to_dict()
        ),
    }


def attribute_summary(
    gdf: gpd.GeoDataFrame,
) -> dict:
    """
    Return a compact attribute summary.

    We do not dump every row because some UNOSAT layers can contain
    many features.
    """

    summary = {}

    for column in gdf.columns:

        if column == "geometry":
            continue

        series = gdf[column]

        try:
            unique_values = series.drop_duplicates().tolist()
        except Exception:
            unique_values = []

        # Keep output manageable.
        if len(unique_values) > 20:
            unique_values = unique_values[:20]
            truncated = True
        else:
            truncated = False

        summary[column] = {
            "dtype": str(series.dtype),
            "unique_value_count": int(
                series.nunique(dropna=False)
            ),
            "sample_values": unique_values,
            "sample_values_truncated": truncated,
        }

    return summary


def reproject_for_analysis(
    gdf: gpd.GeoDataFrame,
    target_crs,
) -> gpd.GeoDataFrame:

    if gdf.crs is None:
        raise RuntimeError(
            "Layer has no CRS and cannot be reprojected safely."
        )

    if gdf.crs != target_crs:
        return gdf.to_crs(target_crs)

    return gdf.copy()


# =============================================================================
# MAIN
# =============================================================================

def main():

    print_header(
        "PHASE 9.11.3 - UNOSAT OBSERVATION DOMAIN INVESTIGATION"
    )

    report = {
        "phase": "9.11.3",
        "purpose": (
            "Investigate Nairobi/Kiambu Pléiades observation-domain "
            "layers before creating an external-validation reference raster."
        ),
        "project_root": str(PROJECT_ROOT),
        "unosat_root": str(UNOSAT_ROOT),
        "mcda_raster": str(MCDA_RASTER),
        "candidate_layers": {},
        "comparisons": {},
        "scientific_interpretation": [],
        "status": "IN_PROGRESS",
    }

    # =========================================================================
    # 1. Validate project inputs
    # =========================================================================

    print_header("1. INPUT VALIDATION")

    if not UNOSAT_ROOT.exists():
        raise FileNotFoundError(
            f"UNOSAT directory does not exist:\n{UNOSAT_ROOT}"
        )

    if not MCDA_RASTER.exists():
        raise FileNotFoundError(
            f"MCDA raster does not exist:\n{MCDA_RASTER}"
        )

    print("UNOSAT package: PASS")
    print("MCDA raster: PASS")

    # =========================================================================
    # 2. Read MCDA reference grid
    # =========================================================================

    print_header("2. MCDA REFERENCE GRID")

    with rasterio.open(MCDA_RASTER) as src:

        mcda_crs = src.crs
        mcda_width = src.width
        mcda_height = src.height
        mcda_transform = src.transform
        mcda_bounds = src.bounds
        mcda_resolution = src.res

    mcda_box = box(
        mcda_bounds.left,
        mcda_bounds.bottom,
        mcda_bounds.right,
        mcda_bounds.top,
    )

    print(f"CRS: {mcda_crs}")
    print(f"Dimensions: {mcda_width} x {mcda_height}")
    print(
        f"Resolution: "
        f"{mcda_resolution[0]:.9f} x "
        f"{mcda_resolution[1]:.9f} m"
    )

    report["mcda_grid"] = {
        "crs": str(mcda_crs),
        "width": mcda_width,
        "height": mcda_height,
        "resolution_x": mcda_resolution[0],
        "resolution_y": mcda_resolution[1],
        "bounds": {
            "left": mcda_bounds.left,
            "bottom": mcda_bounds.bottom,
            "right": mcda_bounds.right,
            "top": mcda_bounds.top,
        },
    }

    # =========================================================================
    # 3. Locate candidate layers
    # =========================================================================

    print_header("3. LOCATE CANDIDATE OBSERVATION LAYERS")

    located_layers = {}

    for role, filename in CANDIDATE_LAYERS.items():

        path = locate_layer(filename)

        located_layers[role] = path

        print(f"{role}:")
        print(f"  {path}")

    # =========================================================================
    # 4. Inspect each candidate
    # =========================================================================

    print_header("4. CANDIDATE LAYER INSPECTION")

    projected_layers = {}

    for role, path in located_layers.items():

        print()
        print("-" * 80)
        print(f"ROLE: {role}")
        print(f"FILE: {path.name}")
        print("-" * 80)

        gdf = gpd.read_file(path)

        if gdf.empty:
            raise RuntimeError(
                f"Candidate layer is empty:\n{path}"
            )

        if gdf.crs is None:
            raise RuntimeError(
                f"Candidate layer has no CRS:\n{path}"
            )

        diagnostics = geometry_diagnostics(gdf)

        print(f"Features: {diagnostics['feature_count']}")
        print(f"CRS: {gdf.crs}")

        print(
            "Geometry types: "
            f"{diagnostics['geometry_types']}"
        )

        print(
            "Invalid geometries: "
            f"{diagnostics['invalid_geometry_count']}"
        )

        print(
            "Null geometries: "
            f"{diagnostics['null_geometry_count']}"
        )

        print(
            "Empty geometries: "
            f"{diagnostics['empty_geometry_count']}"
        )

        print()
        print("Fields:")
        print("  " + ", ".join(gdf.columns))

        print()
        print("Attribute summary:")

        attrs = attribute_summary(gdf)

        for field, details in attrs.items():

            print(
                f"  {field}: "
                f"{details['sample_values']}"
            )

        # Reproject in memory for spatial comparison.
        projected = reproject_for_analysis(
            gdf,
            mcda_crs,
        )

        projected_layers[role] = projected

        union = projected.geometry.union_all()

        overlap = union.intersection(mcda_box)

        union_area_km2 = geometry_area_km2(union)
        overlap_area_km2 = geometry_area_km2(overlap)

        print()
        print(
            f"Total layer geometry area: "
            f"{union_area_km2:.6f} km²"
        )

        print(
            f"Overlap with MCDA footprint: "
            f"{overlap_area_km2:.6f} km²"
        )

        report["candidate_layers"][role] = {
            "path": str(path),
            "filename": path.name,
            "feature_count": diagnostics["feature_count"],
            "source_crs": str(gdf.crs),
            "analysis_crs": str(projected.crs),
            "geometry_diagnostics": diagnostics,
            "attribute_summary": attrs,
            "total_geometry_area_km2": union_area_km2,
            "mcda_overlap_area_km2": overlap_area_km2,
            "bounds_in_mcda_crs": geometry_bounds(union),
        }

    # =========================================================================
    # 5. Compare analysis extent with crop-land extent
    # =========================================================================

    print_header(
        "5. ANALYSIS EXTENT VS CROP-LAND ANALYSIS EXTENT"
    )

    analysis_union = (
        projected_layers["analysis_extent"]
        .geometry
        .union_all()
    )

    crop_union = (
        projected_layers["crop_land_analysis_extent"]
        .geometry
        .union_all()
    )

    analysis_area = geometry_area_km2(
        analysis_union
    )

    crop_area = geometry_area_km2(
        crop_union
    )

    crop_inside_analysis = crop_union.intersection(
        analysis_union
    )

    crop_inside_area = geometry_area_km2(
        crop_inside_analysis
    )

    analysis_outside_crop = analysis_union.difference(
        crop_union
    )

    analysis_outside_crop_area = geometry_area_km2(
        analysis_outside_crop
    )

    crop_overlap_percentage = (
        crop_inside_area / crop_area * 100.0
        if crop_area > 0
        else 0.0
    )

    analysis_non_crop_percentage = (
        analysis_outside_crop_area / analysis_area * 100.0
        if analysis_area > 0
        else 0.0
    )

    print(
        f"Analysis extent area: "
        f"{analysis_area:.6f} km²"
    )

    print(
        f"Crop-land analysis area: "
        f"{crop_area:.6f} km²"
    )

    print(
        f"Crop-land area inside analysis extent: "
        f"{crop_inside_area:.6f} km²"
    )

    print(
        f"Crop-land overlap percentage: "
        f"{crop_overlap_percentage:.3f}%"
    )

    print(
        f"Analysis extent outside crop-land area: "
        f"{analysis_outside_crop_area:.6f} km²"
    )

    print(
        f"Non-crop portion of analysis extent: "
        f"{analysis_non_crop_percentage:.3f}%"
    )

    report["comparisons"]["analysis_vs_crop_land"] = {
        "analysis_extent_area_km2": analysis_area,
        "crop_land_analysis_area_km2": crop_area,
        "crop_land_inside_analysis_area_km2": crop_inside_area,
        "crop_land_overlap_percentage": crop_overlap_percentage,
        "analysis_outside_crop_area_km2": (
            analysis_outside_crop_area
        ),
        "analysis_non_crop_percentage": (
            analysis_non_crop_percentage
        ),
    }

    # =========================================================================
    # 6. Compare cloud obstruction with analysis extent
    # =========================================================================

    print_header(
        "6. CLOUD OBSTRUCTION VS ANALYSIS EXTENT"
    )

    cloud_union = (
        projected_layers["cloud_obstruction"]
        .geometry
        .union_all()
    )

    cloud_area = geometry_area_km2(
        cloud_union
    )

    cloud_inside_analysis = cloud_union.intersection(
        analysis_union
    )

    cloud_inside_analysis_area = geometry_area_km2(
        cloud_inside_analysis
    )

    analysis_minus_cloud = analysis_union.difference(
        cloud_union
    )

    analysis_minus_cloud_area = geometry_area_km2(
        analysis_minus_cloud
    )

    cloud_percentage_of_analysis = (
        cloud_inside_analysis_area
        / analysis_area
        * 100.0
        if analysis_area > 0
        else 0.0
    )

    observable_percentage = (
        analysis_minus_cloud_area
        / analysis_area
        * 100.0
        if analysis_area > 0
        else 0.0
    )

    print(
        f"Cloud obstruction geometry area: "
        f"{cloud_area:.6f} km²"
    )

    print(
        f"Cloud obstruction inside analysis extent: "
        f"{cloud_inside_analysis_area:.6f} km²"
    )

    print(
        f"Cloud-obstructed percentage of analysis extent: "
        f"{cloud_percentage_of_analysis:.3f}%"
    )

    print(
        f"Analysis extent remaining after cloud obstruction: "
        f"{analysis_minus_cloud_area:.6f} km²"
    )

    print(
        f"Potential observable percentage: "
        f"{observable_percentage:.3f}%"
    )

    report["comparisons"]["cloud_vs_analysis"] = {
        "cloud_obstruction_area_km2": cloud_area,
        "cloud_inside_analysis_area_km2": (
            cloud_inside_analysis_area
        ),
        "cloud_percentage_of_analysis": (
            cloud_percentage_of_analysis
        ),
        "analysis_minus_cloud_area_km2": (
            analysis_minus_cloud_area
        ),
        "potential_observable_percentage": (
            observable_percentage
        ),
    }

    # =========================================================================
    # 7. Flood extent relationship
    # =========================================================================

    print_header(
        "7. FLOOD EXTENT VS OBSERVATION DOMAIN"
    )

    flood_filename = (
        "PL_20240501_FloodExtent_Nairobi_Kiambu.shp"
    )

    flood_path = locate_layer(
        flood_filename
    )

    flood_gdf = gpd.read_file(
        flood_path
    )

    if flood_gdf.crs is None:
        raise RuntimeError(
            "Flood extent has no CRS."
        )

    flood_projected = reproject_for_analysis(
        flood_gdf,
        mcda_crs,
    )

    flood_union = flood_projected.geometry.union_all()

    flood_total_area = geometry_area_km2(
        flood_union
    )

    flood_inside_analysis = flood_union.intersection(
        analysis_union
    )

    flood_inside_analysis_area = geometry_area_km2(
        flood_inside_analysis
    )

    flood_inside_crop_land = flood_union.intersection(
        crop_union
    )

    flood_inside_crop_land_area = geometry_area_km2(
        flood_inside_crop_land
    )

    flood_inside_mcda = flood_union.intersection(
        mcda_box
    )

    flood_inside_mcda_area = geometry_area_km2(
        flood_inside_mcda
    )

    flood_inside_analysis_and_mcda = (
        flood_union
        .intersection(analysis_union)
        .intersection(mcda_box)
    )

    flood_inside_analysis_and_mcda_area = (
        geometry_area_km2(
            flood_inside_analysis_and_mcda
        )
    )

    print(
        f"Flood extent total area: "
        f"{flood_total_area:.6f} km²"
    )

    print(
        f"Flood extent inside analysis extent: "
        f"{flood_inside_analysis_area:.6f} km²"
    )

    print(
        f"Flood extent inside crop-land analysis: "
        f"{flood_inside_crop_land_area:.6f} km²"
    )

    print(
        f"Flood extent inside MCDA footprint: "
        f"{flood_inside_mcda_area:.6f} km²"
    )

    print(
        f"Flood extent inside analysis + MCDA footprint: "
        f"{flood_inside_analysis_and_mcda_area:.6f} km²"
    )

    report["comparisons"]["flood_relationship"] = {
        "flood_total_area_km2": flood_total_area,
        "flood_inside_analysis_area_km2": (
            flood_inside_analysis_area
        ),
        "flood_inside_crop_land_area_km2": (
            flood_inside_crop_land_area
        ),
        "flood_inside_mcda_area_km2": (
            flood_inside_mcda_area
        ),
        "flood_inside_analysis_and_mcda_area_km2": (
            flood_inside_analysis_and_mcda_area
        ),
    }

    # =========================================================================
    # 8. Determine whether cloud obstruction is contained within
    #    the analysis domain and calculate potential valid domain.
    # =========================================================================

    print_header(
        "8. OBSERVATION-DOMAIN GEOMETRY ASSESSMENT"
    )

    cloud_difference_from_analysis = (
        cloud_union.difference(
            analysis_union
        )
    )

    cloud_outside_analysis_area = geometry_area_km2(
        cloud_difference_from_analysis
    )

    analysis_minus_cloud_and_mcda = (
        analysis_union
        .difference(cloud_union)
        .intersection(mcda_box)
    )

    valid_observation_mcda_area = geometry_area_km2(
        analysis_minus_cloud_and_mcda
    )

    print(
        f"Cloud area outside analysis extent: "
        f"{cloud_outside_analysis_area:.6f} km²"
    )

    print(
        f"Potential valid observation domain "
        f"inside MCDA footprint: "
        f"{valid_observation_mcda_area:.6f} km²"
    )

    report["comparisons"]["valid_observation_domain"] = {
        "cloud_outside_analysis_area_km2": (
            cloud_outside_analysis_area
        ),
        "potential_valid_observation_mcda_area_km2": (
            valid_observation_mcda_area
        ),
    }

    # =========================================================================
    # 9. Scientific interpretation
    # =========================================================================

    print_header(
        "9. SCIENTIFIC INTERPRETATION"
    )

    report["scientific_interpretation"] = [
        (
            "The primary observation-domain candidate is the "
            "Nairobi/Kiambu Pléiades analysis extent and must be "
            "distinguished from the crop-land-specific analysis extent."
        ),
        (
            "The crop-land analysis extent should not automatically "
            "replace the full analysis extent because it represents a "
            "specific land-cover subset rather than necessarily the "
            "complete observation domain."
        ),
        (
            "Cloud obstruction represents areas where observation may "
            "have been compromised and must not automatically be "
            "classified as observed non-flood."
        ),
        (
            "The final validation domain should therefore be based on "
            "the valid UNOSAT analysis domain, with cloud-obstructed "
            "areas excluded where appropriate."
        ),
        (
            "Unobserved areas must remain NoData rather than being "
            "converted to non-flood observations."
        ),
        (
            "The flood extent should only be evaluated against the "
            "valid observation domain and the MCDA analysis footprint."
        ),
        (
            "This investigation does not yet establish statistical "
            "predictive validity. Statistical validation belongs to "
            "Phases 9.11.4 and 9.11.5."
        ),
    ]

    for item in report["scientific_interpretation"]:
        print(f"- {item}")

    # =========================================================================
    # 10. Final status
    # =========================================================================

    report["status"] = (
        "PHASE_9_11_3_OBSERVATION_DOMAIN_INVESTIGATION_COMPLETED"
    )

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            json_safe(report),
            file,
            indent=2,
            ensure_ascii=False,
        )

    print_header(
        "OBSERVATION DOMAIN INVESTIGATION COMPLETE"
    )

    print("Report:")
    print(f"  {REPORT_PATH}")

    print()
    print(
        "Original UNOSAT source files were not modified."
    )

    print()
    print(
        "No binary validation raster was created at this stage."
    )

    print()
    print(
        "PHASE_9_11_3_OBSERVATION_DOMAIN_INVESTIGATION_COMPLETED"
    )


if __name__ == "__main__":
    main()