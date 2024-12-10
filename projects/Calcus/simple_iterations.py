import numpy as np


def simple_iteration(A, tol=1e-5, max_iter=1000):
    x = np.ones(A.shape[0])
    x = x / np.linalg.norm(x)
    eigenvalue_old = 0
    iter_count = 0

    for _ in range(max_iter):
        iter_count += 1

        y = A @ x
        eigenvalue = y @ x
        x_new = y / np.linalg.norm(y)

        if (np.linalg.norm(np.sign(eigenvalue) * x - x_new) < tol
                and abs(eigenvalue - eigenvalue_old) < tol):
            print(f"Метод завершился за {iter_count} итераций.")
            return eigenvalue, x_new

        x = x_new
        eigenvalue_old = eigenvalue

    print(f"Достигнут максимум итераций ({max_iter}) без нужной точности.")
    return eigenvalue_old, x


def main():
    tol = 1e-6
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
        print(f"Матрица №{i+1}")
        print("A:", matrices[i])
        eigenvalue, eigenvector = simple_iteration(matrices[i], tol)
        print("Собственные значения матрицы:", np.linalg.eigvals(matrices[i]))
        print("Наибольшее собственное значение по модулю:", eigenvalue)
        print("Собственный вектор соответствующий этому значению:", eigenvector)
        # Ax - lmd * x
        print("Проверка вида:", np.linalg.norm(matrices[i] @ eigenvector - eigenvalue * eigenvector), end="\n\n")


if __name__ == '__main__':
    main()
