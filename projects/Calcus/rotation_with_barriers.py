import math
import numpy as np


def rotation_with_barriers(A, sigma):
    a = A.copy()
    c = np.zeros_like(a)
    n = a.shape[0]

    def sgn(value: float) -> int:
        return 1 if value >= 0 else -1

    def is_positive_definite(matrix: np.ndarray) -> bool:
        minors = [np.linalg.det(matrix[:i, :i]) for i in range(1, matrix.shape[0] + 1)]
        return all(minor > 0 for minor in minors)

    def max_diag(A: np.ndarray, size: int) -> tuple:
        max_abs_value = 0
        indices = (0, 0)
        for i in range(size):
            for j in range(i + 1, size):
                if abs(A[i, j]) > max_abs_value:
                    max_abs_value = abs(A[i, j])
                    indices = (i, j)
        return indices

    def is_converged(A: np.ndarray, sigmas: list, size: int) -> bool:
        min_sigma = min(sigmas)
        for i in range(size):
            for j in range(i + 1, size):
                if abs(A[i, j]) > min_sigma:
                    return False
        return True

    def perform_rotation(A: np.ndarray, i: int, j: int) -> np.ndarray:
        d = np.sqrt((A[i, i] - A[j, j]) ** 2 + 4 * A[i, j] ** 2)
        c = np.sqrt(0.5 * (1 + abs(A[i, i] - A[j, j]) / d))
        s = sgn(A[i, j] * (A[i, i] - A[j, j])) * np.sqrt(0.5 * (1 - abs(A[i, i] - A[j, j]) / d))

        # Обновление элементов матрицы
        C = A.copy()
        C[i, i] = c ** 2 * A[i, i] + 2 * c * s * A[i, j] + s ** 2 * A[j, j]
        C[j, j] = s ** 2 * A[i, i] - 2 * c * s * A[i, j] + c ** 2 * A[j, j]
        C[i, j] = 0.0
        C[j, i] = 0.0

        for k in range(n):
            if k != i and k != j:
                C[k, i] = c * A[k, i] + s * A[k, j]
                C[i, k] = C[k, i]
                C[k, j] = -s * A[k, i] + c * A[k, j]
                C[j, k] = C[k, j]

        return C

    if is_positive_definite(a):
        print("Матрица является положительно определённой.")
    else:
        print("Матрица не является положительно определённой.")


    iterations = 0
    while not is_converged(a, sigma, n):
        i, j = max_diag(a, n)
        a = perform_rotation(a, i, j)
        iterations += 1
        if iterations > 10000:
            print("Превышено максимальное количество итераций.")
            break

    eigenvalues = [a[i, i] for i in range(n)]
    eigenvalues.sort()

    return eigenvalues, iterations


def verify_eigenvalues(A: np.ndarray, eigenvalues, sigma):
    is_passed = True
    for idx, lambda_i in enumerate(eigenvalues):
        determinant = np.linalg.det(A - lambda_i * np.eye(A.shape[0]))
        if abs(determinant) < 10 ** (-len(sigma)):
            print(f"Собственный вектор {idx}: Удача (|det(A - λI)| = {determinant:.2e})")
        else:
            print(f"Собственный вектор {idx}: Провал |det(A - λI)| = {determinant:.2e}")
            is_passed = False
    if is_passed:
        print("Ура")
    else:
        print("Плохо")
    return is_passed


def main():
    matrices = [
        np.array(
            [
                [2.2, 1, 0.5, 2],
                [1, 1.3, 2, 1],
                [0.5, 2, 0.5, 1.6],
                [2, 1, 1.6, 2],
            ],
            dtype=float,
        ),
        np.array(
            [
                [-0.168700, 0.353699, 0.008540, 0.733624],
                [0.353699, 0.056519, -0.723182, -0.076440],
                [0.008540, -0.723182, 0.015938, 0.342333],
                [0.733624, -0.076440, 0.342333, -0.045744],
            ],
            dtype=float,
        ),
        np.array(
            [
                [1.00, 0.42, 0.54, 0.66],
                [0.42, 1.00, 0.32, 0.44],
                [0.54, 0.32, 1.00, 0.22],
                [0.66, 0.44, 0.22, 1.00],
            ],
            dtype=float,
        ),
        np.array(
            [
                [2, 1],
                [1, 2],
            ],
            dtype=float,
        ),
    ]

    sigma = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]

    for idx, matrix in enumerate(matrices, start=1):
        print(f"\n--- Матрица {idx} ---")
        print("Исходная матрица:")
        print(matrix)

        eigenvalues, iterations = rotation_with_barriers(matrix.copy(), sigma)

        print(f"\nСконвергировалось за {iterations} итераций.")
        print(f"Собственные значения: {eigenvalues}")

        print("\nПроверка собственных значений:")
        verify_eigenvalues(matrix, eigenvalues, sigma)


if __name__ == "__main__":
    main()
