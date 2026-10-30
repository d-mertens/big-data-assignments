#ifndef CSR_MATRIX_H
#define CSR_MATRIX_H

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

typedef struct {
    int nrows;
    int ncols;
    int nnz;
    int *row_ptr;      // size nrows + 1
    int *col_indices;  // size nnz
    double *values;    // size nnz
} CSRMatrix;

CSRMatrix *csr_create(int nrows, int ncols, int nnz);
void csr_free(CSRMatrix *mat);

CSRMatrix *csr_from_dense(const double *dense, int n, double zero_tolerance);
void csr_to_dense(const CSRMatrix *csr, double *dense);

/*
 * Sparse-Matrix Sparse-Matrix Multiplication (SpGEMM): C = A * B
 * Both A and B are in CSR format. Output C is constructed in CSR format.
 */
CSRMatrix *csr_spgemm(const CSRMatrix *A, const CSRMatrix *B);

/* Memory footprint calculation in bytes */
static inline size_t csr_memory_bytes(const CSRMatrix *mat) {
    if (!mat) return 0;
    return sizeof(CSRMatrix) +
           ((size_t)mat->nrows + 1) * sizeof(int) +
           ((size_t)mat->nnz) * (sizeof(int) + sizeof(double));
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

#endif // CSR_MATRIX_H
