"""
Generates:
  1. CSVs in assignment-2/data/processed/:
     - dense_summary.csv
     - sparse_summary.csv
     - comparison_dense_sparse.csv
  2. Figures in assignment-2/report/figures/:
     - dense_optimization_speedup.png
     - runtime_vs_sparsity.png
     - sparse_breakeven_frontier.png
     - memory_dense_vs_sparse.png
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIG_DIR = BASE_DIR / "report" / "figures"

# Style settings for IEEE paper publication quality
plt.rcParams.update({
    "font.size": 10,
    "font.family": "serif",
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 12,
    "lines.linewidth": 1.75,
    "lines.markersize": 6,
    "grid.alpha": 0.35,
    "grid.linestyle": ":",
})

def process_data():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    dense_raw_path = RAW_DIR / "dense_results.csv"
    sparse_raw_path = RAW_DIR / "sparse_results.csv"
    
    if not dense_raw_path.exists() or not sparse_raw_path.exists():
        raise FileNotFoundError(f"Raw data missing. Please run run_benchmarks.py first.")
        
    df_dense = pd.read_csv(dense_raw_path)
    df_sparse = pd.read_csv(sparse_raw_path)
    
    # Filter out warmup runs
    df_dense = df_dense[df_dense["is_warmup"] == 0].copy()
    df_sparse = df_sparse[df_sparse["is_warmup"] == 0].copy()
    
    # Process Dense Summary
    dense_summary = df_dense.groupby(["method", "matrix_size"]).agg(
        median_time_sec=("runtime_sec", "median"),
        iqr_time_sec=("runtime_sec", lambda x: np.percentile(x, 75) - np.percentile(x, 25)),
        mean_time_sec=("runtime_sec", "mean"),
        std_time_sec=("runtime_sec", "std"),
        min_time_sec=("runtime_sec", "min"),
        max_time_sec=("runtime_sec", "max"),
        median_rss_kb=("peak_rss_kb", "median")
    ).reset_index()
    
    # Compute speedup relative to Dense_Baseline_IJK
    baseline_df = dense_summary[dense_summary["method"] == "Dense_Baseline_IJK"][["matrix_size", "median_time_sec"]].rename(
        columns={"median_time_sec": "baseline_median_sec"}
    )
    dense_summary = dense_summary.merge(baseline_df, on="matrix_size")
    dense_summary["speedup"] = dense_summary["baseline_median_sec"] / dense_summary["median_time_sec"]
    dense_summary.to_csv(PROCESSED_DIR / "dense_summary.csv", index=False)
    print(f"[✓] Saved {PROCESSED_DIR / 'dense_summary.csv'}")
    
    # Process Sparse Summary
    sparse_summary = df_sparse.groupby(["method", "matrix_size", "density"]).agg(
        median_kernel_sec=("kernel_time_sec", "median"),
        iqr_kernel_sec=("kernel_time_sec", lambda x: np.percentile(x, 75) - np.percentile(x, 25)),
        mean_kernel_sec=("kernel_time_sec", "mean"),
        std_kernel_sec=("kernel_time_sec", "std"),
        median_gen_sec=("gen_time_sec", "median"),
        nnz_a=("nnz_a", "first"),
        nnz_b=("nnz_b", "first"),
        nnz_c=("nnz_c", "first"),
        mem_csr_kb=("mem_csr_kb", "first"),
        median_rss_kb=("peak_rss_kb", "median")
    ).reset_index()
    
    sparse_summary["sparsity_pct"] = (1.0 - sparse_summary["density"]) * 100.0
    sparse_summary["fill_in_ratio"] = sparse_summary["nnz_c"] / sparse_summary["nnz_a"]
    sparse_summary["dense_mem_kb"] = (2 * (sparse_summary["matrix_size"] ** 2) * 8) / 1024 # 2 input matrices A and B in double
    sparse_summary["mem_savings_pct"] = (1.0 - (sparse_summary["mem_csr_kb"] / sparse_summary["dense_mem_kb"])) * 100.0
    sparse_summary.to_csv(PROCESSED_DIR / "sparse_summary.csv", index=False)
    print(f"[✓] Saved {PROCESSED_DIR / 'sparse_summary.csv'}")
    
    # Cross Comparison: Sparse vs Dense Methods for matching matrix sizes
    common_sizes = sorted(list(set(sparse_summary["matrix_size"]).intersection(set(dense_summary["matrix_size"]))))
    
    dense_pivot = dense_summary.pivot(index="matrix_size", columns="method", values="median_time_sec").reset_index()
    comparison = sparse_summary.merge(dense_pivot, on="matrix_size")
    
    comparison["speedup_over_baseline_ijk"] = comparison["Dense_Baseline_IJK"] / comparison["median_kernel_sec"]
    comparison["speedup_over_reordered_ikj"] = comparison["Dense_Reordered_IKJ"] / comparison["median_kernel_sec"]
    comparison["time_ratio_vs_reordered_ikj"] = comparison["median_kernel_sec"] / comparison["Dense_Reordered_IKJ"]
    
    comparison.to_csv(PROCESSED_DIR / "comparison_dense_sparse.csv", index=False)
    print(f"[✓] Saved {PROCESSED_DIR / 'comparison_dense_sparse.csv'}")
    
    return dense_summary, sparse_summary, comparison

def plot_figures(dense_summary, sparse_summary, comparison):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # -------------------------------------------------------------
    # Figure 1: Dense Optimization Speedup vs Matrix Size N
    # -------------------------------------------------------------
    plt.figure(figsize=(6, 4.2))
    
    methods = [
        ("Dense_Baseline_IJK", "Baseline (i-j-k)", "tab:gray", "o", ":"),
        ("Dense_Reordered_IKJ", "Loop Reordered (i-k-j)", "#2b5c8f", "s", "-"),
        ("Dense_Tiled_Blocked_B64", "Cache-Blocked Tiled (B=64)", "#d95f02", "^", "--")
    ]
    
    for method_key, label, color, marker, ls in methods:
        sub = dense_summary[dense_summary["method"] == method_key].sort_values("matrix_size")
        plt.plot(sub["matrix_size"], sub["speedup"], label=label, color=color, marker=marker, linestyle=ls)
        
    plt.axhline(1.0, color="gray", linestyle=":", linewidth=1, alpha=0.7)
    plt.xscale("log", base=2)
    plt.xlabel("Matrix Dimension $N$ ($N \\times N$)")
    plt.ylabel("Speedup vs. Baseline $i\\text{-}j\\text{-}k$ ($T_{base} / T$)")
    plt.title("Dense Multiplication Optimizations on Apple Silicon M4")
    plt.xticks([64, 128, 256, 512, 1024, 1536, 2048], ["64", "128", "256", "512", "1024", "1536", "2048"])
    plt.grid(True, which="both")
    plt.legend(frameon=True, facecolor="white", framealpha=0.9)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "dense_optimization_speedup.png", dpi=300)
    plt.close()
    print(f"[✓] Generated {FIG_DIR / 'dense_optimization_speedup.png'}")
    
    # -------------------------------------------------------------
    # Figure 2: Runtime vs Density (Sparsity) across Matrix Sizes
    # -------------------------------------------------------------
    plt.figure(figsize=(6.5, 4.5))
    sizes_to_plot = [512, 1024, 2048]
    colors = {512: "#2ca02c", 1024: "#1f77b4", 2048: "#d62728"}
    
    for n in sizes_to_plot:
        sub_sp = sparse_summary[sparse_summary["matrix_size"] == n].sort_values("density")
        c = colors[n]
        # Sparse curve
        plt.plot(sub_sp["density"], sub_sp["median_kernel_sec"], label=f"CSR SpGEMM (N={n})",
                 color=c, marker="o", linestyle="-")
        
        # Dense Reordered horizontal reference line
        dense_ikj_time = dense_summary[(dense_summary["method"] == "Dense_Reordered_IKJ") & 
                                       (dense_summary["matrix_size"] == n)]["median_time_sec"].values[0]
        ref_label = f"Dense i-k-j (N={n}: {dense_ikj_time:.3f}s)"
        plt.axhline(dense_ikj_time, color=c, linestyle="--", alpha=0.6, label=ref_label)
        
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Matrix Density $d = nnz / N^2$ (Log Scale)")
    plt.ylabel("Kernel Execution Time [seconds] (Log Scale)")
    plt.title("CSR SpGEMM vs. Dense Loop-Reordered ($i\\text{-}k\\text{-}j$)")
    plt.grid(True, which="both")
    plt.legend(frameon=True, facecolor="white", framealpha=0.85, fontsize=8, loc="upper left")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "runtime_vs_sparsity.png", dpi=300)
    plt.close()
    print(f"[✓] Generated {FIG_DIR / 'runtime_vs_sparsity.png'}")
    
    # -------------------------------------------------------------
    # Figure 3: Sparse Break-Even Frontier (T_CSR / T_Dense_IKJ vs Density)
    # -------------------------------------------------------------
    plt.figure(figsize=(6, 4.2))
    
    for n in sizes_to_plot:
        sub_comp = comparison[comparison["matrix_size"] == n].sort_values("density")
        plt.plot(sub_comp["density"] * 100.0, sub_comp["time_ratio_vs_reordered_ikj"],
                 label=f"$N = {n}$", color=colors[n], marker="s", linestyle="-")
        
    plt.axhline(1.0, color="black", linestyle="-.", linewidth=1.5, label="Break-Even Threshold ($T_{CSR} = T_{IKJ}$)")
    plt.xscale("log")
    plt.xlabel("Matrix Density [%] ($100 \\times nnz / N^2$)")
    plt.ylabel("Execution Time Ratio ($T_{\\text{CSR}} / T_{\\text{Dense\\_IKJ}}$)")
    plt.title("SpGEMM Runtime Break-Even Frontier vs. Dense $i\\text{-}k\\text{-}j$")
    plt.grid(True, which="both")
    plt.legend(frameon=True, facecolor="white", framealpha=0.9)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "sparse_breakeven_frontier.png", dpi=300)
    plt.close()
    print(f"[✓] Generated {FIG_DIR / 'sparse_breakeven_frontier.png'}")
    
    # -------------------------------------------------------------
    # Figure 4: Memory Savings Curve & Break-even
    # -------------------------------------------------------------
    plt.figure(figsize=(6, 4.2))
    
    # Theoretical curve: CSR bytes = 12 * nnz + 4(n+1) -> for n=1024:
    # Dense bytes = 8 * n^2
    # Memory ratio M_CSR / M_Dense = (12 * d * n^2 + 4(n+1)) / (8 * n^2) ~= 1.5 * d
    # Break-even memory occurs at 1.5 * d = 1.0 => d = 2/3 = 66.7% (sparsity = 33.3%)
    densities_theory = np.linspace(0.001, 0.90, 200)
    theory_ratio = 1.5 * densities_theory # asymptotic
    
    plt.plot(densities_theory * 100.0, theory_ratio * 100.0, label="Theoretical CSR / Dense Memory",
             color="tab:blue", linestyle="-", linewidth=2)
    
    # Empirical points from sparse_summary for N=1024 and N=2048
    for n in [1024, 2048]:
        sub = sparse_summary[sparse_summary["matrix_size"] == n].sort_values("density")
        ratio_emp = (sub["mem_csr_kb"] / sub["dense_mem_kb"]) * 100.0
        plt.scatter(sub["density"] * 100.0, ratio_emp, label=f"Empirical ($N={n}$)", marker="o")
        
    plt.axhline(100.0, color="tab:red", linestyle="--", linewidth=1.5, label="Memory Parity Line (100%)")
    plt.axvline(66.67, color="tab:purple", linestyle=":", linewidth=1.5, label="Break-Even Density ($d^* \\approx 66.7\\%$)")
    
    plt.xlabel("Matrix Density [%] ($100 \\times nnz / N^2$)")
    plt.ylabel("CSR Memory as % of Dense Array ($M_{\\text{CSR}} / M_{\\text{Dense}} \\times 100$)")
    plt.title("Memory Footprint: CSR Representation vs. Dense 2D Array")
    plt.grid(True)
    plt.legend(frameon=True, facecolor="white", framealpha=0.9, loc="upper left")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "memory_dense_vs_sparse.png", dpi=300)
    plt.close()
    print(f"[✓] Generated {FIG_DIR / 'memory_dense_vs_sparse.png'}")

if __name__ == "__main__":
    dense_summary, sparse_summary, comparison = process_data()
    plot_figures(dense_summary, sparse_summary, comparison)
    print("\n[✓] All data processing and publication figures generated successfully.")
