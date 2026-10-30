#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#define LCG_MULTIPLIER 6364136223846793005ULL
#define LCG_ADDEND 1ULL
#define DIVISOR 9007199254740992.0 // 2^53

static inline uint64_t lcg_next(uint64_t *state) {
    *state = (*state * LCG_MULTIPLIER) + LCG_ADDEND;
    return *state;
}

static inline double lcg_double(uint64_t *state) {
    uint64_t val = lcg_next(state) >> 11;
    return (double)val / DIVISOR;
}

void matrix_multiply(const double *A, const double *B, double *C, int n) {
    for (int i = 0; i < n; i++) {
        int i_offset = i * n;
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i_offset + k] * B[k * n + j];
            }
            C[i_offset + j] = sum;
        }
    }
}

int test_identity(int n) {
    double *A = (double *)malloc(n * n * sizeof(double));
    double *I = (double *)calloc(n * n, sizeof(double));
    double *C = (double *)malloc(n * n * sizeof(double));

    uint64_t state = 42ULL;
    for (int i = 0; i < n * n; i++) {
        A[i] = lcg_double(&state);
    }
    for (int i = 0; i < n; i++) {
        I[i * n + i] = 1.0;
    }

    matrix_multiply(A, I, C, n);

    int passed = 1;
    for (int i = 0; i < n * n; i++) {
        if (fabs(C[i] - A[i]) > 1e-12) {
            passed = 0;
            break;
        }
    }

    free(A); free(I); free(C);
    return passed;
}

int test_zero(int n) {
    double *A = (double *)malloc(n * n * sizeof(double));
    double *Z = (double *)calloc(n * n, sizeof(double));
    double *C = (double *)malloc(n * n * sizeof(double));

    uint64_t state = 42ULL;
    for (int i = 0; i < n * n; i++) {
        A[i] = lcg_double(&state);
    }

    matrix_multiply(A, Z, C, n);

    int passed = 1;
    for (int i = 0; i < n * n; i++) {
        if (fabs(C[i]) > 1e-12) {
            passed = 0;
            break;
        }
    }

    free(A); free(Z); free(C);
    return passed;
}

int test_analytical_2x2(void) {
    double A[4] = {1.0, 2.0, 3.0, 4.0};
    double B[4] = {2.0, 0.0, 1.0, 2.0};
    // Expected: [1*2+2*1, 1*0+2*2, 3*2+4*1, 3*0+4*2] = [4, 4, 10, 8]
    double expected[4] = {4.0, 4.0, 10.0, 8.0};
    double C[4] = {0};

    matrix_multiply(A, B, C, 2);

    for (int i = 0; i < 4; i++) {
        if (fabs(C[i] - expected[i]) > 1e-12) {
            return 0;
        }
    }
    return 1;
}

int main(void) {
    printf("Running C correctness tests...\n");
    int p1 = test_analytical_2x2();
    printf("  [1/3] Analytical 2x2 test: %s\n", p1 ? "PASSED" : "FAILED");

    int p2 = test_identity(32);
    printf("  [2/3] Identity property test (n=32): %s\n", p2 ? "PASSED" : "FAILED");

    int p3 = test_zero(32);
    printf("  [3/3] Zero annihilation test (n=32): %s\n", p3 ? "PASSED" : "FAILED");

    if (p1 && p2 && p3) {
        printf("ALL C TESTS PASSED SUCCESSFULLY.\n");
        return 0;
    } else {
        printf("SOME C TESTS FAILED.\n");
        return 1;
    }
}
