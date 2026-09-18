"""
Phase 9.10 - Uncertainty and Limitations Assessment

GeoAI Flood Risk Decision Agent
Nairobi County, Kenya

Purpose
-------
This script creates a reproducible, structured assessment of the major
uncertainty sources and limitations associated with the flood susceptibility
model developed in Phases 1-9.

The assessment distinguishes between:

1. Input-data uncertainty
2. Spatial-resolution uncertainty
3. Temporal consistency
4. Standardization assumptions
5. AHP/MCDA weight uncertainty
6. Classification uncertainty
7. Population/exposure interpretation
8. External validation status
9. Model-scope limitations
10. Implementation versus model uncertainty

Important
---------
This script does NOT calculate artificial confidence intervals or claim
statistical uncertainty that the available data cannot support.

The Phase 9.9 +/-10% weight perturbation experiments are treated as
sensitivity analysis, not as confidence intervals.

Outputs
-------
results/phase9_validation/uncertainty_limitations/
    uncertainty_limitations.csv
    uncertainty_limitations.json
"""

from pathlib import Path
import json
from datetime import datetime

import pandas as pd


# ---------------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "uncertainty_limitations"
)

SENSITIVITY_RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "phase9_validation"
    / "sensitivity_robustness"
)

SENSITIVITY_CSV = (
    SENSITIVITY_RESULTS_DIR
    / "sensitivity_scenario_summary.csv"
)


# ---------------------------------------------------------------------------
# DOCUMENTED PROJECT FACTS
# ---------------------------------------------------------------------------

REFERENCE_CRS = "EPSG:32737"

GRID_WIDTH = 1603
GRID_HEIGHT = 1019

PIXEL_SIZE_METERS = 30.86551681907227
PIXEL_AREA_M2 = 952.6801

VALID_CELLS = 553860
TOTAL_GRID_CELLS = 1633457

AHP_WEIGHTS = {
    "elevation": 0.1868744589,
    "slope": 0.1868744589,
    "distance_to_rivers": 0.4352900433,
    "landcover": 0.1285887446,
    "population": 0.0623722944,
}

AHP_CONSISTENCY_RATIO = 0.0269475117

NO_DATA_CONTINUOUS = -9999
NO_DATA_CLASSIFIED = 0

CLASSIFICATION_METHOD = "Quantile classification"

NUMBER_OF_CLASSES = 5

CLASS_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High",
}


# ---------------------------------------------------------------------------
# OUTPUT SETUP
# ---------------------------------------------------------------------------

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def check_file_exists(path):
    """Return a simple file-status description."""
    if path.exists():
        return f"Available: {path}"
    return f"Not available: {path}"


def load_sensitivity_evidence():
    """
    Read the Phase 9.9 sensitivity output when available.

    The uncertainty assessment should remain usable even if the sensitivity
    CSV is unavailable. Therefore, failure to read the file does not stop
    the assessment.
    """

    evidence = {
        "file_exists": SENSITIVITY_CSV.exists(),
        "rows": None,
        "columns": [],
    }

    if not SENSITIVITY_CSV.exists():
        return evidence

    try:
        df = pd.read_csv(SENSITIVITY_CSV)

        evidence["rows"] = len(df)
        evidence["columns"] = df.columns.tolist()

        # Try to identify useful sensitivity fields without assuming
        # exact column naming.
        lower_columns = {
            str(column).lower(): column
            for column in df.columns
        }

        def find_column(possible_names):
            for name in possible_names:
                if name in lower_columns:
                    return lower_columns[name]

            for lower_name, original_name in lower_columns.items():
                for name in possible_names:
                    if name in lower_name:
                        return original_name

            return None

        spearman_col = find_column(
            [
                "spearman_correlation",
                "spearman",
                "correlation",
            ]
        )

        mad_col = find_column(
            [
                "mean_absolute_difference",
                "mean_absolute_diff",
                "mad",
            ]
        )

        stability_col = find_column(
            [
                "same_class_percentage",
                "same_class_percent",
                "class_stability",
            ]
        )

        retention_col = find_column(
            [
                "high_very_high_retention_percentage",
                "high_very_high_retention_percent",
                "high_very_high_retention",
            ]
        )

        if spearman_col is not None:
            values = pd.to_numeric(
                df[spearman_col],
                errors="coerce"
            ).dropna()

            if len(values) > 0:
                evidence["minimum_spearman"] = float(values.min())
                evidence["maximum_spearman"] = float(values.max())

        if mad_col is not None:
            values = pd.to_numeric(
                df[mad_col],
                errors="coerce"
            ).dropna()

            if len(values) > 0:
                evidence["maximum_mean_absolute_difference"] = float(
                    values.max()
                )

        if stability_col is not None:
            values = pd.to_numeric(
                df[stability_col],
                errors="coerce"
            ).dropna()

            if len(values) > 0:
                evidence["minimum_same_class_percentage"] = float(
                    values.min()
                )

        if retention_col is not None:
            values = pd.to_numeric(
                df[retention_col],
                errors="coerce"
            ).dropna()

            if len(values) > 0:
                evidence["minimum_high_very_high_retention"] = float(
                    values.min()
                )

    except Exception as exc:
        evidence["read_error"] = str(exc)

    return evidence


