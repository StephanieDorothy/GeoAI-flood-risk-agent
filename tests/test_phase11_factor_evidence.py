from src.interpreter.input_loader import load_model_inputs
from src.interpreter.cell_selector import select_raster_cell
from src.interpreter.factor_evidence import extract_factor_evidence

# Load validated production data.
inputs = load_model_inputs()

# Re-select yesterday's production cell.
selection = select_raster_cell(
    model_inputs=inputs,
    row=509,
    column=801,
)

# Extract the five factor values.
evidence = extract_factor_evidence(
    model_inputs=inputs,
    selection=selection,
)

print("\n--- REAL PRODUCTION FACTOR EVIDENCE ---")
print(f"Row: {evidence.row}")
print(f"Column: {evidence.column}")
print(f"CRS: {evidence.crs}")
print(f"Susceptibility score: {evidence.susceptibility_score:.8f}")

print("\n--- FIVE FACTOR SCORES ---")
for factor, score in evidence.factor_scores.items():
    print(f"{factor}: {score:.8f}")

print("\nFactor evidence extraction: PASS")
