CC ?= clang
CFLAGS = -Wall -Wextra -std=c99 -O3 -fno-vectorize

TARGETS = csr_spgemm verify_sparse

all: $(TARGETS)

csr_matrix.o: csr_matrix.c csr_matrix.h
	$(CC) $(CFLAGS) -c $< -o $@

csr_spgemm: csr_spgemm.c csr_matrix.o
	$(CC) $(CFLAGS) -o $@ $^

verify_sparse: verify_sparse.c csr_matrix.o
	$(CC) $(CFLAGS) -o $@ $^ -lm

clean:
	rm -f $(TARGETS) *.o

.PHONY: all clean
