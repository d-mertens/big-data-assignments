# Assignment 2: Optimised Matrix Multiplication and Sparse Matrices

**Author:** Dennis Mertens  
**Course:** Big Data (2026–2027)
**GitHub Repository:** [https://github.com/d-mertens/big-data-assignments](https://github.com/d-mertens/big-data-assignments)

---

## Overview

This directory contains the complete source code, verification test suites, benchmark harness and research report for **Individual Assignment 2**:

- **Part A (Dense Optimizations):** Investigates the impact of memory access patterns by comparing:
  - Canonical Baseline ($i\text{-}j\text{-}k$) with stride-$n$ access on $B$.
  - Loop-Reordered ($i\text{-}k\text{-}j$) with contiguous stride-1 streaming across $B$ and $C$.
  - Cache-Blocked Tiling ($B=64$) fitted to the 128 KB L1 data cache.
- **Part B (Sparse Matrices):** Implements Compressed Sparse Row (CSR) matrix representation and Gustavson's SpGEMM algorithm with dynamic dense row accumulators, evaluating performance across densities $d \in [0.001, 0.50]$ for matrix dimensions up to $n=2048$.

---

## Directory Layout

```text
assignment-2/
├── src/
│   ├── dense_opt/               # C implementations of i-j-k, i-k-j and tiled kernels
│   │   ├── dense_matrix.h       # Data structures, LCG, timing and RSS tracking
│   │   ├── baseline_ijk.c       # i-j-k triple loop
│   │   ├── reordered_ikj.c      # Loop-reordered i-k-j stride-1
│   │   ├── tiled_blocked.c      # Cache-blocked B=64 tiling
│   │   ├── verify_dense.c       # Test suite for dense kernels
│   │   └── Makefile             # Clang build targets (-O3 -fno-vectorize)
│   └── sparse/                  # C implementations of CSR and SpGEMM
│       ├── csr_matrix.h         # CSR struct definition and memory footprint calculation
│       ├── csr_matrix.c         # Allocation, dense conversions and Gustavson's SpGEMM
│       ├── csr_spgemm.c         # SpGEMM benchmarking
│       ├── verify_sparse.c      # Test suite for sparse multiplication
│       └── Makefile             # Clang build targets (-O3 -fno-vectorize)
├── scripts/
│   ├── run_benchmarks.py        # Benchmark pipeline (5 reps + 1 warmup)
│   ├── analyze_and_plot.py      # Aggregation (medians/IQRs) of results and 4 figures
│   └── watch_report.py          
├── data/
│   ├── raw/                     # Raw benchmark CSVs (dense_results.csv, sparse_results.csv)
│   └── processed/               # Summary CSVs and cross-comparison tables
├── report/
│   └── figures/                 # Generated plots
└── Makefile                     # Main Runner for all (all, verify, benchmark, analyze, report, clean)
```

---

## Quick Start & Reproduction

### 1. Build and Run Correctness Tests

```bash
make verify
```

This builds all C binaries and runs:

- `verify_dense`: Analytical $2\times 2$ multiplication and cross-equivalence tests between $i\text{-}j\text{-}k$, $i\text{-}k\text{-}j$, and Tiled kernels.
- `verify_sparse`: Analytical $2\times 2$ sparse multiplication and cross-validation against dense products for $90\%$ and $95\%$ sparse matrices.

### 2. Run Benchmarks

```bash
make benchmark
```

Executes the full automated benchmarking pipeline:

- **Dense:** Sizes $n \in [64, 128, 256, 512, 1024, 1536, 2048]$ (5 repetitions, 1 warm-up).
- **Sparse:** Densities $d \in [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]$ for $n \in [256, 512, 1024, 2048]$.
Raw outputs are saved directly to `data/raw/`.

### 3. Analyze Data and Generate Figures

```bash
make analyze
```

Processes raw results into `data/processed/` and exports 4 publication figures to `report/figures/`:

1. `dense_optimization_speedup.png` (Speedup vs. $n$).
2. `runtime_vs_sparsity.png` (Execution time vs. density on log-log scale).
3. `sparse_breakeven_frontier.png` (Break-even threshold identification).
4. `memory_dense_vs_sparse.png` (CSR vs. dense memory consumption).

### 4. Compile Research Report

```bash
make report
```

Compiles `Assignment02_Report.tex` to PDF and updates `Assignment02_Report_DennisMertens.pdf` in the root workspace.

### 5. Auto-Compile on Save (Watcher Daemon)

```bash
python3 scripts/watch_report.py
```

Automatically detects changes to `Assignment02_Report.tex` and re-generates both `report/Assignment02_Report.pdf` and the root deliverable `Assignment02_Report_DennisMertens.pdf`.
