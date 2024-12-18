import numpy as np
from scipy.optimize import linprog


def simplex_method(A, b, c):
    """
    Реализация симплекс-метода для максимизации функции.
    A - матрица ограничений
    b - вектор правой части
    c - вектор коэффициентов целевой функции
    """
    # Инициализация симплекс-таблицы
    m, n = A.shape
    table = np.zeros((m + 1, n + m + 1))

    # Заполнение таблицы
    table[:m, :n] = A
    table[:m, n:n + m] = np.eye(m)  # Добавляем базисные переменные
    table[:m, -1] = b
    table[-1, :n] = -c

    print("Начальная симплекс-таблица:")
    print(table)

    while np.min(table[-1, :-1]) < 0:  # Пока есть отрицательные коэффициенты в последней строке
        # Выбор ведущего столбца
        pivot_col = np.argmin(table[-1, :-1])

        # Вычисление отношения для выбора ведущей строки
        ratios = []
        for i in range(m):
            if table[i, pivot_col] > 0:
                ratios.append(table[i, -1] / table[i, pivot_col])
            else:
                ratios.append(float('inf'))  # Исключаем отрицательные элементы

        pivot_row = np.argmin(ratios)
        if ratios[pivot_row] == float('inf'):
            raise Exception("Задача не имеет решений (неограниченная).")

        # Нормализация ведущей строки
        table[pivot_row, :] /= table[pivot_row, pivot_col]

        # Обновление остальных строк
        for i in range(m + 1):
            if i != pivot_row:
                table[i, :] -= table[i, pivot_col] * table[pivot_row, :]

        print("\nОбновлённая симплекс-таблица:")
        print(table)

    # Оптимальное значение и переменные
    solution = np.zeros(n)
    for i in range(m):
        basic_var_index = np.where(table[i, :n] == 1)[0]
        if len(basic_var_index) == 1:
            solution[basic_var_index[0]] = table[i, -1]

    optimal_value = table[-1, -1]
    return solution, optimal_value

A = np.array([[2, 4],
              [1, 1],
              [2, 1]])
b = np.array([560, 170, 300])
c = np.array([4, 5])


solution, optimal_value = simplex_method(A, b, c)
print("\nОптимальное решение задачи:")
print("x =", solution)
print("Оптимальное значение целевой функции:", optimal_value)

# Формирование двойственной задачи
A_dual = A.T
b_dual = -c
c_dual = b

# Решение двойственной задачи
print("\nРешение двойственной задачи:")
dual_result = linprog(c=c_dual, A_ub=-A_dual, b_ub=b_dual, method='highs')
if dual_result.success:
    print("Оптимальное значение двойственной задачи:", dual_result.fun)
    print("Оптимальное решение для двойственной задачи (y):", dual_result.x)
else:
    print("Решение не найдено для двойственной задачи.")

# 790
# 60 110
