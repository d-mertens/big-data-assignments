"""
Generating script for analysis and figure generation.

Processes raw benchmark CSV, computes central metrics (median, IQR) and then produces figures.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 13,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 15,
    'figure.dpi': 300
})

COLORS = {
    'C (-O3)': '#1f77b4',
    'C (-O0)': '#aec7e8',
    'Java (HotSpot)': '#2ca02c',
    'Python (CPython)': '#d62728'
}

MARKERS = {
    'C (-O3)': 'o',
    'C (-O0)': 's',
    'Java (HotSpot)': '^',
    'Python (CPython)': 'D'
}

def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Filter only successful benchmark repetitions (exclude warmups)
    clean_df = df[(df['status'] == 'SUCCESS') & (df['is_warmup'] == 0)].copy()
    clean_df['runtime_sec'] = clean_df['runtime_sec'].astype(float)
    clean_df['peak_rss_mb'] = clean_df['peak_rss_kb'].astype(float) / 1024.0
    clean_df['matrix_size'] = clean_df['matrix_size'].astype(int)
    
    # Standardize label
    clean_df['label'] = clean_df.apply(
        lambda r: f"{r['language']} ({r['configuration']})", axis=1
    )
    return clean_df

def compute_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    def iqr(x):
        return np.percentile(x, 75) - np.percentile(x, 25)

    summary = df.groupby(['language', 'configuration', 'label', 'matrix_size']).agg(
        reps=('runtime_sec', 'count'),
        median_time=('runtime_sec', 'median'),
        iqr_time=('runtime_sec', iqr),
        mean_time=('runtime_sec', 'mean'),
        std_time=('runtime_sec', 'std'),
        min_time=('runtime_sec', 'min'),
        max_time=('runtime_sec', 'max'),
        median_rss_mb=('peak_rss_mb', 'median')
    ).reset_index()

    # Compute relative slowdown vs C (-O3)
    c_o3_times = summary[summary['label'] == 'C (-O3)'].set_index('matrix_size')['median_time']
    summary['slowdown_vs_c_o3'] = summary.apply(
        lambda r: r['median_time'] / c_o3_times.get(r['matrix_size'], np.nan), axis=1
    )
    return summary

def fit_empirical_scaling(summary: pd.DataFrame) -> dict:
    scaling_fits = {}
    for label, group in summary.groupby('label'):
        # Only fit on n >= 64 to avoid small-constant / timer-resolution distortions
        valid = group[group['matrix_size'] >= 64]
        if len(valid) >= 3:
            log_n = np.log(valid['matrix_size'])
            log_t = np.log(valid['median_time'])
            slope, intercept, r_value, p_value, std_err = linregress(log_n, log_t)
            scaling_fits[label] = {
                'exponent_b': slope,
                'intercept_a': np.exp(intercept),
                'r_squared': r_value**2,
                'std_err': std_err
            }
    return scaling_fits

def plot_runtime_loglog(summary: pd.DataFrame, scaling_fits: dict, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    for label, group in summary.groupby('label'):
        group_sorted = group.sort_values('matrix_size')
        color = COLORS.get(label, 'black')
        marker = MARKERS.get(label, 'o')
        
        # Plot median with error bars (IQR)
        ax.errorbar(
            group_sorted['matrix_size'],
            group_sorted['median_time'],
            yerr=group_sorted['iqr_time'],
            label=f"{label} (fit: ~N^{scaling_fits.get(label, {}).get('exponent_b', 0):.2f})",
            color=color,
            marker=marker,
            linewidth=2,
            capsize=4,
            alpha=0.9
        )

    # Reference cubic line O(n^3)
    sizes = np.array([32, 64, 128, 256, 512, 1024, 2048])
    c_ref = summary[(summary['label'] == 'C (-O3)') & (summary['matrix_size'] == 256)]
    if not c_ref.empty:
        t_base = c_ref['median_time'].values[0]
        n_base = 256
        ref_line = t_base * (sizes / n_base)**3
        ax.plot(sizes, ref_line, 'k--', alpha=0.5, label='Theoretical O(n³) scaling')

    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=10)
    ax.set_xlabel('Matrix Dimension N (N x N elements)')
    ax.set_ylabel('Execution Time (seconds, log scale)')
    ax.set_title('Empirical Runtime Scaling Across Languages (Log-Log Scale)')
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def plot_relative_slowdown(summary: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    for label, group in summary.groupby('label'):
        if label == 'C (-O3)':
            continue
        group_sorted = group.sort_values('matrix_size')
        color = COLORS.get(label, 'black')
        marker = MARKERS.get(label, 'o')
        
        ax.plot(
            group_sorted['matrix_size'],
            group_sorted['slowdown_vs_c_o3'],
            label=label,
            color=color,
            marker=marker,
            linewidth=2,
            alpha=0.9
        )

    ax.set_xscale('log', base=2)
    ax.axhline(1.0, color='gray', linestyle=':', label='C (-O3) Baseline (1.0x)')
    ax.set_xlabel('Matrix Dimension N')
    ax.set_ylabel('Slowdown Factor vs C (-O3) [T_lang / T_C-O3]')
    ax.set_title('Execution Slowdown Relative to Native C (-O3)')
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def plot_memory_vs_size(summary: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    for label, group in summary.groupby('label'):
        group_sorted = group.sort_values('matrix_size')
        color = COLORS.get(label, 'black')
        marker = MARKERS.get(label, 'o')
        
        ax.plot(
            group_sorted['matrix_size'],
            group_sorted['median_rss_mb'],
            label=label,
            color=color,
            marker=marker,
            linewidth=2,
            alpha=0.9
        )

    # Theoretical raw data size (3 matrices * N^2 * 8 bytes / 10^6)
    all_sizes = np.sort(summary['matrix_size'].unique())
    raw_mb = (3 * 8 * (all_sizes ** 2)) / (1024 * 1024)
    ax.plot(all_sizes, raw_mb, 'k:', label='Raw Matrix Elements (3 × 8N² B)', alpha=0.7)

    ax.set_xscale('log', base=2)
    ax.set_xlabel('Matrix Dimension N')
    ax.set_ylabel('Peak Resident Set Size (RSS) [MB]')
    ax.set_title('Process Peak Memory Usage vs Matrix Dimension')
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def main():
    raw_csv = "data/raw/benchmark_results.csv"
    if not os.path.exists(raw_csv):
        print(f"Error: {raw_csv} not found. Run benchmark suite first.")
        sys.exit(1)

    print("Processing benchmark results...")
    df = load_and_clean_data(raw_csv)
    summary = compute_summary_statistics(df)
    scaling_fits = fit_empirical_scaling(summary)

    # Save processed summary
    os.makedirs("data/processed", exist_ok=True)
    summary_path = "data/processed/benchmark_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Saved summary statistics to {summary_path}")

    # Print empirical fits
    print("\n--- Empirical Scaling Exponents (T(n) ~ n^b) ---")
    for label, fit in scaling_fits.items():
        print(f"  {label:20s}: b = {fit['exponent_b']:.3f} ± {fit['std_err']:.3f} (R² = {fit['r_squared']:.4f})")

    # Generate plots
    plot_runtime_loglog(summary, scaling_fits, "report/figures/runtime_vs_size_loglog.png")
    plot_relative_slowdown(summary, "report/figures/relative_slowdown.png")
    plot_memory_vs_size(summary, "report/figures/memory_vs_size.png")

    print("\nAnalysis and plotting complete.")

if __name__ == "__main__":
    main()
