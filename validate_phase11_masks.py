import numpy as np
import rasterio
from src.flood_factors.mcda_flood_susceptibility import (
    FACTOR_FILES,
    FACTOR_ORDER,
    OUTPUT_FILE,
)

factor_masks = []
factor_ranges = {}

for factor in FACTOR_ORDER:
    with rasterio.open(FACTOR_FILES[factor]) as src:
        data = src.read(1, masked=True)
        mask = src.read_masks(1) != 0

        factor_masks.append(mask)

        valid_values = data.compressed()
        factor_ranges[factor] = (
            float(valid_values.min()),
            float(valid_values.max()),
        )

        print(
            f"{factor}: valid={np.count_nonzero(mask):,}, "
            f"min={valid_values.min():.6f}, "
            f"max={valid_values.max():.6f}"
        )

common_mask = np.logical_and.reduce(factor_masks)

with rasterio.open(OUTPUT_FILE) as src:
    output_mask = src.read_masks(1) != 0

print("\n--- COMMON MASK VALIDATION ---")
print(f"Common factor pixels: {np.count_nonzero(common_mask):,}")
print(f"Output valid pixels: {np.count_nonzero(output_mask):,}")
print(f"Masks exactly equal: {np.array_equal(common_mask, output_mask)}")
print(f"Mask mismatch pixels: {np.count_nonzero(common_mask != output_mask):,}")

print("\n--- FACTOR RANGE VALIDATION ---")
for factor, (minimum, maximum) in factor_ranges.items():
    passed = minimum >= 0.0 and maximum <= 1.0
    print(f"{factor}: {'PASS' if passed else 'FAIL'}")

print("\n--- FINAL OUTPUT ---")
print(f"All five factor ranges valid: {all(0 <= lo <= hi <= 1 for lo, hi in factor_ranges.values())}")
print(f"Output mask matches common mask: {np.array_equal(common_mask, output_mask)}")
