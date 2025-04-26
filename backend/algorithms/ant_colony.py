from pydantic import BaseModel
from typing import List, Tuple
import numpy as np
from math import pi


def normalize(arr: np.ndarray):
    norm = np.linalg.norm(arr)

    if norm == 0:
        return arr
    return arr / norm


def random_unit_circle():
    arr = np.random.rand(2)
    arr[0] -= 0.5
    arr[1] -= 0.5

    return normalize(arr)


def circle_intersect(center1: Tuple[float, float], rad1: float, center2: Tuple[float, float], rad2: float) -> bool:
    return ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** .5 <= rad1 + rad2


class Ant:
    max_speed: float = 10
    wander_strength: float = 0.2
    size: float = 2.5

    position: np.ndarray
    velocity: np.ndarray
    direction: np.ndarray

    is_holding_food: bool
    current_pheromone_delay: int
    current_pheromone_strength: float

    def __init__(self, home: Tuple[float, float] = [0, 0]):
        self.position = np.array([home[0], home[1]])
        self.velocity = np.array([0, 0])
        self.direction = random_unit_circle()
        self.is_holding_food = False
        self.current_pheromone_delay = 0
        self.current_pheromone_strength = 1
    
    def rotate_vector(self, angle: float, vec: np.ndarray):
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        return np.dot(rot_matrix, vec)
    
    def get_pheromones_in_circle(self, angle: float, distance_forward: float, circle_radius: float, pheromones: List[Tuple[float, float, float, int]]):
        current_direction = self.rotate_vector(angle, self.direction)
        current_direction = current_direction * distance_forward
        currrent_position = self.position + current_direction

        pheromones_strength = 0
        for pheromone in pheromones:
            if circle_intersect(currrent_position, circle_radius, pheromone[:2], 0) and self.is_holding_food == (pheromone[3] == 0):
                pheromones_strength += pheromone[2]
        return pheromones_strength


    
    def get_direction(self, pheromones: List[Tuple[float, float, float, int]]):
        angle = pi / 3
        distance_forward = self.size * 5
        circle_radius = self.size * 5

        left_pheromones = self.get_pheromones_in_circle(-angle, distance_forward, circle_radius, pheromones)
        center_pheromones = self.get_pheromones_in_circle(0, distance_forward, circle_radius, pheromones)
        right_pheromones = self.get_pheromones_in_circle(angle, distance_forward, circle_radius, pheromones)

        if center_pheromones >= left_pheromones and center_pheromones >= right_pheromones:
            return self.direction
        elif right_pheromones > left_pheromones:
            return self.rotate_vector(angle, self.direction)
        else:
            return self.rotate_vector(-angle, self.direction)



    def update(self, delta_time: float, pheromones: List[Tuple[float, float, float, int]]):
        self.direction = normalize(normalize(self.get_direction(pheromones)) + random_unit_circle() * self.wander_strength)

        self.velocity = self.direction * self.max_speed
        self.position += self.velocity * delta_time


class AntDto(BaseModel):
    position: List[float]
    velocity: List[float]
    direction: List[float]

    is_holding_food: bool
    current_pheromone_delay: int
    current_pheromone_strength: float

    def to_ant(self):
        ant = Ant()

        ant.position = np.array(self.position)
        ant.velocity = np.array(self.velocity)
        ant.direction = np.array(self.direction)

        ant.is_holding_food = self.is_holding_food
        ant.current_pheromone_delay = self.current_pheromone_delay
        ant.current_pheromone_strength = self.current_pheromone_strength
        
        return ant


class AntColony:
    field_size = 500

    # home position
    home: Tuple[float, float]
    home_size: float = 25

    # for each food source [x, y, food_cnt]
    food_sources: List[Tuple[float, float, float]]
    food_size: float = 25

    ants: List[Ant]

    # [x, y, durability, type]
    # 0 - from home to food
    # 1 - from food to home
    pheromones: List[Tuple[float, float, float, int]]
    pheromone_delay: int = 1
    pheromone_step: float = 0.95
    phermone_epsilon: float = 0.01

    def __init__(self, home: Tuple[float, float] = [0, 0], colony_size: int = 0):
        super().__init__()
        self.ants = [Ant(home) for _ in range(colony_size)]
        self.home = home
        self.food_sources = []
        self.pheromones = []

    def update(self, delta_time):
        # update ants
        for ant in self.ants:
            ant.update(delta_time, self.pheromones)

            if ant.position[0] < 0 or ant.position[1] < 0 or ant.position[0] > self.field_size or ant.position[1] > self.field_size:
                ant.direction = -ant.direction

            # update is_holding_food field
            if ant.is_holding_food:
                if circle_intersect(ant.position, ant.size, self.home, self.home_size):
                    ant.is_holding_food = False
                    ant.direction = -ant.direction
                    ant.current_pheromone_strength = 1
            else:
                for food_source in self.food_sources:
                    if circle_intersect(ant.position, ant.size, (food_source[0], food_source[1]), self.food_size):
                        ant.is_holding_food = True
                        ant.direction = -ant.direction
                        ant.current_pheromone_strength = food_source[2] / 100
                        break
            
            # add pheromones
            if ant.current_pheromone_delay == 0:
                self.pheromones.append((ant.position[0], ant.position[1], ant.current_pheromone_strength, 1 if ant.is_holding_food else 0))
            ant.current_pheromone_delay = (ant.current_pheromone_delay + 1) % self.pheromone_delay

            if ant.current_pheromone_strength > 0:
                ant.current_pheromone_strength *= self.pheromone_step

        
        # update pheromones
        self.pheromones = list(filter(lambda phe: phe[2] > self.phermone_epsilon, map(lambda phe: (phe[0], phe[1], phe[2] * self.pheromone_step, phe[3]), self.pheromones)))
    

    def denumpy_array(self, arr: np.ndarray):
        return [float(el) for el in arr]

    def to_json(self):
        return {
            "home": self.home,
            "food_sources": self.food_sources,
            "ants": [{
                "position": self.denumpy_array(ant.position),
                "velocity": self.denumpy_array(ant.velocity),
                "direction": self.denumpy_array(ant.direction),
                "is_holding_food": ant.is_holding_food,
                "current_pheromone_delay": ant.current_pheromone_delay,
                "current_pheromone_strength": ant.current_pheromone_strength
            } for ant in self.ants],
            "pheromones": self.pheromones
        }

class AntColonyDto(BaseModel):
        # home position
    home: Tuple[float, float]

    # for each food source [x, y, food_cnt]
    food_sources: List[Tuple[float, float, float]]

    ants: List[AntDto]
    pheromones: List[Tuple[float, float, float, int]]

    def to_colony(self):
        colony = AntColony()
        
        colony.home = self.home
        colony.food_sources = self.food_sources
        colony.ants = [ant.to_ant() for ant in self.ants]
        colony.pheromones = self.pheromones

        return colony

"""
1. Put food sources + field for ants + ui + food collision. DONE
2. Add pheromones.  DONE
3. Turn back after finding food.    DONE
4. Add food detection (pathinding)
5. Add ui for editing home
6. Add ui for editing food sources

EXTRA
1. Collision detection
    1.1 Forbid from moving outside the canvas
    1.2 Add walls
2. Add control over game speed (batches?)
3. Add ui for adding walls
4. Transparent (merging) pheromones
"""
