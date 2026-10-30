#define _DARWIN_C_SOURCE
#define _POSIX_C_SOURCE 199309L
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>

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

void generate_matrix(double *mat, int n, uint64_t seed) {
    uint64_t state = seed;
    for (int i = 0; i < n * n; i++) {
        mat[i] = lcg_double(&state);
    }
}

/*
 * Canonical dense matrix multiplication: C = A * B
 * Loop order: i - j - k
 * Work: 2 * n^3 FLOPs (n^3 multiplications, n^3 additions)
 */
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

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static long get_peak_rss_kb(void) {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
#if defined(__APPLE__) && defined(__MACH__)
    // On macOS, ru_maxrss is reported in bytes
    return usage.ru_maxrss / 1024;
#else
    // On Linux, ru_maxrss is reported in kilobytes
    return usage.ru_maxrss;
#endif
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <n> [repetitions] [warmup_runs] [opt_flag]\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    int reps = (argc > 2) ? atoi(argv[2]) : 5;
    int warmups = (argc > 3) ? atoi(argv[3]) : 1;
    const char *opt_flag = (argc > 4) ? argv[4] : "unknown";

    if (n <= 0 || reps <= 0 || warmups < 0) {
        fprintf(stderr, "Error: Invalid arguments\n");
        return 1;
    }

    size_t num_elements = (size_t)n * (size_t)n;
    double *A = (double *)malloc(num_elements * sizeof(double));
    double *B = (double *)malloc(num_elements * sizeof(double));
    double *C = (double *)malloc(num_elements * sizeof(double));

    if (!A || !B || !C) {
        fprintf(stderr, "Error: Memory allocation failed for n=%d\n", n);
        free(A); free(B); free(C);
        return 2;
    }

    // Deterministic generation
    generate_matrix(A, n, 123456789ULL);
    generate_matrix(B, n, 987654321ULL);

    // Warm-up runs
    for (int w = 0; w < warmups; w++) {
        double t_start = get_time_sec();
        matrix_multiply(A, B, C, n);
        double t_end = get_time_sec();
        long rss_kb = get_peak_rss_kb();
        // CSV: language,compiler_flags,matrix_size,rep_idx,is_warmup,runtime_sec,peak_rss_kb,checksum
        printf("C,%s,%d,%d,1,%.9f,%ld,%.6f\n", opt_flag, n, w, t_end - t_start, rss_kb, C[0]);
    }

    // Benchmark repetitions
    for (int r = 0; r < reps; r++) {
        double t_start = get_time_sec();
        matrix_multiply(A, B, C, n);
        double t_end = get_time_sec();
        long rss_kb = get_peak_rss_kb();
        printf("C,%s,%d,%d,0,%.9f,%ld,%.6f\n", opt_flag, n, r, t_end - t_start, rss_kb, C[0]);
    }

    free(A);
    free(B);
    free(C);
    return 0;
}
