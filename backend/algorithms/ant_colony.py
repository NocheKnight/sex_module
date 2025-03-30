import numpy as np

class AntColony:
    def __init__(self, n_ants=20, n_iterations=100, decay=0.1, alpha=1, beta=1):
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.pheromone = None
        self.distances = None
        
    def initialize(self, distances):
        """
        Инициализация феромонов и расстояний
        """
        self.distances = distances
        self.pheromone = np.ones(distances.shape) / len(distances)
        
    def select_next_city(self, current_city, unvisited):
        """
        Выбор следующего города для муравья
        """
        pheromone = self.pheromone[current_city, unvisited]
        distances = self.distances[current_city, unvisited]
        
        # Вычисление вероятностей
        probabilities = (pheromone ** self.alpha) * ((1/distances) ** self.beta)
        probabilities = probabilities / probabilities.sum()
        
        # Выбор следующего города
        next_city = np.random.choice(unvisited, p=probabilities)
        return next_city
    
    def construct_solution(self):
        """
        Построение решения одним муравьем
        """
        n_cities = len(self.distances)
        current_city = np.random.randint(n_cities)
        unvisited = list(range(n_cities))
        unvisited.remove(current_city)
        path = [current_city]
        
        while unvisited:
            next_city = self.select_next_city(current_city, unvisited)
            path.append(next_city)
            unvisited.remove(next_city)
            current_city = next_city
            
        return path
    
    def update_pheromone(self, solutions):
        """
        Обновление феромонов
        """
        # Испарение феромонов
        self.pheromone *= (1 - self.decay)
        
        # Добавление нового феромона
        for solution in solutions:
            for i in range(len(solution) - 1):
                self.pheromone[solution[i], solution[i+1]] += 1
            self.pheromone[solution[-1], solution[0]] += 1
    
    def optimize(self):
        """
        Оптимизация маршрута
        """
        best_solution = None
        best_distance = float('inf')
        
        for _ in range(self.n_iterations):
            # Построение решений всеми муравьями
            solutions = [self.construct_solution() for _ in range(self.n_ants)]
            
            # Обновление феромонов
            self.update_pheromone(solutions)
            
            # Поиск лучшего решения
            for solution in solutions:
                distance = self.calculate_distance(solution)
                if distance < best_distance:
                    best_distance = distance
                    best_solution = solution
                    
        return best_solution, best_distance
    
    def calculate_distance(self, solution):
        """
        Вычисление длины маршрута
        """
        distance = 0
        for i in range(len(solution) - 1):
            distance += self.distances[solution[i], solution[i+1]]
        distance += self.distances[solution[-1], solution[0]]
        return distance 