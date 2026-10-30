#include "dense_matrix.h"

int test_analytical_2x2(void) {
    double A[4] = {1.0, 2.0, 3.0, 4.0};
    double B[4] = {2.0, 0.0, 1.0, 2.0};
    double expected[4] = {4.0, 4.0, 10.0, 8.0};
    double C_ijk[4] = {0};
    double C_ikj[4] = {0};
    double C_tiled[4] = {0};

    matmul_ijk(A, B, C_ijk, 2);
    matmul_ikj(A, B, C_ikj, 2);
    matmul_tiled(A, B, C_tiled, 2, 1);

    for (int i = 0; i < 4; i++) {
        if (fabs(C_ijk[i] - expected[i]) > 1e-12 ||
            fabs(C_ikj[i] - expected[i]) > 1e-12 ||
            fabs(C_tiled[i] - expected[i]) > 1e-12) {
            return 0;
        }
    }
    return 1;
}

int test_cross_equivalence(int n) {
    size_t sz = (size_t)n * (size_t)n;
    double *A = (double *)malloc(sz * sizeof(double));
    double *B = (double *)malloc(sz * sizeof(double));
    double *C_ijk = (double *)malloc(sz * sizeof(double));
    double *C_ikj = (double *)malloc(sz * sizeof(double));
    double *C_tiled = (double *)malloc(sz * sizeof(double));

    generate_dense_matrix(A, n, 123456789ULL);
    generate_dense_matrix(B, n, 987654321ULL);

    matmul_ijk(A, B, C_ijk, n);
    matmul_ikj(A, B, C_ikj, n);
    matmul_tiled(A, B, C_tiled, n, 32);

    int passed = 1;
    double max_diff_ikj = 0.0;
    double max_diff_tiled = 0.0;

    for (size_t i = 0; i < sz; i++) {
        double diff1 = fabs(C_ijk[i] - C_ikj[i]);
        double diff2 = fabs(C_ijk[i] - C_tiled[i]);
        if (diff1 > max_diff_ikj) max_diff_ikj = diff1;
        if (diff2 > max_diff_tiled) max_diff_tiled = diff2;
        if (diff1 > 1e-10 || diff2 > 1e-10) {
            passed = 0;
            break;
        }
    }

    free(A); free(B); free(C_ijk); free(C_ikj); free(C_tiled);
    return passed;
}

int main(void) {
    printf("Running Dense Optimization Correctness Tests...\n");
    
    int p1 = test_analytical_2x2();
    printf("  [1/3] Analytical 2x2 test (all 3 methods): %s\n", p1 ? "PASSED" : "FAILED");

    int p2 = test_cross_equivalence(64);
    printf("  [2/3] Cross-equivalence i-j-k vs i-k-j vs Tiled (n=64): %s\n", p2 ? "PASSED" : "FAILED");

    int p3 = test_cross_equivalence(128);
    printf("  [3/3] Cross-equivalence i-j-k vs i-k-j vs Tiled (n=128): %s\n", p3 ? "PASSED" : "FAILED");

    if (p1 && p2 && p3) {
        printf("ALL DENSE OPTIMIZATION TESTS PASSED SUCCESSFULLY.\n");
        return 0;
    } else {
        printf("SOME TESTS FAILED.\n");
        return 1;
    }
}
