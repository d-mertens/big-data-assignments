
CC ?= clang
JAVAC ?= javac
JAVA ?= java
PYTHON ?= python3

.PHONY: all clean verify benchmark analyze report watch help

all: build-c build-java

build-c:
	@echo "==> Building C executables..."
	$(MAKE) -C src/c

build-java:
	@echo "==> Building Java classes..."
	$(MAKE) -C src/java

verify: all
	@echo "==> Running full cross-language correctness verification..."
	$(PYTHON) scripts/verify_all.py

benchmark: all
	@echo "==> Running full benchmark suite..."
	$(PYTHON) scripts/run_benchmarks.py

analyze:
	@echo "==> Processing benchmark results and generating plots..."
	$(PYTHON) scripts/analyze_and_plot.py

report:
	@echo "==> Compiling LaTeX report to PDF..."
	cd report && /Library/TeX/texbin/pdflatex -interaction=nonstopmode Assignment01_Report.tex
	cp report/Assignment01_Report.pdf Assignment01_Report_DennisMertens.pdf

watch:
	@echo "==> Starting continuous LaTeX report auto-compiler on save..."
	$(PYTHON) scripts/watch_report.py

clean:
	@echo "==> Cleaning build artifacts and outputs..."
	$(MAKE) -C src/c clean
	$(MAKE) -C src/java clean
	rm -rf data/inputs/*.bin data/processed/*.csv report/figures/*.png

help:
	@echo "Available targets:"
	@echo "  make all        - Compile C and Java code"
	@echo "  make verify     - Run automated correctness tests across C, Java, and Python"
	@echo "  make benchmark  - Run the benchmarking suite across all declared configurations"
	@echo "  make analyze    - Compute summary statistics, empirical fits, and generate figures"
	@echo "  make report     - Compile LaTeX report to PDF"
	@echo "  make watch      - Automatically recompile PDF on every save to Assignment01_Report.tex"
	@echo "  make clean      - Remove build artifacts and generated figures"
	@echo "  make benchmark  - Run the benchmarking suite across all declared configurations"
	@echo "  make analyze    - Compute summary statistics, empirical fits, and generate figures"
	@echo "  make clean      - Remove build artifacts and generated figures"
