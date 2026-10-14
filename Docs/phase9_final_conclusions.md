# Phase 9 — Final Conclusions

## 1. Overview

Phase 9 evaluated the spatial behaviour, factor influence, robustness, uncertainty, and external validation of the GeoAI Flood Risk Decision Agent developed for Nairobi County, Kenya.

The objective was to move beyond generating a flood susceptibility map and systematically examine how the model behaves, how sensitive its outputs are to its assumptions, and whether an independent flood reference supports its expected interpretation.

The assessment combined internal spatial diagnostics, sensitivity experiments, uncertainty analysis, and comparison against UNOSAT flood extent information associated with satellite observations from 1 May 2024.

The conclusions below reflect the evidence produced during Phase 9. They do not assume that a technically functioning model is necessarily an accurate flood predictor.

## 2. Technical and Computational Findings

The MCDA workflow successfully generated a continuous susceptibility surface and a five-class susceptibility raster.

The principal analytical rasters use a common projected coordinate reference system, EPSG:32737, and a consistent grid of 1,603 columns by 1,019 rows, with a pixel resolution of approximately 30.87 metres.

The continuous susceptibility raster contains 553,860 valid cells.

Computational validation confirmed the consistency of the principal outputs and their spatial alignment. The sensitivity workflow also reconstructed the baseline susceptibility surface with a maximum absolute difference of approximately 2.99 × 10⁻⁸.

These findings support the technical consistency and reproducibility of the implemented workflow. They do not independently establish that the model's susceptibility scores correspond to real-world flood occurrence.

## 3. Spatial Patterns and Susceptibility Classification

The model generated five relative susceptibility classes: Very Low, Low, Moderate, High, and Very High.

Each class contains 20% of the valid classified cells because the classification uses quantile thresholds.

The overall eight-neighbour spatial cohesion score was approximately 0.7167, and the Very High class had a cohesion score of approximately 0.7951. The spatial-pattern diagnostic identified minor fragmentation.

These results indicate that the model produces a spatially structured surface rather than a wholly fragmented distribution of susceptibility scores.

However, the classes are relative rankings within the modelled study area. The Very High class represents the upper 20% of valid model scores, not an 80–100% probability of flooding. Class membership should therefore not be interpreted as a calibrated estimate of flood probability.

## 4. Factor Influence

The AHP-weighted MCDA combines five factors: elevation, slope, distance to rivers, land cover, and population.

Distance to rivers has the greatest assigned weight, approximately 0.4353. Elevation and slope each have weights of approximately 0.1869, land cover approximately 0.1286, and population approximately 0.0624.

The sensitivity analysis showed that changing factor weights can alter susceptibility classifications. A 10% increase in the distance-to-rivers weight produced approximately 79.77% same-class agreement with the baseline, compared with approximately 95% for the slope perturbation and 92% for the elevation perturbation.

This indicates that the model's outputs are particularly sensitive to the river-distance weighting assumption among the reported scenarios.

These weights express the selected MCDA assumptions. They should not be treated as empirical proof of causal influence or as independently measured predictive feature importance.

Population also requires a distinct interpretation: it represents a population-related exposure consideration, not a direct physical mechanism that causes floodwater to occur.

## 5. External Validation Findings

The model was compared against prepared UNOSAT flood extent observations associated with 1 May 2024.

The validation workflow established technical compatibility between the model rasters and the prepared reference raster. The valid observation domain contained 228,194 cells, approximately 13.97% of the full raster grid. Within that observed domain, 19,201 cells were classified as flood and 208,993 as non-flood, giving an observed flood rate of approximately 8.41%.

The observed flood rates did not increase consistently with susceptibility class:

- Very Low: approximately 4.13%
- Low: approximately 13.05%
- Moderate: approximately 11.72%
- High: approximately 10.22%
- Very High: approximately 4.19%

The combined High and Very High classes contained approximately 48.87% of the observed flood cells while accounting for approximately 64.50% of the observed validation domain.

The continuous susceptibility scores were also lower on average in observed flood cells than in observed non-flood cells. The mean difference was approximately -0.022566, and Spearman's rank correlation was approximately -0.138730. The ROC AUC was approximately 0.355737, indicating reverse-direction discrimination in this particular reference sample.

Taken together, these findings do not support the expected positive relationship between the current susceptibility ranking and observed flooding in this validation sample.

