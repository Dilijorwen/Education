import numpy as np

def gradient_descent(A, b, h_0=1, epsilon=1e-9, max_iterations=10000):
    x = np.zeros(len(b))
    h_k = h_0
    for i in range(max_iterations):
        gradient = A @ x + b
        x_new = x - h_k * gradient

        f_k = 0.5 * x.T @ A @ x + b.T @ x
        f_k_1 = 0.5 * x_new.T @ A @ x_new + b.T @ x_new


        if f_k_1 > f_k:
            h_k /= 2

        if np.linalg.norm(gradient, ord=2) < epsilon:
            print("Шаг:", i, end="\n\n")
            print("h:", h_k, end="\n\n")
            break
        # if np.abs(np.linalg.norm(x_new, ord=2) - np.linalg.norm(x, ord=2)) < epsilon:
        #     print("Шаг:", i, end="\n\n")
        #     print("h:", h_k, end="\n\n")
        #     break
        if np.abs(f_k_1 - f_k) < epsilon:
            print("Шаг:", i, end="\n\n")
            print("h:", h_k, end="\n\n")
            break

        x = x_new

    eigenvalues = np.linalg.eigvals(A)
    if all(eigenvalues > 0):
        point_type = "минимум"
    elif all(eigenvalues < 0):
        point_type = "максимум"
    else:
        point_type = "седловая точка"

    f_min = 0.5 * x.T @ A @ x + b.T @ x

    return x, point_type, f_min

A = np.array([[2, 1, -1],
              [1, 3, 2],
              [-1, 2, 4]])
b = np.array([1, 4, 3])

x, point_type, f_min = gradient_descent(A, b)
print("Координаты стационарной точки:", x, end="\n\n")
print("Тип стационарной точки:", point_type, end="\n\n")
print("Значение функции в стационарной точке:", f_min)





# import numpy as np
#
# def gradient_descent(A, b, epsilon=1e-9, max_iterations=10000):
#     x = np.zeros(len(b))  # Начальная точка
#
#     for i in range(max_iterations):
#         gradient = A @ x + b
#         grad_norm = np.linalg.norm(gradient)
#         if grad_norm < epsilon:
#             break
#
#         h_k = (gradient @ gradient) / (gradient @ A @ gradient)
#
#         x_new = x - h_k * gradient
#
#         x = x_new
#
#     eigenvalues = np.linalg.eigvals(A)
#     if np.all(eigenvalues > 0):
#         point_type = "минимум"
#     elif np.all(eigenvalues < 0):
#         point_type = "максимум"
#     else:
#         point_type = "седловая точка"
#
#     # Значение функции в найденной точке
#     f_min = 0.5 * x.T @ A @ x + b.T @ x
#
#     return x, point_type, f_min
#
# A = np.array([[2, 1, -1],
#               [1, 3, 2],
#               [-1, 2, 4]])
# b = np.array([1, 4, 3])
#
# x, point_type, f_min = gradient_descent(A, b)
# print("Координаты стационарной точки:", x)
# print("Тип стационарной точки:", point_type)
# print("Значение функции в стационарной точке:", f_min)

