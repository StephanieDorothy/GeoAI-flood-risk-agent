from src.interpreter.input_loader import load_model_inputs
from src.interpreter.cell_selector import select_raster_cell
from src.interpreter.factor_evidence import extract_factor_evidence
from src.interpreter.weighted_contributions import calculate_weighted_contributions

# Load validated production data.
inputs = load_model_inputs()

# Select the same real production cell.
selection = select_raster_cell(
    model_inputs=inputs,
    row=509,
    column=801,
)

# Extract the five factor scores.
evidence = extract_factor_evidence(
    model_inputs=inputs,
    selection=selection,
)

# Calculate individual weighted contributions.
result = calculate_weighted_contributions(
    model_inputs=inputs,
    evidence=evidence,
)

print("\n--- REAL PRODUCTION WEIGHTED CONTRIBUTIONS ---")
print(f"Cell: row {result.row}, column {result.column}")
print(f"Stored susceptibility score: {result.susceptibility_score:.8f}")

print("\n{:<22} {:>12} {:>12} {:>16}".format(
    "FACTOR", "SCORE", "AHP WEIGHT", "CONTRIBUTION"
))

for factor, item in result.factor_contributions.items():
    print("{:<22} {:>12.8f} {:>12.8f} {:>16.8f}".format(
        factor,
        item.factor_score,
        item.weight,
        item.weighted_contribution,
    ))

print("\nWeighted contribution calculation: PASS")
