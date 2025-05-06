import numpy as np
import matplotlib.pyplot as plt

"""Математический маятник: линейная vs нелинейная модель
---------------------------------------------------------
Интегрирование методом **симплектического Эйлера** (Euler-Cromer).

* Нелинейная:   θ'' + (g/l)·sinθ + (b/m)·θ' = F·sin(ω_f t)
* Линейная:     θ'' + (g/l)·θ   + (b/m)·θ' = F·sin(ω_f t)

Обе модели решаются одной и той же энергосохраняющей схемой;
результаты выводятся на общих графиках.
"""

g = 9.81
l = 100.0
m = 1.0

b = 0.0
F = 0.0
omega_f = np.sqrt(g / l)

theta0 = np.pi / 100
omega0 = 0

def omega_dot_nl(theta: float, omega: float, t: float) -> float:

    return -(g / l) * np.sin(theta) - (b / m) * omega + F * np.sin(omega_f * t)


def omega_dot_lin(theta: float, omega: float, t: float) -> float:
    return -(g / l) * theta - (b / m) * omega + F * np.sin(omega_f * t)



def symplectic_euler(t_start: float, t_end: float, dt: float, y0, omega_dot):
    n_steps = int(np.ceil((t_end - t_start) / dt)) + 1
    t_values = np.linspace(t_start, t_end, n_steps)

    theta = np.empty(n_steps)
    omega = np.empty(n_steps)
    theta[0], omega[0] = y0

    for i in range(1, n_steps):
        t = t_values[i - 1]
        omega[i] = omega[i - 1] + dt * omega_dot(theta[i - 1], omega[i - 1], t)
        theta[i] = theta[i - 1] + dt * omega[i]

    return t_values, np.vstack([theta, omega]).T


def draw(t_nl, sol_nl, t_lin, sol_lin):
    theta_nl, omega_nl = sol_nl.T
    theta_lin, omega_lin = sol_lin.T

    plt.figure(figsize=(12, 6))

    # Angle vs time ---------------------------------------------------------
    plt.subplot(1, 2, 1)
    plt.plot(t_nl, theta_nl, label="Нелинейная модель")
    plt.plot(t_lin, theta_lin, "--", label="Линейная модель")
    plt.scatter([t_nl[0]], [theta_nl[0]], s=40, zorder=3)
    plt.scatter([t_lin[0]], [theta_lin[0]], s=40, zorder=3)
    plt.xlabel("Время, с")
    plt.ylabel("Угол, рад")
    plt.title("Динамика математического маятника")
    plt.grid(True)
    plt.legend()

    # Phase portrait --------------------------------------------------------
    plt.subplot(1, 2, 2)
    plt.plot(theta_nl, omega_nl, label="Нелинейная модель")
    plt.plot(theta_lin, omega_lin, "--", label="Линейная модель")
    plt.scatter([theta_nl[0]], [omega_nl[0]], s=40, zorder=3)
    plt.scatter([theta_lin[0]], [omega_lin[0]], s=40, zorder=3)
    plt.xlabel("Угол, рад")
    plt.ylabel("Угловая скорость, рад/с")
    plt.title("Фазовый портрет")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    t0, t_end, dt = 0.0, 60.0, 0.025

    t_nl, sol_nl = symplectic_euler(t0, t_end, dt, [theta0, omega0], omega_dot_nl)

    t_lin, sol_lin = symplectic_euler(t0, t_end, dt, [theta0, omega0], omega_dot_lin)

    draw(t_nl, sol_nl, t_lin, sol_lin)
