
import numpy as np

from src.interpreter.input_loader import load_model_inputs
from src.interpreter.cell_selector import select_raster_cell

inputs = load_model_inputs()

rows, columns = np.where(inputs.valid_mask)

centre_row = (inputs.height - 1) / 2
centre_column = (inputs.width - 1) / 2

distances = (
    (rows - centre_row) ** 2
    + (columns - centre_column) ** 2
)

index = int(np.argmin(distances))
selected_row = int(rows[index])
selected_column = int(columns[index])

selection = select_raster_cell(
    model_inputs=inputs,
    row=selected_row,
    column=selected_column,
)

print("\n--- PRODUCTION CELL SELECTION ---")
print(f"Row: {selection.row}")
print(f"Column: {selection.column}")
print(f"CRS: {selection.crs}")
print(f"Cell-centre X: {selection.x:.3f}")
print(f"Cell-centre Y: {selection.y:.3f}")
print(f"Susceptibility score: {selection.susceptibility_score:.8f}")
print(f"Valid-data footprint: {inputs.valid_cell_count:,} cells")
