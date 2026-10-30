#include "csr_matrix.h"

int test_analytical_sparse_2x2(void) {
    // A = [[1.0, 0.0], [0.0, 4.0]]
    // B = [[0.0, 2.0], [3.0, 0.0]]
    // Expected C = [[0.0, 2.0], [12.0, 0.0]]
    double A_dense[4] = {1.0, 0.0, 0.0, 4.0};
    double B_dense[4] = {0.0, 2.0, 3.0, 0.0};
    double expected[4] = {0.0, 2.0, 12.0, 0.0};

    CSRMatrix *A = csr_from_dense(A_dense, 2, 1e-12);
    CSRMatrix *B = csr_from_dense(B_dense, 2, 1e-12);
    CSRMatrix *C = csr_spgemm(A, B);

    double C_dense[4] = {0};
    csr_to_dense(C, C_dense);

    int passed = 1;
    for (int i = 0; i < 4; i++) {
        if (fabs(C_dense[i] - expected[i]) > 1e-12) {
            passed = 0;
            break;
        }
    }

    csr_free(A); csr_free(B); csr_free(C);
    return passed;
}

int test_sparse_vs_dense(int n, double density) {
    size_t sz = (size_t)n * (size_t)n;
    double *A_dense = (double *)calloc(sz, sizeof(double));
    double *B_dense = (double *)calloc(sz, sizeof(double));
    double *C_dense_ref = (double *)calloc(sz, sizeof(double));
    double *C_sparse_recovered = (double *)calloc(sz, sizeof(double));

    uint64_t state = 42ULL;
    // Populate with density d
    for (size_t i = 0; i < sz; i++) {
        state = (state * 6364136223846793005ULL) + 1ULL;
        double p = (double)(state >> 11) / 9007199254740992.0;
        if (p < density) {
            state = (state * 6364136223846793005ULL) + 1ULL;
            A_dense[i] = (double)(state >> 11) / 9007199254740992.0;
        }

        state = (state * 6364136223846793005ULL) + 1ULL;
        p = (double)(state >> 11) / 9007199254740992.0;
        if (p < density) {
            state = (state * 6364136223846793005ULL) + 1ULL;
            B_dense[i] = (double)(state >> 11) / 9007199254740992.0;
        }
    }

    // Dense reference multiplication (i-k-j)
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            double a_ik = A_dense[i * n + k];
            if (fabs(a_ik) < 1e-15) continue;
            for (int j = 0; j < n; j++) {
                C_dense_ref[i * n + j] += a_ik * B_dense[k * n + j];
            }
        }
    }

    // CSR SpGEMM
    CSRMatrix *A_csr = csr_from_dense(A_dense, n, 1e-15);
    CSRMatrix *B_csr = csr_from_dense(B_dense, n, 1e-15);
    CSRMatrix *C_csr = csr_spgemm(A_csr, B_csr);

    csr_to_dense(C_csr, C_sparse_recovered);

    int passed = 1;
    double max_diff = 0.0;
    for (size_t i = 0; i < sz; i++) {
        double diff = fabs(C_dense_ref[i] - C_sparse_recovered[i]);
        if (diff > max_diff) max_diff = diff;
        if (diff > 1e-10) {
            passed = 0;
            break;
        }
    }

    free(A_dense); free(B_dense); free(C_dense_ref); free(C_sparse_recovered);
    csr_free(A_csr); csr_free(B_csr); csr_free(C_csr);
    return passed;
}

int main(void) {
    printf("Running Sparse Matrix (CSR SpGEMM) Correctness Tests...\n");

    int p1 = test_analytical_sparse_2x2();
    printf("  [1/3] Analytical 2x2 sparse product: %s\n", p1 ? "PASSED" : "FAILED");

    int p2 = test_sparse_vs_dense(32, 0.10);
    printf("  [2/3] CSR SpGEMM vs Dense reference (n=32, 90%% sparse): %s\n", p2 ? "PASSED" : "FAILED");

    int p3 = test_sparse_vs_dense(64, 0.05);
    printf("  [3/3] CSR SpGEMM vs Dense reference (n=64, 95%% sparse): %s\n", p3 ? "PASSED" : "FAILED");

    if (p1 && p2 && p3) {
        printf("ALL SPARSE MATRIX TESTS PASSED SUCCESSFULLY.\n");
        return 0;
    } else {
        printf("SOME TESTS FAILED.\n");
        return 1;
    }
}
