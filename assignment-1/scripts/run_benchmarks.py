"""
Benchmark runner for C (-O0, -O3), Java (HotSpot), and Python (CPython).
Includes warm-ups, repetition counts and per-run timeouts.
"""

import subprocess
import sys
import os
import time
import csv

CSV_HEADER = [
    "language",
    "configuration",
    "matrix_size",
    "repetition_idx",
    "is_warmup",
    "runtime_sec",
    "peak_rss_kb",
    "checksum",
    "status"
]

CONFIGURATIONS = [
    {
        "language": "C",
        "configuration": "-O3",
        "cmd_template": ["./src/c/matrix_mul_O3", "{n}", "{reps}", "1", "-O3"],
        "warmups": 1,
        "sizes": [16, 32, 64, 128, 256, 512, 1024, 1536, 2048],
        "reps": 5
    },
    {
        "language": "C",
        "configuration": "-O0",
        "cmd_template": ["./src/c/matrix_mul_O0", "{n}", "{reps}", "1", "-O0"],
        "warmups": 1,
        "sizes": [16, 32, 64, 128, 256, 512, 1024],
        "reps": 5
    },
    {
        "language": "Java",
        "configuration": "HotSpot",
        "cmd_template": ["java", "-cp", "src/java/bin", "matrix.MatrixMul", "{n}", "{reps}", "3", "HotSpot"],
        "warmups": 3,
        "sizes": [16, 32, 64, 128, 256, 512, 1024, 1536, 2048],
        "reps": 5
    },
    {
        "language": "Python",
        "configuration": "CPython",
        "cmd_template": ["python3", "src/python/matrix_mul.py", "{n}", "{reps}", "{warmups}", "CPython"],
        "warmups": 1,
        "sizes": [16, 32, 64, 128, 256, 512],
        "reps": 5,
        "costly_sizes": [1024],  # for run with 1 repetition (justified costly run, protocol p.2)
        "attempted_timeout_sizes": [1536]  # was used to confirm timeout boundary
    }
]

def run_benchmarks(output_file="data/raw/benchmark_results.csv"):
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Check executables exist
    if not os.path.exists("./src/c/matrix_mul_O3") or not os.path.exists("./src/c/matrix_mul_O0"):
        print("Compiling C binaries...")
        subprocess.run(["make", "-C", "src/c"], check=True)
    if not os.path.exists("./src/java/bin/matrix/MatrixMul.class"):
        print("Compiling Java classes...")
        subprocess.run(["make", "-C", "src/java"], check=True)

    print(f"Beginning benchmarking suite. Saving results to {output_file}")

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        f.flush()

        for config in CONFIGURATIONS:
            lang = config["language"]
            cfg_name = config["configuration"]
            sizes = config["sizes"]
            reps = config["reps"]
            warmups = config["warmups"]

            print(f"\n==================================================")
            print(f"Benchmarking: {lang} ({cfg_name})")
            print(f"==================================================")

            # Regular sizes (5 reps)
            for n in sizes:
                cmd = [arg.format(n=n, reps=reps, warmups=warmups) for arg in config["cmd_template"]]
                print(f"  n={n:4d} (reps={reps}): Executing... ", end="", flush=True)

                t_start = time.time()
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180.0)
                    elapsed = time.time() - t_start

                    if res.returncode != 0:
                        print(f"FAILED (code {res.returncode}): {res.stderr.strip()[:100]}")
                        writer.writerow([lang, cfg_name, n, 0, 0, "", "", "", f"ERROR_{res.returncode}"])
                        f.flush()
                        continue

                    lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
                    parsed_count = 0
                    for line in lines:
                        parts = line.split(",")
                        if len(parts) >= 8:
                            row = [
                                parts[0], parts[1], parts[2], parts[3],
                                parts[4], parts[5], parts[6], parts[7],
                                "SUCCESS"
                            ]
                            writer.writerow(row)
                            parsed_count += 1
                    f.flush()
                    print(f"DONE ({parsed_count} samples in {elapsed:.2f}s)")
                except subprocess.TimeoutExpired:
                    print(f"TIMEOUT (exceeded 180s)")
                    writer.writerow([lang, cfg_name, n, 0, 0, "", "", "", "TIMEOUT"])
                    f.flush()

            # Costly sizes (fewer repetitions)
            if "costly_sizes" in config:
                for n in config["costly_sizes"]:
                    print(f"  n={n:4d} (costly run, 1 rep, 0 warmup): Executing... ", end="", flush=True)
                    cmd = [arg.format(n=n, reps=1, warmups=0) for arg in config["cmd_template"]]
                    t_start = time.time()
                    try:
                        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180.0)
                        elapsed = time.time() - t_start
                        lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
                        for line in lines:
                            parts = line.split(",")
                            if len(parts) >= 8:
                                writer.writerow([
                                    parts[0], parts[1], parts[2], parts[3],
                                    parts[4], parts[5], parts[6], parts[7],
                                    "SUCCESS"
                                ])
                        f.flush()
                        print(f"DONE (in {elapsed:.2f}s)")
                    except subprocess.TimeoutExpired:
                        print(f"TIMEOUT (exceeded 180s)")
                        writer.writerow([lang, cfg_name, n, 0, 0, "", "", "", "TIMEOUT"])
                        f.flush()

            # Declared timeout tests (for documenting the timeout limits)
            if "attempted_timeout_sizes" in config:
                for n in config["attempted_timeout_sizes"]:
                    print(f"  n={n:4d} (budget limit test, timeout=15s): Executing... ", end="", flush=True)
                    cmd = [arg.format(n=n, reps=1, warmups=0) for arg in config["cmd_template"]]
                    try:
                        subprocess.run(cmd, capture_output=True, text=True, timeout=15.0)
                        print("UNEXPECTED SUCCESS")
                    except subprocess.TimeoutExpired:
                        print("TIMEOUT (exceeded 15s budget limit)")
                        writer.writerow([lang, cfg_name, n, 0, 0, "", "", "", "TIMEOUT_BUDGET_LIMIT"])
                        f.flush()

    print("\nBenchmark suite completed successfully.")

if __name__ == "__main__":
    run_benchmarks()
