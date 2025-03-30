import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

class DecisionTree:
    def __init__(self, task_type='classification', max_depth=None, min_samples_split=2):
        """
        Инициализация дерева решений
        
        Parameters:
        -----------
        task_type : str
            Тип задачи: 'classification' или 'regression'
        max_depth : int, optional
            Максимальная глубина дерева
        min_samples_split : int, optional
            Минимальное количество образцов для разделения узла
        """
        self.task_type = task_type
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.model = None
        
    def fit(self, X, y):
        """
        Обучение модели
        
        Parameters:
        -----------
        X : array-like
            Матрица признаков
        y : array-like
            Целевая переменная
        """
        if self.task_type == 'classification':
            self.model = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split
            )
        else:
            self.model = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split
            )
            
        self.model.fit(X, y)
        return self
    
    def predict(self, X):
        """
        Предсказание значений
        
        Parameters:
        -----------
        X : array-like
            Матрица признаков для предсказания
            
        Returns:
        --------
        array-like
            Предсказанные значения
        """
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """
        Предсказание вероятностей классов (только для классификации)
        
        Parameters:
        -----------
        X : array-like
            Матрица признаков для предсказания
            
        Returns:
        --------
        array-like
            Вероятности классов
        """
        if self.task_type != 'classification':
            raise ValueError("Метод predict_proba доступен только для классификации")
        return self.model.predict_proba(X)
    
    def get_feature_importance(self):
        """
        Получение важности признаков
        
        Returns:
        --------
        array-like
            Важность каждого признака
        """
        return self.model.feature_importances_
    
    def get_tree_structure(self):
        """
        Получение структуры дерева
        
        Returns:
        --------
        dict
            Структура дерева в виде словаря
        """
        return self.model.tree_ 