from src.interpreter.input_loader import load_model_inputs
from src.interpreter.cell_selector import select_raster_cell
from src.interpreter.factor_evidence import extract_factor_evidence
from src.interpreter.weighted_contributions import calculate_weighted_contributions
from src.interpreter.score_verification import verify_susceptibility_score

# Load validated production data.
inputs = load_model_inputs()

# Select the production cell.
selection = select_raster_cell(
    model_inputs=inputs,
    row=509,
    column=801,
)

# Extract factor evidence.
evidence = extract_factor_evidence(
    model_inputs=inputs,
    selection=selection,
)

# Calculate individual weighted contributions.
contributions = calculate_weighted_contributions(
    model_inputs=inputs,
    evidence=evidence,
)

# Reconstruct and verify the stored susceptibility score.
verification = verify_susceptibility_score(contributions)

print("\n--- REAL PRODUCTION SCORE VERIFICATION ---")
print(f"Cell: row {verification.row}, column {verification.column}")
print(f"CRS: {verification.crs}")
print(f"Stored score:        {verification.stored_score:.10f}")
print(f"Reconstructed score: {verification.reconstructed_score:.10f}")
print(f"Absolute difference: {verification.absolute_difference:.12f}")
print(f"Accepted tolerance:  {verification.tolerance:.12f}")
print(f"Verification passed: {verification.verification_passed}")

assert verification.verification_passed, (
    "The reconstructed score does not match the stored score "
    "within the accepted tolerance."
)

print("\nProduction score reconstruction: PASS")
