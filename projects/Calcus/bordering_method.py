import numpy as np
from tabulate import tabulate

def get_inv(A):
    n = len(A)
    A_inv = np.zeros(A.shape)

    for i in range(n):
        A_i = A[:i+1, :i+1]
        if i == 0:
            A_inv = np.array([[1 / A_i[0, 0]]], dtype=float)
        else:
            # Разбиваем матрицу на блоки
            A11 = A_inv
            a12 = A[:i, i:i+1]
            a21 = A[i:i+1, :i]
            alpha = A[i, i]


            S = alpha - (a21 @ A11 @ a12)[0, 0]

            # Вычисляем блоки обратной матрицы
            B11_new = A11 + (A11 @ a12 @ a21 @ A11) / S
            b12_new = -(A11 @ a12) / S
            b21_new = -(a21 @ A11) / S
            beta_new = np.array([[1 / S]])

            # Собираем итоговую матрицу
            top = np.hstack((B11_new, b12_new))
            bottom = np.hstack((b21_new, beta_new))
            A_inv = np.vstack((top, bottom))

    return A_inv



def main():
    A = np.array([
        [0.411, 0.421, -0.333, 0.313, -0.141, -0.381, 0.245],
        [0.241, 0.705, 0.139, -0.409, 0.321, 0.0625, 0.101],
        [0.123, -0.239, 0.502, 0.901, 0.243, 0.819, 0.321],
        [0.413, 0.309, 0.801, 0.865, 0.423, 0.118, 0.183],
        [0.241, -0.221, -0.243, 0.134, 1.274, 0.712, 0.423],
        [0.281, 0.525, 0.719, 0.118, -0.974, 0.808, 0.923],
        [0.246, -0.301, 0.231, 0.813, -0.702, 1.223, 1.105],
    ])
    b = np.array([0.096, 1.252, 1.024, 1.023, 1.155, 1.937, 1.673])

    A_inv = get_inv(A)
    x = np.dot(A_inv, b)
    print("Решение системы Ax = b", x, end="\n\n")

    residual = b - np.dot(A, x)
    residual_norm = np.linalg.norm(residual)
    print("Невязка решения (норма вектора b - Ax):", residual_norm, end="\n\n")

    print(tabulate(np.dot(A, A_inv)))


if __name__ == "__main__":
    main()