# ---------------------------------------------------------------------------
# PHASE 9.9 SENSITIVITY EVIDENCE
# ---------------------------------------------------------------------------

sensitivity_evidence = load_sensitivity_evidence()


# ---------------------------------------------------------------------------
# UNCERTAINTY AND LIMITATION ASSESSMENT
# ---------------------------------------------------------------------------

assessments = [
    {
        "category": "Input data",
        "uncertainty_source": "Source-data accuracy, resolution, completeness, and thematic accuracy",
        "why_it_matters": (
            "Errors or limitations in the DEM, river network, land-cover data, "
            "population data, boundary data, or derived layers can propagate "
            "into the final susceptibility surface."
        ),
        "current_evidence_or_mitigation": (
            "Input datasets were validated during the earlier project phases. "
            "Coordinate reference systems, raster dimensions, spatial properties, "
            "and derived processing steps were checked before MCDA integration."
        ),
        "remaining_limitation": (
            "Source datasets still contain their own positional, thematic, "
            "measurement, classification, and completeness uncertainties."
        ),
        "recommended_future_improvement": (
            "Use higher-accuracy or locally validated datasets where available, "
            "and document source uncertainty and acquisition dates explicitly."
        ),
        "assessment_status": "Partially constrained",
    },
    {
        "category": "Spatial resolution",
        "uncertainty_source": (
            f"Final analysis grid resolution of approximately "
            f"{PIXEL_SIZE_METERS:.2f} m"
        ),
        "why_it_matters": (
            "Features smaller than a raster cell or processes occurring below "
            "the grid resolution may not be represented explicitly."
        ),
        "current_evidence_or_mitigation": (
            f"The final MCDA grid is spatially aligned in {REFERENCE_CRS} "
            f"with {GRID_WIDTH} x {GRID_HEIGHT} cells and approximately "
            f"{PIXEL_SIZE_METERS:.2f} m cell size."
        ),
        "remaining_limitation": (
            "Sub-cell drainage structures, culverts, small channels, buildings, "
            "roads, and local surface-flow barriers may not be resolved."
        ),
        "recommended_future_improvement": (
            "Incorporate higher-resolution terrain, drainage infrastructure, "
            "building footprints, road drainage, and local hydrological data."
        ),
        "assessment_status": "Documented limitation",
    },
    {
        "category": "Temporal consistency",
        "uncertainty_source": (
            "Input datasets may represent different acquisition or reference periods"
        ),
        "why_it_matters": (
            "Land cover, population, drainage networks, and terrain-related "
            "conditions can change over time. Combining datasets from different "
            "periods may not represent one synchronized environmental snapshot."
        ),
        "current_evidence_or_mitigation": (
            "Input sources and preprocessing stages were documented during "
            "the data acquisition and preparation phases."
        ),
        "remaining_limitation": (
            "The current model does not guarantee that all input layers represent "
            "the same date or flood-event period."
        ),
        "recommended_future_improvement": (
            "Use temporally harmonized datasets and explicitly associate the "
            "susceptibility analysis with a defined reference period."
        ),
        "assessment_status": "Partially constrained",
    },
    {
        "category": "Standardization",
        "uncertainty_source": (
            "Transformation of raw factors into standardized 0-1 susceptibility scores"
        ),
        "why_it_matters": (
            "The mathematical transformation determines how differences in "
            "elevation, slope, river distance, land cover, and population "
            "translate into comparable MCDA scores."
        ),
        "current_evidence_or_mitigation": (
            "Factor direction and standardized 0-1 ranges were validated before "
            "MCDA integration. Higher standardized values were defined to represent "
            "greater susceptibility contribution."
        ),
        "remaining_limitation": (
            "Alternative standardization functions, thresholds, or transformation "
            "assumptions could produce different susceptibility surfaces."
        ),
        "recommended_future_improvement": (
            "Compare alternative theoretically justified standardization "
            "functions using independent flood observations."
        ),
        "assessment_status": "Model assumption",
    },
    {
        "category": "AHP/MCDA weights",
        "uncertainty_source": (
            "AHP-derived factor weights represent modelling assumptions rather "
            "than physical constants"
        ),
        "why_it_matters": (
            "Changing factor weights changes the relative influence of the "
            "five susceptibility factors in the final MCDA surface."
        ),
        "current_evidence_or_mitigation": (
            f"The documented AHP consistency ratio is approximately "
            f"{AHP_CONSISTENCY_RATIO:.4f}. Phase 9.9 also tested one-factor-at-a-time "
            "±10% weight perturbations while preserving a normalized weight sum."
        ),
        "remaining_limitation": (
            "Other defensible weight sets may produce somewhat different "
            "continuous values and categorical class assignments."
        ),
        "recommended_future_improvement": (
            "Use additional expert elicitation, empirical calibration, or "
            "independent flood observations to evaluate alternative weighting schemes."
        ),
        "assessment_status": "Sensitivity assessed",
    },
    {
        "category": "Classification",
        "uncertainty_source": (
            "Relative quantile classification into five susceptibility classes"
        ),
        "why_it_matters": (
            "Quantile thresholds divide the valid susceptibility surface into "
            "relative groups. They do not represent absolute flood probabilities."
        ),
        "current_evidence_or_mitigation": (
            "The five-class classification was independently checked against "
            "the continuous susceptibility raster. Each class contains 20% of "
            "the valid MCDA cells as expected for the selected quantile method."
        ),
        "remaining_limitation": (
            "Class boundaries are relative to the current study area and can "
            "change when the study extent, data, or classification method changes."
        ),
        "recommended_future_improvement": (
            "Evaluate empirically derived or hazard-based thresholds using "
            "independent observed flood data."
        ),
        "assessment_status": "Documented limitation",
    },
    {
        "category": "Population/exposure",
        "uncertainty_source": (
            "Population is an exposure-related factor rather than a direct "
            "physical flood-generation mechanism"
        ),
        "why_it_matters": (
            "Population can identify areas where flood susceptibility may affect "
            "more people, but population density itself does not physically cause flooding."
        ),
        "current_evidence_or_mitigation": (
            "Phase 9.7 separately evaluated the relationship between the "
            "population score and the final susceptibility surface."
        ),
        "remaining_limitation": (
            "The population layer should not be interpreted as direct evidence "
            "of hydrological flood generation."
        ),
        "recommended_future_improvement": (
            "Extend the decision-support framework to report physical "
            "susceptibility and exposure as distinguishable dimensions."
        ),
        "assessment_status": "Interpretation constraint",
    },
    {
        "category": "External validation",
        "uncertainty_source": (
            "Independent observed historical flood locations have not yet been "
            "used to validate the susceptibility classes"
        ),
        "why_it_matters": (
            "Internal consistency demonstrates that the model behaves according "
            "to its formulation, but it does not establish whether high-susceptibility "
            "areas correspond to observed real-world flooding."
        ),
        "current_evidence_or_mitigation": (
            "Phases 9.2-9.9 provide internal validation, spatial relationship "
            "analysis, factor influence analysis, reconstruction checks, and "
            "sensitivity testing."
        ),
        "remaining_limitation": (
            "Predictive or external validity against independently observed "
            "historical flood events remains untested at this stage."
        ),
        "recommended_future_improvement": (
            "Phase 9.11 will obtain an independent historical flood inventory "
            "or flood-extent dataset and quantitatively compare observed flooding "
            "with the continuous susceptibility surface and susceptibility classes."
        ),
        "assessment_status": "Pending external validation",
    },
    {
        "category": "Model scope",
        "uncertainty_source": "Flood susceptibility model scope",
        "why_it_matters": (
            "The MCDA output represents relative spatial susceptibility. It is "
            "not a hydraulic simulation, flood-depth model, flood-forecasting system, "
            "or direct probability-of-flooding estimate."
        ),
        "current_evidence_or_mitigation": (
            "The model formulation, factor definitions, standardization, weighting, "
            "classification, and validation procedures are documented."
        ),
        "remaining_limitation": (
            "The current model does not estimate flood depth, velocity, arrival time, "
            "duration, discharge, or event-specific inundation extent."
        ),
        "recommended_future_improvement": (
            "Integrate hydrological and hydraulic modelling where event-specific "
            "flood extent, depth, or flow information is required."
        ),
        "assessment_status": "Scope limitation",
    },
    {
        "category": "Implementation versus model uncertainty",
        "uncertainty_source": (
            "Correct implementation does not guarantee that the modelling formulation "
            "fully represents real-world flooding"
        ),
        "why_it_matters": (
            "A software implementation can accurately reproduce the mathematical "
            "formulation while the formulation itself remains subject to assumptions "
            "and empirical uncertainty."
        ),
        "current_evidence_or_mitigation": (
            "Phase 9.8 independently reconstructed the MCDA susceptibility surface. "
            "Phase 9.9 also reproduced the baseline surface before sensitivity testing."
        ),
        "remaining_limitation": (
            "Implementation validation cannot substitute for comparison with "
            "independent observations of actual flooding."
        ),
        "recommended_future_improvement": (
            "Combine implementation validation with Phase 9.11 external validation "
            "against independent historical flood observations."
        ),
        "assessment_status": "Important distinction documented",
    },
]


