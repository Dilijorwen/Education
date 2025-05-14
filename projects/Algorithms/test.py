import numpy as np
import matplotlib.pyplot as plt
import random


# Функция для генерации случайного пути
def generate_random_path(start, end, max_steps=100):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Вверх, вниз, влево, вправо
    path = [start]
    current = start

    for _ in range(max_steps):
        possible_moves = []
        for d in directions:
            next_pos = (current[0] + d[0], current[1] + d[1])
            # Проверяем границы и отсутствие возврата назад
            if (0 <= next_pos[0] < 20 and 0 <= next_pos[1] < 20 and
                    (len(path) < 2 or next_pos != path[-2])):
                possible_moves.append(d)
        if not possible_moves:
            break
        move = random.choice(possible_moves)
        current = (current[0] + move[0], current[1] + move[1])
        path.append(current)
        if current == end:
            return path
    return None  # Путь не достиг цели


# Функция для поиска путей методом Монте-Карло
def monte_carlo_path_search(start, end, num_simulations):
    paths = []
    for sim in range(num_simulations):
        path = generate_random_path(start, end)
        if path:
            paths.append(path)
        if sim % 100 == 0:
            print(f'Прошло {sim} итераций')
    return paths


# Функция для визуализации кратчайшего пути
def visualize_shortest_path(n, shortest_path):
    grid = np.zeros((n, n))
    for i, j in shortest_path:
        grid[i, j] = 1  # Закрашиваем ячейки пути
    fig, ax = plt.subplots()
    ax.imshow(grid, cmap='Blues', alpha=0.5, interpolation='none')
    start_i, start_j = shortest_path[0]
    end_i, end_j = shortest_path[-1]
    ax.text(start_j, start_i, 'S', ha='center', va='center', color='green', fontsize=12, fontweight='bold')
    ax.text(end_j, end_i, 'E', ha='center', va='center', color='red', fontsize=12, fontweight='bold')
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5)
    ax.tick_params(which='minor', size=0)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    plt.title(f'Кратчайший путь (длина: {len(shortest_path) - 1} шагов)')
    plt.show()


# Параметры
n = 20
start_coords = (2, 7)  # Начальная точка
end_coords = (8, 17)  # Конечная точка
num_simulations = 1000  # Количество симуляций

# Запуск Монте-Карло
paths = monte_carlo_path_search(start_coords, end_coords, num_simulations)

# Проверка результатов
if not paths:
    print("Пути не найдены. Попробуйте увеличить количество симуляций.")
else:
    shortest_path = min(paths, key=len)
    print(f'Длина кратчайшего пути: {len(shortest_path) - 1} шагов')
    visualize_shortest_path(n, shortest_path)