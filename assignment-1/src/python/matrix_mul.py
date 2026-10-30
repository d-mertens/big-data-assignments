"""
Triple-loop matrix multiplication benchmark harness.
"""

import sys
import time
import resource
import platform

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

def generate_matrix(n: int, seed: int) -> list[list[float]]:
    state = [seed & LCG_MASK]
    mat = []
    for _ in range(n):
        row = [lcg_double(state) for _ in range(n)]
        mat.append(row)
    return mat

def allocate_matrix(n: int) -> list[list[float]]:
    return [[0.0] * n for _ in range(n)]

def matrix_multiply(A: list[list[float]], B: list[list[float]], C: list[list[float]], n: int) -> None:
    """
    Canonical dense matrix multiplication: C = A * B
    Loop order: i - j - k
    Storage: nested lists (list of lists of floats)
    """
    for i in range(n):
        for j in range(n):
            total = 0.0
            for k in range(n):
                total += A[i][k] * B[k][j]
            C[i][j] = total

def get_peak_rss_kb() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # macOS reports in bytes; Linux in kilobytes
    if platform.system() == "Darwin":
        return ru.ru_maxrss // 1024
    return ru.ru_maxrss

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python3 matrix_mul.py <n> [repetitions] [warmup_runs] [runtime_flag]\n")
        sys.exit(1)

    n = int(sys.argv[1])
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    warmups = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rt_flag = sys.argv[4] if len(sys.argv) > 4 else "CPython"

    A = generate_matrix(n, 123456789)
    B = generate_matrix(n, 987654321)
    C = allocate_matrix(n)

    # Warm-up runs
    for w in range(warmups):
        t0 = time.perf_counter_ns()
        matrix_multiply(A, B, C, n)
        t1 = time.perf_counter_ns()
        duration_sec = (t1 - t0) * 1e-9
        rss_kb = get_peak_rss_kb()
        sys.stdout.write(f"Python,{rt_flag},{n},{w},1,{duration_sec:.9f},{rss_kb},{C[0][0]:.6f}\n")
        sys.stdout.flush()

    # Benchmark repetitions
    for r in range(reps):
        t0 = time.perf_counter_ns()
        matrix_multiply(A, B, C, n)
        t1 = time.perf_counter_ns()
        duration_sec = (t1 - t0) * 1e-9
        rss_kb = get_peak_rss_kb()
        sys.stdout.write(f"Python,{rt_flag},{n},{r},0,{duration_sec:.9f},{rss_kb},{C[0][0]:.6f}\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
