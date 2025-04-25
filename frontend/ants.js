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

        this.pheromones = [];
        this.home_to_food_color = [0, 0, 255];
        this.food_to_home_color = [255, 0, 0];
        this.pheromones_size = this.ant_size * 3 / 5;

        this.colony_size = 40;

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

        const editTools = [
            { id: 'home', icon: '🚀', label: 'Колония' },
            { id: 'food', icon: '🎯', label: 'Еда' },
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
    
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        
        const x = (e.clientX - rect.left);
        const y = (e.clientY - rect.top);

        if (this.currentTool == 'home') {
            this.home = [x, y];
        } else if (this.currentTool == 'food') {
            this.food_sources.add([x, y, 1]);
        } else if (this.currentTool == 'erase') {
            let food_sources_set = new Set(this.food_sources);
            let intersections = this.food_sources.filter((source) => ((source[0] - x) * (source[0] - 1) + (source[1] - y) * (source[1] - y) <= this.food_size * this.food_size));
            intersections.forEach((source) => food_sources_set.remove(source));
            this.food_sources = [...food_sources_set];
        }

        this.draw();
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
