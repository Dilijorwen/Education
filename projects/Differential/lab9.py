import numpy as np
import pandas as pd
from scipy import integrate
import matplotlib.pyplot as plt

# Определяем интервал и сетку
a, b = 0, 1
x = np.linspace(a, b, 1000)

# Определяем базисные функции
def alpha1(x): return x
def alpha2(x): return x
def alpha3(x): return x**2
def alpha4(x): return x**2
def beta1(s): return 0.2 * s
def beta2(s): return 0.2 * s**2
def beta3(s): return 0.02 * s**2
def beta4(s): return 0.02 * s**3
def f(x): return np.exp(-x)

# Численное интегрирование для f_i
def compute_fi(beta, f):
    integrand = lambda s: beta(s) * f(s)
    result, _ = integrate.quad(integrand, a, b)
    return result

f1 = compute_fi(beta1, f)
f2 = compute_fi(beta2, f)
f3 = compute_fi(beta3, f)
f4 = compute_fi(beta4, f)

# Вычисляем A_ij
def compute_Aij(beta_i, alpha_j):
    integrand = lambda s: beta_i(s) * alpha_j(s)
    result, _ = integrate.quad(integrand, a, b)
    return result

A = np.zeros((4, 4))
A[0, 0] = compute_Aij(beta1, alpha1)
A[0, 1] = compute_Aij(beta1, alpha2)
A[0, 2] = compute_Aij(beta1, alpha3)
A[0, 3] = compute_Aij(beta1, alpha4)
A[1, 0] = compute_Aij(beta2, alpha1)
A[1, 1] = compute_Aij(beta2, alpha2)
A[1, 2] = compute_Aij(beta2, alpha3)
A[1, 3] = compute_Aij(beta2, alpha4)
A[2, 0] = compute_Aij(beta3, alpha1)
A[2, 1] = compute_Aij(beta3, alpha2)
A[2, 2] = compute_Aij(beta3, alpha3)
A[2, 3] = compute_Aij(beta3, alpha4)
A[3, 0] = compute_Aij(beta4, alpha1)
A[3, 1] = compute_Aij(beta4, alpha2)
A[3, 2] = compute_Aij(beta4, alpha3)
A[3, 3] = compute_Aij(beta4, alpha4)

# Решаем систему C - A C = f
lambda_val = 1
b_vec = np.array([f1, f2, f3, f4])
A_system = np.eye(4) - lambda_val * A
C = np.linalg.solve(A_system, b_vec)

# Приближённое решение
def u_approx(x, C):
    return f(x) + ((C[0] + C[1]) * x + (C[2] + C[3]) * x**2)

# Вычисляем u(x) для графика
u_x = u_approx(x, C)

# Выводим результаты
print("Коэффициенты C:", C)
print("Приближённое u(x) в точках x=0, 0.5, 1:")
print(u_x[0], u_x[500], u_x[999])

# Создаём таблицу
points = [0, 0.5, 1]
indices = [0, 500, 999]
f_values = [f(p) for p in points]

table_data = {
    'x': points,
    'Приближённое u(x)': [u_x[i] for i in indices],
    'f(x) = e^(-x)': f_values,
    'Невязка': [abs(u_x[i] - f_values[idx]) for idx, i in enumerate(indices)]
}

df = pd.DataFrame(table_data)
print("\nТаблица с результатами:")
print(df)

# Визуализация
plt.figure(figsize=(8, 6))
plt.plot(x, u_x, label='Приближённое решение', color='blue')
plt.plot(x, np.exp(-x), label='f(x)', color='orange')
plt.xlabel('x')
plt.ylabel('u(x)')
plt.title('Решение интегрального уравнения')
plt.legend()
plt.grid(True)
plt.show()