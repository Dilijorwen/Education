import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def f(x, y):
    return x + y


def exact_solution(x):
    return 2 * np.exp(x) - x - 1


def runge_kutta_3(f, x0, y0, x_end, h):
    x_values = np.arange(x0, x_end + h, h)
    y_values = np.zeros_like(x_values)
    y_values[0] = y0

    for i in range(1, len(x_values)):
        x_n = x_values[i - 1]
        y_n = y_values[i - 1]

        k1 = f(x_n, y_n)
        k2 = f(x_n + h / 3, y_n + h / 3 * k1)
        k3 = f(x_n + h / 3, y_n + h / 3 * k2)

        y_values[i] = y_n + h / 4 * (k1 + 3 * k3)

    return x_values, y_values



x0, y0 = 0, 1
x_end = 1
h = 0.01


x_h, y_h = runge_kutta_3(f, x0, y0, x_end, h)

x_h2, y_h2 = runge_kutta_3(f, x0, y0, x_end, h / 2)

x_exact = np.linspace(x0, x_end, 100)
y_exact = exact_solution(x_exact)


exact_y_h = exact_solution(x_h)
exact_y_h2 = exact_solution(x_h2)
errors_h = np.abs(y_h - exact_y_h)
errors_h2 = np.abs(y_h2 - exact_y_h2)


data = {
    'x': x_h,
    'y (h)': y_h,
    'Точное y (h)': exact_y_h,
    'Погрешность (h)': errors_h,
    'y (h/2)': y_h2[::2],
    'Точное y (h/2)': exact_y_h2[::2],
    'Погрешность (h/2)': errors_h2[::2]
}
df = pd.DataFrame(data)
print(df)

# График
plt.plot(x_h, y_h, 'o-', label=f'h = {h}')
plt.plot(x_h2, y_h2, 's-', label=f'h = {h / 2}')
plt.plot(x_exact, y_exact, 'k-', label='Точное решение')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid()
plt.title('Решение методом Рунге-Кутта 3-го порядка')
plt.show()
