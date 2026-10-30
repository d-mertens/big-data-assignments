#include "csr_matrix.h"

CSRMatrix *csr_create(int nrows, int ncols, int nnz) {
    CSRMatrix *mat = (CSRMatrix *)malloc(sizeof(CSRMatrix));
    if (!mat) return NULL;

    mat->nrows = nrows;
    mat->ncols = ncols;
    mat->nnz = nnz;

    mat->row_ptr = (int *)malloc(((size_t)nrows + 1) * sizeof(int));
    mat->col_indices = (nnz > 0) ? (int *)malloc((size_t)nnz * sizeof(int)) : NULL;
    mat->values = (nnz > 0) ? (double *)malloc((size_t)nnz * sizeof(double)) : NULL;

    if (!mat->row_ptr || (nnz > 0 && (!mat->col_indices || !mat->values))) {
        csr_free(mat);
        return NULL;
    }

    return mat;
}

void csr_free(CSRMatrix *mat) {
    if (!mat) return;
    if (mat->row_ptr) free(mat->row_ptr);
    if (mat->col_indices) free(mat->col_indices);
    if (mat->values) free(mat->values);
    free(mat);
}

CSRMatrix *csr_from_dense(const double *dense, int n, double zero_tolerance) {
    int nnz = 0;
    for (int i = 0; i < n * n; i++) {
        if (fabs(dense[i]) > zero_tolerance) {
            nnz++;
        }
    }

    CSRMatrix *mat = csr_create(n, n, nnz);
    if (!mat) return NULL;

    int idx = 0;
    mat->row_ptr[0] = 0;
    for (int i = 0; i < n; i++) {
        int i_offset = i * n;
        for (int j = 0; j < n; j++) {
            double val = dense[i_offset + j];
            if (fabs(val) > zero_tolerance) {
                mat->col_indices[idx] = j;
                mat->values[idx] = val;
                idx++;
            }
        }
        mat->row_ptr[i + 1] = idx;
    }

    return mat;
}

void csr_to_dense(const CSRMatrix *csr, double *dense) {
    memset(dense, 0, (size_t)csr->nrows * (size_t)csr->ncols * sizeof(double));
    for (int i = 0; i < csr->nrows; i++) {
        int row_start = csr->row_ptr[i];
        int row_end = csr->row_ptr[i + 1];
        int i_offset = i * csr->ncols;
        for (int p = row_start; p < row_end; p++) {
            int j = csr->col_indices[p];
            dense[i_offset + j] = csr->values[p];
        }
    }
}

/*
 * Gustavson's Algorithm for Sparse Matrix-Matrix Multiplication (SpGEMM)
 * Output C = A * B in CSR format.
 * Employs a dense row accumulator array and visited marker array.
 */
CSRMatrix *csr_spgemm(const CSRMatrix *A, const CSRMatrix *B) {
    if (A->ncols != B->nrows) return NULL;

    int nrows = A->nrows;
    int ncols = B->ncols;

    // Estimate initial capacity for C
    // Max nnz can be nrows * ncols, initial buffer based on nnz(A) + nnz(B)
    size_t capacity = (size_t)A->nnz * 2 + (size_t)nrows * 4;
    if (capacity < 1024) capacity = 1024;
    size_t max_possible = (size_t)nrows * (size_t)ncols;
    if (capacity > max_possible) capacity = max_possible;

    int *col_indices = (int *)malloc(capacity * sizeof(int));
    double *values = (double *)malloc(capacity * sizeof(double));
    int *row_ptr = (int *)malloc(((size_t)nrows + 1) * sizeof(int));

    if (!col_indices || !values || !row_ptr) {
        free(col_indices); free(values); free(row_ptr);
        return NULL;
    }

    double *accum = (double *)calloc((size_t)ncols, sizeof(double));
    int *marker = (int *)malloc((size_t)ncols * sizeof(int));
    int *active_cols = (int *)malloc((size_t)ncols * sizeof(int));

    if (!accum || !marker || !active_cols) {
        free(col_indices); free(values); free(row_ptr);
        free(accum); free(marker); free(active_cols);
        return NULL;
    }

    for (int j = 0; j < ncols; j++) {
        marker[j] = -1;
    }

    int total_nnz = 0;
    row_ptr[0] = 0;

    for (int i = 0; i < nrows; i++) {
        int active_count = 0;
        int a_start = A->row_ptr[i];
        int a_end = A->row_ptr[i + 1];

        for (int p = a_start; p < a_end; p++) {
            int k = A->col_indices[p];
            double a_ik = A->values[p];

            int b_start = B->row_ptr[k];
            int b_end = B->row_ptr[k + 1];

            for (int q = b_start; q < b_end; q++) {
                int j = B->col_indices[q];
                double b_kj = B->values[q];

                if (marker[j] != i) {
                    marker[j] = i;
                    active_cols[active_count++] = j;
                    accum[j] = a_ik * b_kj;
                } else {
                    accum[j] += a_ik * b_kj;
                }
            }
        }

        // Check if dynamic buffer needs growth
        if ((size_t)total_nnz + (size_t)active_count > capacity) {
            capacity = (capacity * 2 > (size_t)total_nnz + (size_t)active_count) ?
                        capacity * 2 : (size_t)total_nnz + (size_t)active_count + 1024;
            if (capacity > max_possible) capacity = max_possible;

            int *new_cols = (int *)realloc(col_indices, capacity * sizeof(int));
            double *new_vals = (double *)realloc(values, capacity * sizeof(double));
            if (!new_cols || !new_vals) {
                free(col_indices); free(values); free(row_ptr);
                free(accum); free(marker); free(active_cols);
                return NULL;
            }
            col_indices = new_cols;
            values = new_vals;
        }

        // Store non-zeros of row i into C
        for (int c = 0; c < active_count; c++) {
            int j = active_cols[c];
            double val = accum[j];
            if (fabs(val) > 1e-15) {
                col_indices[total_nnz] = j;
                values[total_nnz] = val;
                total_nnz++;
            }
            accum[j] = 0.0; // Reset accumulator for next reuse
        }

        row_ptr[i + 1] = total_nnz;
    }

    free(accum);
    free(marker);
    free(active_cols);

    // Build final CSR matrix structure
    CSRMatrix *C = (CSRMatrix *)malloc(sizeof(CSRMatrix));
    C->nrows = nrows;
    C->ncols = ncols;
    C->nnz = total_nnz;
    C->row_ptr = row_ptr;
    // Shrink arrays to exact total_nnz
    C->col_indices = (total_nnz > 0) ? (int *)realloc(col_indices, (size_t)total_nnz * sizeof(int)) : NULL;
    C->values = (total_nnz > 0) ? (double *)realloc(values, (size_t)total_nnz * sizeof(double)) : NULL;

    return C;
}
