# Assignment 1: Basic Matrix Multiplication in Python, Java, and C

This repository contains the complete implementation, automated benchmarking suite, statistical analysis pipeline, and research report for **Assignment 1: Basic Matrix Multiplication in Different Languages**.

---

## 1. Research Objective

Investigate how matrix size ($N \times N$) affects execution time and memory footprint under controlled conditions across three distinct language execution models:

1. **C (Compiled Native)**: Low-level contiguous memory allocation with direct pointer arithmetic and compiler optimization levels (`-O0` and `-O3`).
2. **Java (JIT-Compiled / Managed Virtual Machine)**: HotSpot tiered compilation with array-of-arrays memory layout (`double[][]`) and generational garbage collection.
3. **Python (Interpreted Bytecode)**: CPython 3.12 dynamic dispatch with boxed floating-point objects and nested lists (`list[list[float]]`).

All implementations execute the exact canonical **$O(n^3)$ triple-loop algorithm** (`i-j-k` order) without external linear algebra libraries (BLAS/LAPACK/NumPy) inside the timed kernel.

---

## 2. Experimental Environment & Fixed Settings

- **Hardware Platform:** Apple Silicon M4 (10 cores: 4 performance + 6 efficiency / 10 execution threads), 24 GB Unified Memory, 128-byte cache lines.
- **Operating System:** macOS Darwin 24.x (ARM64).
- **C Compiler:** Apple Clang version 21.0.0 (`-O0` and `-O3 -fno-vectorize`).
- **Java Virtual Machine:** OpenJDK 11.0.25 (Temurin 64-Bit Server VM, mixed mode, tiered compilation enabled).
- **Python Runtime:** CPython 3.12.7 (Standard 64-bit interpreter).
- **Numeric Precision:** IEEE 754 64-bit double-precision floating-point (`double` / `float64`).
- **Input Generation:** Standardized 64-bit Linear Congruential Generator (LCG) with multiplier $a = 6364136223846793005$ and addend $c = 1$, ensuring identical bitwise pseudo-random inputs across C, Java and Python.

---

## 3. Directory Structure

```text
BD-assignment-1/
├── Makefile                       # Run to build, test and benchmark
├── README.md                      # Reproduction documentation
├── requirements.txt               # Required Python packages
├── src/
│   ├── c/
│   │   ├── Makefile               # C compilation (-O0 and -O3 targets)
│   │   ├── matrix_mul.c           # Benchmarking harness and i-j-k kernel
│   │   └── verify.c               # C correctness suite
│   ├── java/
│   │   ├── Makefile               # Java compilation and test execution
│   │   ├── MatrixMul.java         # Benchmarking harness with JIT warmup & heap tracking
│   │   └── Verify.java            # Java correctness suite
│   └── python/
│       ├── matrix_mul.py          # Pure Python triple-loop harness
│       └── verify.py              # Python correctness suite & NumPy cross-validation
├── scripts/
│   ├── generate_inputs.py         # Input generator
│   ├── verify_all.py              # Automated cross-language validation
│   ├── run_benchmarks.py          # Benchmark orchestrator managing warm-ups and timeouts
│   └── analyze_and_plot.py        # Computes statistics and generates figures
├── data/
│   ├── inputs/                    # Binary test matrices
│   ├── raw/                       # benchmark_results.csv (raw repetition logs)
│   └── processed/                 # benchmark_summary.csv (medians, IQRs, slowdown ratios)
└── report/
    └── figures/                   # Generated plots
```

---

## 4. Build & Execution Instructions

### 4.1 Prerequisites

Ensure Clang, Java 11+, Python 3.12+ and required Python packages are installed:

```bash
pip install -r requirements.txt
```

### 4.2 Compile All Sources

```bash
make all
```

### 4.3 Automated Verification

Run correctness validation across all three languages:

```bash
make verify
```

### 4.4 Run Full Benchmarking Suite

Executes the defined matrix size sequence ($N \in [16, 2048]$) across C (`-O0`, `-O3`), Java, and Python with warm-ups, 5 repetitions and per-run timeout limits:

```bash
make benchmark
```

### 4.5 Statistical Analysis & Plot Generation

Computes median, IQR, empirical scaling exponents and generates publication plots:

```bash
make analyze
```

---

## 5. Timing & Memory Measurement Protocol

1. **Kernel Timing Isolation:** Timing boundaries strictly encapsulate the $O(n^3)$ triple-loop computation. Allocation, initialization, input generation and file operations occur entirely outside the measured interval.
2. **Clock Source:** High-resolution monotonic timers (`clock_gettime(CLOCK_MONOTONIC)` in C, `System.nanoTime()` in Java, `time.perf_counter_ns()` in Python).
3. **Warm-up Protocol:**
   - Java: 3 warm-up runs executed and discarded to allow HotSpot JIT C2 compiler tier optimization.
   - C and Python: 1 warm-up run executed and discarded to prime caches and memory page mappings.
4. **Memory Metrics:** Peak Resident Set Size (RSS) recorded via `getrusage(RUSAGE_SELF)` in C and Python; heap occupancy recorded in Java via `Runtime.getRuntime()`.
