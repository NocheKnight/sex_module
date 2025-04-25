from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from algorithms.kmeans import kmeans_clustering
# from algorithms.genetic_algorithm import genetic_algorithm
from backend.algorithms.kmeans import KMeansData, kmeans_algorithm
from backend.algorithms.astar import AStar
from backend.algorithms.ai.neural_network import NeuralNetwork
import pandas as pd
import numpy as np
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random

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


@app.post("/genetic/")
async def run_genetic_algorithm():
    # result = genetic_algorithm()
    return {"result": "result"}


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
