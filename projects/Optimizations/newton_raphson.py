import numpy as np


def F(x, lambd, A, b, x0, r):
    F_vec = np.zeros(5)
    Ax_minus_b = A @ x - b
    x_minus_x0 = x - x0
    F_vec[:4] = Ax_minus_b - 2 * lambd * x_minus_x0
    F_vec[4] = x_minus_x0 @ x_minus_x0 - r ** 2
    return F_vec


def J(x, lambd, A, x0):
    J_mat = np.zeros((5, 5))
    x_minus_x0 = x - x0
    # Первые 4 строки
    for i in range(4):
        for j in range(4):
            J_mat[i, j] = A[i, j] - 2 * lambd * (1 if i == j else 0)
        J_mat[i, 4] = -2 * x_minus_x0[i]
    # Последняя строка
    J_mat[4, :4] = 2 * x_minus_x0
    J_mat[4, 4] = 0
    return J_mat


def newton_raphson(x_init, A, b, x0, r, lambd_init=0, tol=1e-6, max_iter=100):
    x = np.array(x_init, dtype=np.float64)  # Приводим x_init к типу float64
    lambd = float(lambd_init)  # Также приводим lambd к float
    for k in range(max_iter):
        F_vec = F(x, lambd, A, b, x0, r)
        J_mat = J(x, lambd, A, x0)
        try:
            delta = np.linalg.solve(J_mat, -F_vec)
        except np.linalg.LinAlgError:
            print("Якобиан вырожден на итерации", k)
            return x, lambd
        x += delta[:4]
        lambd += delta[4]
        if np.linalg.norm(delta) < tol:
            print(f"Сошлось на итерации {k}")

            f_min = 0.5 * np.dot(x.T, np.dot(A, x)) + np.dot(b, x)
            return x, lambd, f_min
    print("Не сошлось за максимальное число итераций")

    return x, lambd


def initial_points(x_0, r):
    initial_guess = []
    for i in range(len(x_0)):
        x_minus = np.array(x_0, dtype=np.float64)  # Приводим x_0 к типу float64
        x_minus[i] -= r
        initial_guess.append(x_minus)

        x_plus = np.array(x_0, dtype=np.float64)  # Приводим x_0 к типу float64
        x_plus[i] += r
        initial_guess.append(x_plus)

    return np.array(initial_guess, dtype=np.float64)  # Приводим результат к типу float64


# Запуск программы
A = np.array([
    [1, 2, 0, 0],
    [2, 2, 4, 0],
    [0, 4, 2, 1],
    [0, 0, 1, 3]
], dtype=float)

b = np.array([2, -1, -3, 1], dtype=float)
x0 = np.array([2, -1, 1, 0], dtype=float)
r = 6

initial_guesses = initial_points(x0, r)

lambd_init = 0
for i in range(len(initial_guesses)):
    # Запуск метода Ньютона-Рафсона
    print("№", i + 1)
    x_solution, lambd_solution, f_min = newton_raphson(initial_guesses[i], A, b, x0, r)

    print("Решение x:", x_solution)
    print("Значение функции в минимуме:", f_min)
    print("Множитель Лагранжа λ:", lambd_solution, end="\n\n")
