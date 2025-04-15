from typing import List, Tuple
from pydantic import BaseModel


class KMeansData(BaseModel):
    clusters_cnt: int
    points: List[Tuple[float, float]]


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5


def kmeans_algorithm(data: KMeansData):
    data.clusters_cnt = min(data.clusters_cnt, len(data.points))

    centers = data.points[:data.clusters_cnt]
    points_cnt = len(data.points)
    point_to_cluster = [-1] * points_cnt

    changed = True
    while changed:
        changed = False

        for i in range(points_cnt):
            prev_center = point_to_cluster[i]
            cur_point = data.points[i]

            cur_center = 0
            cur_min_dist = 1e9
            for center_idx in range(data.clusters_cnt):
                if distance(cur_point, centers[center_idx]) < cur_min_dist:
                    cur_center = center_idx
                    cur_min_dist = distance(cur_point, centers[center_idx])
            
            if prev_center != cur_center:
                changed = True
                point_to_cluster[i] = cur_center
        
        for center_idx in range(data.clusters_cnt):
            updated_center = [0, 0]
            points_in_cluster = 0
            for point_idx in range(points_cnt):
                cur_point = data.points[point_idx]
                if point_to_cluster[point_idx] == center_idx:
                    updated_center[0] += cur_point[0]
                    updated_center[1] += cur_point[1]
                    points_in_cluster += 1
            if points_in_cluster != 0:
                updated_center[0] /= points_in_cluster
                updated_center[1] /= points_in_cluster

            centers[center_idx] = tuple(updated_center)
    
    return [(data.points[i][0], data.points[i][1], point_to_cluster[i]) for i in range(points_cnt)]
