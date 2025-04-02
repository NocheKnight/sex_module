document.addEventListener('DOMContentLoaded', () => {
    const algorithmLinks = document.querySelectorAll('nav a');
    const visualizationContainer = document.getElementById('visualization');
    let astarVisualization = null;
    
    algorithmLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const algorithm = e.target.dataset.algorithm;
            
            if (algorithm === 'astar') {
                if (!astarVisualization) {
                    astarVisualization = new AStarVisualization(visualizationContainer);
                    await astarVisualization.initialize();
                }
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

class AStarVisualization {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.ctx = null;
        this.cellSize = 20;
        this.maze = null;
        this.start = null;
        this.end = null;
        this.path = null;
        this.visited = new Set();
        this.frontier = new Set();
        this.isDrawing = false;
        this.isEditing = false;
        this.currentTool = 'wall'; // wall, start, end, erase
    }
    
    async initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'visualization-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);

        // https://ru.stackoverflow.com/questions/1357899/%D0%A0%D0%B8%D1%81%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BD%D0%B0-%D1%85%D0%BE%D0%BB%D1%81%D1%82%D0%B5-html5-%D1%81-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D1%8C%D1%8E-%D0%BC%D1%8B%D1%88%D0%B8
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.createToolbar();
        
        visualizationContainer.appendChild(this.toolbar);
        visualizationContainer.appendChild(this.canvas);
        
        await this.generateMaze();
        
        this.setupEventListeners();
        
        // Добавляем обработчик изменения размера окна TODO: Адаптивность
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.draw();
        });
    }
    
    createToolbar() {
        this.toolbar = document.createElement('div');
        this.toolbar.className = 'astar-toolbar';
        
        const algorithmSelector = document.createElement('div');
        algorithmSelector.className = 'algorithm-selector';
        
        const select = document.createElement('select');
        select.innerHTML = `
            <option value="prim">Алгоритм Прима</option>
            <option value="kruskal">Алгоритм Краскала</option>
        `;
        
        select.addEventListener('change', () => {
            this.generateMaze(select.value);
        });
        
        algorithmSelector.appendChild(select);
        this.toolbar.appendChild(algorithmSelector);
        
        const divider = document.createElement('div');
        divider.className = 'toolbar-divider';
        this.toolbar.appendChild(divider);
        
        const editTools = [
            { id: 'start', icon: '🚀', label: 'Старт' },
            { id: 'end', icon: '🎯', label: 'Финиш' },
            { id: 'wall', icon: '🧱', label: 'Стена' },
            { id: 'erase', icon: '🧹', label: 'Ластик' }
        ];
        
        editTools.forEach(tool => {
            const button = document.createElement('button');
            button.className = 'astar-tool-button';
            button.innerHTML = `${tool.icon} ${tool.label}`;
            button.dataset.tool = tool.id;
            button.addEventListener('click', () => this.handleToolClick(tool.id));
            this.toolbar.appendChild(button);
        });
        
        const divider2 = document.createElement('div');
        divider2.className = 'toolbar-divider';
        this.toolbar.appendChild(divider2);
        
        const actionTools = [
            { id: 'generate', icon: '🔄', label: 'Новый лабиринт' },
            { id: 'start_search', icon: '▶️', label: 'Запуск' }
        ];
        
        actionTools.forEach(tool => {
            const button = document.createElement('button');
            button.className = 'astar-tool-button action-button';
            button.innerHTML = `${tool.icon} ${tool.label}`;
            button.dataset.tool = tool.id;
            button.addEventListener('click', () => this.handleToolClick(tool.id));
            this.toolbar.appendChild(button);
        });
    }
    
    async generateMaze(algorithm = 'prim') {
        try {
            const response = await fetch(`http://localhost:8000/astar/generate?algorithm=${algorithm}`);
            const data = await response.json();
            this.maze = data.maze;
            this.start = data.start;
            this.end = data.end;
            this.path = null;
            this.visited = new Set();
            this.frontier = new Set();
            this.resizeCanvas();
            this.draw();
        } catch (error) {
            console.error('Ошибка при генерации лабиринта:', error);
        }
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth - this.toolbar.offsetWidth - 16; // 16px для gap
        const containerHeight = container.clientHeight;
        
        // Вычисляем размер клетки, чтобы лабиринт помещался в контейнер
        this.cellSize = Math.min(
            containerWidth / this.maze[0].length,
            containerHeight / this.maze.length
        );
        
        this.canvas.width = this.maze[0].length * this.cellSize;
        this.canvas.height = this.maze.length * this.cellSize;
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());
    }
    
    handleMouseDown(e) {
        this.isDrawing = true;
        this.handleMouseMove(e);
    }
    
    handleMouseMove(e) {
        // https://habr.com/ru/articles/244545/
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        const x = Math.floor((e.clientX - rect.left) * scaleX / this.cellSize);
        const y = Math.floor((e.clientY - rect.top) * scaleY / this.cellSize);
        
        if (x >= 0 && x < this.maze[0].length && y >= 0 && y < this.maze.length) {
            this.updateCell(x, y);
        }
    }
    
    handleMouseUp() {
        this.isDrawing = false;
    }
    
    async handleToolClick(tool) {
        // Убираем выделение со всех кнопок
        this.toolbar.querySelectorAll('.astar-tool-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // активная кнопка
        const activeButton = this.toolbar.querySelector(`[data-tool="${tool}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        switch (tool) {
            case 'wall':
            case 'start':
            case 'end':
            case 'erase':
                this.currentTool = tool;
                break;
            case 'generate':
                await this.generateMaze();
                this.draw();
                break;
            case 'start_search':
                await this.startPathfinding();
                break;
        }
    }
    
    updateCell(x, y) {
        if (this.currentTool === 'wall') {
            this.maze[y][x] = 1;
        } else if (this.currentTool === 'erase') {
            this.maze[y][x] = 0;
        } else if (this.currentTool === 'start') {
            this.start = [x, y];
        } else if (this.currentTool === 'end') {
            this.end = [x, y];
        }
        this.draw();
    }
    
    async startPathfinding() {
        try {
            const response = await fetch('http://localhost:8000/astar/find-path', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    maze: this.maze,
                    start: this.start,
                    end: this.end
                })
            });
            
            const data = await response.json();
            this.path = data.path;
            this.visited = new Set(data.visited);
            this.frontier = new Set(data.frontier);
            
            this.animatePathfinding();
        } catch (error) {
            console.error('Ошибка при поиске пути:', error);
        }
    }
    
    animatePathfinding() {
        let step = 0;
        const animate = () => {
            this.draw(step);
            step++;
            if (step < this.path.length) {
                requestAnimationFrame(animate);
            }
        };
        animate();
    }
    
    draw(currentStep = null) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Отрисовка лабиринта
        for (let y = 0; y < this.maze.length; y++) {
            for (let x = 0; x < this.maze[0].length; x++) {
                const cell = this.maze[y][x];
                this.ctx.fillStyle = cell === 1 ? '#2a2a2a' : '#1a1a1a';
                this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
                
                // Отрисовка границ клеток
                this.ctx.strokeStyle = '#333';
                this.ctx.strokeRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
            }
        }
        
        // Отрисовка посещенных клеток
        this.visited.forEach(([x, y]) => {
            this.ctx.fillStyle = 'rgba(0, 255, 157, 0.3)';
            this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
        });
        
        // Отрисовка границы поиска
        this.frontier.forEach(([x, y]) => {
            this.ctx.fillStyle = 'rgba(100, 255, 218, 0.3)';
            this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
        });
        
        // Отрисовка пути
        if (this.path && currentStep !== null) {
            for (let i = 0; i <= currentStep; i++) {
                const [x, y] = this.path[i];
                this.ctx.fillStyle = '#00ff9d';
                this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
            }
        }
        
        // Отрисовка начальной и конечной точек
        if (this.start) {
            this.ctx.fillStyle = '#00ff9d';
            this.ctx.beginPath();
            this.ctx.arc(
                this.start[0] * this.cellSize + this.cellSize/2,
                this.start[1] * this.cellSize + this.cellSize/2,
                this.cellSize/2,
                0,
                Math.PI * 2
            );
            this.ctx.fill();
        }
        
        if (this.end) {
            this.ctx.fillStyle = '#ff4d4d';
            this.ctx.beginPath();
            this.ctx.arc(
                this.end[0] * this.cellSize + this.cellSize/2,
                this.end[1] * this.cellSize + this.cellSize/2,
                this.cellSize/2,
                0,
                Math.PI * 2
            );
            this.ctx.fill();
        }
    }
} 