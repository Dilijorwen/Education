import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from scipy.interpolate import make_interp_spline
from tabulate import tabulate

np.set_printoptions(suppress=True)

# ---------------------------------------------------------------------------
# Коэффициенты ОДУ и точное решение
# ---------------------------------------------------------------------------

def p(x):
    return 4 * x / (x**2 + 1)


def q(x):
    return -1 / (x**2 + 1)


def f(x):
    return -3 / (x**2 + 1) ** 2


def u_exact(x):
    return 1 / (x**2 + 1)


# ---------------------------------------------------------------------------
# Построение разностной схемы и sparse‑матрицы
# ---------------------------------------------------------------------------

def build_system(N: int, a: float = 0.0, b: float = 1.0):

    x = np.linspace(a, b, N + 1)
    h = (b - a) / N

    # Внутренние узлы
    xi = x[1:-1]
    pi, qi, fi = p(xi), q(xi), f(xi)

    lower = 1 / h**2 - pi / (2 * h)      # a_i (смещение -1)
    main  = -2 / h**2 + qi               # b_i (смещение  0)
    upper = 1 / h**2 + pi / (2 * h)      # c_i (смещение +1)

    # Диагонали (numpy автоматически заполняет нулями)
    diag0  = np.zeros(N + 1)       # главная  (0)
    diag_p1 = np.zeros(N)          # +1       (1)
    diag_m1 = np.zeros(N)          # -1      (-1)
    diag_p2 = np.zeros(N - 1)      # +2       (2)

    # Заполнение внутренних узлов (i = 1..N-1)
    diag0[1:-1]   = main
    diag_p1[1:]   = upper          # длина N‑1
    diag_m1[:-1]  = lower          # длина N‑1

    # ------------------------------------------------------------------
    # Краевые условия
    # ------------------------------------------------------------------
    # Neumann u'(0)=0  →  (-u2 + 4u1 - 3u0)/(2h) = 0
    diag0[0]  = -3.0
    diag_p1[0] = 4.0
    diag_p2[0] = -1.0

    # Дирихле в x = 1
    diag0[-1] = 1.0

    # ------------------------------------------------------------------
    # Сборка sparse‑матрицы
    # ------------------------------------------------------------------
    A = diags(
        diagonals=[diag0, diag_p1, diag_m1, diag_p2],
        offsets=[0, 1, -1, 2],
        format="csr",
    )

    # Правая часть
    rhs = np.zeros(N + 1)
    rhs[1:-1] = fi
    rhs[-1] = 0.5

    return A, rhs, x


# ---------------------------------------------------------------------------
# Основной вычислительный цикл + вывод
# ---------------------------------------------------------------------------

def main(N: int = 20, *, a: float = 0.0, b: float = 1.0):
    A, rhs, x = build_system(N, a, b)
    u_num = spsolve(A, rhs)

    # Сплайн для гладкого графика
    spline = make_interp_spline(x, u_num, k=3)
    x_fine = np.linspace(a, b, 800)

    # Ошибки
    err_nodes = np.abs(u_num - u_exact(x))

    # --- Таблица
    headers = ("x", "Числ. u", "Точн. u", "|Δ|")
    rows = [
        (f"{xi:5.2f}", f"{un: .6f}", f"{ut: .6f}", f"{e: .2e}")
        for xi, un, ut, e in zip(x, u_num, u_exact(x), err_nodes)
    ]
    print("\nТаблица узловых значений:")
    print(tabulate(rows, headers=headers, tablefmt="grid", stralign="center"))
    print(f"\nМаксимальная узловая ошибка: {err_nodes.max():.3e}\n")

    # --- График
    plt.figure(figsize=(8, 5))
    plt.plot(x_fine, u_exact(x_fine), "b--", linewidth=2, label="точное u(x)")
    plt.plot(x_fine, spline(x_fine), "r-", linewidth=2, label="B‑сплайн")
    plt.plot(x, u_num, "ko", markersize=4, label="узлы ККР")
    plt.title(f"FDM + кубический B‑сплайн (N = {N})", fontsize=11)
    plt.xlabel("x"); plt.ylabel("u(x)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main(20)
