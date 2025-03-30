document.addEventListener('DOMContentLoaded', () => {
    const algorithmLinks = document.querySelectorAll('nav a');
    const visualizationContainer = document.getElementById('visualization');
    
    algorithmLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const algorithm = e.target.dataset.algorithm;
            
            try {
                const response = await fetch(`http://localhost:8000/${algorithm}`);
                const data = await response.json();
                
                // Здесь будет логика визуализации результатов
                visualizationContainer.innerHTML = `<h3>Результаты для ${algorithm} ${data.result}</h3>`;
            } catch (error) {
                console.error('Ошибка при получении данных:', error);
                visualizationContainer.innerHTML = '<p class="error">Произошла ошибка при получении данных</p>';
            }
        });
    });
}); 