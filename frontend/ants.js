class AntsColony {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.canvas_size = 500;
        this.ctx = null;

        this.ants = [];
        this.ant_color = "black";
        this.ant_size = 5;

        this.home = [0, 0];
        this.home_color = "brown";

        this.food_sources = [];
        this.food_color = "green";
    }
    
    async initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'visualization-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);

        this.canvas = document.createElement('canvas');
        this.canvas.width = this.canvas_size;
        this.canvas.height = this.canvas_size;
        this.ctx = this.canvas.getContext('2d');
        
        visualizationContainer.appendChild(this.canvas);

        await this.generate_colony();
    }

    async generate_colony() {
        const response = await fetch('http://localhost:8000/ants/generate');
        const data = await response.json();
        this.ants = data.ants;
    }

    draw() {
        this.ants.forEach(ant => {
            this.ctx.beginPath();
            this.ctx.fillStyle = this.ant_color;
            this.ctx.arc(ant.position.x, ant.position.y, this.ant_size, 0, 2 * Math.PI);
            
        })
    }
}
