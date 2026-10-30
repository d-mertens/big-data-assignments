.PHONY: all a1 a2 verify-a1 verify-a2 clean-a1 clean-a2 clean help

all: a1 a2

a1:
	$(MAKE) -C assignment-1 all

a2:
	$(MAKE) -C assignment-2 all

verify-a1:
	$(MAKE) -C assignment-1 verify

verify-a2:
	$(MAKE) -C assignment-2 verify

clean-a1:
	$(MAKE) -C assignment-1 clean

clean-a2:
	$(MAKE) -C assignment-2 clean

clean: clean-a1 clean-a2

help:
	@echo "Big Data Individual Assignments"
	@echo "Available targets:"
	@echo "  make a1        - Build Assignment 1 (C & Java)"
	@echo "  make a2        - Build Assignment 2 (Dense & Sparse C)"
	@echo "  make verify-a1 - Run correctness tests for Assignment 1"
	@echo "  make verify-a2 - Run correctness tests for Assignment 2"
	@echo "  make clean     - Remove all build artifacts across assignments"
