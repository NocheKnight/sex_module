class Genetic {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.ctx = null;
        this.canvasSize = 500;
        this.currentTool = 'draw'; // draw, erase
        this.points = new Set();
        this.pointR = 10;
        this.defaultPointColor = [0, 0, 0];
        this.iterationCnt = 200;
        this.generation = [];
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

        const randomLabel = document.createElement('label');
        randomLabel.innerHTML = 'Введите количество точек';
        this.toolbar.appendChild(randomLabel);
        const randomInputField = document.createElement('input');
        randomInputField.id = 'random';
        randomInputField.type = 'text';
        randomInputField.className = 'astar-tool-button';
        this.toolbar.appendChild(randomInputField);

        const divider = document.createElement('div');
        divider.className = 'toolbar-divider';
        this.toolbar.appendChild(divider);

        const actionTools = [
            { id: 'start', icon: '▶️', label: 'Запуск' },
            { id: 'random-tool', icon: '🎲', label: 'Рандом' },
            { id: 'clear', icon: '🔄', label: 'Стереть'}
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
                await this.getSolution();
                break;
            case 'random-tool':
                let pointCnt = +document.getElementById('random').value;

                if (isNaN) {
                    let getRandomCoord = () => Math.random() * (this.canvasSize - 2 * this.pointR) + this.pointR;

                    for (let i = 0; i < pointCnt; ++i) {
                        this.points.add([getRandomCoord(), getRandomCoord()]);
                    }
                    
                    this.draw();
                }

                break;
            case 'clear':
                this.points.clear();
                this.draw();
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

    draw(clear=true) {
        if (clear) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }

        this.points.forEach(point => {
            this.ctx.beginPath();
            this.ctx.fillStyle = `rgb(${point[2]})`;
            this.ctx.arc(point[0], point[1], this.pointR, 0, 2 * Math.PI);
            this.ctx.fill();
        });
    }

    async getSolution() {
        try {
            let arrayPoints = [...this.points].map(point => [point[0], point[1]]);

            for (let i = 0; i < this.iterationCnt; ++i) {
                const response = await fetch('http://localhost:8000/tsp/genetic', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        points: arrayPoints,
                        prev_generation: this.generation
                    })
                });
                
                let data = await response.json();
                this.generation = data[2];

                if (i % 10 == 0) {
                    this.draw(true);
                    this.draw_path(data[0], 'red');
                    console.log(data[1]);
                    // await new Promise(resolve => setTimeout(resolve, 200));
                }
            }

            if (arrayPoints.length <= 15) {
                const response = await fetch('http://localhost:8000/tsp/exact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(arrayPoints)
                });
                
                let data = await response.json();

                this.draw_path(data[0], 'green');
                console.log(data[1]);
            }
                        
        } catch (error) {
            console.error(error);
        }
    }

    draw_path(points, color='red'){

        this.ctx.beginPath();
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 5;
        this.ctx.moveTo(points[0][0], points[0][1]);

        for (let i = 0; i < points.length; ++i) {
            this.ctx.lineTo(points[(i + 1) % points.length][0], points[(i + 1) % points.length][1]);
        }

        this.ctx.stroke();
        this.draw(false);
    }
}
