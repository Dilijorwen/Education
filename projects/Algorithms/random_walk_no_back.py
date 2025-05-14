import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Функция для создания матрицы смежности для графа 20x20
def create_adjacency_matrix(n):
    adj = np.zeros((n*n, n*n))
    for i in range(n):
        for j in range(n):
            index = i*n + j
            if i > 0:  # Вверх
                adj[index, index - n] = 1
            if i < n - 1:  # Вниз
                adj[index, index + n] = 1
            if j > 0:  # Влево
                adj[index, index - 1] = 1
            if j < n - 1:  # Вправо
                adj[index, index + 1] = 1
    return adj

# Модифицированная функция случайного блуждания, предотвращающая возврат назад
def random_walk(adj, start, end, num_sim):
    n = adj.shape[0]
    paths = []  # Список для хранения всех путей
    for sim in range(num_sim):
        curr = start
        path = [start]  # Текущий путь начинается с начальной точки
        previous = None  # Инициализируем previous как None
        while curr != end:
            neighbors = np.where(adj[curr, :] > 0)[0]
            if previous is not None:
                neighbors = [n for n in neighbors if n != previous]  # Исключаем предыдущую вершину
            next_node = np.random.choice(neighbors)
            path.append(next_node)
            previous = curr  # Обновляем previous
            curr = next_node
        paths.append(path)  # Сохраняем путь, когда достигли конечной точки
        if sim % 100 == 0:
            print(f'Прошло {sim} итераций')
    return paths

# Функция для визуализации кратчайшего пути
def visualize_shortest_path(n, shortest_path):
    grid = np.zeros((n, n))
    for node in shortest_path:
        i, j = divmod(node, n)
        grid[i, j] = 1  # Закрашиваем клетки пути
    fig, ax = plt.subplots()
    # Отображаем сетку с полупрозрачными закрашенными клетками пути
    ax.imshow(grid, cmap='Reds', alpha=0.3, interpolation='none')
    # Добавляем стрелки между центрами клеток
    for k in range(len(shortest_path) - 1):
        node1 = shortest_path[k]
        node2 = shortest_path[k + 1]
        i1, j1 = divmod(node1, n)
        i2, j2 = divmod(node2, n)
        # Создаем стрелку с толстой линией и крупным наконечником
        arrow = patches.FancyArrowPatch(
            (j1, i1),
            (j2, i2),
            mutation_scale=10,
            color='red',
            arrowstyle='->',
            linewidth=1,
            shrinkA=0,
            shrinkB=0
        )
        ax.add_patch(arrow)
    # Разметка начальной и конечной точек
    start_i, start_j = divmod(shortest_path[0], n)
    end_i, end_j = divmod(shortest_path[-1], n)
    ax.text(start_j, start_i, 'S', ha='center', va='center',
            color='blue', fontsize=14, weight='bold')
    ax.text(end_j, end_i, 'E', ha='center', va='center',
            color='green', fontsize=14, weight='bold')
    # Настройка осей и сетки
    ax.set_xticks(np.arange(n) + 0.5)
    ax.set_yticks(np.arange(n) + 0.5)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(which='both', color='black', linestyle='-', linewidth=0.5)
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.show()

# Параметры
n = 20
start_coords = (2, 7)  # Начальная точка
end_coords = (8, 17)  # Конечная точка
num_sim = 1000  # Количество симуляций

# Преобразование координат в индексы
start = start_coords[0] * n + start_coords[1]
end = end_coords[0] * n + end_coords[1]

# Создание матрицы смежности
adj = create_adjacency_matrix(n)

# Запуск случайного блуждания
paths = random_walk(adj, start, end, num_sim)

# Поиск кратчайшего пути
shortest_path = min(paths, key=len)

print(shortest_path)

# Визуализация кратчайшего пути
visualize_shortest_path(n, shortest_path)