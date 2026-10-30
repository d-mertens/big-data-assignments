import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORT_DIR = BASE_DIR / "assignment-2" / "report"
TEX_FILE = REPORT_DIR / "Assignment02_Report.tex"
PDF_LOCAL = REPORT_DIR / "Assignment02_Report.pdf"
ROOT_PDF = BASE_DIR / "Assignment02_Report_DennisMertens.pdf"

PDFLATEX_BIN = "/Library/TeX/texbin/pdflatex"
if not os.path.exists(PDFLATEX_BIN):
    PDFLATEX_BIN = "pdflatex"

def compile_pdf():
    if not TEX_FILE.exists():
        print(f"[{time.strftime('%H:%M:%S')}] Waiting for {TEX_FILE.name} to be created...")
        return False
        
    try:
        res = subprocess.run(
            [PDFLATEX_BIN, "-interaction=nonstopmode", TEX_FILE.name],
            cwd=str(REPORT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        if res.returncode == 0:
            if PDF_LOCAL.exists():
                import shutil
                shutil.copyfile(str(PDF_LOCAL), str(ROOT_PDF))
                print(f"[{time.strftime('%H:%M:%S')}] PDF updated successfully -> {PDF_LOCAL.relative_to(BASE_DIR)} and {ROOT_PDF.name}")
                return True
        else:
            print(f"[{time.strftime('%H:%M:%S')}] LaTeX compilation error:")
            for line in res.stdout.splitlines()[-15:]:
                print("  " + line)
            return False
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to invoke pdflatex: {e}")
        return False

def main():
    print(f"Watching {TEX_FILE} for changes...")
    print("Whenever you save the .tex file, the PDF will automatically recompile.")
    print("Press Ctrl+C to stop.")

    last_mtime = 0
    if TEX_FILE.exists():
        last_mtime = TEX_FILE.stat().st_mtime
        compile_pdf()

    while True:
        try:
            time.sleep(1)
            if TEX_FILE.exists():
                mtime = TEX_FILE.stat().st_mtime
                if mtime != last_mtime:
                    last_mtime = mtime
                    print(f"[{time.strftime('%H:%M:%S')}] Detected change in {TEX_FILE.name}. Compiling PDF...")
                    compile_pdf()
        except KeyboardInterrupt:
            print("\nStopped watcher.")
            break

if __name__ == "__main__":
    main()
