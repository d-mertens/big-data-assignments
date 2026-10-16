"""
Script to verify matrix multiplication implementations across C, Java, and Python.
"""

import subprocess
import sys

def run_step(desc, cmd):
    print(f"--> {desc}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {desc}")
        print(res.stderr)
        print(res.stdout)
        return False
    print(res.stdout.strip())
    return True

def main():
    print("=" * 60)
    print("CROSS-LANGUAGE CORRECTNESS VERIFICATION SUITE")
    print("=" * 60)

    # 1. Build C
    if not run_step("Compiling C executables", "make -C src/c"):
        sys.exit(1)
    if not run_step("Running C test suite", "./src/c/verify"):
        sys.exit(1)

    # 2. Build Java
    if not run_step("Compiling Java classes", "make -C src/java"):
        sys.exit(1)
    if not run_step("Running Java test suite", "make -C src/java verify"):
        sys.exit(1)

    # 3. Python
    if not run_step("Running Python test suite", "python3 src/python/verify.py"):
        sys.exit(1)

    print("\n" + "=" * 60)
    print("ALL CROSS-LANGUAGE VERIFICATION CHECKS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
