# Phase 9.13.7 — Model Strengths and Limitations

## 1. Purpose

This document evaluates the strengths and limitations of the GeoAI Flood Risk Decision Agent developed for Nairobi County, Kenya. It synthesizes evidence from the multi-criteria decision analysis (MCDA), spatial diagnostics, sensitivity analysis, uncertainty assessment, and external validation against UNOSAT flood extent data from May 2024.

The purpose is to distinguish demonstrated technical capabilities from conclusions that the current evidence does not support. This assessment also identifies priorities for future model development.

## 2. Model Strengths

### 2.1 Reproducible geospatial processing workflow

The project implements a structured geospatial workflow that includes raster preprocessing, spatial alignment, factor preparation, MCDA computation, susceptibility classification, validation, and documentation.

The core analytical rasters share a consistent projected coordinate reference system, grid dimensions, spatial transform, and resolution. Validation scripts check input compatibility and numerical consistency.

**Evidence:** The MCDA output validation and UNOSAT raster compatibility checks passed. The reconstructed susceptibility surface differed from the baseline by a maximum absolute difference of approximately 2.99 × 10⁻⁸.

**Significance:** These checks support the technical reproducibility and numerical consistency of the implemented workflow. They do not, by themselves, demonstrate that the model accurately predicts flooding.

### 2.2 Integration of multiple spatial factors

The model combines five factors:

- Elevation
- Slope
- Distance to rivers
- Land cover
- Population

An Analytic Hierarchy Process (AHP) weighting scheme integrates these factors into a composite susceptibility surface.

The approximate weights are:

| Factor | Weight |
|---|---:|
| Distance to rivers | 0.4353 |
| Elevation | 0.1869 |
| Slope | 0.1869 |
| Land cover | 0.1286 |
| Population | 0.0624 |

**Significance:** The model combines terrain, hydrological proximity, land-cover characteristics, and a population-related factor within one spatial decision-support framework.

These weights represent the chosen MCDA weighting assumptions. They should not be interpreted as empirically proven causal effects or independently measured predictive feature importance.

### 2.3 Spatial interpretability

The continuous susceptibility raster and five classified susceptibility levels provide spatially explicit outputs that can be examined in GIS software.

The eight-neighbour spatial cohesion analysis reported an overall cohesion score of approximately 0.7167. The Very High class had a cohesion score of approximately 0.7951. The diagnostic classified the overall pattern as having minor fragmentation.

**Significance:** The model produces spatial structure that can be investigated and communicated, rather than only producing an opaque numerical result.

The five classes are quantile-based relative rankings. In particular, the Very High class represents the highest-ranking 20% of valid model scores; it does not represent an 80–100% probability of flooding.

### 2.4 Sensitivity and robustness assessment

The sensitivity analysis evaluated 11 scenarios: the baseline model and perturbations of factor weights by approximately ±10%.

The analysis showed that the model's response varied by factor. Increasing the river-distance weight by 10% produced approximately 79.77% same-class agreement with the baseline, while the slope and elevation perturbations produced approximately 95% and 92% agreement, respectively.

**Significance:** The analysis identifies which assumptions have the greatest influence on the resulting susceptibility classes. It shows that model stability is factor-dependent and that river-distance weighting deserves particular attention.

Robustness under these tested scenarios does not establish predictive accuracy. A stable model can consistently produce a ranking that does not match a particular observed flood event.

### 2.5 Independent reference-data comparison

The project incorporated UNOSAT flood extent information associated with satellite observations from 1 May 2024. The workflow prepared the reference geometry, accounted for the observation domain and cloud-obstruction information, aligned the data to the MCDA grid, and evaluated the overlapping observed cells.

The comparison identified an important mismatch: observed flood locations did not consistently correspond to higher model susceptibility scores.

**Significance:** The project goes beyond generating a susceptibility map. It tests the model against an external observation and reports the findings even when they do not support the expected relationship.

The reference product's metadata states that confidence was still to be evaluated and that field validation had not yet been completed. The validation results must therefore be interpreted in light of reference-data uncertainty.

### 2.6 Transparent scientific reporting

The project distinguishes technical correctness, internal model behaviour, external event-level agreement, and general predictive capability.

It documents the observed mismatch, uncertainty sources, validation-domain restrictions, and the limitations of interpreting statistical results from spatial data.

**Significance:** Transparent reporting makes the project more scientifically credible and provides a defensible basis for future improvements.

## 3. Model Limitations

### 3.1 External validation did not support the expected positive relationship

The UNOSAT comparison did not show increasing observed flood rates across the five susceptibility classes.

Observed flood rates were approximately:

| Susceptibility class | Observed flood rate |
|---|---:|
| Very Low | 4.13% |
| Low | 13.05% |
| Moderate | 11.72% |
| High | 10.22% |
| Very High | 4.19% |

The Very High class therefore did not have the highest observed flood rate in this validation sample.

The continuous susceptibility scores were also lower on average for observed flood cells than for observed non-flood cells. Spearman's rank correlation was approximately -0.1387, and the ROC AUC was approximately 0.3557, indicating reverse-direction discrimination in this particular reference sample.

**Implication:** The current model formulation did not demonstrate strong positive event-level discrimination against this UNOSAT reference. The results must not be presented as evidence of validated flood prediction.

They also do not establish that MCDA is universally unsuitable for flood susceptibility mapping. They describe the performance of this particular model, reference dataset, observation domain, and event comparison.

### 3.2 Limited temporal and event coverage

The external assessment uses one flood observation associated with May 2024. A single event cannot establish that the model will generalize to other storms, seasons, flood mechanisms, or future conditions.

The model inputs and reference observations may also represent different time periods and conditions.

