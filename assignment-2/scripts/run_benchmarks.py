"""
Runs:
  1. Dense Optimizations: baseline_ijk, reordered_ikj, tiled_blocked
     Sizes N: [64, 128, 256, 512, 1024, 1536, 2048]
     Repetitions: 5 (plus 1 warmup)
  2. Sparse CSR SpGEMM: csr_spgemm
     Densities: [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]
     Sizes N: [256, 512, 1024, 2048]
     Repetitions: 5 (plus 1 warmup)
"""

import os
import sys
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DENSE_BIN_DIR = BASE_DIR / "src" / "dense_opt"
SPARSE_BIN_DIR = BASE_DIR / "src" / "sparse"
DATA_RAW_DIR = BASE_DIR / "data" / "raw"

DENSE_SIZES = [64, 128, 256, 512, 1024, 1536, 2048]
SPARSE_SIZES = [256, 512, 1024, 2048]
SPARSE_DENSITIES = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]

REPETITIONS = 5
WARMUPS = 1

def build_binaries():
    print("[*] Building dense optimization binaries...")
    subprocess.run(["make", "-C", str(DENSE_BIN_DIR)], check=True)
    print("[*] Building sparse matrix binaries...")
    subprocess.run(["make", "-C", str(SPARSE_BIN_DIR)], check=True)
    print("[✓] All binaries built successfully.\n")

def run_dense_benchmarks():
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    dense_csv = DATA_RAW_DIR / "dense_results.csv"
    
    dense_bins = [
        ("Dense_Baseline_IJK", DENSE_BIN_DIR / "baseline_ijk"),
        ("Dense_Reordered_IKJ", DENSE_BIN_DIR / "reordered_ikj"),
        ("Dense_Tiled_Blocked_B64", DENSE_BIN_DIR / "tiled_blocked")
    ]
    
    print(f"[*] Starting Dense Optimization Benchmarks...")
    print(f"    Output CSV: {dense_csv}")
    print(f"    Sizes: {DENSE_SIZES}")
    print(f"    Repetitions: {REPETITIONS} (warmup: {WARMUPS})")
    
    with open(dense_csv, "w") as f:
        f.write("method,matrix_size,rep_idx,is_warmup,runtime_sec,peak_rss_kb,checksum\n")
        
        for name, bin_path in dense_bins:
            if not bin_path.exists():
                raise FileNotFoundError(f"Binary not found: {bin_path}")
            
            print(f"\n--- Testing {name} ---")
            for n in DENSE_SIZES:
                cmd = [str(bin_path), str(n), str(REPETITIONS), str(WARMUPS)]
                t0 = time.time()
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                elapsed = time.time() - t0
                
                # Write stdout lines directly to csv
                lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
                for line in lines:
                    f.write(line + "\n")
                f.flush()
                
                # Extract benchmark runs (is_warmup == 0) for quick console summary
                bench_times = [float(l.split(",")[4]) for l in lines if l.split(",")[3] == "0"]
                avg_time = sum(bench_times) / len(bench_times) if bench_times else 0.0
                print(f"    n={n:<5}: avg = {avg_time:8.4f}s (wall: {elapsed:6.2f}s)")
                
    print(f"\n[✓] Dense benchmarks completed: {dense_csv}\n")

def run_sparse_benchmarks():
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    sparse_csv = DATA_RAW_DIR / "sparse_results.csv"
    
    sparse_bin = SPARSE_BIN_DIR / "csr_spgemm"
    if not sparse_bin.exists():
        raise FileNotFoundError(f"Binary not found: {sparse_bin}")
        
    print(f"[*] Starting Sparse CSR SpGEMM Benchmarks...")
    print(f"    Output CSV: {sparse_csv}")
    print(f"    Sizes: {SPARSE_SIZES}")
    print(f"    Densities: {SPARSE_DENSITIES}")
    print(f"    Repetitions: {REPETITIONS} (warmup: {WARMUPS})")
    
    with open(sparse_csv, "w") as f:
        f.write("method,matrix_size,density,nnz_a,nnz_b,nnz_c,rep_idx,is_warmup,kernel_time_sec,gen_time_sec,mem_csr_kb,peak_rss_kb,checksum\n")
        
        for n in SPARSE_SIZES:
            print(f"\n--- Testing CSR SpGEMM for n={n} ---")
            for d in SPARSE_DENSITIES:
                cmd = [str(sparse_bin), str(n), str(d), str(REPETITIONS), str(WARMUPS)]
                t0 = time.time()
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                elapsed = time.time() - t0
                
                lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
                for line in lines:
                    f.write(line + "\n")
                f.flush()
                
                bench_times = [float(l.split(",")[8]) for l in lines if l.split(",")[7] == "0"]
                avg_time = sum(bench_times) / len(bench_times) if bench_times else 0.0
                nnz_c = int(lines[0].split(",")[5]) if lines else 0
                print(f"    d={d:6.3f} (sparsity={100*(1-d):5.1f}%): avg kernel = {avg_time:8.5f}s, nnz(C)={nnz_c:<8} (wall: {elapsed:5.2f}s)")
                
    print(f"\n[✓] Sparse benchmarks completed: {sparse_csv}\n")

if __name__ == "__main__":
    t_start = time.time()
    build_binaries()
    
    dense_csv = DATA_RAW_DIR / "dense_results.csv"
    if "--force-dense" in sys.argv or not dense_csv.exists() or len(dense_csv.read_text().strip().splitlines()) < 127:
        run_dense_benchmarks()
    else:
        print(f"[*] Dense benchmarks already complete ({dense_csv}), skipping. Use --force-dense to rerun.\n")
        
    run_sparse_benchmarks()
    print(f"[✓] All Assignment 2 benchmarks finished successfully in {time.time() - t_start:.2f} seconds.")