# ---------------------------------------------------------------------------
# ADD PROJECT-LEVEL METADATA
# ---------------------------------------------------------------------------

metadata = {
    "project": "GeoAI Flood Risk Decision Agent",
    "study_area": "Nairobi County, Kenya",
    "phase": "Phase 9.10 - Uncertainty and Limitations",
    "reference_crs": REFERENCE_CRS,
    "grid_width": GRID_WIDTH,
    "grid_height": GRID_HEIGHT,
    "pixel_size_m": PIXEL_SIZE_METERS,
    "pixel_area_m2": PIXEL_AREA_M2,
    "total_grid_cells": TOTAL_GRID_CELLS,
    "valid_mcda_cells": VALID_CELLS,
    "classification_method": CLASSIFICATION_METHOD,
    "number_of_classes": NUMBER_OF_CLASSES,
    "class_names": CLASS_NAMES,
    "nodata_continuous": NO_DATA_CONTINUOUS,
    "nodata_classified": NO_DATA_CLASSIFIED,
    "ahp_weights": AHP_WEIGHTS,
    "ahp_weight_sum": sum(AHP_WEIGHTS.values()),
    "ahp_consistency_ratio": AHP_CONSISTENCY_RATIO,
    "external_validation_status": (
        "Not yet performed; planned as Phase 9.11"
    ),
    "generated_at": datetime.now().isoformat(timespec="seconds"),
}


