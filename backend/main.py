from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
# from algorithms.kmeans import kmeans_clustering
# from algorithms.genetic_algorithm import genetic_algorithm
from backend.algorithms.kmeans import KMeansData, kmeans_algorithm
from backend.algorithms.astar import AStar
from backend.algorithms.ai.neural_network import NeuralNetwork
from backend.algorithms.genetic_algorithm import get_exact_solution, GeneticAlgorithm
from backend.algorithms.ant_colony import AntColony, AntColonyDto
import pandas as pd
import numpy as np
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
import random
from typing import Tuple
from pydantic import BaseModel

app = FastAPI(title="Web Application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class MazeRequest(BaseModel):
    maze: List[List[int]]
    start: List[int]
    end: List[int]


class ImageRequest(BaseModel):
    image: List[List[float]]


# Инициализация алгоритмов
astar = AStar()
neural_network = NeuralNetwork()


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Web Application"}


@app.get("/astar/generate")
async def generate_maze(algorithm: str = "prim", rows: int = 20, cols: int = 20):
    """
    Генерирует лабиринт для алгоритма A*
    
    Parameters:
    - algorithm: Алгоритм генерации лабиринта (prim или kruskal)
    - rows: Количество строк (высота) лабиринта
    - cols: Количество столбцов (ширина) лабиринта
    """
    try:
        # Проверяем алгоритм
        if algorithm not in ["prim", "kruskal"]:
            algorithm = "prim"

        # Проверяем и ограничиваем размеры лабиринта
        rows = max(5, min(50, rows))
        cols = max(5, min(50, cols))

        result = astar.generate_maze(rows=rows, cols=cols, algorithm=algorithm)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/astar/find-path")
async def find_path(request: MazeRequest):
    """
    Находит путь от начальной до конечной точки с использованием алгоритма A*
    """
    try:
        result = astar.find_path(request.maze, request.start, request.end)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/neural/recognize")
async def recognize_digit(request: ImageRequest):
    """
    Распознает цифру на изображении с помощью нейронной сети
    
    Parameters:
    - image: 2D массив изображения размером 28x28, со значениями от 0 до 1
    """
    try:
        if (len(request.image) != 28 or
                any(len(row) != 28 for row in request.image)):
            raise HTTPException(status_code=400, detail="Изображение должно быть размером 28x28")

        image_array = np.array(request.image, dtype=np.float32)

        digit, confidence = neural_network.predict(image_array)

        return {
            "digit": int(digit),
            "confidence": float(confidence)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kmeans/")
async def run_kmeans(data: KMeansData):
    try:
        return kmeans_algorithm(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tsp/genetic")
async def tsp_genetic(points: List[Tuple[float, float]]):
    genetic = GeneticAlgorithm(points)
    return genetic.run()


@app.post("/tsp/exact")
async def tsp_exact(points: List[Tuple[float, float]]):
    return get_exact_solution(points)



@app.get("/ant")
async def get_ant_algorithm():
    return {"data": "Ant Colony Optimization data"}


@app.get("/decision")
async def get_decision_tree():
    return {"data": "Decision Tree data"}


@app.get("/ping")
async def ping():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


class GenerateParams(BaseModel):
    home: Tuple[float, float]
    colony_size: int

@app.post("/ants/generate")
async def ants_generate(data: GenerateParams):
    colony = AntColony(data.home, data.colony_size)
    return colony.to_json()

class SimulateParams(BaseModel):
    colony_dto: AntColonyDto
    delta_time: float

@app.post("/ants/simulate")
async def ants_simulate(data: SimulateParams):
    colony = data.colony_dto.to_colony()
    colony.update(data.delta_time)
    return colony.to_json()

