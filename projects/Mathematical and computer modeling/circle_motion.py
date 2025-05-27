import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp



class CircleMotion:

    def __init__(self, omega, phi):
        self.omega = float(omega)
        self.phi = float(phi)
        self._sin_phi = np.sin(self.phi)

    def f(self, t, x):
        vx, vy = x[2], x[3]
        ax = 2 * self.omega * vy * self._sin_phi
        ay = -2 * self.omega * vx * self._sin_phi
        return np.array([vx, vy, ax, ay], dtype=float)


    def rk4(self, y0, t0, tn, h):
        if h <= 0:
            raise ValueError("Шаг h должен быть положительным")

        num = int(np.floor((tn - t0) / h)) + 1
        t_values = t0 + np.arange(num) * h

        y_values = np.zeros((num, len(y0)), dtype=float)
        y_values[0] = y0

        for i in range(num - 1):
            k1 = h * self.f(t_values[i], y_values[i])
            k2 = h * self.f(t_values[i] + h / 2, y_values[i] + k1 / 2)
            k3 = h * self.f(t_values[i] + h / 2, y_values[i] + k2 / 2)
            k4 = h * self.f(t_values[i] + h, y_values[i] + k3)
            y_values[i + 1] = y_values[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6

        return t_values, y_values

    def dop853(self, y0, t0, tn, rtol=1e-9, atol=1e-12):
        """Вызов solve_ivp с методом DOP853 и dense_output=True."""
        sol = solve_ivp(
            lambda t, x: self.f(t, x),
            (t0, tn),
            y0,
            method="DOP853",
            rtol=rtol,
            atol=atol,
            dense_output=True,
        )
        if not sol.success:
            raise RuntimeError("Интегратор DOP853 не сошёлся: " + sol.message)
        return sol



def plot_trajectories(motion, initial_conditions, t0, tn, h, use_dop=True):
    fig, ax = plt.subplots(figsize=(8, 8))

    for idx, y0 in enumerate(initial_conditions, start=1):
        if use_dop:
            sol = motion.dop853(y0, t0, tn)

            t_plot = np.linspace(t0, tn, 2000)
            y = sol.sol(t_plot).T
        else:
            _, y = motion.rk4(y0, t0, tn, h)

        ax.plot(y[:, 0], y[:, 1],label=f"Траектория {idx}")
        ax.scatter(y0[0], y0[1], marker="o", label=f"Нач. точка {y0[0], y0[1]}")

    ax.set_title("Движение во вращающейся системе координат")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    plt.show()




def run_experiments():
    initial_conditions = [
        [2.0, 0.0, -1.0, 1.0],
        [0.7, 0.2, -0.5, 0.5],
        [-1.0, 0.5, 1.0, -1.0],
        [2.0, 4.0, -2.0, 3.0],
        [6.0, 1.0, -2.0, -1.0],
        [5.0, 4.0, -0.5, -2.0],
    ]

    experiments = [
        {"omega": 1.0, "phi": np.radians(45)},
        {"omega": 2.0, "phi": np.radians(54)},
        {"omega": 1.0, "phi": np.radians(22)},
        {"omega": 2.0, "phi": np.radians(55)},
    ]

    t0, tn, h = 0.0, 200.0, 0.01

    for exp in experiments:
        phi_deg = np.degrees(exp["phi"])
        print(f"Running ω={exp['omega']}, φ={phi_deg:.0f}°")
        motion = CircleMotion(exp["omega"], exp["phi"])
        plot_trajectories(motion, initial_conditions, t0, tn, h, use_dop=True)


if __name__ == "__main__":
    run_experiments()
