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
        this.visitedOrder = []; // Порядок посещения клеток
        this.frontierOrder = []; // Порядок добавления в границу
        this.pathOrder = []; // Порядок построения пути
        this.isDrawing = false;
        this.isEditing = false;
        this.currentTool = 'wall'; // wall, start, end, erase
        this.animationSpeed = 20; // мс между кадрами
        this.mazeSize = {
            rows: 20,
            cols: 20
        };
        this.animationState = {
            running: false,
            visitedIndex: 0,
            frontierIndex: 0,
            pathIndex: 0
        };
    }
    
    async initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'visualization-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);

        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.createToolbar();
        
        visualizationContainer.appendChild(this.toolbar1);
        visualizationContainer.appendChild(this.canvas);
        visualizationContainer.appendChild(this.toolbar2);

        
        await this.generateMaze();
        
        this.setupEventListeners();
        
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.draw();
        });
    }
    
    createToolbar() {
        this.toolbar1 = document.createElement('div');
        this.toolbar1.className = 'astar-toolbar';
        
        // Выбор алгоритма генерации
        const algorithmSelector = document.createElement('div');
        algorithmSelector.className = 'algorithm-selector';
        
        const algorithmLabel = document.createElement('label');
        algorithmLabel.textContent = 'Алгоритм:';
        algorithmLabel.className = 'selector-label';
        algorithmSelector.appendChild(algorithmLabel);
        
        const select = document.createElement('select');
        select.innerHTML = `
            <option value="prim">Алгоритм Прима</option>
            <option value="kruskal">Алгоритм Краскала</option>
        `;
        
        select.addEventListener('change', () => {
            this.generateMaze(select.value);
        });
        
        algorithmSelector.appendChild(select);
        this.toolbar1.appendChild(algorithmSelector);

        const divider5 = document.createElement('div');
        divider5.className = 'toolbar-divider';
        this.toolbar1.appendChild(divider5);


        // Слайдер размера
        const sizeControl = document.createElement('div');
        sizeControl.className = 'speed-control';

        const sizeLabel = document.createElement('div');
        sizeLabel.className = 'size-label';
        sizeLabel.innerHTML = '<label>Размер: 20x20</label>';

        const sizeSlider = document.createElement('input');
        sizeSlider.type = 'range';
        sizeSlider.min = '5';
        sizeSlider.max = '25';
        sizeSlider.value = '20';
        sizeSlider.addEventListener('input', (e) => {
            sizeLabel.textContent = `Размер: ${sizeSlider.value}x${sizeSlider.value}`;

            let value = parseInt(e.target.value);
            if (isNaN(value)) {
                value = 20;
            } else {
                value = Math.max(5, Math.min(25, value));
            }
            this.mazeSize.rows = value;
            this.mazeSize.cols = value;
        });

        sizeControl.appendChild(sizeLabel);
        sizeControl.appendChild(sizeSlider);

        
        const applyButton = document.createElement('button');
        applyButton.className = 'astar-tool-button apply-button';
        applyButton.innerHTML = 'Применить';
        applyButton.addEventListener('click', () => {
            const currentAlgorithm = select.value;
            this.generateMaze(currentAlgorithm);
        });
        
        sizeControl.appendChild(applyButton);
        this.toolbar1.appendChild(sizeControl);

        const divider2 = document.createElement('div');
        divider2.className = 'toolbar-divider';
        this.toolbar1.appendChild(divider2);

        // Слайдер скорости
        const speedControl = document.createElement('div');
        speedControl.className = 'speed-control';
        speedControl.innerHTML = '<label>Скорость:</label>';

        const speedSlider = document.createElement('input');
        speedSlider.type = 'range';
        speedSlider.min = '1';
        speedSlider.max = '100';
        speedSlider.value = '20';
        speedSlider.addEventListener('input', (e) => {
            this.animationSpeed = 101 - parseInt(e.target.value);
        });

        speedControl.appendChild(speedSlider);
        this.toolbar1.appendChild(speedControl);

        this.toolbar2 = document.createElement('div');
        this.toolbar2.className = 'astar-toolbar';
        
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
            this.toolbar2.appendChild(button);
        });
        
        const divider3 = document.createElement('div');
        divider3.className = 'toolbar-divider';
        this.toolbar2.appendChild(divider3);
        
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
            this.toolbar2.appendChild(button);
        });
    }
    
    async generateMaze(algorithm = 'prim') {
        try {
            // Останавливаем анимацию если она запущена
            this.stopAnimation();
            
            const response = await fetch(`http://localhost:8000/astar/generate?algorithm=${algorithm}&rows=${this.mazeSize.rows}&cols=${this.mazeSize.cols}`);
            const data = await response.json();
            this.maze = data.maze;
            this.start = data.start;
            this.end = data.end;
            this.resetPathData();
            this.resizeCanvas();
            this.draw();
        } catch (error) {
            console.error('Ошибка при генерации лабиринта:', error);
            alert('Ошибка при генерации лабиринта. Проверьте консоль для деталей.');
        }
    }
    
    resetPathData() {
        this.path = null;
        this.visited = new Set();
        this.frontier = new Set();
        this.visitedOrder = [];
        this.frontierOrder = [];
        this.pathOrder = [];
        this.animationState = {
            running: false,
            visitedIndex: 0,
            frontierIndex: 0,
            pathIndex: 0
        };
    }
    
    resizeCanvas() {
        if (!this.maze || !this.canvas) return;
        
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth;
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
        // Останавливаем анимацию при редактировании
        this.stopAnimation();
        
        this.isDrawing = true;
        this.handleMouseMove(e);
    }
    
    handleMouseMove(e) {
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
        this.toolbar1.querySelectorAll('.astar-tool-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // активная кнопка
        const activeButton = this.toolbar1.querySelector(`[data-tool="${tool}"]`);
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
                break;
            case 'start_search':
                await this.startPathfinding();
                break;
        }
    }
    
    updateCell(x, y) {
        if (this.currentTool === 'wall') {
            this.maze[y][x] = 1;
            this.resetPathData();
        } else if (this.currentTool === 'erase') {
            this.maze[y][x] = 0;
            this.resetPathData();
        } else if (this.currentTool === 'start') {
            // Проверяем что клетка не стена
            if (this.maze[y][x] === 0) {
                this.start = [x, y];
                this.resetPathData();
            }
        } else if (this.currentTool === 'end') {
            // Проверяем что клетка не стена
            if (this.maze[y][x] === 0) {
                this.end = [x, y];
                this.resetPathData();
            }
        }
        this.draw();
    }
    
    async startPathfinding() {
        // Останавливаем предыдущую анимацию
        this.stopAnimation();
        this.resetPathData();
        
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
            
            // Сохраняем данные для анимации
            this.pathOrder = data.path || [];
            this.visitedOrder = data.visited || [];
            this.frontierOrder = data.frontier || [];
            
            // Запускаем анимацию
            this.animatePathfinding();
            
        } catch (error) {
            console.error('Ошибка при поиске пути:', error);
            alert('Ошибка при поиске пути. Проверьте консоль для деталей.');
        }
    }
    
    stopAnimation() {
        this.animationState.running = false;
    }
    
    animatePathfinding() {
        this.animationState = {
            running: true,
            visitedIndex: 0,
            frontierIndex: 0,
            pathIndex: 0
        };
        
        const animate = () => {
            if (!this.animationState.running) return;
            
            let updated = false;
            
            // Добавляем посещенные клетки
            if (this.animationState.visitedIndex < this.visitedOrder.length) {
                const [x, y] = this.visitedOrder[this.animationState.visitedIndex];
                this.visited.add(`${x},${y}`);
                this.animationState.visitedIndex++;
                updated = true;
            }
            
            // Добавляем клетки границы
            if (this.animationState.frontierIndex < this.frontierOrder.length) {
                const [x, y] = this.frontierOrder[this.animationState.frontierIndex];
                this.frontier.add(`${x},${y}`);
                this.animationState.frontierIndex++;
                updated = true;
            }
            
            // Рисуем путь
            if (this.animationState.pathIndex < this.pathOrder.length && 
                this.animationState.visitedIndex >= this.visitedOrder.length &&
                this.animationState.frontierIndex >= this.frontierOrder.length) {
                this.path = this.pathOrder.slice(0, this.animationState.pathIndex + 1);
                this.animationState.pathIndex++;
                updated = true;
            }
            
            if (updated) {
                this.draw();
                setTimeout(() => requestAnimationFrame(animate), this.animationSpeed);
            } else {
                this.animationState.running = false;
            }
        };
        
        animate();
    }
    
    draw() {
        if (!this.ctx || !this.maze) return;
        
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
        this.visited.forEach(coord => {
            const [x, y] = coord.split(',').map(Number);
            this.ctx.fillStyle = 'rgba(0,255,157,0.18)';
            this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
        });
        
        // Отрисовка границы поиска
        this.frontier.forEach(coord => {
            const [x, y] = coord.split(',').map(Number);
            this.ctx.fillStyle = 'rgba(65,94,85,0.29)';
            this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
        });
        
        // Отрисовка пути
        if (this.path) {
            for (let i = 0; i < this.path.length; i++) {
                const [x, y] = this.path[i];
                this.ctx.fillStyle = '#00ff9d';
                this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
            }
        }
        
        // Отрисовка начальной и конечной точек
        if (this.start) {
            this.ctx.fillStyle = '#0b858a';
            this.ctx.beginPath();
            this.ctx.arc(
                this.start[0] * this.cellSize + this.cellSize/2,
                this.start[1] * this.cellSize + this.cellSize/2,
                this.cellSize/2 - 2,
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
                this.cellSize/2 - 2,
                0,
                Math.PI * 2
            );
            this.ctx.fill();
        }
    }
} 