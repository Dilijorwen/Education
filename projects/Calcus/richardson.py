import numpy as np
from rotation_with_barriers import rotation_with_barriers

def v_k(k, n):
    return np.cos((2 * k - 1) * np.pi / (2 * n))


def t_k(k, tau_0, rho_0, n):
    return tau_0 / (1 + rho_0 * v_k(k, n))


def richardson_method(A, b, x0, sigma):
    tol = 10 ** -(len(sigma) - 1)
    n = 8

    eigenvalues, _ = rotation_with_barriers(A, sigma)
    positive_eigenvalues = [val for val in eigenvalues if val > 0]
    if not positive_eigenvalues:
        raise ValueError("Нет положительных собственных значений в спектре матрицы.")

    lambda_max = max(positive_eigenvalues)
    lambda_min = min(positive_eigenvalues)

    # Оптимальные параметры
    tau_0 = 2 / (lambda_min + lambda_max)
    eta = lambda_min / lambda_max
    rho_0 = (1 - eta) / (1 + eta)

    x = x0.copy()
    iterations = 0

    # Итерационный процесс
    while np.linalg.norm(A @ x - b) > tol:
        for k in range(1, n + 1):
            tk = t_k(k, tau_0, rho_0, n)
            x = x + tk * (b - A @ x)
        iterations += 1
        if iterations > 1e6:
            raise ValueError("Метод не сошёлся за заданное число итераций.")

    total_iterations = iterations * n
    return x, total_iterations, eigenvalues


def main():
    A = np.array([[2, 1],
                  [1, 2]], dtype=float)
    b = np.array([4, 5], dtype=float)
    x0 = np.zeros_like(b)

    sigma = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]

    x, iterations, eig = richardson_method(A, b, x0, sigma)


    print(f"Итерационный процесс завершился за {iterations} итераций")
    print("Решение системы Ax = b:", x)
    print(f"Собственные значения матрицы: {eig}")

    residual = b - np.dot(A, x)
    residual_norm = np.linalg.norm(residual)
    print("Невязка решения (норма вектора b - Ax):", residual_norm)
    print("Модуль разности нашего решения и решения через библиотеку np: ", np.linalg.norm(np.linalg.solve(A, b) - x))


if __name__ == '__main__':
    main()
