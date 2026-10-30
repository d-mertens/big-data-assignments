#include "dense_matrix.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <n> [repetitions] [warmup_runs]\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    int reps = (argc > 2) ? atoi(argv[2]) : 5;
    int warmups = (argc > 3) ? atoi(argv[3]) : 1;

    size_t num_elements = (size_t)n * (size_t)n;
    double *A = (double *)malloc(num_elements * sizeof(double));
    double *B = (double *)malloc(num_elements * sizeof(double));
    double *C = (double *)malloc(num_elements * sizeof(double));

    if (!A || !B || !C) {
        fprintf(stderr, "Error: Memory allocation failed for n=%d\n", n);
        free(A); free(B); free(C);
        return 2;
    }

    generate_dense_matrix(A, n, 123456789ULL);
    generate_dense_matrix(B, n, 987654321ULL);

    // Warm-up runs
    for (int w = 0; w < warmups; w++) {
        double t_start = get_time_sec();
        matmul_ikj(A, B, C, n);
        double t_end = get_time_sec();
        long rss_kb = get_peak_rss_kb();
        printf("Dense_Reordered_IKJ,%d,%d,1,%.9f,%ld,%.6f\n", n, w, t_end - t_start, rss_kb, C[0]);
    }

    // Benchmark repetitions
    for (int r = 0; r < reps; r++) {
        double t_start = get_time_sec();
        matmul_ikj(A, B, C, n);
        double t_end = get_time_sec();
        long rss_kb = get_peak_rss_kb();
        printf("Dense_Reordered_IKJ,%d,%d,0,%.9f,%ld,%.6f\n", n, r, t_end - t_start, rss_kb, C[0]);
    }

    free(A); free(B); free(C);
    return 0;
}
