from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.algorithms.ai.neural_network import NeuralNetwork
from backend.algorithms.astar import AStar
from backend.algorithms.decision_tree import DecisionTree
# from algorithms.kmeans import kmeans_clustering
from backend.algorithms.kmeans import KMeansData, kmeans_algorithm
from backend.algorithms.genetic_algorithm import get_exact_solution, GeneticAlgorithm, GeneticsDto
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


class MazeRequest(BaseModel):
    maze: List[List[int]]
    start: List[int]
    end: List[int]


class ImageRequest(BaseModel):
    image: List[List[float]]


class DecisionTreeData(BaseModel):
    csv_data: str
    regression: bool = False
    ccp_alpha: float = 0.01


class DecisionTreePredictionData(BaseModel):
    csv_data: str
    tree_data: Dict[str, Any]


astar = AStar()
neural_network = NeuralNetwork()
decision_tree = DecisionTree()


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Web Application"}


@app.get("/astar/generate")
async def generate_maze(algorithm: str = "prim", rows: int = 20, cols: int = 20):
    try:
        if algorithm not in ["prim", "kruskal"]:
            algorithm = "prim"

        rows = max(5, min(50, rows))
        cols = max(5, min(50, cols))

        result = astar.generate_maze(rows=rows, cols=cols, algorithm=algorithm)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/astar/find-path")
async def find_path(request: MazeRequest):
    try:
        result = astar.find_path(request.maze, request.start, request.end)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/neural/recognize")
async def recognize_digit(request: ImageRequest):
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


@app.post("/decision/build")
async def build_decision_tree(file: UploadFile = File(...),
                              regression: bool = Form(False),
                              ccp_alpha: float = Form(0.01)):
    """
    Parameters:
    - file: CSV файл
    - regression: Флаг режима регрессии (False для классификации)
    - ccp_alpha
    """
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name

            content = await file.read()
            tmp.write(content)

        try:
            tree = DecisionTree(regression=regression, ccp_alpha=ccp_alpha)
            tree.build_tree(tmp_path)

            tree_dict = {
                "tree": tree.tree,
                "feature_names": tree.feature_names,
                "target_name": tree.target_name
            }
            result = convert_numpy_types(tree_dict)

            return result
        finally:
            # Удаляем временный файл
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decision/predict")
async def predict_decision_tree(file: UploadFile = File(...),
                                tree_data: str = Form(...)):
    """
    Parameters:
    - file: CSV файл
    - tree_data: JSON-строка со структурой дерева решений
    """
    try:
        tree_data_dict = json.loads(tree_data)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name

            content = await file.read()
            tmp.write(content)

        try:
            tree = DecisionTree()
            tree.feature_names = tree_data_dict.get("feature_names", [])
            tree.target_name = tree_data_dict.get("target_name", "")
            tree.tree = tree_data_dict.get("tree", {})

            result = tree.predict(tmp_path)

            if isinstance(result, dict):
                prediction = result.get("value")
                path = result.get("path", "")
            else:
                prediction = result
                path = ""

            return convert_numpy_types({
                "prediction": prediction,
                "path": path
            })
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tsp/genetic")
async def tsp_genetic(data: GeneticsDto):
    genetic = GeneticAlgorithm(data.points, [])
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

