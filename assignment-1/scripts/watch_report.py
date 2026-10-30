#!/usr/bin/env python3
"""
scripts/watch_report.py
Continuous auto-compiler for LaTeX report.
Watches report/Assignment01_Report.tex and automatically recompiles to PDF
whenever the file is saved.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

REPORT_DIR = os.path.abspath("report")
TEX_FILE = os.path.join(REPORT_DIR, "Assignment01_Report.tex")
PDF_FILE = os.path.join(REPORT_DIR, "Assignment01_Report.pdf")
ROOT_PDF = os.path.abspath("Assignment01_Report_DennisMertens.pdf")
PDFLATEX_BIN = "/Library/TeX/texbin/pdflatex"

if not os.path.exists(PDFLATEX_BIN):
    # Fallback to PATH lookup
    import shutil
    PDFLATEX_BIN = shutil.which("pdflatex") or "pdflatex"

def get_last_mtime():
    try:
        return os.path.getmtime(TEX_FILE)
    except OSError:
        return 0

def compile_pdf():
    now_str = datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}] Detected change in Assignment01_Report.tex. Compiling PDF...", flush=True)
    try:
        res = subprocess.run(
            [PDFLATEX_BIN, "-interaction=nonstopmode", "Assignment01_Report.tex"],
            cwd=REPORT_DIR,
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            import shutil
            shutil.copy2(PDF_FILE, ROOT_PDF)
            done_str = datetime.now().strftime("%H:%M:%S")
            print(f"[{done_str}] PDF updated successfully -> report/Assignment01_Report.pdf", flush=True)
        else:
            # Extract last error lines from output
            err_lines = [l for l in res.stdout.splitlines() if l.startswith("!")]
            err_msg = err_lines[0] if err_lines else "Check LaTeX log for syntax errors."
            print(f"[{now_str}] Compilation error: {err_msg}", flush=True)
    except Exception as e:
        print(f"[{now_str}] Failed to invoke pdflatex: {e}", flush=True)

def main():
    if not os.path.exists(TEX_FILE):
        print(f"Error: {TEX_FILE} not found.")
        sys.exit(1)

    print(f"Watching {TEX_FILE} for changes...")
    print("Whenever you save the .tex file, the PDF will automatically recompile.\nPress Ctrl+C to stop.")
    
    last_mtime = get_last_mtime()
    try:
        while True:
            time.sleep(0.5)
            curr_mtime = get_last_mtime()
            if curr_mtime != last_mtime:
                last_mtime = curr_mtime
                # Small grace period to allow editor to finish writing
                time.sleep(0.1)
                compile_pdf()
                last_mtime = get_last_mtime()
    except KeyboardInterrupt:
        print("\nStopped watching LaTeX report.")

if __name__ == "__main__":
    main()
