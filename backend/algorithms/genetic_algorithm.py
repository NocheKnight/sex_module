import numpy as np

class GeneticAlgorithm:
    def __init__(self, population_size=100, mutation_rate=0.01, crossover_rate=0.7):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population = None
        
    def initialize_population(self, chromosome_length):
        """
        Инициализация начальной популяции
        """
        self.population = np.random.randint(2, size=(self.population_size, chromosome_length))
        return self.population
    
    def fitness_function(self, chromosome):
        """
        Функция приспособленности (должна быть переопределена для конкретной задачи)
        """
        raise NotImplementedError("Функция приспособленности должна быть реализована")
    
    def select_parents(self):
        """
        Выбор родителей для скрещивания
        """
        fitness_scores = np.array([self.fitness_function(chrom) for chrom in self.population])
        parents_idx = np.random.choice(
            self.population_size,
            size=self.population_size,
            p=fitness_scores/fitness_scores.sum()
        )
        return self.population[parents_idx]
    
    def crossover(self, parents):
        """
        Скрещивание родителей
        """
        offspring = np.zeros_like(parents)
        for i in range(0, self.population_size, 2):
            if np.random.random() < self.crossover_rate:
                crossover_point = np.random.randint(1, parents.shape[1])
                offspring[i] = np.concatenate([parents[i, :crossover_point], parents[i+1, crossover_point:]])
                offspring[i+1] = np.concatenate([parents[i+1, :crossover_point], parents[i, crossover_point:]])
            else:
                offspring[i] = parents[i]
                offspring[i+1] = parents[i+1]
        return offspring
    
    def mutate(self, population):
        """
        Мутация популяции
        """
        mutation_mask = np.random.random(size=population.shape) < self.mutation_rate
        population[mutation_mask] = 1 - population[mutation_mask]
        return population
    
    def evolve(self, generations):
        """
        Эволюция популяции
        """
        for _ in range(generations):
            parents = self.select_parents()
            offspring = self.crossover(parents)
            offspring = self.mutate(offspring)
            self.population = offspring 