# ---------------------------------------------------------------------------
# ADD SENSITIVITY EVIDENCE TO METADATA
# ---------------------------------------------------------------------------

metadata["phase_9_9_sensitivity_evidence"] = sensitivity_evidence


# ---------------------------------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------------------------------

df = pd.DataFrame(assessments)


# ---------------------------------------------------------------------------
# SAVE CSV
# ---------------------------------------------------------------------------

csv_path = RESULTS_DIR / "uncertainty_limitations.csv"

df.to_csv(
    csv_path,
    index=False,
    encoding="utf-8"
)


# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------

json_path = RESULTS_DIR / "uncertainty_limitations.json"

json_output = {
    "metadata": metadata,
    "assessments": assessments,
}

with open(
    json_path,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        json_output,
        file,
        indent=4,
        ensure_ascii=False
    )


# ---------------------------------------------------------------------------
# TERMINAL SUMMARY
# ---------------------------------------------------------------------------

print("=" * 72)
print("PHASE 9.10 - UNCERTAINTY AND LIMITATIONS ASSESSMENT")
print("GeoAI Flood Risk Decision Agent")
print("=" * 72)

print("\nPROJECT")
print("-" * 72)
print(f"Study area: {metadata['study_area']}")
print(f"Reference CRS: {REFERENCE_CRS}")
print(
    f"Analysis grid: "
    f"{GRID_WIDTH} x {GRID_HEIGHT} cells"
)
print(
    f"Pixel size: "
    f"{PIXEL_SIZE_METERS:.6f} m"
)
print(
    f"Valid MCDA cells: "
    f"{VALID_CELLS:,}"
)

