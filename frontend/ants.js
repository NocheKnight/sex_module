class AntsColony {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.canvas_size = 500;
        this.ctx = null;
        this.currentTool = 'home';

        this.ants = [];
        this.ant_color = [0, 0, 0];
        this.ant_size = this.canvas_size / 200;

        this.home = [this.canvas_size / 2, this.canvas_size / 2];
        this.home_color = [102, 51, 0];
        this.home_size = this.canvas_size / 20;

        // (x, y, source_capacity)
        this.food_sources = [];
        this.food_color = [0, 255, 0];
        this.food_size = this.canvas_size / 20;

        this.current_food_idx = -1;

        this.pheromones = [];
        this.home_to_food_color = [0, 0, 255];
        this.food_to_home_color = [255, 0, 0];
        this.pheromones_size = this.ant_size * 3 / 5;

        this.running = false;
    }
    
    initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'visualization-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);

        this.canvas = document.createElement('canvas');
        this.canvas.width = this.canvas_size;
        this.canvas.height = this.canvas_size;
        this.ctx = this.canvas.getContext('2d');

        this.createToolbar();
        
        visualizationContainer.appendChild(this.canvas);
        visualizationContainer.append(this.toolbar);

        this.setupEventListeners();

        this.draw();
    }

    createToolbar() {
        this.toolbar = document.createElement('div');
        this.toolbar.className = 'astar-toolbar';

        const editTools = [
            { id: 'home', icon: '🚀', label: 'Колония' },
            { id: 'food', icon: '🎯', label: 'Еда' },
            { id: 'erase', icon: '🧹', label: 'Ластик' },
            { id: 'edit', icon: '🖊️', label: 'Редактировать' }
        ];
        
        editTools.forEach(tool => {
            const button = document.createElement('button');
            button.className = 'astar-tool-button';
            button.innerHTML = `${tool.icon} ${tool.label}`;
            button.dataset.tool = tool.id;
            button.addEventListener('click', () => this.handleToolClick(tool.id));
            this.toolbar.appendChild(button);
        });

        const foodCount = document.createElement('label');
        foodCount.innerHTML = 'Введите количество еды от 1 до 100';
        this.toolbar.appendChild(foodCount);
        const foodCountInputField = document.createElement('input');
        foodCountInputField.id = 'food-cnt';
        foodCountInputField.type = 'text';
        foodCountInputField.className = 'astar-tool-button';
        this.toolbar.appendChild(foodCountInputField);

        const button = document.createElement('button');
        button.className = 'astar-tool-button';
        button.innerHTML = 'Сохранить';
        button.addEventListener('click', () => this.handleSaveButton());
        this.toolbar.appendChild(button);
        
        const divider2 = document.createElement('div');
        divider2.className = 'toolbar-divider';
        this.toolbar.appendChild(divider2);

        const antsCntLabel = document.createElement('label');
        antsCntLabel.innerHTML = 'Введите количество муравьев';
        this.toolbar.appendChild(antsCntLabel);
        const antsCntInputField = document.createElement('input');
        antsCntInputField.id = 'ants-cnt';
        antsCntInputField.type = 'text';
        antsCntInputField.className = 'astar-tool-button';
        this.toolbar.appendChild(antsCntInputField);

        const actionTools = [
            { id: 'stop', icon: '🧱', label: 'Остановить' },
            { id: 'start', icon: '▶️', label: 'Запуск' },
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
            case 'home':
            case 'food':
            case 'edit':
            case 'erase':
                this.currentTool = tool;
                break;
            case 'stop':
                this.running = false;
                this.ants = [];
                this.pheromones = [];
                this.draw();
                break;
            case 'start':
                this.running = true;
                await this.generate_colony();
                this.algortithm_step();
                break;
        }
    }

    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    }

    intersectCircle(point, circleCenter, radius) {
        return (point[0] - circleCenter[0]) * (point[0] - circleCenter[0]) +
         (point[1] - circleCenter[1]) * (point[1] - circleCenter[1]) <= radius * radius;
    }
    
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;

        if (this.currentTool == 'home') {
            this.home = [x, y];
        } else if (this.currentTool == 'food') {
            this.food_sources.push([x, y, 100]);
        } else if (this.currentTool == 'erase') {
            let foodSourcesSet = new Set(this.food_sources);
            let intersections = this.food_sources.filter((source) => this.intersectCircle([x, y], [source[0], source[1]], this.food_size));
            intersections.forEach((source) => foodSourcesSet.delete(source));
            this.food_sources = [...foodSourcesSet];
        } else if (this.currentTool == 'edit') {
            for (let i = 0; i < this.food_sources.length; ++i) {
                if (this.intersectCircle([x, y], [this.food_sources[i][0], this.food_sources[i][1]], this.food_size)) {
                    document.getElementById('food-cnt').value = this.food_sources[i][2];
                    this.current_food_idx = i;
                    break;
                }
            }
        }

        this.draw();
    }

    handleSaveButton() {
        let currentFood = +document.getElementById('food-cnt').value;
        console.log(currentFood);
        if (this.currentTool == 'edit' && this.current_food_idx != -1 && !isNaN(currentFood)) {
            this.food_sources[this.current_food_idx][2] = currentFood;
        }
    }
    

    async algortithm_step() {
        if (!this.running) return;

        try {
            const response = await fetch('http://localhost:8000/ants/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    colony_dto: {
                        home: this.home,
                        ants: this.ants,
                        food_sources: this.food_sources,
                        pheromones: this.pheromones
                    },
                    delta_time: 1
                })
            });
            
            const data = await response.json();
            this.ants = data.ants;
            this.pheromones = data.pheromones;
            console.log(this.pheromones.length);
            this.draw();

            await new Promise(resolve => setTimeout(resolve, 50));

            this.algortithm_step();
        } catch (error) {
            console.error(error);
        }
    }

    async generate_colony() {
        const response = await fetch('http://localhost:8000/ants/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                home: this.home,
                colony_size: +document.getElementById('ants-cnt').value
            })
        });

        const data = await response.json();
        this.ants = data.ants;
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        let get_color = ((t, r_a = 1) => {
            return `rgba(${t}, ${Math.min(r_a, 1)})`;
        });

        this.pheromones.forEach(phe => {
            this.ctx.beginPath();
            this.ctx.fillStyle = get_color(phe[3] == 0 ? this.home_to_food_color : this.food_to_home_color, phe[2]);
            this.ctx.arc(phe[0], phe[1], this.pheromones_size, 0, 2 * Math.PI);
            this.ctx.fill();
        });

        this.ants.forEach(ant => {
            this.ctx.beginPath();
            this.ctx.fillStyle = get_color(this.ant_color);
            this.ctx.arc(ant.position[0], ant.position[1], this.ant_size, 0, 2 * Math.PI);
            this.ctx.fill();

            if (ant.is_holding_food) {
                this.ctx.beginPath();
                this.ctx.fillStyle = get_color(this.food_color);
                this.ctx.arc(ant.position[0], ant.position[1], this.ant_size * 1 / 3, 0, 2 * Math.PI);
                this.ctx.fill();
            }
        });

        this.food_sources.forEach(source => {
            this.ctx.beginPath();
            this.ctx.fillStyle = get_color(this.food_color);
            this.ctx.arc(source[0], source[1], this.food_size, 0, 2 * Math.PI);
            this.ctx.fill();
        });

        this.ctx.beginPath();
        this.ctx.fillStyle = get_color(this.home_color);
        this.ctx.arc(this.home[0], this.home[1], this.home_size, 0, 2 * Math.PI);
        this.ctx.fill();
    }
}
