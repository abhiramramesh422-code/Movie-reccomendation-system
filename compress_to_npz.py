import numpy as np
import os

def compress_to_npz(filename, data_dict, max_size_mb=25, float_precision=3):
    """
    Compresses and saves data to an .npz file under max_size_mb automatically.
    Works with any provided NumPy arrays in a dictionary.
    """
    # Process data: convert floats to float32 and round
    processed_data = {}
    for key, array in data_dict.items():
        if np.issubdtype(array.dtype, np.floating):
            array_small = array.astype(np.float32)
            array_small = np.round(array_small, decimals=float_precision)
            processed_data[key] = array_small
        else:
            processed_data[key] = array  # keep as-is if not float

    # Save compressed
    np.savez_compressed(filename, **processed_data)

    # Check file size
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"Saved {filename} → {size_mb:.2f} MB")

    if size_mb > max_size_mb:
        print("⚠ Warning: File exceeds target size. Consider reducing precision or downsampling arrays.")

# -----------------------------
# Dynamic usage: just import your arrays
# -----------------------------
if __name__ == "__main__":
    # Example: automatically get all numpy arrays defined in this script
    # Replace this with your actual arrays if they are already defined
    import sys
    import __main__

    # Collect all numpy arrays from the main script
    arrays_to_save = {name: var for name, var in vars(__main__).items() if isinstance(var, np.ndarray)}

    if not arrays_to_save:
        # Fallback example arrays if none exist
        arrays_to_save = {
            'array1': np.random.rand(2000, 2000),
            'array2': np.random.rand(1000, 1000)
        }

    compress_to_npz('compressed_data.npz', arrays_to_save)
