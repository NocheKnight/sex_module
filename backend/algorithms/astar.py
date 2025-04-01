import numpy as np
import random
import heapq


class AStar:
    # https: // neerc.ifmo.ru / wiki / index.php?title = % D0 % 90 % D0 % BB % D0 % B3 % D0 % BE % D1 % 80 % D0 % B8 % D1 % 82 % D0 % BC_A * & mobileaction = toggle_view_desktop
    def __init__(self, size=20):
        self.size = size
        self.maze = None
        self.start = None
        self.end = None
        self.path = None
        self.visited = None
        self.frontier = None

    def generate_maze(self, algorithm='prim'):
        """
        Генерация лабиринта с помощью алгоритма Прима или Краскала
        """
        if algorithm == 'prim':
            self._generate_prim_maze()
        else:
            self._generate_kruskal_maze()  # TODO

        self.start = (1, 1)
        self.maze[self.start[1]][self.start[0]] = 0

        # Ищем подходящую конечную точку
        for x in range(self.size - 2, 0, -1):
            for y in range(self.size - 2, 0, -1):
                if self.maze[y][x] == 0:
                    self.end = (x, y)
                    return self.maze

        # Если не нашли подходящую точку, создаем путь в правом нижнем углу
        self.end = (self.size - 2, self.size - 2)
        self.maze[self.end[1]][self.end[0]] = 0

        return self.maze

    def _generate_prim_maze(self):
        # Инициализация сетки (1 - стена, 0 - путь)
        self.maze = np.ones((self.size, self.size))

        start = (1, 1)
        self.maze[start[1]][start[0]] = 0

        walls = set()
        walls.add((1, 2))
        walls.add((2, 1))

        while walls:
            wall = random.choice(list(walls))
            walls.remove(wall)

            neighbors = self._get_neighbors(wall)
            paths = [n for n in neighbors if self.maze[n[1]][n[0]] == 0]

            if len(paths) == 1:
                self.maze[wall[1]][wall[0]] = 0
                for n in self._get_neighbors(wall):
                    if self.maze[n[1]][n[0]] == 1:
                        walls.add(n)

    def _generate_kruskal_maze(self):
        """
        TODO: Генерация лабиринта с помощью алгоритма Краскала
        """
        pass

    def _get_neighbors(self, cell):
        """
        Получение соседних клеток
        """
        x, y = cell
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                neighbors.append((new_x, new_y))
        return neighbors

    def heuristic(self, a, b):
        """
        Эвристическая функция (манхэттенское расстояние)
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self):
        self.visited = set()
        self.frontier = set()
        frontier = [(0, self.start, [self.start])]  # (f_score, current, path)
        g_scores = {self.start: 0}
        f_scores = {self.start: self.heuristic(self.start, self.end)}

        while frontier:
            _, current, path = heapq.heappop(frontier)

            if current == self.end:
                return path

            self.visited.add(current)

            # Проверяем все соседние клетки
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = current[0] + dx, current[1] + dy
                next_pos = (next_x, next_y)

                # Проверяем, что клетка в пределах лабиринта и не является стеной
                if (len(self.maze[0]) > next_x >= 0 == self.maze[next_y][next_x] and
                        0 <= next_y < len(self.maze) and
                        next_pos not in self.visited):

                    g_score = g_scores[current] + 1

                    if next_pos not in g_scores or g_score < g_scores[next_pos]:
                        g_scores[next_pos] = g_score
                        f_score = g_score + self.heuristic(self.end, next_pos)
                        f_scores[next_pos] = f_score

                        new_path = path + [next_pos]
                        heapq.heappush(frontier, (f_score, next_pos, new_path))
                        self.frontier.add(next_pos)

        return None

    def update_cell(self, x, y, value):
        """
        0 - путь, 1 - стена
        """
        if 0 <= x < self.size and 0 <= y < self.size:
            self.maze[x, y] = value

    def set_start(self, x, y):
        if self.size > x >= 0 == self.maze[x, y] and 0 <= y < self.size:
            self.start = (x, y)
            return True
        return False

    def set_end(self, x, y):
        if self.size > x >= 0 == self.maze[x, y] and 0 <= y < self.size:
            self.end = (x, y)
            return True
        return False