**Implication:** Future evaluation should use additional independent flood events and suitable reference data, with input dates and event timing explicitly documented.

### 3.3 Incomplete observation coverage

The aligned validation grid contains 1,633,457 cells, while the valid UNOSAT observation domain contains 228,194 cells, approximately 13.97% of the full grid.

The validation domain is therefore a subset of the study grid rather than a complete observation of flood and non-flood conditions everywhere.

Coverage also differs between susceptibility classes. For example, the Very High class had approximately 84.69% observation coverage, while the Very Low class had approximately 0.22% coverage.

**Implication:** Results describe the observed portion of the study area. They cannot automatically be generalized to unobserved cells, and class comparisons may be affected by differences in where valid observations are available.

### 3.4 Preliminary reference-data status

The UNOSAT layer metadata identifies its confidence as “To be evaluated” and its field-validation status as “Not yet field validated.”

Satellite-derived flood extents can also be affected by acquisition timing, cloud obstruction, surface conditions, and the ability to distinguish inundated areas from other land-surface features.

**Implication:** The reference data provide useful external evidence but should not be treated as a complete, error-free representation of all flooding during the event.

### 3.5 Static representation of flood processes

The current MCDA combines spatial factors into a static susceptibility surface. It does not dynamically simulate rainfall, runoff generation, river discharge, drainage capacity, or the movement and depth of floodwater.

Consequently, it cannot represent the complete physical evolution of a flood event.

**Implication:** The current output is best understood as a relative spatial susceptibility assessment and decision-support layer, not as a hydrodynamic flood forecast.

### 3.6 AHP weighting assumptions

AHP provides a structured way to assign relative importance to factors, but the resulting weights depend on the selected criteria and the judgments used to compare them.

The dominance of distance to rivers in the current model is therefore a property of the implemented weighting scheme. It does not establish that river distance is the strongest empirical predictor under every flood mechanism or location.

**Implication:** Future work could compare alternative weighting strategies and evaluate them against independent observations. Any new weights should be justified and tested rather than adjusted solely to obtain a more favourable validation result.

### 3.7 Population is not a direct physical flood mechanism

Population contributes to the current composite score, but population density describes human presence or exposure rather than directly modelling the physical processes that produce inundation.

**Implication:** The role of population should remain explicit. Future work may distinguish physical flood susceptibility from population exposure and overall risk, depending on the intended decision-support use.

### 3.8 Statistical significance is not equivalent to predictive usefulness

The statistical evaluation found strong statistical evidence of differences and associations in the validation sample, but the direction of the observed relationships did not support the expected positive susceptibility–flood relationship. The categorical association, measured by Cramér's V, was approximately 0.1308.

Spatial cells may also be spatially dependent, meaning that neighbouring observations are not necessarily independent. Conventional statistical tests can overstate the amount of independent evidence when spatial dependence is not accounted for.

**Implication:** Statistical significance must be interpreted alongside effect size, relationship direction, sampling design, spatial dependence, reference-data quality, and the intended predictive task.

### 3.9 No calibrated flood probability

The continuous MCDA score is a weighted combination of standardized or otherwise prepared factor values. It is not calibrated against observed flood frequencies to estimate the probability that a location will flood.

**Implication:** Scores must not be communicated as flood probabilities, annual probabilities, or return-period estimates.

## 4. Priorities for Future Development

The findings suggest the following priorities:

1. **Improve independent validation:** Assess additional flood events and obtain suitable, documented reference observations.
2. **Investigate the observed mismatch:** Examine the study area's flood mechanisms, event timing, reference coverage, factor transformations, and model assumptions before changing the model.
3. **Evaluate alternative weighting approaches:** Compare defensible alternatives using a predefined validation strategy and report all outcomes.
4. **Incorporate dynamic information:** Where reliable data are available, explore rainfall, antecedent wetness, river discharge, drainage characteristics, and other relevant physical variables.
5. **Separate susceptibility, hazard, exposure, and risk:** Keep the physical likelihood of inundation conceptually distinct from the people and assets that may be affected.
6. **Quantify uncertainty more comprehensively:** Consider reference-data uncertainty, spatial dependence, alternative model specifications, and validation across multiple events.
7. **Consider probability calibration only when appropriate data are available:** Probability claims would require suitable observations and independent calibration and evaluation, not merely rescaling the current MCDA scores.

These are future research directions, not claims that the current model already implements these capabilities.

## 5. Overall Assessment

The GeoAI Flood Risk Decision Agent demonstrates a structured and reproducible geospatial analysis workflow, interpretable factor integration, spatial diagnostics, sensitivity testing, and transparent external validation.

Its engineering and analytical strengths should be distinguished from its predictive evidence. The UNOSAT comparison did not demonstrate the expected positive relationship between susceptibility scores and observed flooding for the evaluated event. The available evidence therefore does not justify describing the current model as a validated or generalizable flood predictor.

The most defensible current description is:

**An exploratory, AHP-weighted MCDA framework for relative flood-susceptibility mapping and spatial decision support in Nairobi County, with documented sensitivity analysis and external validation that identifies important limitations requiring further investigation.**

The model and its existing weights remain unchanged as part of this assessment. The negative validation result is retained as evidence to guide future development rather than being removed by tuning the model to fit the reference event.

## 6. Phase 9.13.7 Completion Criteria

This assessment is complete when:

- The strengths are linked to specific analytical or technical evidence.
- Limitations are stated explicitly and without exaggeration.
- Internal robustness is not confused with external predictive validity.
- The UNOSAT mismatch and reference-data uncertainty are acknowledged.
- Future improvements are presented as proposals rather than existing capabilities.
- No model parameters or validation results are altered to improve the narrative.

**Status:** Documentation drafted. Save this document in the project and verify it against the existing results before treating it as finalized.
