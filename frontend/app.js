document.addEventListener('DOMContentLoaded', () => {
    const algorithmLinks = document.querySelectorAll('nav a');
    const visualizationContainer = document.getElementById('visualization');

    algorithmLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const algorithm = e.target.dataset.algorithm;
            
            visualizationContainer.innerHTML = '';

            if (algorithm === 'astar') {
                let astarVisualization = new AStarVisualization(visualizationContainer);
                await astarVisualization.initialize();
            } else if (algorithm === 'kmeans') {
                let kmeansVisualization = new KMeans(visualizationContainer);
                kmeansVisualization.initialize();
            } else if (algorithm === 'neural') {
                let neuralVisualization = new NeuralVisualization(visualizationContainer);
                await neuralVisualization.initialize();
            } else if (algorithm === 'genetic') {
                let geneticVisualization = new Genetic(visualizationContainer);
                geneticVisualization.initialize();
            } else if (algorithm === 'ant') {
                let antsVisualization = new AntsColony(visualizationContainer);
                await antsVisualization.initialize();
            } else {
                // Обработка других алгоритмов
                try {
                    const response = await fetch(`http://localhost:8000/${algorithm}`);
                    const data = await response.json();
                    visualizationContainer.innerHTML = `<h3>Результаты для ${algorithm}</h3>`;
                } catch (error) {
                    console.error('Ошибка при получении данных:', error);
                    visualizationContainer.innerHTML = '<p class="error">Произошла ошибка при получении данных</p>';
                }
            }
        });
    });
});
