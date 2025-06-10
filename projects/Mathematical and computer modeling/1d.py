#!/usr/bin/env python
"""1‑D linear advection on a periodic domain.

* **Explicit**   – Upwind (1‑st order).
* **Implicit**   – Implicit‑upwind (backward Euler in time, upwind in space).
* **Semi‑implicit** – Crank–Nicolson (2‑nd order in time, central in space).

Initial profiles:
  • **cosine_bump** – гладкий компактный горб
  • **triangle**    – линейный пилообразный импульс

Запуск без аргументов рассчитывает 6 комбинаций (3 схемы × 2 IC), строит
графики и выводит относ. погрешность массы (≈ 1e‑15).

Зависимости: NumPy, Matplotlib.
"""

import math
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Grid / time parameters (periodic BC)
# ---------------------------------------------------------------------------

class Params:
    def __init__(self, L=5.0, c=1.0, Nx=150, CFL=0.8, t_end=5.0):
        self.L, self.c, self.Nx, self.CFL, self.t_end = L, c, Nx, CFL, t_end
    @property
    def dx(self): return self.L / self.Nx
    @property
    def dt(self): return self.CFL * self.dx / self.c
    @property
    def Nt(self): return int(math.ceil(self.t_end / self.dt))
    @property
    def x(self): return np.linspace(0.0, self.L, self.Nx + 1, endpoint=False)

# discrete mass --------------------------------------------------------------

def _mass(u_layer, dx):
    return float(dx * u_layer.sum())

# ---------------------------------------------------------------------------
# Improved initial conditions
# ---------------------------------------------------------------------------

def ic_cosine_bump(x, p):
    """Smooth bump based on half‑cosine, compact support on [0.25L, 0.75L]."""
    w = 0.25 * p.L
    x0 = 0.5 * p.L
    mask = np.abs(x - x0) < w
    y = 0.5 * (1 + np.cos(np.pi * (x - x0) / w))
    return y * mask.astype(float)


def ic_triangle(x, p):
    """Symmetric triangular pulse spanning the whole domain."""
    return np.where(x < 0.5 * p.L, 2 * x / p.L, 2 * (1 - x / p.L))

IC_FNS = {
    "cosine_bump": ic_cosine_bump,
    "triangle":     ic_triangle,
}

# roll helpers ---------------------------------------------------------------

def _roll(u):
    return np.roll(u, 1), u, np.roll(u, -1)

# ---------------------------------------------------------------------------
# 1) Explicit upwind (Godunov)
# ---------------------------------------------------------------------------

def explicit_upwind(u0, p):
    k = p.c * p.dt / p.dx
    u = np.empty((p.Nt + 1, u0.size)); u[0] = u0
    for n in range(p.Nt):
        um1, uj, _ = _roll(u[n])
        u[n+1] = uj - k * (uj - um1)
    return u

# ---------------------------------------------------------------------------
# 2) Implicit‑upwind (backward Euler in time)
# ---------------------------------------------------------------------------

def _build_matrix_implicit_upwind(N, k):
    A = np.eye(N) * (1.0 + k)
    for j in range(N):
        A[j, (j - 1) % N] = -k
    return A


def implicit_upwind(u0, p):
    k = p.c * p.dt / p.dx
    N = u0.size
    LU = np.linalg.inv(_build_matrix_implicit_upwind(N, k))
    u = np.empty((p.Nt + 1, N)); u[0] = u0
    for n in range(p.Nt):
        u[n+1] = LU @ u[n]
    return u

# ---------------------------------------------------------------------------
# 3) Crank–Nicolson (semi‑implicit)
# ---------------------------------------------------------------------------

def _build_matrix_cn(N, k):
    A = np.eye(N)
    for j in range(N):
        A[j, (j + 1) % N] +=  k / 2.0
        A[j, (j - 1) % N] += -k / 2.0
    return A


def crank_nicolson(u0, p):
    k = p.c * p.dt / p.dx
    N = u0.size
    LU = np.linalg.inv(_build_matrix_cn(N, k))
    u = np.empty((p.Nt + 1, N)); u[0] = u0
    for n in range(p.Nt):
        up1 = np.roll(u[n], -1)
        um1 = np.roll(u[n],  1)
        rhs = u[n] - 0.5 * k * (up1 - um1)
        u[n+1] = LU @ rhs
    return u

SCHEMES = {
    "explicit": explicit_upwind,
    "implicit": implicit_upwind,
    "semi_implicit": crank_nicolson,
}

# ---------------------------------------------------------------------------
# Plot snapshots
# ---------------------------------------------------------------------------

def plot_snapshots(x, u, p, title):
    times  = np.linspace(0.0, p.t_end, 5)
    layers = (times / p.dt).astype(int)
    for t, n in zip(times, layers):
        plt.plot(x, u[n], label=f"t={t:.2f}")
    plt.title(title)
    plt.xlabel("x"); plt.ylabel("u")
    plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

# ---------------------------------------------------------------------------
# Run all experiments
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    p = Params()
    x = p.x
    for scheme_name, solver in SCHEMES.items():
        for ic_name, ic_fn in IC_FNS.items():
            u0 = ic_fn(x, p)
            u  = solver(u0, p)
            plot_snapshots(x, u, p, f"{scheme_name} – {ic_name}")
            m0   = _mass(u[0], p.dx)
            mend = _mass(u[-1], p.dx)
            print(f"{scheme_name:13s} {ic_name:12s} rel_mass_err = {abs(mend-m0)/max(abs(m0),1e-15):.2e}")
