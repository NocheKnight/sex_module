from typing import Tuple, List
import numpy as np
from numpy import random
import random
from pydantic import BaseModel


def dist(point1: Tuple[float, float], point2: Tuple[float, float]):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

class GeneticsDto(BaseModel):
    points: List[Tuple[float, float]]
    prev_generation: List[List[int]]


class GeneticAlgorithm:
    mutation_rate = 0.02
    generation_size = 200
    # iteration_count = 100
    tournament_size = 10

    generation = []
    points = []

    def __init__(self, points, generation):
        self.points = points
        self.generation = generation

        if len(self.generation) == 0:
            path = [i for i in range(len(points))]

            for _ in range(self.generation_size):
                random.shuffle(path)
                self.generation.append(path)
    
    def fitness(self, chromosome):
        suma = 0
        
        for i in range(len(chromosome)):
            suma += dist(self.points[chromosome[i]], self.points[chromosome[(i + 1) % len(chromosome)]])
        
        return suma

    def select_parent(self):
        selected = random.sample(self.generation, self.tournament_size)
        return min(selected, key=lambda route: self.fitness(route))
    
    def crossover(self, parent1, parent2):
        idx = random.randint(0, len(parent1) - 1)
        child = parent1[:idx+1]
        child_set = set(child)

        for city in parent2:
            if not city in child_set:
                child.append(city)
                child_set.add(city)
        
        return child

    def mutate(self, child):
        idx1 = random.randint(0, len(self.points) - 1)
        idx2 = random.randint(0, len(self.points) - 1)

        child[idx1], child[idx2] = child[idx2], child[idx1]
        return child

    def run(self):
        # for _ in range(self.iteration_count):
        next_generation = []

        for _ in range(self.generation_size // 2):
            parent1 = self.select_parent()
            parent2 = self.select_parent()

            child1 = self.crossover(parent1, parent2)
            child2 = self.crossover(parent2, parent1)
            

            if random.random() < self.mutation_rate:
                child1 = self.mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self.mutate(child2)
            
            next_generation.append(child1)
            next_generation.append(child2)
        
        self.generation = next_generation
        
        answer = min(self.generation, key=lambda route: self.fitness(route))
        return [[self.points[i] for i in answer], self.fitness(answer), self.generation]


def get_exact_solution(points: List[Tuple[float, float]]):
    INFINITY = 2e9

    dp = [[INFINITY for _ in range(len(points))] for _ in range(2**len(points))]
    dp[1][0] = 0

    for mask in range(2, 2 ** len(points)):
        for cur_city in range(0, len(points)):
            if not (mask & (2**cur_city)):
                continue
            for prev_city in range(0, len(points)):
                if cur_city == prev_city or not (mask & (2**prev_city)):
                    continue
                dp[mask][cur_city] = min(dp[mask][cur_city], dp[mask ^ (2**cur_city)][prev_city] + dist(points[cur_city], points[prev_city]))
    
    min_dist = INFINITY
    last_city = -1
    for i in range(0, len(points)):
        cur_dist = dp[2**len(points) - 1][i] + dist(points[0], points[i])
        if cur_dist < min_dist:
            min_dist = cur_dist
            last_city = i
    
    path = [last_city]
    cur_mask = 2**len(points) - 1
    while last_city != 0:
        for i in range(0, len(points)):
            if dp[cur_mask ^ (2**last_city)][i] + dist(points[last_city], points[i]) == dp[cur_mask][last_city]:
                cur_mask = cur_mask ^ (2**last_city)
                last_city = i
                path.append(last_city)
                break
    
    return ([points[i] for i in path], min_dist)
