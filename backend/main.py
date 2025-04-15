from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
# from algorithms.kmeans import kmeans_clustering
# from algorithms.genetic_algorithm import genetic_algorithm
from backend.algorithms.astar import AStar
from backend.algorithms.ant_colony import AntColony, AntColonyDto
import pandas as pd
import numpy as np
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

astar = AStar(size=20)

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Web Application"}


@app.get("/astar/generate")
async def generate_maze(algorithm: str = 'prim'):
    try:
        maze = astar.generate_maze(algorithm=algorithm)
        return {
            "maze": maze.tolist(),
            "start": astar.start,
            "end": astar.end
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/astar/find-path")
async def find_path(data: dict):
    try:
        astar.maze = np.array(data["maze"])
        astar.start = tuple(data["start"])
        astar.end = tuple(data["end"])
        
        path = astar.find_path()
        
        # Преобразование множеств в списки для JSON
        visited = [list(cell) for cell in astar.visited]
        frontier = [list(cell) for cell in astar.frontier]
        
        return {
            "path": path,
            "visited": visited,
            "frontier": frontier
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kmeans/")
async def run_kmeans(file: UploadFile = File(...), n_clusters: int = 3):
    data = pd.read_csv(file.file)
    # result = kmeans_clustering(data, n_clusters)
    return {"clusters": "result"}

@app.post("/genetic/")
async def run_genetic_algorithm():
    # result = genetic_algorithm()
    return {"result": "result"}

@app.get("/ping")
async def ping():
    return {"message": "Server is running!"}


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

