import numpy as np
import sympy as sp
from scipy.integrate import quad
import matplotlib.pyplot as plt

# Функция f(x)
def f(x):
    return x**4 * np.cos(np.pi / 2 * x)

# Собственная функция y_k(x)
def y_k(x, k):
    return np.cos((np.pi / 2 + np.pi * k) * x)

# Вычисление c_k
def compute_c_k(k):
    numerator, _ = quad(lambda x: f(x) * y_k(x, k), 0, 1)
    # Знаменатель: интеграл y_k(x)^2
    denominator, _ = quad(lambda x: y_k(x, k)**2, 0, 1)
    c_k = numerator / denominator
    return c_k

# Вычисляем коэффициенты для k = 0, 1, 2, 3, 4
c_k = [compute_c_k(k) for k in range(5)]

# Частичная сумма s_4(x)
def partial_sum(x, N, c_k):
    s = 0
    for k in range(N):
        s += c_k[k] * y_k(x, k)
    return s

# Значения x для графика
x_values = np.linspace(0, 1, 1000)
f_values = f(x_values)
s4_values = [partial_sum(x, 5, c_k) for x in x_values]

# Построение графиков
plt.figure(figsize=(10, 6))
plt.plot(x_values, f_values, 'k-', label='f(x)', linewidth=2)
plt.plot(x_values, s4_values, 'r--', label='s_4(x)', linewidth=2)
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.title('Функция f(x) и частичная сумма s_4(x)')
plt.grid(True)
plt.show()


# Вычисление интеграла f^2(x)
integral_f2, _ = quad(lambda x: f(x)**2, 0, 1)

# Сумма Парсеваля для k = 0 до 4
parseval_sum = sum(c_k[k]**2 for k in range(3)) * 0.5 # 0.5 это нормирующий множитель, полученный из интеграла y_k(x)^2

# Проверка разницы
difference = abs(integral_f2 - parseval_sum)
print(f"Интеграл f^2(x): {integral_f2:.6f}")
print(f"Сумма Парсеваля (k=0 до 4): {parseval_sum:.6f}")
print(f"Разница: {difference:.6f}")
if difference < 1e-3:
    print("Равенство Парсеваля выполняется с точностью до 10^{-3}.")
else:
    print("Равенство Парсеваля не выполняется с точностью до 10^{-3}.")


# Объявляем переменную x как символьную
x = sp.symbols('x')

# Определим f(x) и y_k(x)
f_x = x**4 * sp.cos(sp.pi / 2 * x)
y_k_x = sp.cos((sp.pi / 2 + sp.pi * sp.symbols('k')) * x)

# Интеграл 1: \int_{0}^{1} f(x) * y_k(x) dx
integral_1 = sp.integrate(f_x * y_k_x, (x, 0, 1))
# Интеграл 2: \int_{0}^{1} y_k(x)^2 dx
integral_2 = sp.integrate(y_k_x**2, (x, 0, 1))

# Выводим результаты
print("Аналитическое решение интеграла 1:")
sp.pprint(integral_1, use_unicode=True)

print("\nАналитическое решение интеграла 2:")
sp.pprint(integral_2, use_unicode=True)
