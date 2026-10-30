package matrix;

import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;

public class MatrixMul {

    private static final long LCG_MULTIPLIER = 6364136223846793005L;
    private static final long LCG_ADDEND = 1L;
    private static final double DIVISOR = 9007199254740992.0; // 2^53

    public static long lcgNext(long[] state) {
        state[0] = (state[0] * LCG_MULTIPLIER) + LCG_ADDEND;
        return state[0];
    }

    public static double lcgDouble(long[] state) {
        long val = lcgNext(state) >>> 11;
        return (double) val / DIVISOR;
    }

    public static double[][] generateMatrix(int n, long seed) {
        long[] state = new long[]{seed};
        double[][] mat = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                mat[i][j] = lcgDouble(state);
            }
        }
        return mat;
    }

    /*
     * Canonical dense matrix multiplication: C = A * B
     * Loop order: i - j - k
     * Storage layout: double[][] array of arrays
     */
    public static void multiply(double[][] A, double[][] B, double[][] C, int n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) {
                    sum += A[i][k] * B[k][j];
                }
                C[i][j] = sum;
            }
        }
    }

    private static long getHeapUsedKb() {
        Runtime rt = Runtime.getRuntime();
        return (rt.totalMemory() - rt.freeMemory()) / 1024;
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: java matrix.MatrixMul <n> [repetitions] [warmup_runs] [vm_flag]");
            System.exit(1);
        }

        int n = Integer.parseInt(args[0]);
        int reps = (args.length > 1) ? Integer.parseInt(args[1]) : 5;
        int warmups = (args.length > 2) ? Integer.parseInt(args[2]) : 3;
        String vmFlag = (args.length > 3) ? args[3] : "HotSpot";

        double[][] A = generateMatrix(n, 123456789L);
        double[][] B = generateMatrix(n, 987654321L);
        double[][] C = new double[n][n];

        // Warm-up runs to ensure JIT tier compilation
        for (int w = 0; w < warmups; w++) {
            long tStart = System.nanoTime();
            multiply(A, B, C, n);
            long tEnd = System.nanoTime();
            double durationSec = (tEnd - tStart) * 1e-9;
            long heapKb = getHeapUsedKb();
            System.out.printf(java.util.Locale.US, "Java,%s,%d,%d,1,%.9f,%d,%.6f\n",
                    vmFlag, n, w, durationSec, heapKb, C[0][0]);
        }

        // Benchmark repetitions
        for (int r = 0; r < reps; r++) {
            long tStart = System.nanoTime();
            multiply(A, B, C, n);
            long tEnd = System.nanoTime();
            double durationSec = (tEnd - tStart) * 1e-9;
            long heapKb = getHeapUsedKb();
            System.out.printf(java.util.Locale.US, "Java,%s,%d,%d,0,%.9f,%d,%.6f\n",
                    vmFlag, n, r, durationSec, heapKb, C[0][0]);
        }
    }
}
