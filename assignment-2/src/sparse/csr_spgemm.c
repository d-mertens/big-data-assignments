#include "csr_matrix.h"

#define LCG_MULTIPLIER 6364136223846793005ULL
#define LCG_ADDEND 1ULL
#define DIVISOR 9007199254740992.0

static inline uint64_t lcg_next(uint64_t *state) {
    *state = (*state * LCG_MULTIPLIER) + LCG_ADDEND;
    return *state;
}

static inline double lcg_double(uint64_t *state) {
    uint64_t val = lcg_next(state) >> 11;
    return (double)val / DIVISOR;
}

/*
 * Generates a sparse matrix directly in CSR format with exact expected density d.
 * Non-zero placements use an LCG uniform distribution; values in (0, 1].
 */
CSRMatrix *generate_sparse_csr(int n, double density, uint64_t seed) {
    uint64_t state = seed;
    int total_nnz = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double prob = lcg_double(&state);
            if (prob < density) {
                total_nnz++;
            }
        }
    }

    CSRMatrix *mat = csr_create(n, n, total_nnz);
    if (!mat) {
        return NULL;
    }

    // Reset pattern generator and use separate value generator
    state = seed;
    uint64_t val_state = seed ^ 0x5deece66dULL;
    int idx = 0;
    mat->row_ptr[0] = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double prob = lcg_double(&state);
            if (prob < density) {
                mat->col_indices[idx] = j;
                double val = lcg_double(&val_state);
                mat->values[idx] = (val < 1e-12) ? 0.5 : val;
                idx++;
            }
        }
        mat->row_ptr[i + 1] = idx;
    }

    return mat;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <n> <density> [repetitions] [warmup_runs]\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    double density = atof(argv[2]);
    int reps = (argc > 3) ? atoi(argv[3]) : 5;
    int warmups = (argc > 4) ? atoi(argv[4]) : 1;

    if (n <= 0 || density <= 0.0 || density > 1.0) {
        fprintf(stderr, "Error: Invalid parameters (n=%d, density=%.4f)\n", n, density);
        return 1;
    }

    // Measure creation/generation time
    double t_gen_start = get_time_sec();
    CSRMatrix *A = generate_sparse_csr(n, density, 123456789ULL);
    CSRMatrix *B = generate_sparse_csr(n, density, 987654321ULL);
    double t_gen_end = get_time_sec();
    double gen_time_sec = t_gen_end - t_gen_start;

    if (!A || !B) {
        fprintf(stderr, "Error: Sparse matrix generation failed\n");
        if (A) csr_free(A);
        if (B) csr_free(B);
        return 2;
    }

    long mem_csr_kb = (long)((csr_memory_bytes(A) + csr_memory_bytes(B)) / 1024);

    // Warm-up runs
    for (int w = 0; w < warmups; w++) {
        double t_start = get_time_sec();
        CSRMatrix *C = csr_spgemm(A, B);
        double t_end = get_time_sec();
        double kernel_time = t_end - t_start;
        long rss_kb = get_peak_rss_kb();
        double c0 = (C && C->nnz > 0) ? C->values[0] : 0.0;
        int nnz_c = C ? C->nnz : 0;
        printf("Sparse_CSR_SpGEMM,%d,%.4f,%d,%d,%d,%d,1,%.9f,%.9f,%ld,%ld,%.6f\n",
               n, density, A->nnz, B->nnz, nnz_c, w, kernel_time, gen_time_sec, mem_csr_kb, rss_kb, c0);
        if (C) csr_free(C);
    }

    // Benchmark repetitions
    for (int r = 0; r < reps; r++) {
        double t_start = get_time_sec();
        CSRMatrix *C = csr_spgemm(A, B);
        double t_end = get_time_sec();
        double kernel_time = t_end - t_start;
        long rss_kb = get_peak_rss_kb();
        double c0 = (C && C->nnz > 0) ? C->values[0] : 0.0;
        int nnz_c = C ? C->nnz : 0;
        printf("Sparse_CSR_SpGEMM,%d,%.4f,%d,%d,%d,%d,0,%.9f,%.9f,%ld,%ld,%.6f\n",
               n, density, A->nnz, B->nnz, nnz_c, r, kernel_time, gen_time_sec, mem_csr_kb, rss_kb, c0);
        if (C) csr_free(C);
    }

    csr_free(A);
    csr_free(B);
    return 0;
}
