import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Параметры задачи
a = 1.0  # Коэффициент теплопроводности
l = 1.0  # Длина стержня
T = 0.1  # Время окончания
M = 10   # Количество шагов по пространству
N = 100  # Количество шагов по времени
h = l / M  # Шаг по пространству
tau = T / N  # Шаг по времени

# Начальные и граничные условия
def phi(x, t):
    return 2 * x * (1 - x)

def psi(x):
    return 3 * (x**2 - x)

def gamma0(t):
    return 0

def gamma1(t):
    return 0

# Создание сетки
x = np.linspace(0, l, M+1)
t = np.linspace(0, T, N+1)
u = np.zeros((M+1, N+1))  # Массив для явного метода
u_implicit = np.zeros((M+1, N+1))  # Массив для неявного метода

# Начальное условие
u[:, 0] = psi(x)
u_implicit[:, 0] = psi(x)

# Явный метод
for n in range(N):
    for m in range(1, M):
        u[m, n+1] = u[m, n] + (a**2 * tau / h**2) * (u[m+1, n] - 2*u[m, n] + u[m-1, n]) + tau * phi(x[m], t[n])
    # Граничные условия
    u[0, n+1] = gamma0(t[n+1])
    u[M, n+1] = gamma1(t[n+1])

# Неявный метод (чисто неявная схема)
alpha = a**2 * tau / h**2
A = np.zeros((M+1, M+1))
b = np.zeros(M+1)

for n in range(N):
    for m in range(1, M):
        A[m, m-1] = -alpha
        A[m, m] = 1 + 2*alpha
        A[m, m+1] = -alpha
        b[m] = u_implicit[m, n] + tau * phi(x[m], t[n+1])
    # Граничные условия
    A[0, 0] = 1
    A[0, 1] = 0
    b[0] = gamma0(t[n+1])
    A[M, M] = 1
    A[M, M-1] = 0
    b[M] = gamma1(t[n+1])

    # Решение системы уравнений
    u_implicit[:, n+1] = np.linalg.solve(A, b)


# Сравнение результатов явного и неявного методов
plt.figure(figsize=(10, 6))
for n in range(0, N+1, N//5):
    plt.plot(x, u[:, n], '--', label=f'Явный метод, t={t[n]:.3f}')
    plt.plot(x, u_implicit[:, n], label=f'Неявный метод, t={t[n]:.3f}')
plt.title('Сравнение явного и неявного методов')
plt.xlabel('x')
plt.ylabel('u(x,t)')
plt.legend()
plt.grid()
plt.show()

# Выбор точек для сравнения (например, каждые 2 точки по пространству и каждые 10 шагов по времени)
x_indices = range(0, M+1, 2)  # Индексы точек по пространству
t_indices = range(0, N+1, N//5)  # Индексы временных слоев

# Создание таблицы для сравнения
results = []

for n in t_indices:
    for m in x_indices:
        results.append({
            'x': x[m],
            't': t[n],
            'Явный метод': u[m, n],
            'Неявный метод': u_implicit[m, n],
            'Разница': abs(u[m, n] - u_implicit[m, n])
        })

# Создание DataFrame
df = pd.DataFrame(results)

# Вывод таблицы
print("Таблица сравнения результатов явного и неявного методов:")
print(df)