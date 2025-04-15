document.addEventListener('DOMContentLoaded', () => {
    const algorithmLinks = document.querySelectorAll('nav a');
    const visualizationContainer = document.getElementById('visualization');
    let astarVisualization = null;
    
    algorithmLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const algorithm = e.target.dataset.algorithm;
            
            visualizationContainer.innerHTML = '';

            if (algorithm === 'astar') {
                if (!astarVisualization) {
                    astarVisualization = new AStarVisualization(visualizationContainer);
                    await astarVisualization.initialize();
                } else {
                    const container = document.createElement('div');
                    container.className = 'visualization-container';
                    container.appendChild(astarVisualization.canvas);
                    container.appendChild(astarVisualization.toolbar);
                    visualizationContainer.appendChild(container);
                    astarVisualization.draw();
                }
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
