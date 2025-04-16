import numpy as np
import matplotlib.pyplot as plt

# Параметры задачи
a = 1.0  # скорость волны
l = 1.0  # длина струны
T = 1.0  # конечное время
M = 10   # число разбиений по x
N = 10   # число разбиений по t
h = l / M    # шаг по x
tau = T / N  # шаг по t

# Сетка
x = np.linspace(0, l, M+1)  # значения x от 0 до l
t = np.linspace(0, T, N+1)  # значения t от 0 до T

# Заданные функции
def phi(x):
    """Начальное смещение"""
    return x**2 * (1 - x)

def psi(x):
    """Начальная скорость"""
    return x**2 - x

def g(x, t):
    """Внешняя сила"""
    return t * x * (1 - x)

# Инициализация массива решения
u = np.zeros((N+1, M+1))  # u[n, m] = u(x_m, t_n)

# Начальные условия
u[0, :] = phi(x)  # u(x, 0) = phi(x)

# Граничные условия
u[:, 0] = 0  # u(0, t) = 0
u[:, M] = 0  # u(l, t) = 0

# Первый временной слой (n = 1)
for m in range(1, M):
    u[1, m] = (u[0, m] +
               (tau**2 / 2) * (a**2 * (u[0, m-1] - 2*u[0, m] + u[0, m+1]) / h**2 + g(x[m], t[0])) +
               tau * psi(x[m]))

# Последующие временные слои (n = 1, 2, ..., 9)
for n in range(1, N):
    for m in range(1, M):
        u[n+1, m] = (2 * u[n, m] - u[n-1, m] +
                     a**2 * (tau**2 / h**2) * (u[n, m-1] - 2*u[n, m] + u[n, m+1]) +
                     tau**2 * g(x[m], t[n]))

# Визуализация с помощью matplotlib
plt.figure(figsize=(10, 6))  # задаем размер графика
times_to_plot = [0, 2, 4, 6, 8, 10]  # индексы n для t ≈ 0, 0.2, 0.4, 0.6, 0.8, 1.0
for n in times_to_plot:
    plt.plot(x, u[n, :], label=f't = {t[n]:.1f}')

# Настройки графика
plt.xlabel('x')  # метка оси x
plt.ylabel('u(x, t)')  # метка оси y
plt.title('Решение u(x, t) для различных моментов времени')  # заголовок
plt.legend()  # легенда
plt.grid(True)  # сетка
plt.show()  # отображение графика

print("Решение u(x, t) на t = T = 1:")
for m in range(M+1):
    print(f"x = {x[m]:.1f}, u = {u[N, m]:.6f}")