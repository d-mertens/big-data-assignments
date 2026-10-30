.PHONY: all dense sparse verify benchmark analyze report clean

all: dense sparse

dense:
	$(MAKE) -C src/dense_opt

sparse:
	$(MAKE) -C src/sparse

verify: all
	@echo "=== Running Dense Optimization Verification ==="
	./src/dense_opt/verify_dense
	@echo "\n=== Running Sparse CSR Matrix Verification ==="
	./src/sparse/verify_sparse

benchmark: all
	python3 scripts/run_benchmarks.py

analyze:
	python3 scripts/analyze_and_plot.py

report:
	@echo "=== Compiling Assignment 2 Report ==="
	cd report && pdflatex -interaction=nonstopmode Assignment02_Report.tex
	cd report && pdflatex -interaction=nonstopmode Assignment02_Report.tex
	cp report/Assignment02_Report.pdf ../Assignment02_Report_DennisMertens.pdf
	@echo "[✓] Generated deliverable: ../Assignment02_Report_DennisMertens.pdf"

clean:
	$(MAKE) -C src/dense_opt clean
	$(MAKE) -C src/sparse clean
	rm -f report/*.aux report/*.log report/*.out
