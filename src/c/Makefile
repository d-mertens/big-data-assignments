CC ?= clang
CFLAGS_COMMON = -Wall -Wextra -std=c99
CFLAGS_O0 = $(CFLAGS_COMMON) -O0
CFLAGS_O3 = $(CFLAGS_COMMON) -O3 -fno-vectorize

TARGETS = matrix_mul_O0 matrix_mul_O3 verify

all: $(TARGETS)

matrix_mul_O0: matrix_mul.c
	$(CC) $(CFLAGS_O0) -o $@ $<

matrix_mul_O3: matrix_mul.c
	$(CC) $(CFLAGS_O3) -o $@ $<

verify: verify.c
	$(CC) $(CFLAGS_O3) -o $@ $< -lm

clean:
	rm -f $(TARGETS)

.PHONY: all clean
