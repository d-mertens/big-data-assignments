CC ?= clang
CFLAGS = -Wall -Wextra -std=c99 -O3 -fno-vectorize

TARGETS = baseline_ijk reordered_ikj tiled_blocked verify_dense

all: $(TARGETS)

baseline_ijk: baseline_ijk.c dense_matrix.h
	$(CC) $(CFLAGS) -o $@ $<

reordered_ikj: reordered_ikj.c dense_matrix.h
	$(CC) $(CFLAGS) -o $@ $<

tiled_blocked: tiled_blocked.c dense_matrix.h
	$(CC) $(CFLAGS) -o $@ $<

verify_dense: verify_dense.c dense_matrix.h
	$(CC) $(CFLAGS) -o $@ $< -lm

clean:
	rm -f $(TARGETS)

.PHONY: all clean
