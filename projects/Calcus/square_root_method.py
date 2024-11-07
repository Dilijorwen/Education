import numpy as np

def square_root_method(A, b):
    n = A.shape[0]
    B = np.zeros(A.shape, dtype=np.complex128)  # Используем complex128 для поддержки комплексных чисел
    y = np.zeros(n, dtype=np.complex128)
    x = np.zeros(n, dtype=np.complex128)

    # Вычисление матрицы B и вектора y
    for i in range(n):
        # Расчет диагональных элементов B
        sum_b_diag = sum(B[k][i] ** 2 for k in range(i))
        diagonal_value = A[i][i] - sum_b_diag

        # Проверка на положительность диагонального значения
        if diagonal_value < 0:
            diagonal_value = np.complex128(diagonal_value)  # Преобразуем к комплексному типу

        B[i][i] = np.sqrt(diagonal_value)  # Используем np.sqrt

        # Вычисление наддиагональных элементов B
        for j in range(i + 1, n):
            sum_b_off_diag = sum(B[k][i] * B[k][j] for k in range(i))
            B[i][j] = (A[i][j] - sum_b_off_diag) / B[i][i]

        # Вычисление элементов y
        sum_y = sum(B[k][i] * y[k] for k in range(i))
        y[i] = (b[i] - sum_y) / B[i][i]

    # Вычисление вектора x
    for i in range(n - 1, -1, -1):
        sum_x = sum(B[i][k] * x[k] for k in range(i + 1, n))
        x[i] = (y[i] - sum_x) / B[i][i]

    return x

def main():
    A = np.array([
        [2.2, 4, -3, 1.5, 0.6, 2, 0.7],
        [4, 3.2, 1.5, -0.7, -0.8, 3, 1],
        [-3, 1.5, 1.8, 0.9, 3, 2, 2],
        [1.5, -0.7, 0.9, 2.2, 4, 3, 1],
        [0.6, -0.8, 3, 4, 3.2, 0.6, 0.7],
        [2, 3, 2, 3, 0.6, 2.2, 4],
        [0.7, 1, 2, 1, 0.7, 4, 3.2]
    ], dtype=np.float64)

    b = np.array([3.2, 4.3, -0.1, 3.5, 5.3, 9.0, 3.7], dtype=np.float64)

    x = square_root_method(A, b)

    print("Решение системы Ax = b:", x, end="\n\n")

    print("Решение системы Ax = b через np.linalg.solve:", np.linalg.solve(A, b), end="\n\n")

    print("Первая норма разности решения через np.linalg.solve и нашего решения:",
          np.linalg.norm(np.linalg.solve(A, b) - x, ord=1), end="\n\n")

if __name__ == '__main__':
    main()