This is a material limitation of the current model formulation. It must not be obscured by the successful technical processing or the favourable internal spatial diagnostics.

## 6. Interpretation of the Validation Outcome

The external validation findings do not establish that the MCDA approach is universally unsuitable for flood susceptibility assessment. They show that the current factor selection, transformations, weighting assumptions, study-area representation, and reference comparison did not demonstrate the expected positive event-level relationship.

Several considerations limit the conclusions that can be drawn:

1. The assessment uses one event and cannot establish generalization to other floods.
2. The observation domain covers only a subset of the full model grid and varies in coverage across susceptibility classes.
3. The UNOSAT reference metadata states that confidence was to be evaluated and that field validation had not yet been completed.
4. The model represents static spatial factors rather than dynamically simulating rainfall, runoff, river discharge, and inundation.
5. Spatial dependence between neighbouring cells may affect the interpretation of conventional statistical significance tests.

These considerations provide reasons for further investigation, but they do not erase the observed mismatch or justify claiming that the model has been validated as a predictor.

## 7. Overall Assessment of Model Capability

The evidence supports the following assessment:

**Technical implementation:** The principal geospatial processing, raster compatibility, and numerical consistency checks passed.

**Internal spatial behaviour:** The model generates a structured and interpretable relative susceptibility surface.

**Sensitivity and robustness:** The tested perturbations provide useful evidence about the stability of classifications and the influence of selected weighting assumptions. Sensitivity varies by factor.

**External event-level predictive evidence:** The UNOSAT comparison did not support the expected positive susceptibility–flood relationship for the evaluated event.

**Generalization and probability calibration:** These have not been established. The current scores are not calibrated flood probabilities and should not be presented as such.

## 8. Recommended Future Direction

The next stage should build on the existing analytical foundation while addressing the limitations identified in Phase 9.

Priorities include:

- Investigating the negative-direction external validation findings without tuning the current model merely to improve one event's results.
- Obtaining additional independent flood reference datasets and evaluating multiple events where suitable data are available.
- Examining the physical and temporal processes that may explain differences between static susceptibility and observed inundation.
- Exploring defensible alternative factor representations and weighting strategies through a transparent evaluation process.
- Considering rainfall, antecedent wetness, river discharge, drainage characteristics, and other relevant dynamic or physical variables where reliable data are available.
- Distinguishing physical flood susceptibility, flood hazard, population exposure, and overall risk.
- Developing probability estimates only if appropriate calibration data and independent evaluation support that interpretation.

These are proposed future improvements, not capabilities already demonstrated by the current model.

## 9. Final Conclusion

Phase 9 established an evidence-based understanding of the GeoAI Flood Risk Decision Agent's technical behaviour, spatial structure, factor weighting, sensitivity, uncertainty, and external validation performance.

The project demonstrates a structured and reproducible geospatial MCDA workflow, with interpretable outputs and transparent analytical checks. It also demonstrates the importance of external validation: a model can produce technically consistent and spatially coherent outputs without those outputs necessarily matching observed flood occurrence.

The UNOSAT comparison identified a substantial mismatch between the expected susceptibility ranking and the observed flood pattern for the evaluated event. Accordingly, the current model should not be described as a validated, calibrated, or generalizable flood prediction system.

The most defensible description is:

**An exploratory, AHP-weighted MCDA framework for relative flood-susceptibility mapping and spatial decision support in Nairobi County, with documented internal diagnostics, sensitivity analysis, uncertainty assessment, and external validation findings that identify priorities for further development.**

The current model is retained without changes to its factor weights, classification thresholds, or validation outcomes. Phase 9 provides the evidence base for deciding how to improve the project responsibly in Phase 10 and beyond.

## 10. Phase 9 Completion Conditions

Phase 9 can be formally closed after:

- The Phase 9 synthesis documents have been saved and reviewed.
- The final conclusions agree with the recorded analytical outputs.
- The model strengths, limitations, and external validation findings are documented.
- The README is updated to reflect the completed project stages and actual evidence.
- Relevant methodology and dataset documentation is reconciled with the final project state.
- Source code and documentation changes are reviewed before committing, with generated `results/` files excluded from the Git commit unless explicitly intended otherwise.

**Status:** Final conclusions drafted. Verify the document against the existing project outputs before formal closure of Phase 9.