print("\nMCDA")
print("-" * 72)
print("AHP weights:")

for factor, weight in AHP_WEIGHTS.items():
    print(f"  {factor}: {weight:.10f}")

print(
    f"Weight sum: "
    f"{sum(AHP_WEIGHTS.values()):.10f}"
)

print(
    f"AHP consistency ratio: "
    f"{AHP_CONSISTENCY_RATIO:.10f}"
)

print("\nCLASSIFICATION")
print("-" * 72)
print(f"Method: {CLASSIFICATION_METHOD}")
print(f"Number of classes: {NUMBER_OF_CLASSES}")

for class_id, class_name in CLASS_NAMES.items():
    print(f"  {class_id}: {class_name}")

print("\nSENSITIVITY EVIDENCE")
print("-" * 72)

if sensitivity_evidence["file_exists"]:
    print(
        "Phase 9.9 sensitivity output found:"
    )
    print(
        f"  {SENSITIVITY_CSV}"
    )

    if sensitivity_evidence.get("rows") is not None:
        print(
            f"  Scenario rows: "
            f"{sensitivity_evidence['rows']}"
        )

    if "minimum_spearman" in sensitivity_evidence:
        print(
            f"  Minimum Spearman correlation: "
            f"{sensitivity_evidence['minimum_spearman']:.6f}"
        )

    if "maximum_mean_absolute_difference" in sensitivity_evidence:
        print(
            f"  Maximum mean absolute difference: "
            f"{sensitivity_evidence['maximum_mean_absolute_difference']:.6f}"
        )

    if "minimum_same_class_percentage" in sensitivity_evidence:
        print(
            f"  Minimum same-class percentage: "
            f"{sensitivity_evidence['minimum_same_class_percentage']:.3f}%"
        )

    if "minimum_high_very_high_retention" in sensitivity_evidence:
        print(
            f"  Minimum High + Very High retention: "
            f"{sensitivity_evidence['minimum_high_very_high_retention']:.3f}%"
        )

else:
    print(
        "Phase 9.9 sensitivity CSV was not found."
    )

print("\nUNCERTAINTY CATEGORIES")
print("-" * 72)

for index, row in df.iterrows():
    print(
        f"{index + 1:02d}. "
        f"{row['category']} - "
        f"{row['assessment_status']}"
    )

print("\nOUTPUTS")
print("-" * 72)
print(f"CSV : {csv_path}")
print(f"JSON: {json_path}")

print("\nVALIDATION")
print("-" * 72)

if csv_path.exists():
    print("CSV output exists: PASS")
else:
    print("CSV output exists: FAIL")

if json_path.exists():
    print("JSON output exists: PASS")
else:
    print("JSON output exists: FAIL")

if len(df) == len(assessments):
    print("Assessment record count: PASS")
else:
    print("Assessment record count: FAIL")

print("\nIMPORTANT")
print("-" * 72)
print(
    "External validation against independent historical flood observations "
    "has NOT yet been performed."
)
print(
    "It is formally planned as Phase 9.11."
)

print("\nPHASE STATUS")
print("-" * 72)
print("PHASE_9_10_UNCERTAINTY_LIMITATIONS_COMPLETED")
print("=" * 72)