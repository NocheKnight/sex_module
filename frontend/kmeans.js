class KMeans {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.ctx = null;
        this.canvasSize = 500;
        this.currentTool = 'draw'; // draw, erase
        this.points = new Set();
        this.pointR = 10;
        this.defaultPointColor = [0, 0, 0];
        this.colors = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 128, 0], [0, 255, 255], [204, 0, 204]]
    }

    initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'visualization-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);

        this.canvas = document.createElement('canvas');
        this.canvas.width = this.canvasSize;
        this.canvas.height = this.canvasSize;
        this.ctx = this.canvas.getContext('2d');
        
        this.createToolbar();

        visualizationContainer.appendChild(this.canvas);
        visualizationContainer.appendChild(this.toolbar);

        this.setupEventListeners();

        this.handleToolClick('draw');
    }

    createToolbar() {
        this.toolbar = document.createElement('div');
        this.toolbar.className = 'astar-toolbar';

        const editTools = [
            { id: 'draw', icon: '🎯', label: 'Рисовать' },
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

        const label = document.createElement('label');
        label.innerHTML = 'Введите количество кластеров';
        this.toolbar.appendChild(label);
        const inputField = document.createElement('input');
        inputField.id = 'clusters-cnt';
        inputField.type = 'text';
        inputField.className = 'astar-tool-button';
        this.toolbar.appendChild(inputField);

        const divider = document.createElement('div');
        divider.className = 'toolbar-divider';
        this.toolbar.appendChild(divider);

        const actionTools = [
            { id: 'start', icon: '▶️', label: 'Запуск' }
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
            case 'draw':
            case 'erase':
                this.currentTool = tool;
                break;
            case 'start':
                await this.getClusters();
                break;
        }
    }

    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    }

    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        const x = Math.floor((e.clientX - rect.left) * scaleX);
        const y = Math.floor((e.clientY - rect.top) * scaleY);
        
        if (this.currentTool === 'draw') {
            this.points.add([x, y, this.defaultPointColor]);
        } else if (this.currentTool === 'erase') {
            let toRemove = new Set();

            this.points.forEach(point => {
                if ((point[0] - x) ** 2 + (point[1] - y) ** 2 <= this.pointR ** 2) {
                    toRemove.add(point);
                }
            });

            toRemove.forEach(point => {
                this.points.delete(point);
            })
        }

        this.draw();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.points.forEach(point => {
            this.ctx.beginPath();
            this.ctx.fillStyle = `rgb(${point[2]})`;
            console.log(point[2]);
            this.ctx.arc(point[0], point[1], this.pointR, 0, 2 * Math.PI);
            this.ctx.fill();
        });
    }

    getColorFromCluster(clusterIdx, clustersCnt) {
        if (clustersCnt <= this.colors.length) return this.colors[clusterIdx];
        let color = [255 * clusterIdx / clustersCnt, 0 , 255 - 255 * clusterIdx / clustersCnt];
        color[1] = (color[0] + color[2]) / 2;
        return color;
    }

    async getClusters() {
        try {
            let arrayPoints = [...this.points].map(point => [point[0], point[1]]);

            const response = await fetch('http://localhost:8000/kmeans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    clusters_cnt: +document.getElementById('clusters-cnt').value,
                    points: arrayPoints
                })
            });
            
            let data = await response.json();
            data = data.map(point => [point[0], point[1], this.getColorFromCluster(point[2], +document.getElementById('clusters-cnt').value)]);
            this.points = new Set(data);

            this.draw();
        } catch (error) {
            console.error(error);
        }
    }
}
