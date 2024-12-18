import numpy as np
import matplotlib.pyplot as plt



def f(A, x, b):
    return 0.5 * np.dot(x, np.dot(A, x)) - np.dot(b, x)

# Градиент функции f(x)
def grad_f(A, x, b):
    return np.dot(A, x) - b

# Метод координатного спуска с отслеживанием траектории
def coord_descent(A, b, x_init, h_initial, tol_f=1e-6, tol_x=1e-6, max_iter=100000):
    x = x_init.copy()
    f_current = f(A, x, b)
    f_history = [f_current]
    x_history = [x.copy()]
    n = len(x)
    iter_count = 0
    h = h_initial
    reduction_factor = 0.5
    h_min = tol_x
    max_adjust_steps = 20  # Максимальное число попыток изменения шага

    while iter_count < max_iter:
        x_prev = x.copy()
        f_prev = f_current
        improvement = False  # Флаг для отслеживания улучшений

        for i in range(n):
            # Попытка уменьшить i-ю координату на шаг h
            x_new = x.copy()
            x_new[i] -= h
            f_new = f(A, x_new, b)

            if f_new < f_current - tol_f:
                # Если функция уменьшилась, принимаем шаг
                x[i] -= h
                f_current = f_new
                f_history.append(f_current)
                x_history.append(x.copy())
                improvement = True
                # Сбрасываем шаг до начального после успешного шага
                h = h_initial
                continue  # Переходим к следующей координате

            # Попытка увеличить i-ю координату на шаг h
            x_new = x.copy()
            x_new[i] += h
            f_new = f(A, x_new, b)

            if f_new < f_current - tol_f:
                # Если функция уменьшилась, принимаем шаг
                x[i] += h
                f_current = f_new
                f_history.append(f_current)
                x_history.append(x.copy())
                improvement = True
                # Сбрасываем шаг до начального после успешного шага
                h = h_initial
                continue  # Переходим к следующей координате

            # Если ни уменьшение, ни увеличение не помогли, уменьшаем шаг
            h_temp = h

            for _ in range(max_adjust_steps):
                h_temp *= reduction_factor
                if h_temp < h_min:
                    break  # Прекращаем попытки, если шаг стал слишком мал

                # Попытка уменьшить координату с новым шагом
                x_new = x.copy()
                x_new[i] -= h_temp
                f_new = f(A, x_new, b)
                if f_new < f_current - tol_f:
                    x[i] -= h_temp
                    f_current = f_new
                    f_history.append(f_current)
                    x_history.append(x.copy())
                    improvement = True
                    h = h_initial  # Сбрасываем шаг после успешного шага
                    break  # Переходим к следующей координате

                # Попытка увеличить координату с новым шагом
                x_new = x.copy()
                x_new[i] += h_temp
                f_new = f(A, x_new, b)
                if f_new < f_current - tol_f:
                    x[i] += h_temp
                    f_current = f_new
                    f_history.append(f_current)
                    x_history.append(x.copy())
                    improvement = True
                    h = h_initial  # Сбрасываем шаг после успешного шага
                    break  # Переходим к следующей координате

            else:
                # Если после всех попыток улучшения не найдено, оставляем шаг как есть
                h = h_min

        # Проверка на сходимость
        delta_x = np.linalg.norm(x - x_prev)
        delta_f = abs(f_current - f_prev)

        if delta_x < tol_x and delta_f < tol_f:
            print(f'Сходимость достигнута за {iter_count} итераций.')
            break

        iter_count += 1

        # Опционально: вывод промежуточных результатов
        if iter_count % 1000 == 0:
            print(f'Итерация {iter_count}: f(x) = {f_current}')

        # Если за всю итерацию не было улучшений, можно уменьшить шаг глобально
        if not improvement:
            h *= reduction_factor
            if h < tol_x:
                print('Шаг слишком мал, прекращение итераций.')
                break

    else:
        print('Достигнуто максимальное число итераций без сходимости.')

    return x, f_history, x_history

