import numpy as np


def hurwitz_matrix(coefficients):
    n = len(coefficients) - 1  # Степень полинома
    hurwitz = np.zeros((n, n))  # Создаем пустую квадратную матрицу n x n

    for i in range(n):
        for j in range(n):
            # Индекс в списке коэффициентов
            index = 2 * i - j + 1
            if 0 <= index < len(coefficients):
                hurwitz[i, j] = coefficients[index]

    return hurwitz


def calculate_principal_minors(matrix):
    minors = []
    for k in range(1, len(matrix) + 1):
        sub_matrix = matrix[:k, :k]  # Выбираем ведущую подматрицу размера k x k
        determinant = np.linalg.det(sub_matrix)  # Вычисляем определитель
        minors.append(determinant)
    return minors


# Пример использования
coefficients = [1, 2, 4, 3, 2]  # Коэффициенты полинома P(s)
hurwitz = hurwitz_matrix(coefficients)
print("Матрица Гурвица:")
print(hurwitz)

# Нахождение угловых миноров
minors = calculate_principal_minors(hurwitz)
print("Угловые миноры:")
for i, minor in enumerate(minors, start=1):
    print(f"Δ{i} = {minor}")
