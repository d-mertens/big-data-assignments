"""
Matrix generator / verification helper.

Implements a 64-bit Linear Congruential Generator (LCG) matching C and Java
implementations bit-for-bit to provide identical logical input matrices.
"""

import sys
import os
import argparse
import numpy as np

LCG_MULTIPLIER = 6364136223846793005
LCG_ADDEND = 1
LCG_MASK = 0xFFFFFFFFFFFFFFFF
DIVISOR = 9007199254740992.0  # 2^53

def lcg_next(state: list[int]) -> int:
    state[0] = (state[0] * LCG_MULTIPLIER + LCG_ADDEND) & LCG_MASK
    return state[0]

def lcg_double(state: list[int]) -> float:
    val = lcg_next(state) >> 11
    return float(val) / DIVISOR

def generate_matrix(n: int, seed: int) -> np.ndarray:
    """Generate an n x n matrix of 64-bit floats using the deterministic LCG."""
    state = [seed & LCG_MASK]
    mat = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            mat[i, j] = lcg_double(state)
    return mat

def save_matrix_binary(mat: np.ndarray, filepath: str):
    """Save matrix as binary: 4-byte integer N followed by N*N float64 values."""
    n = mat.shape[0]
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "wb") as f:
        np.array([n], dtype=np.int32).tofile(f)
        mat.tofile(f)

def load_matrix_binary(filepath: str) -> np.ndarray:
    """Load matrix from binary format."""
    with open(filepath, "rb") as f:
        n = np.fromfile(f, dtype=np.int32, count=1)[0]
        mat = np.fromfile(f, dtype=np.float64, count=n*n).reshape((n, n))
    return mat

def compute_reference_product(n: int, seed_a: int = 123456789, seed_b: int = 987654321) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    A = generate_matrix(n, seed_a)
    B = generate_matrix(n, seed_b)
    C_ref = np.matmul(A, B)
    return A, B, C_ref

def main():
    parser = argparse.ArgumentParser(description="Generate deterministic test matrices.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[16, 32, 64, 128], help="Matrix dimensions to generate")
    parser.add_argument("--output-dir", type=str, default="data/inputs", help="Output directory")
    args = parser.parse_args()

    for n in args.sizes:
        print(f"Generating deterministic matrices for n={n}...")
        A, B, C = compute_reference_product(n)
        save_matrix_binary(A, os.path.join(args.output_dir, f"A_{n}.bin"))
        save_matrix_binary(B, os.path.join(args.output_dir, f"B_{n}.bin"))
        save_matrix_binary(C, os.path.join(args.output_dir, f"C_ref_{n}.bin"))
    print("Done generating sample inputs.")

if __name__ == "__main__":
    main()
