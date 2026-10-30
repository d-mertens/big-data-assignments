# Big Data Individual Assignments — Matrix Multiplication

**Author:** Dennis Mertens  
**Course:** Big Data (2026–2027)
**Repository:** [https://github.com/d-mertens/big-data-assignments](https://github.com/d-mertens/big-data-assignments)

---

## Repository Structure

```text
big-data-assignments/
├── assignment-1/                          # Assignment 1: Basic Matrix Multiplication
│   ├── src/                               # Implementations in C, Java, and Python
│   ├── scripts/                           # Benchmarking, verification, and plotting scripts
│   ├── data/                              # Raw data and summary metrics
│   ├── report/                            # Research report (LaTeX source, markdown, figures)
│   ├── Makefile                           # Assignment 1 build and test
│   └── README.md                          # Assignment 1 reproduction guide
│
├── assignment-2/                          # Assignment 2: Optimized Approaches & Sparse Matrices
│   ├── src/
│   │   ├── dense_opt/                     # Baseline i-j-k, reordered i-k-j, and cache blocking
│   │   └── sparse/                        # Compressed Sparse Row (CSR) and SpGEMM
│   ├── scripts/                           # Sparsity generators, benchmark harnesses and plots
│   ├── data/                              # Raw data and processed summaries
│   ├── report/                            # Assignment 2 research report and figures
│   ├── Makefile                           # Assignment 2 build and test
│   └── README.md                          # Assignment 2 reproduction guide
│
├── Assignment01_Report_DennisMertens.pdf  # Submitted report for Assignment 1
├── Assignment02_Report_DennisMertens.pdf  # Submitted report for Assignment 2
├── Makefile                               # Top-level build across assignments
├── requirements.txt                       # Shared Python dependencies
└── .gitignore
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Assignment 1

```bash
make verify-a1
```

### 3. Verify Assignment 2

```bash
make verify-a2
```

Detailed reproduction instructions, environment specifications and analysis are documented inside each assignment's subfolder:

- [Assignment 1 README](assignment-1/README.md)
- [Assignment 2 README](assignment-2/README.md)
