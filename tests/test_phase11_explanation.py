from pprint import pprint

from src.interpreter.input_loader import load_model_inputs
from src.interpreter.cell_selector import select_raster_cell
from src.interpreter.factor_evidence import extract_factor_evidence
from src.interpreter.weighted_contributions import calculate_weighted_contributions
from src.interpreter.score_verification import verify_susceptibility_score
from src.interpreter.explanation_generator import generate_deterministic_explanation

# 1. Load production data.
inputs = load_model_inputs()

# 2. Select the same production cell.
selection = select_raster_cell(
    model_inputs=inputs,
    row=509,
    column=801,
)

# 3. Extract actual factor evidence.
evidence = extract_factor_evidence(
    model_inputs=inputs,
    selection=selection,
)

# 4. Calculate weighted contributions.
contributions = calculate_weighted_contributions(
    model_inputs=inputs,
    evidence=evidence,
)

# 5. Verify the reconstructed score.
verification = verify_susceptibility_score(contributions)

# 6. Generate the deterministic explanation.
explanation = generate_deterministic_explanation(
    contributions=contributions,
    verification=verification,
)

# 7. Validate important expected outputs.
assert explanation["location"]["row"] == 509
assert explanation["location"]["column"] == 801
assert explanation["susceptibility"]["verification_status"] == "PASS"
assert explanation["susceptibility"]["verification_passed"] is True

ranking = explanation["contribution_ranking"]
assert ranking is not None
assert ranking[0]["factor"] == "distance_to_rivers"
assert explanation["interpretation"]["dominant_factor"] == "distance_to_rivers"

assert len(explanation["factor_evidence"]) == 5
assert len(explanation["limitations"]) >= 1

print("\n--- REAL PRODUCTION CELL EXPLANATION ---")

print("\nLOCATION")
pprint(explanation["location"])

print("\nSUSCEPTIBILITY VERIFICATION")
pprint(explanation["susceptibility"])

print("\nCONTRIBUTION RANKING")
for item in ranking:
    print(
        f"Rank {item['rank']}: {item['label']} | "
        f"Contribution: {item['weighted_contribution']:.8f} | "
        f"Type: {item['factor_type']}"
    )

print("\nOVERALL INTERPRETATION")
print(explanation["interpretation"]["overall"])

print("\nPOPULATION EXPOSURE NOTE")
print(explanation["interpretation"]["population_exposure_note"])

print("\nSCIENTIFIC LIMITATIONS")
for number, limitation in enumerate(explanation["limitations"], start=1):
    print(f"{number}. {limitation}")

print("\nDeterministic explanation generation: PASS")
