from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from algorithms.kmeans import kmeans_clustering
# from algorithms.genetic_algorithm import genetic_algorithm
from backend.algorithms.astar import AStar
import pandas as pd
import numpy as np

app = FastAPI(title="Web Application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр A*
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
        # Обновление состояния лабиринта
        astar.maze = np.array(data["maze"])
        astar.start = tuple(data["start"])
        astar.end = tuple(data["end"])
        
        # Поиск пути
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
