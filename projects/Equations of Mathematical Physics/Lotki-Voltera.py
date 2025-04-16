import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Параметры модели
params = {
    'alpha': 2.0,  # коэффициент размножения жертв
    'beta': 1.0,  # вероятность поедания жертв
    'delta': 0.1,  # коэффициент прироста хищников
    'gamma': 0.8  # смертность хищников
}


def lotka_volterra(t, state, params):
    """
    Вычисляет производные для модели Лотки-Вольтерра.

    Args:
        t: Время (не используется явно, для совместимости).
        state: Вектор состояния [x, y], где x - жертвы, y - хищники.
        params: Словарь параметров модели (alpha, beta, delta, gamma).

    Returns:
        np.array: Вектор производных [dx/dt, dy/dt].
    """
    x, y = state
    dxdt = params['alpha'] * x - params['beta'] * x * y
    dydt = params['delta'] * x * y - params['gamma'] * y
    return np.array([dxdt, dydt])


def runge_kutta_4(f, x0, y0, T, dt, params):
    """
    Решает систему ОДУ методом Рунге-Кутта 4-го порядка.

    Args:
        f: Функция, задающая систему ОДУ.
        x0, y0: Начальные условия для жертв и хищников.
        T: Время моделирования.
        dt: Шаг интегрирования.
        params: Словарь параметров модели.

    Returns:
        t_values, x_values, y_values: Временной ряд и популяции.
    """
    if x0 <= 0 or y0 <= 0:
        raise ValueError("Начальные популяции должны быть положительными.")

    t_values = np.arange(0, T, dt)
    x_values = np.zeros(len(t_values))
    y_values = np.zeros(len(t_values))

    x_values[0] = x0
    y_values[0] = y0

    for i in range(1, len(t_values)):
        x, y = x_values[i - 1], y_values[i - 1]
        t = t_values[i - 1]
        state = np.array([x, y])

        # Вычисление коэффициентов Рунге-Кутта
        k1 = f(t, state, params)
        k2 = f(t + 0.5 * dt, state + 0.5 * dt * k1, params)
        k3 = f(t + 0.5 * dt, state + 0.5 * dt * k2, params)
        k4 = f(t + dt, state + dt * k3, params)

        # Обновление значений
        x_values[i] = x + (dt / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y_values[i] = y + (dt / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])

        # Проверка на отрицательные значения
        if x_values[i] < 0 or y_values[i] < 0:
            print(f"Предупреждение: Отрицательная популяция на шаге {i}. Прерывание.")
            x_values[i:] = np.nan
            y_values[i:] = np.nan
            break

    return t_values, x_values, y_values


# Начальные условия и параметры
initial_conditions = [(6, 1), (5, 3), (2, 1), (8, 2)]
T = 11.0  # Время моделирования
n = 1000  # Количество шагов
dt = T / n  # Шаг интегрирования

# Настройка стиля графиков
sns.set_theme(style="darkgrid")
plt.rcParams.update({'font.size': 12})

# График динамики популяций
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharex=True)

for x0, y0 in initial_conditions:
    t_values, x_values, y_values = runge_kutta_4(lotka_volterra, x0, y0, T, dt, params)
    ax1.plot(t_values, x_values, label=f'x0={x0}, y0={y0}', linewidth=2)
    ax2.plot(t_values, y_values, label=f'x0={x0}, y0={y0}', linewidth=2, linestyle='--')

ax1.set_xlabel("Время")
ax1.set_ylabel("Популяция жертв")
ax1.set_title("Динамика популяции жертв")
ax1.legend()

ax2.set_xlabel("Время")
ax2.set_ylabel("Популяция хищников")
ax2.set_title("Динамика популяции хищников")
ax2.legend()

plt.tight_layout()
plt.show()

# Фазовые портреты
plt.figure(figsize=(8, 6))

for x0, y0 in initial_conditions:
    t_values, x_values, y_values = runge_kutta_4(lotka_volterra, x0, y0, T, dt, params)
    plt.plot(x_values, y_values, linewidth=2, label=f'Нач. усл. ({x0}, {y0})')
    plt.plot(x_values[0], y_values[0], 'o', markersize=8, label=f'Нач. точка ({x0}, {y0})')

plt.xlabel("Жертвы")
plt.ylabel("Хищники")
plt.title("Фазовые портреты системы Лотки-Вольтерра")
plt.legend()
plt.grid(True)
plt.show()