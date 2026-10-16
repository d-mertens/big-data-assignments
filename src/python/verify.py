"""
Verification test suite for Python implementation and cross-validation against NumPy.
"""

import math
import numpy as np
from matrix_mul import generate_matrix, allocate_matrix, matrix_multiply

def test_analytical_2x2():
    A = [[1.0, 2.0], [3.0, 4.0]]
    B = [[2.0, 0.0], [1.0, 2.0]]
    expected = [[4.0, 4.0], [10.0, 8.0]]
    C = allocate_matrix(2)
    matrix_multiply(A, B, C, 2)
    for i in range(2):
        for j in range(2):
            if abs(C[i][j] - expected[i][j]) > 1e-12:
                return False
    return True

def test_identity(n=32):
    A = generate_matrix(n, 42)
    I = allocate_matrix(n)
    for i in range(n):
        I[i][i] = 1.0
    C = allocate_matrix(n)
    matrix_multiply(A, I, C, n)
    for i in range(n):
        for j in range(n):
            if abs(C[i][j] - A[i][j]) > 1e-12:
                return False
    return True

def test_zero(n=32):
    A = generate_matrix(n, 42)
    Z = allocate_matrix(n)
    C = allocate_matrix(n)
    matrix_multiply(A, Z, C, n)
    for i in range(n):
        for j in range(n):
            if abs(C[i][j]) > 1e-12:
                return False
    return True

def test_against_numpy(n=64):
    A_list = generate_matrix(n, 123456789)
    B_list = generate_matrix(n, 987654321)
    C_list = allocate_matrix(n)
    matrix_multiply(A_list, B_list, C_list, n)

    A_np = np.array(A_list, dtype=np.float64)
    B_np = np.array(B_list, dtype=np.float64)
    C_np = np.matmul(A_np, B_np)
    C_calc = np.array(C_list, dtype=np.float64)

    # Calculate max relative error
    rel_diff = np.max(np.abs(C_calc - C_np) / (np.abs(C_np) + 1e-14))
    passed = rel_diff < 1e-9
    return passed, rel_diff, C_calc[0, 0]

def main():
    print("Running Python correctness tests...")
    p1 = test_analytical_2x2()
    print(f"  [1/4] Analytical 2x2 test: {'PASSED' if p1 else 'FAILED'}")

    p2 = test_identity(32)
    print(f"  [2/4] Identity property test (n=32): {'PASSED' if p2 else 'FAILED'}")

    p3 = test_zero(32)
    print(f"  [3/4] Zero annihilation test (n=32): {'PASSED' if p3 else 'FAILED'}")

    p4, max_rel_err, c00 = test_against_numpy(64)
    print(f"  [4/4] NumPy reference cross-check (n=64): {'PASSED' if p4 else 'FAILED'} (max rel error: {max_rel_err:.2e}, C[0][0]: {c00:.6f})")

    if p1 and p2 and p3 and p4:
        print("ALL PYTHON TESTS PASSED SUCCESSFULLY.")
        return 0
    else:
        print("SOME PYTHON TESTS FAILED.")
        return 1

if __name__ == "__main__":
    exit(main())
