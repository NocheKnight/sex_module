import numpy as np
from sklearn.neural_network import MLPClassifier, MLPRegressor

class NeuralNetwork:
    def __init__(self, task_type='classification', hidden_layer_sizes=(100,), 
                 activation='relu', solver='adam', max_iter=1000):
        """
        Инициализация нейронной сети
        
        Parameters:
        -----------
        task_type : str
            Тип задачи: 'classification' или 'regression'
        hidden_layer_sizes : tuple, optional
            Размеры скрытых слоев
        activation : str, optional
            Функция активации: 'identity', 'logistic', 'tanh', 'relu'
        solver : str, optional
            Оптимизатор: 'lbfgs', 'sgd', 'adam'
        max_iter : int, optional
            Максимальное количество итераций
        """
        self.task_type = task_type
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.solver = solver
        self.max_iter = max_iter
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
            self.model = MLPClassifier(
                hidden_layer_sizes=self.hidden_layer_sizes,
                activation=self.activation,
                solver=self.solver,
                max_iter=self.max_iter
            )
        else:
            self.model = MLPRegressor(
                hidden_layer_sizes=self.hidden_layer_sizes,
                activation=self.activation,
                solver=self.solver,
                max_iter=self.max_iter
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
    
    def get_weights(self):
        """
        Получение весов нейронной сети
        
        Returns:
        --------
        list
            Список массивов весов для каждого слоя
        """
        return self.model.coefs_
    
    def get_biases(self):
        """
        Получение смещений нейронной сети
        
        Returns:
        --------
        list
            Список массивов смещений для каждого слоя
        """
        return self.model.intercepts_
    
    def get_loss(self):
        """
        Получение значения функции потерь
        
        Returns:
        --------
        float
            Значение функции потерь
        """
        return self.model.loss_ 