class AntsColony {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.canvas_size = 1000;
        this.ctx = null;

        this.ants = [];
        this.ant_color = "black";
        this.ant_size = 5;

        this.home = [this.canvas_size / 2, this.canvas_size / 2];
        this.home_color = "brown";
        this.home_size = 30;

        this.food_sources = [];
        this.food_color = "green";
        this.food_size = 20;

        this.colony_size = 100;

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
                        food_sources: this.food_sources
                    },
                    delta_time: 1
                })
            });
            
            const data = await response.json();
            this.ants = data.ants;
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

        this.ants.forEach(ant => {
            this.ctx.beginPath();
            this.ctx.fillStyle = this.ant_color;
            this.ctx.arc(ant.position[0], ant.position[1], this.ant_size, 0, 2 * Math.PI);
            this.ctx.fill();
        })

        this.food_sources.forEach(source => {
            this.ctx.beginPath();
            this.ctx.fillStyle = this.food_color;
            this.ctx.arc(source[0], source[1], this.food_size, 0, 2 * Math.PI);
            this.ctx.fill();
        })

        this.ctx.beginPath();
        this.ctx.fillStyle = this.home_color;
        this.ctx.arc(this.home[0], this.home[1], this.home_size, 0, 2 * Math.PI);
        this.ctx.fill();
    }
}
