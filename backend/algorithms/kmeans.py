import numpy as np
from sklearn.cluster import KMeans

class KMeansAlgorithm:
    def __init__(self, n_clusters=3):
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        
    def fit(self, data):
        """
        Обучение модели на данных
        """
        return self.model.fit(data)
    
    def predict(self, data):
        """
        Предсказание кластеров для новых данных
        """
        return self.model.predict(data) 