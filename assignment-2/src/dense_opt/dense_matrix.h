#ifndef DENSE_MATRIX_H
#define DENSE_MATRIX_H

#define _DARWIN_C_SOURCE
#define _POSIX_C_SOURCE 199309L
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>
#include <math.h>

#define LCG_MULTIPLIER 6364136223846793005ULL
#define LCG_ADDEND 1ULL
#define DIVISOR 9007199254740992.0 // 2^53
#define DEFAULT_BLOCK_SIZE 64

static inline uint64_t lcg_next(uint64_t *state) {
    *state = (*state * LCG_MULTIPLIER) + LCG_ADDEND;
    return *state;
}

static inline double lcg_double(uint64_t *state) {
    uint64_t val = lcg_next(state) >> 11;
    return (double)val / DIVISOR;
}

static inline void generate_dense_matrix(double *mat, int n, uint64_t seed) {
    uint64_t state = seed;
    for (int i = 0; i < n * n; i++) {
        mat[i] = lcg_double(&state);
    }
}

static inline double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static inline long get_peak_rss_kb(void) {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
#if defined(__APPLE__) && defined(__MACH__)
    return usage.ru_maxrss / 1024;
#else
    return usage.ru_maxrss;
#endif
}

/* Method 1: Canonical baseline i-j-k */
static inline void matmul_ijk(const double *A, const double *B, double *C, int n) {
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

/* Method 2: Loop reordered i-k-j (stride-1 on B and C) */
static inline void matmul_ikj(const double *A, const double *B, double *C, int n) {
    memset(C, 0, (size_t)n * (size_t)n * sizeof(double));
    for (int i = 0; i < n; i++) {
        int i_offset = i * n;
        for (int k = 0; k < n; k++) {
            double a_ik = A[i_offset + k];
            int k_offset = k * n;
            for (int j = 0; j < n; j++) {
                C[i_offset + j] += a_ik * B[k_offset + j];
            }
        }
    }
}

/* Method 3: Cache blocking / Tiled i-k-j */
static inline void matmul_tiled(const double *A, const double *B, double *C, int n, int block_size) {
    memset(C, 0, (size_t)n * (size_t)n * sizeof(double));
    for (int ii = 0; ii < n; ii += block_size) {
        int i_end = (ii + block_size < n) ? (ii + block_size) : n;
        for (int kk = 0; kk < n; kk += block_size) {
            int k_end = (kk + block_size < n) ? (kk + block_size) : n;
            for (int jj = 0; jj < n; jj += block_size) {
                int j_end = (jj + block_size < n) ? (jj + block_size) : n;
                for (int i = ii; i < i_end; i++) {
                    int i_offset = i * n;
                    for (int k = kk; k < k_end; k++) {
                        double a_ik = A[i_offset + k];
                        int k_offset = k * n;
                        for (int j = jj; j < j_end; j++) {
                            C[i_offset + j] += a_ik * B[k_offset + j];
                        }
                    }
                }
            }
        }
    }
}

#endif // DENSE_MATRIX_H
