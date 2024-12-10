import numpy as np
from tabulate import tabulate


def optimal_elimination(A, b):
    A = A.astype(float)
    n = len(b)
    Ab = np.hstack((A, b.reshape(-1, 1)))
    # Массив для отслеживания перестановок столбцов
    column_order = np.arange(n)

    print("Начальная расширенная матрица [A|b]:")
    print(tabulate(Ab, tablefmt="fancy_grid"))
    print("\n")

    for k in range(n):
        # Поиск максимального элемента в подматрице
        sub_matrix = np.abs(Ab[k:n, k:n])
        max_idx = np.unravel_index(np.argmax(sub_matrix, axis=None), sub_matrix.shape)
        i_max = max_idx[0] + k
        j_max = max_idx[1] + k

        # Перестановка строк
        Ab[[k, i_max], :] = Ab[[i_max, k], :]

        # Перестановка столбцов
        Ab[:, [k, j_max]] = Ab[:, [j_max, k]]
        column_order[[k, j_max]] = column_order[[j_max, k]]

        if Ab[k, k] == 0:
            return "Матрица вырожденная!"

        # Нормализация главной строки
        Ab[k, :] = Ab[k, :] / Ab[k, k]

        # Обнуление элементов в столбце k
        for i in range(n):
            if i != k:
                factor = Ab[i, k]
                Ab[i, :] = Ab[i, :] - factor * Ab[k, :]

        print(f"Матрица после шага {k + 1}:")
        print(tabulate(Ab, tablefmt="fancy_grid"))
        print("\n")

    x = Ab[:, -1]

    # Приведение решения в исходный порядок переменных
    x_correct_order = np.zeros_like(x)
    for i in range(n):
        x_correct_order[column_order[i]] = x[i]


    return x_correct_order


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

# x_answer = np.array([11.092, -2.516, 0.721, -2.515, -1.605, 3.624, -4.95])
x = optimal_elimination(A, b)
print("Решение x:", x)
x_lin = np.linalg.solve(A, b)
print("Решение ling.slove:", x_lin)
print("Погрешность:", x - x_lin)
print("Норма", np.linalg.norm(x - x_lin, ord=1))

