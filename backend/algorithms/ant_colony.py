from pydantic import BaseModel
from typing import List, Tuple
import numpy as np


def normalize(arr: np.ndarray):
    norm = np.linalg.norm(arr)

    if norm == 0:
        return arr
    return arr / norm

class Ant(BaseModel):
    max_speed: float = 2
    wander_strength: float = 1

    position: np.ndarray
    velocity: np.ndarray
    direction: np.ndarray

    def update(self, delta_time: float):
        self.direction = normalize(self.direction + normalize(np.random.rand(2)) * self.wander_strength)

        self.velocity = self.direction * self.max_speed
        position += self.velocity * delta_time


class AntColony(BaseModel):
    # home position
    home: Tuple[float, float]

    # for each food source [x, y, food_cnt]
    food_sources: List[Tuple[float, float, float]]

    ants: List[Ant]

    def __init__(self, colony_size):
        super().__init__(colony_size=colony_size)
        self.ants = [Ant() for _ in range(colony_size)]

    def update(self, delta_time):
        for ant in self.ants:
            ant.update(delta_time)
