from pydantic import BaseModel
from typing import List, Tuple
import numpy as np


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

class Ant:
    max_speed: float = 10
    wander_strength: float = 0.3

    position: np.ndarray
    velocity: np.ndarray
    direction: np.ndarray

    def __init__(self, home: Tuple[float, float] = [0, 0]):
        self.position = np.array([home[0], home[1]])
        self.velocity = np.array([0, 0])
        self.direction = random_unit_circle()

    def update(self, delta_time: float):
        self.direction = normalize(self.direction + random_unit_circle() * self.wander_strength)

        self.velocity = self.direction * self.max_speed
        self.position += self.velocity * delta_time

class AntDto(BaseModel):
    position: List[float]
    velocity: List[float]
    direction: List[float]

    def to_ant(self):
        ant = Ant()

        ant.position = np.array(self.position)
        ant.velocity = np.array(self.velocity)
        ant.direction = np.array(self.direction)
        
        return ant


class AntColony:
    # home position
    home: Tuple[float, float]

    # for each food source [x, y, food_cnt]
    food_sources: List[Tuple[float, float, float]]

    ants: List[Ant]

    def __init__(self, home: Tuple[float, float] = [0, 0], colony_size: int = 0):
        super().__init__()
        self.ants = [Ant(home) for _ in range(colony_size)]
        self.home = home
        self.food_sources = []

    def update(self, delta_time):
        for ant in self.ants:
            ant.update(delta_time)
    
    def denumpy_array(self, arr: np.ndarray):
        return [float(el) for el in arr]

    def to_json(self):
        return {
            "home": self.home,
            "food_sources": self.food_sources,
            "ants": [{
                "position": self.denumpy_array(ant.position),
                "velocity": self.denumpy_array(ant.velocity),
                "direction": self.denumpy_array(ant.direction)
            } for ant in self.ants]
        }

class AntColonyDto(BaseModel):
        # home position
    home: Tuple[float, float]

    # for each food source [x, y, food_cnt]
    food_sources: List[Tuple[float, float, float]]

    ants: List[AntDto]

    def to_colony(self):
        colony = AntColony()
        
        colony.home = self.home
        colony.food_sources = self.food_sources
        colony.ants = [ant.to_ant() for ant in self.ants]

        return colony
