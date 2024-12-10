import numpy as np
from gaus_piv import gauss_piv
from tabulate import tabulate

def reverse_iterations(A, x0, tol=1e-5):
    alpha = np.linalg.norm(x0, ord=np.inf)
    x_old = x0.copy()
    while True:
        x_new = gauss_piv(A, x_old / alpha)
        alpha_new = np.linalg.norm(x_new, ord=np.inf)

        if np.abs(alpha_new - alpha) < tol:
            return 1 / alpha_new, x_new

        alpha = alpha_new
        x_old = x_new


def main():
    tol = 1e-5
    matrices = [
        np.array(
            [
                [-0.168700, 0.353699, 0.008540, 0.733624],
                [0.353699, 0.056519, -0.723182, -0.076440],
                [0.008540, -0.723182, 0.015938, 0.342333],
                [0.733624, -0.076440, 0.342333, -0.045744]
            ]
        ),
        np.array(
            [
                [1.00, 0.42, 0.54, 0.66],
                [0.42, 1.00, 0.32, 0.44],
                [0.54, 0.32, 1.00, 0.22],
                [0.66, 0.44, 0.22, 1.00]
            ]
        ),
        np.array(
            [
                [2.2, 1, 0.5, 2],
                [1, 1.3, 2, 1],
                [0.5, 2, 0.5, 1.6],
                [2, 1, 1.6, 2]
            ]
        )
    ]

    for i in range(len(matrices)):
        print(f"Матрица №{i + 1}")
        print("A:", tabulate(matrices[i]), sep="\n")
        x0 = np.ones(matrices[i].shape[0])
        eigenvalue, x = reverse_iterations(matrices[i], x0, tol)
        print("Собственные значения матрицы:", np.linalg.eigvals(matrices[i]))
        print("Наименьшее собственное значение по модулю: ", eigenvalue)
        print("Вектор x:", x)
        # Ax - lmd * x
        print("Проверка:", np.linalg.norm(matrices[i] @ x - eigenvalue * x), end="\n\n")


if __name__ == '__main__':
    main()
