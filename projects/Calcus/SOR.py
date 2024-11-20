import numpy as np


def sor_method(A, b, w, tol=1e-6, max_iter=10000):
    n = len(A)
    x = np.zeros(n)  # Начальное приближение
    x_new = x.copy()

    for iteration in range(1, max_iter + 1):
        x_new = x.copy()
        for i in range(n):
            # Сумма для индексов j < i (используем x_new) и j > i (используем x)
            sigma = np.dot(A[i, :i], x_new[:i]) + np.dot(A[i, i + 1:], x[i + 1:])
            x_new[i] = (1 - w) * x[i] + (w / A[i, i]) * (b[i] - sigma)

        # Проверка на сходимость
        if np.linalg.norm(x_new - x, ord=2) < tol:
            return x_new, iteration

        x = x_new.copy()

    return x_new, max_iter


def simple(A, b, tol=1e-15, max_iter=10000):
    for i in range(A.shape[0]):
        factor = A[i, i]
        A[i, :] /= factor
        b[i] /= factor

    x = np.zeros_like(b)

    for iteration in range(max_iter):
        next_solution = np.zeros_like(x)

        for i in range(len(b)):
            residual = b[i] - np.dot(A[i, :], x)
            next_solution[i] = residual + A[i, i] * x[i]

        if np.max(np.abs(next_solution - x)) < tol:
            return next_solution, iteration + 1

        x = next_solution

    return None, max_iter


# Матрицы A и вектор b
# Пример изначальной матрицы
# A = np.array([
#     [10.9, 1.2, 2.1, 0.9],
#     [1.2, 11.2, 1.5, 2.5],
#     [2.1, 1.5, 9.8, 1.3],
#     [0.9, 2.5, 1.3, 12.1]
# ])
#
# b = np.array([-7.0, 5.3, 10.3, 24.6])

# Ваш текущий пример матрицы
A = np.array([
    [3.82, 1.02, 0.75, 0.81],
    [1.05, 4.53, 0.98, 1.53],
    [0.73, 0.85, 4.71, 0.81],
    [0.88, 0.81, 1.28, 3.50]
])

b = np.array([15.655, 22.705, 23.480, 16.110])

# Проверка строгого диагонального преобладания

# Значения w для сравнения в методе SOR
w_values = [0.01, 0.5, 1, 1.5, 1.99]
sor_results = []

for w in w_values:
    solution, iterations = sor_method(A, b, w)
    sor_results.append((w, iterations, solution))

# Решение методом простой итерации (Якоби)
jacobi_solution, jacobi_iterations = simple(A, b)

# Вывод результатов
print(f"{'Метод':<15} {'w':<6} {'Итерации':<12} {'Решение'}")
print("-" * 60)
for w, iters, sol in sor_results:
    print(f"{'SOR':<12} {w:<6} {iters:<12} {np.round(sol, 6)}")
print(f"{'Простая итерация':<12} {'-':<6} {jacobi_iterations:<12} {np.round(jacobi_solution, 6)}")

"""
При w → 0: Метод нижней релаксации (подрелаксации). Здесь обновления переменных происходят очень медленно, 
что может стабилизировать сходимость, но значительно замедляет процесс.

При w = 1: Метод сводится к стандартному методу Гаусса-Зейделя.

При w → 2: Метод верхней релаксации (надрелаксации). Это может ускорить сходимость, 
но при слишком больших значениях w метод может стать неустойчивым и начать расходиться.

Метод простой итерации (Якоби) можно рассматривать как метод без релаксации.
"""
