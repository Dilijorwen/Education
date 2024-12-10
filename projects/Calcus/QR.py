import numpy as np


def qr(A, b):
    n = A.shape[0]
    R = A.copy()
    Q = np.eye(n)

    for k in range(n - 1):
        # Определяем вектор нормали p^(k) без нормализации
        a = R[k:, k]
        sigma_k = -1 if a[0] < 0 else 1
        p_k = np.zeros_like(a)
        p_k[0] = a[0] + sigma_k * np.linalg.norm(a)
        p_k[1:] = a[1:]

        # Вычисляем матрицу отражения P_k
        P_k = np.eye(n)
        P_k[k:, k:] -= 2 * np.outer(p_k, p_k) / np.dot(p_k, p_k)

        # Применяем отражение к матрице R и вектору b
        R = P_k @ R
        Q = Q @ P_k
        b = P_k @ b

    # Теперь решаем систему Rx = Q^T b, где R - верхнетреугольная
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - np.dot(R[i, i + 1:], x[i + 1:])) / R[i, i]

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
    ])

    b = np.array([3.2, 4.3, -0.1, 3.5, 5.3, 9.0, 3.7])

    x = qr(A, b)

    print("Решение системы Ax = b:", x, end="\n\n")

    # Вычисляем невязку решения
    residual = b - np.dot(A, x)
    residual_norm = np.linalg.norm(residual, ord=2)
    print("Невязка решения (норма вектора b - Ax):", residual_norm, end="\n\n")


if __name__ == '__main__':
    main()