# Метод градиентного спуска с отслеживанием траектории
def gradient_descent(A, b, x_init, h_initial, tol_f=1e-6, tol_x=1e-6, max_iter=100000):
    x = x_init.copy()
    f_current = f(A, x, b)
    f_history = [f_current]
    x_history = [x.copy()]
    iter_count = 0

    while iter_count < max_iter:
        x_prev = x.copy()
        f_prev = f_current
        gradient = grad_f(A, x, b)

        # Обновление координат
        x = x - h_initial * gradient
        f_current = f(A, x, b)

        f_history.append(f_current)
        x_history.append(x.copy())

        # Проверка на сходимость
        delta_x = np.linalg.norm(x - x_prev)
        delta_f = abs(f_current - f_prev)

        if delta_x < tol_x and delta_f < tol_f and np.linalg.norm(gradient, ord=2) < tol_f:
            print(f'Градиентный спуск: сходимость достигнута за {iter_count} итераций.')
            break

        iter_count += 1


    else:
        print('Градиентный спуск: достигнуто максимальное число итераций без сходимости.')

    return x, f_history, x_history


def main():
    # Исходные данные
    A = np.array([[2, 1, 0],
                  [1, 2, 1],
                  [0, 1, 2]], dtype='float')
    b = np.array([2, 0, 5], dtype='float')
    x_init = np.array([2, 8, 5], dtype='float')
    h_initial = 0.2
    # Запуск метода координатного спуска
    optimal_x_cd, f_history_cd, x_history_cd = coord_descent(A, b, x_init, h_initial)

    print('Метод координатного спуска:')
    print('Минимальное значение x:', optimal_x_cd)
    print('Значение функции в минимуме:', f_history_cd[-1])

    # Запуск метода градиентного спуска
    optimal_x_gd, f_history_gd, x_history_gd = gradient_descent(A, b, x_init, h_initial)

    print('Метод градиентного спуска:')
    print('Минимальное значение x:', optimal_x_gd)
    print('Значение функции в минимуме:', f_history_gd[-1])

    # Подготовка данных для визуализации
    x_vals_cd = [x[0] for x in x_history_cd]
    y_vals_cd = [x[1] for x in x_history_cd]
    z_vals_cd = [x[2] for x in x_history_cd]
    f_vals_cd = f_history_cd

    x_vals_gd = [x[0] for x in x_history_gd]
    y_vals_gd = [x[1] for x in x_history_gd]
    z_vals_gd = [x[2] for x in x_history_gd]
    f_vals_gd = f_history_gd

    # Создание фигуры для графиков
    fig = plt.figure(figsize=(18, 14))

    # 3D график функции и траектории
    ax1 = fig.add_subplot(221, projection='3d')
    ax1.plot(x_vals_cd, y_vals_cd, f_vals_cd, color='r', marker='o', label="Координатный спуск")
    ax1.plot(x_vals_gd, y_vals_gd, f_vals_gd, color='b', marker='x', label="Градиентный спуск")
    ax1.set_title("3D Траектория методов оптимизации")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_zlabel("f(x)")
    ax1.legend()

    # Проекция на плоскость XY
    ax2 = fig.add_subplot(222)
    ax2.plot(x_vals_cd, y_vals_cd, color='r', marker='o', label="Координатный спуск")
    ax2.plot(x_vals_gd, y_vals_gd, color='b', marker='x', label="Градиентный спуск")
    ax2.set_title("Проекция на плоскость XY")
    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")
    ax2.legend()

    ax3 = fig.add_subplot(223)
    ax3.plot(x_vals_cd, z_vals_cd, color='r', marker='o', label="Координатный спуск")
    ax3.plot(x_vals_gd, z_vals_gd, color='b', marker='x', label="Градиентный спуск")
    ax3.set_title("Проекция на плоскость XZ")
    ax3.set_xlabel("X")
    ax3.set_ylabel("Z")
    ax3.legend()


    ax4 = fig.add_subplot(224)
    ax4.plot(y_vals_cd, z_vals_cd, color='r', marker='o', label="Координатный спуск")
    ax4.plot(y_vals_gd, z_vals_gd, color='b', marker='x', label="Градиентный спуск")
    ax4.set_title("Проекция на плоскость ZY")
    ax4.set_xlabel("Y")
    ax4.set_ylabel("Z")
    ax4.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
