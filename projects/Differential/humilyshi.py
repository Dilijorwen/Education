import numpy as np
import matplotlib.pyplot as plt


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


def check_hurwitz_stability(minors):
    return all(minor > 0 for minor in minors)


def check_mikhailov_stability(coefficients):
    hurwitz = hurwitz_matrix(coefficients)
    minors = calculate_principal_minors(hurwitz)
    return check_hurwitz_stability(minors)


def check_lyapunov_shihara_stability(coefficients):
    # Критерий Льенара-Шипара: проверка на стабильность через анализ знаков миноров
    hurwitz = hurwitz_matrix(coefficients)
    minors = calculate_principal_minors(hurwitz)
    # Если все угловые миноры положительные, то система стабильна
    return all(minor > 0 for minor in minors)


def plot_roots(coefficients):
    # Вычисляем корни полинома
    roots = np.roots(coefficients)

    # Извлекаем действительную и мнимую части корней
    real_parts = np.real(roots)
    imaginary_parts = np.imag(roots)

    # Создаем график
    plt.figure(figsize=(8, 6))
    plt.scatter(real_parts, imaginary_parts, color='red', label='Корни')

    # Настройка графика
    plt.axhline(0, color='black', linewidth=1)  # Горизонтальная ось
    plt.axvline(0, color='black', linewidth=1)  # Вертикальная ось
    plt.title('Корни полинома на комплексной плоскости')
    plt.xlabel('Действительная часть')
    plt.ylabel('Мнимая часть')

    # Подписи для корней
    for i, root in enumerate(roots):
        plt.text(real_parts[i] + 0.1, imaginary_parts[i] + 0.1, f'Root {i + 1}: {root:.2f}')

    plt.grid(True)
    plt.legend()
    plt.show()



# Пример использования
coefficients = [1, 2, 2, 3]  # Коэффициенты полинома P(s)

# Вычисление матрицы Гурвица
hurwitz = hurwitz_matrix(coefficients)
print("Матрица Гурвица:")
print(hurwitz)

# Нахождение угловых миноров
minors = calculate_principal_minors(hurwitz)
print("Угловые миноры:")
for i, minor in enumerate(minors, start=1):
    print(f"Δ{i} = {minor}")

# Проверка по критерию Гурвица
is_hurwitz_stable = check_hurwitz_stability(minors)
print("Система стабильно по критерию Гурвица:", is_hurwitz_stable)

# Проверка по критерию Михайлова
is_mikhailov_stable = check_mikhailov_stability(coefficients)
print("Система стабильно по критерию Михайлова:", is_mikhailov_stable)

# Проверка по критерию Льенара-Шипара
is_lyapunov_shihara_stable = check_lyapunov_shihara_stability(coefficients)
print("Система стабильно по критерию Льенара-Шипара:", is_lyapunov_shihara_stable)

plot_roots(coefficients)
