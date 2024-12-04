import numpy as np


def gradient_descent(A, b, h_0=1, epsilon=1e-9, max_iterations=10000):
    x = np.zeros(len(b))
    h_k = h_0
    for i in range(max_iterations):
        gradient = np.dot(A, x) - b
        x_new = x - h_k * gradient

        f_k = 0.5 * x.T @ A @ x + b.T @ x
        f_k_1 = 0.5 * x_new.T @ A @ x_new + b.T @ x_new


        if f_k_1 > f_k:
            h_k /= 2

        if np.linalg.norm(gradient, ord=2) < epsilon:
            print("Шаг:", i)
            print("h:", h_k)
            break

        x = x_new

    return x


def main():

    A = np.array([
        [10.9, 1.2, 2.1, 0.9],
        [1.2, 11.2, 1.5, 2.5],
        [2.1, 1.5, 9.8, 1.3],
        [0.9, 2.5, 1.3, 12.1],
    ])
    b = np.array([-7.0, 5.3, 10.3, 24.6])

    x = gradient_descent(A, b)
    print("Координаты стационарной точки:", x)

    residual = A @ x - b
    residual_norm = np.linalg.norm(residual)
    print(f'Невязка (норма вектора Ax - b): {residual_norm}')

if __name__ == '__main__':
    np.set_printoptions(linewidth=200, suppress=True)
    main()
