import numpy as np
import random
import heapq
from collections import defaultdict


class AStar:
    # https: // neerc.ifmo.ru / wiki / index.php?title = % D0 % 90 % D0 % BB % D0 % B3 % D0 % BE % D1 % 80 % D0 % B8 % D1 % 82 % D0 % BC_A * & mobileaction = toggle_view_desktop
    def __init__(self):
        self.maze = None
        self.start = None
        self.end = None
        self.visited = []
        self.frontier = []

    def generate_maze(self, rows=20, cols=20, algorithm='prim'):
        """Генерирует лабиринт заданного размера."""
        self.maze = np.zeros((rows, cols), dtype=int)
        
        if algorithm == 'prim':
            self._generate_prim_maze(rows, cols)
        else:
            self._generate_kruskal_maze(rows, cols)
        
        # Устанавливаем начальную и конечную точки
        # Проверяем, что точки находятся в границах и не являются стенами
        while True:
            self.start = [random.randint(0, cols-1), random.randint(0, rows-1)]
            if self.maze[self.start[1]][self.start[0]] == 0:
                break
                
        while True:
            self.end = [random.randint(0, cols-1), random.randint(0, rows-1)]
            if self.maze[self.end[1]][self.end[0]] == 0 and self.end != self.start:
                break
        
        return {
            "maze": self.maze.tolist(),
            "start": self.start,
            "end": self.end
        }

    def _generate_prim_maze(self, rows, cols):
        """Генерирует лабиринт с использованием алгоритма Прима."""
        # Заполняем лабиринт стенами
        self.maze.fill(1)
        
        # Начинаем с случайной клетки
        start_x, start_y = random.randint(0, cols-1), random.randint(0, rows-1)
        self.maze[start_y][start_x] = 0
        
        # Находим соседей начальной клетки
        walls = []
        if start_x > 0:
            walls.append((start_x-1, start_y))
        if start_x < cols-1:
            walls.append((start_x+1, start_y))
        if start_y > 0:
            walls.append((start_x, start_y-1))
        if start_y < rows-1:
            walls.append((start_x, start_y+1))
        
        # Алгоритм Прима
        while walls:
            # Выбираем случайную стену
            wall_index = random.randint(0, len(walls)-1)
            x, y = walls[wall_index]
            walls.pop(wall_index)
            
            # Подсчитываем количество соседних проходов
            passages = 0
            if x > 0 and self.maze[y][x-1] == 0:
                passages += 1
            if x < cols-1 and self.maze[y][x+1] == 0:
                passages += 1
            if y > 0 and self.maze[y-1][x] == 0:
                passages += 1
            if y < rows-1 and self.maze[y+1][x] == 0:
                passages += 1
            
            # Если есть только один соседний проход, то стена становится проходом
            if passages == 1:
                self.maze[y][x] = 0
                
                # Добавляем новые стены
                if x > 0 and self.maze[y][x-1] == 1:
                    walls.append((x-1, y))
                if x < cols-1 and self.maze[y][x+1] == 1:
                    walls.append((x+1, y))
                if y > 0 and self.maze[y-1][x] == 1:
                    walls.append((x, y-1))
                if y < rows-1 and self.maze[y+1][x] == 1:
                    walls.append((x, y+1))
        
        # Убираем часть стен для создания нескольких путей
        for _ in range((rows * cols) // 10):
            x = random.randint(1, cols-2)
            y = random.randint(1, rows-2)
            self.maze[y][x] = 0

    def _generate_kruskal_maze(self, rows, cols):
        """Генерирует лабиринт с использованием алгоритма Краскала."""
        # Заполняем лабиринт стенами
        self.maze.fill(1)
        
        # Создаем сетку проходов (через одну клетку)
        for y in range(1, rows, 2):
            for x in range(1, cols, 2):
                if y < rows and x < cols:
                    self.maze[y][x] = 0
        
        # Создаем список всех стен, которые могут быть удалены
        walls = []
        for y in range(1, rows-1, 2):
            for x in range(2, cols-1, 2):
                if y < rows and x < cols:
                    walls.append((x, y))
        
        for y in range(2, rows-1, 2):
            for x in range(1, cols-1, 2):
                if y < rows and x < cols:
                    walls.append((x, y))
        
        # Перемешиваем стены
        random.shuffle(walls)
        
        # Создаем множества для каждой клетки прохода
        sets = {}
        for y in range(1, rows, 2):
            for x in range(1, cols, 2):
                if y < rows and x < cols:
                    sets[(x, y)] = (x, y)
        
        def find(cell):
            if sets[cell] != cell:
                sets[cell] = find(sets[cell])
            return sets[cell]
        
        def union(cell1, cell2):
            sets[find(cell1)] = find(cell2)
        
        for wall_x, wall_y in walls:
            cells = []
            
            # Находим две клетки, которые стена разделяет
            if wall_x % 2 == 0:  # Вертикальная стена
                if 0 <= wall_x-1 < cols and (wall_x - 1, wall_y) in sets:
                    cells.append((wall_x-1, wall_y))
                if wall_x+1 < cols and (wall_x+1, wall_y) in sets:
                    cells.append((wall_x+1, wall_y))
            else:  # Горизонтальная стена
                if 0 <= wall_y-1 < rows and (wall_x, wall_y - 1) in sets:
                    cells.append((wall_x, wall_y-1))
                if wall_y+1 < rows and (wall_x, wall_y+1) in sets:
                    cells.append((wall_x, wall_y+1))
            
            # Если стена разделяет две разные клетки прохода, то удаляем стену
            if len(cells) == 2 and find(cells[0]) != find(cells[1]):
                self.maze[wall_y][wall_x] = 0
                union(cells[0], cells[1])
        
        # Убираем часть стен для создания нескольких путей
        for _ in range((rows * cols) // 10):
            x = random.randint(1, cols-2)
            y = random.randint(1, rows-2)
            self.maze[y][x] = 0

    def find_path(self, maze, start, end):
        self.maze = np.array(maze)
        self.start = start
        self.end = end
        
        rows, cols = len(maze), len(maze[0])
        
        g_values = {tuple(start): 0}
        f_values = {tuple(start): self._heuristic(start, end)}
        
        # Словарь для отслеживания предыдущих узлов
        came_from = {}
        
        # Приоритетная очередь для хранения узлов
        open_set = [(self._heuristic(start, end), 0, tuple(start))]
        heapq.heapify(open_set)
        
        open_set_hash = {tuple(start)}
        closed_set = set()
        
        # Для отслеживания анимации
        visited_order = []
        frontier_order = []
        
        while open_set:
            # Получаем узел с наименьшим f-значением
            current = heapq.heappop(open_set)[2]
            open_set_hash.remove(current)
            
            # Если достигли конечной точки, восстанавливаем путь
            if current == tuple(end):
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.append(list(start))
                path.reverse()
                
                # Преобразуем множества в списки координат
                visited_list = [list(node) for node in closed_set]
                frontier_list = [list(node) for node in open_set_hash]
                
                return {
                    "path": path,
                    "visited": visited_list,
                    "frontier": frontier_list
                }
            
            # Добавляем текущий узел в закрытый набор
            closed_set.add(current)
            visited_order.append(list(current))
            
            for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                
                if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows:
                    # Проверяем, не является ли сосед стеной и не находится ли он в закрытом наборе
                    if maze[neighbor[1]][neighbor[0]] == 1 or neighbor in closed_set:
                        continue
                    
                    # Вычисляем временное g-значение
                    temp_g = g_values[current] + 1
                    
                    # Если нашли лучший путь к соседу
                    if neighbor not in open_set_hash or temp_g < g_values.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_values[neighbor] = temp_g
                        f_values[neighbor] = temp_g + self._heuristic(list(neighbor), end)
                        
                        if neighbor not in open_set_hash:
                            count = len(came_from)
                            heapq.heappush(open_set, (f_values[neighbor], count, neighbor))
                            open_set_hash.add(neighbor)
                            frontier_order.append(list(neighbor))
        
        # Если путь не найден
        return {
            "path": [],
            "visited": [list(node) for node in closed_set],
            "frontier": [list(node) for node in open_set_hash]
        }

    def update_cell(self, x, y, value):
        if 0 <= y < len(self.maze) and 0 <= x < len(self.maze[0]):
            self.maze[y][x] = value
            return True
        return False

    def set_start(self, x, y):
        if len(self.maze) > y >= 0 == self.maze[y][x] and 0 <= x < len(self.maze[0]):
            self.start = [x, y]
            return True
        return False

    def set_end(self, x, y):
        if len(self.maze) > y >= 0 == self.maze[y][x] and 0 <= x < len(self.maze[0]):
            self.end = [x, y]
            return True
        return False

    def _heuristic(self, a, b):
        """Эвристическая функция (манхэттенское расстояние)."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
