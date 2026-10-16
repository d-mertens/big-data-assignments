package matrix;

public class Verify {

    public static boolean testAnalytical2x2() {
        double[][] A = {{1.0, 2.0}, {3.0, 4.0}};
        double[][] B = {{2.0, 0.0}, {1.0, 2.0}};
        double[][] expected = {{4.0, 4.0}, {10.0, 8.0}};
        double[][] C = new double[2][2];

        MatrixMul.multiply(A, B, C, 2);

        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                if (Math.abs(C[i][j] - expected[i][j]) > 1e-12) {
                    return false;
                }
            }
        }
        return true;
    }

    public static boolean testIdentity(int n) {
        long[] state = new long[]{42L};
        double[][] A = new double[n][n];
        double[][] I = new double[n][n];
        double[][] C = new double[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                A[i][j] = MatrixMul.lcgDouble(state);
            }
            I[i][i] = 1.0;
        }

        MatrixMul.multiply(A, I, C, n);

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (Math.abs(C[i][j] - A[i][j]) > 1e-12) {
                    return false;
                }
            }
        }
        return true;
    }

    public static boolean testZero(int n) {
        long[] state = new long[]{42L};
        double[][] A = new double[n][n];
        double[][] Z = new double[n][n];
        double[][] C = new double[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                A[i][j] = MatrixMul.lcgDouble(state);
            }
        }

        MatrixMul.multiply(A, Z, C, n);

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (Math.abs(C[i][j]) > 1e-12) {
                    return false;
                }
            }
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println("Running Java correctness tests...");
        boolean p1 = testAnalytical2x2();
        System.out.println("  [1/3] Analytical 2x2 test: " + (p1 ? "PASSED" : "FAILED"));

        boolean p2 = testIdentity(32);
        System.out.println("  [2/3] Identity property test (n=32): " + (p2 ? "PASSED" : "FAILED"));

        boolean p3 = testZero(32);
        System.out.println("  [3/3] Zero annihilation test (n=32): " + (p3 ? "PASSED" : "FAILED"));

        if (p1 && p2 && p3) {
            System.out.println("ALL JAVA TESTS PASSED SUCCESSFULLY.");
            System.exit(0);
        } else {
            System.out.println("SOME JAVA TESTS FAILED.");
            System.exit(1);
        }
    }
}
