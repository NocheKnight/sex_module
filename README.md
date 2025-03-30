# Web Application

Веб-приложение.
![изображение](https://github.com/user-attachments/assets/14feebe9-d547-4345-8384-511771414ef0)


## Структура проекта

```
/ml-web-app
  /backend
    main.py                  # Главный файл FastAPI
    /algorithms              # Реализация алгоритмов
      __init__.py
      kmeans.py              # Кластеризация (K-Means)
      genetic_algorithm.py   # Генетический алгоритм
      ant_colony.py          # Муравьиный алгоритм
      decision_tree.py       # Дерево решений
      neural_network.py      # Нейронная сеть
    requirements.txt         # Зависимости Python
  /frontend
    index.html               # Главная страница фронтенда
    styles.css              # Стили для интерфейса
    app.js                  # Логика фронтенда
```

## Установка и запуск

1. Установите зависимости:
```bash
cd backend
pip install -r requirements.txt
```

2. Запустите бэкенд:
```bash
uvicorn main:app --reload
```

3. Откройте frontend/index.html в браузере 
