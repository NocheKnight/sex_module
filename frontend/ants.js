class AntsColony {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.canvas_size = 1000;
        this.ctx = null;

        this.ants = [];
        this.ant_color = [0, 0, 0];
        this.ant_size = 5;

        this.home = [this.canvas_size / 2, this.canvas_size / 2];
        this.home_color = [102, 51, 0];
        this.home_size = 50;

        // (x, y, source_capacity)
        this.food_sources = [[this.canvas_size / 7, this.canvas_size / 7, 1], [this.canvas_size * 6 / 7, this.canvas_size / 7, 1], [this.canvas_size / 2, this.canvas_size * 6 / 7, 1]];
        this.food_color = [0, 255, 0];
        this.food_size = 50;

        this.pheromones = [];
        this.home_to_food_color = [0, 0, 255];
        this.food_to_home_color = [255, 0, 0];
        this.pheromones_size = this.ant_size * 3 / 5;

        this.colony_size = 50;

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

        this.draw();
    }

    createToolbar() {
        this.toolbar = document.createElement('div');
        this.toolbar.className = 'astar-toolbar';

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
            case 'wall':
            case 'end':
            case 'erase':
                this.currentTool = tool;
                break;
            case 'stop':
                this.running = false;
                this.ants = [];
                this.pheromones = [];
                break;
            case 'start':
                this.running = true;
                await this.generate_colony();
                this.algortithm_step();
                break;
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
                colony_size: this.colony_size
            })
        });

        const data = await response.json();
        this.ants = data.ants;
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        let get_color = ((t, r_a = 1) => {
            return `rgba(${t}, ${r_a})`;
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
                this.ctx.arc(ant.position[0], ant.position[1], this.ant_size * 2 / 5, 0, 2 * Math.PI);
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
