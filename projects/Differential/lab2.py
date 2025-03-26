import numpy as np
import matplotlib.pyplot as plt


# Вариант 4 из таблицы 1
def p(x):
    return -(x+1)


def q(x):
    # Для варианта 4 q(x) = -1 (константа)
    # Возвращаем массив такой же длины, как входной x
    return np.full_like(x, 1)


def f(x):
    return (1*x**3 + 3.2*x**2 + 1.8*x - 2)/(x + 1)**3


def exact_solution(x):
    return -x**2/(x+1)


# Граничные условия (вариант 4)
alpha0, beta0, gamma0 = 1, 0, 0.0
alpha1, beta1, gamma1 = 0, 1, 1/3

# Параметры сетки
N = 100
h = 1 / N
x = np.linspace(0, 1, N + 1)


# Коэффициенты для схемы Булеева-Тимухина (вариант 4 из таблицы 2)
def get_scheme_coefficients(p_values, q_values, h):
    r = p_values * h / 2

    # Коэффициенты схемы Булеева-Тимухина
    a = (1 + r**2 - r**2/(np.sin(np.abs(r)) + 1) - r) / h**2
    c = (1 + r**2 - r**2/(np.sin(np.abs(r)) + 1) + r) / h**2

    # Коэффициент b для внутренних узлов
    b_inner = q_values[1:-1] - a[1:-1] - c[1:-1]

    return a, b_inner, c


# Построение разностной схемы
p_values = p(x)
q_values = q(x)
a, b_inner, c = get_scheme_coefficients(p_values, q_values, h)

# Создание матрицы системы и правой части
A = np.zeros((N + 1, N + 1))
F = np.zeros(N + 1)

# Заполнение матрицы и правой части для внутренних узлов
for i in range(1, N):
    A[i, i - 1] = a[i]
    A[i, i] = b_inner[i - 1]
    A[i, i + 1] = c[i]
    F[i] = f(x[i])

# Обработка левого граничного условия (u(0) = gamma0 / alpha0, так как beta0 = 0)
A[0, 0] = 1
F[0] = gamma0 / alpha0

# Обработка правого граничного условия (u(1) = gamma1 / alpha1, так как beta1 = 0)
A[N, N] = 1
F[N] = -(2 * h * gamma1 + 4 * F[N-1] - F[N-2]) / 3


# Решение системы методом монотонной прогонки
def monotone_sweep_method(A, F, N):
    # Извлечение коэффициентов трехдиагональной матрицы
    a_sweep = np.zeros(N + 1)
    b_sweep = np.zeros(N + 1)
    c_sweep = np.zeros(N + 1)

    for i in range(N + 1):
        if i > 0:
            a_sweep[i] = A[i, i - 1]
        b_sweep[i] = A[i, i]
        if i < N:
            c_sweep[i] = A[i, i + 1]

    # Проверка условия монотонности
    for i in range(1, N):
        if abs(b_sweep[i]) < abs(a_sweep[i]) + abs(c_sweep[i]):
            print(f"Предупреждение: условие монотонности нарушено при i={i}")

    # Прямой ход
    alpha = np.zeros(N + 1)
    beta = np.zeros(N + 1)

    alpha[0] = -c_sweep[0] / b_sweep[0]
    beta[0] = F[0] / b_sweep[0]

    for i in range(1, N + 1):
        denominator = b_sweep[i] + a_sweep[i] * alpha[i - 1]
        if i < N:
            alpha[i] = -c_sweep[i] / denominator
        beta[i] = (F[i] - a_sweep[i] * beta[i - 1]) / denominator

    # Обратный ход
    y = np.zeros(N + 1)
    y[N] = beta[N]

    for i in range(N - 1, -1, -1):
        y[i] = alpha[i] * y[i + 1] + beta[i]

    return y


# Решение системы
y = monotone_sweep_method(A, F, N)

# Вычисление точного решения для сравнения
exact = exact_solution(x)

# Вычисление погрешности
error = np.abs(y - exact)
max_error = np.max(error)
print(f"Максимальная погрешность: {max_error:.10f}")

# Визуализация результатов
plt.figure(figsize=(12, 10))

plt.subplot(3, 1, 1)
plt.plot(x, y, 'b-', label='Численное решение')
plt.plot(x, exact, 'r--', label='Точное решение')
plt.grid(True)
plt.legend()
plt.title('Сравнение численного и точного решений')
plt.show()
print("\nТаблица результатов:")
print("    x      | Численное    | Точное       | Погрешность")
print("-----------+--------------+--------------+------------")
indices = np.linspace(0, N, 11, dtype=int)
for i in indices:
    print(f"{x[i]:.8f} | {y[i]:.8f} | {exact[i]:.8f} | {error[i]:.8e}")