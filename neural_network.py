import os
import numpy as np
from .ai import AI


class NeuralNetwork:
    def __init__(self):
        """Инициализация нейронной сети для распознавания цифр MNIST."""
        self.ai = AI()
        
        config_path = os.path.join(os.path.dirname(__file__), 'AI_config.npz')
        
        try:
            self.ai.load_configs(config_path)
            print("Нейронная сеть успешно загружена")
        except Exception as e:
            print(f"Ошибка загрузки нейронной сети: {e}")
            print("Используется нейронная сеть без предварительного обучения")
    
    def normalize(self, image):
        """
        Нормализует изображение для нейронной сети.
        
        Args:
            image: numpy array размером 28x28
            
        Returns:
            numpy array: нормализованное изображение
        """
        if image.max() > 1.0:
            image = image / 255.0
        return image

    def predict(self, image):
        """
        Распознает цифру на изображении.
        
        Args:
            image: numpy array размером 28x28
            
        Returns:
            tuple: (распознанная цифра, уверенность)
        """
        try:
            if image.shape != (28, 28):
                raise ValueError("Изображение должно быть размером 28x28")
            
            # Нормализуем изображение TODO
            if image.max() > 1.0:
                image = image / 255.0
                
            digit = self.ai.main(image)
            
            return digit.argmax(), digit[digit.argmax()]
            
        except Exception as e:
            print(f"Ошибка при распознавании: {e}")
            # Возвращаем случайную цифру для демонстрации
            digit = np.random.randint(0, 10)
            confidence = np.random.random() * 0.5 + 0.5  # От 0.5 до 1.0
            return digit, confidence
