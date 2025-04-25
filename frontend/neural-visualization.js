class NeuralVisualization {
    constructor(container) {
        this.container = container;
        this.drawingCanvas = null;
        this.drawingCtx = null;
        this.resultCanvas = null;
        this.resultCtx = null;
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        this.recognizedDigit = null;
        this.confidence = null;
        this.pixelData = null; // массив 28x28 для отправки на сервер
    }
    
    async initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'neural-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);

        // Создаем левую панель с канвасом для рисования
        const drawingSection = document.createElement('div');
        drawingSection.className = 'drawing-section';
        
        const drawingTitle = document.createElement('h3');
        drawingTitle.textContent = 'Нарисуйте цифру:';
        drawingSection.appendChild(drawingTitle);
        
        this.drawingCanvas = document.createElement('canvas');
        this.drawingCanvas.width = 280;
        this.drawingCanvas.height = 280;
        this.drawingCanvas.className = 'drawing-canvas';
        this.drawingCtx = this.drawingCanvas.getContext('2d');
        
        this.drawingCtx.lineJoin = 'round';
        this.drawingCtx.lineCap = 'round';
        this.drawingCtx.lineWidth = 20;
        this.drawingCtx.strokeStyle = '#ffffff';

        drawingSection.appendChild(this.drawingCanvas);
        
        const controlPanel = document.createElement('div');
        controlPanel.className = 'control-panel';
        
        const clearButton = document.createElement('button');
        clearButton.className = 'neural-button';
        clearButton.textContent = 'Очистить';
        clearButton.addEventListener('click', () => this.clearCanvas());

        const recognizeButton = document.createElement('button');
        recognizeButton.className = 'neural-button recognize-button';
        recognizeButton.textContent = 'Распознать';
        recognizeButton.addEventListener('click', () => this.recognizeDigit());

        controlPanel.appendChild(clearButton);
        controlPanel.appendChild(recognizeButton);

        drawingSection.appendChild(controlPanel);
        
        const resultSection = document.createElement('div');
        resultSection.className = 'result-section';
        
        const resultTitle = document.createElement('h3');
        resultTitle.textContent = 'Результат:';
        resultSection.appendChild(resultTitle);
        
        this.resultDisplay = document.createElement('div');
        this.resultDisplay.className = 'result-display';
        
        this.resultCanvas = document.createElement('canvas');
        this.resultCanvas.width = 28;
        this.resultCanvas.height = 28;
        this.resultCanvas.className = 'result-canvas';
        this.resultCtx = this.resultCanvas.getContext('2d');
        
        const recognitionResult = document.createElement('div');
        recognitionResult.className = 'recognition-result';
        
        this.digitDisplay = document.createElement('div');
        this.digitDisplay.className = 'digit-display';
        this.digitDisplay.textContent = '?';
        
        this.confidenceDisplay = document.createElement('div');
        this.confidenceDisplay.className = 'confidence-display';
        this.confidenceDisplay.textContent = 'Уверенность: -';
        
        recognitionResult.appendChild(this.digitDisplay);
        recognitionResult.appendChild(this.confidenceDisplay);
        
        this.resultDisplay.appendChild(this.resultCanvas);
        this.resultDisplay.appendChild(recognitionResult);
        
        resultSection.appendChild(this.resultDisplay);
        
        visualizationContainer.appendChild(drawingSection);
        visualizationContainer.appendChild(resultSection);
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.drawingCanvas.addEventListener('mousedown', e => this.startDrawing(e));
        this.drawingCanvas.addEventListener('mousemove', e => this.draw(e));
        this.drawingCanvas.addEventListener('mouseup', () => this.stopDrawing());
        this.drawingCanvas.addEventListener('mouseout', () => this.stopDrawing());
        
        // Поддержка сенсорных устройств TODO: mobile
        this.drawingCanvas.addEventListener('touchstart', e => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.drawingCanvas.dispatchEvent(mouseEvent);
        });
        
        this.drawingCanvas.addEventListener('touchmove', e => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.drawingCanvas.dispatchEvent(mouseEvent);
        });
        
        this.drawingCanvas.addEventListener('touchend', e => {
            e.preventDefault();
            const mouseEvent = new MouseEvent('mouseup');
            this.drawingCanvas.dispatchEvent(mouseEvent);
        });
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.drawingCanvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const rect = this.drawingCanvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        this.drawingCtx.beginPath();
        this.drawingCtx.moveTo(this.lastX, this.lastY);
        this.drawingCtx.lineTo(currentX, currentY);
        this.drawingCtx.stroke();
        
        this.lastX = currentX;
        this.lastY = currentY;
    }
    
    stopDrawing() {
        this.isDrawing = false;
    }
    
    clearCanvas() {
        this.drawingCtx.fillStyle = '#000000';
        this.drawingCtx.fillRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
        
        this.digitDisplay.textContent = '?';
        this.confidenceDisplay.textContent = 'Уверенность: -';
    }
    
    prepareImageData() {
        // Создаем временный канвас размером 28x28
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = 28;
        tempCanvas.height = 28;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Масштабируем нарисованное изображение до 28x28
        tempCtx.drawImage(this.drawingCanvas, 0, 0, 28, 28);
        
        // Получаем данные изображения
        const imageData = tempCtx.getImageData(0, 0, 28, 28);
        const data = imageData.data;
        
        // Создаем массив 28x28 со значениями яркости от 0 до 1
        this.pixelData = new Array(28);
        for (let y = 0; y < 28; y++) {
            this.pixelData[y] = new Array(28);
            for (let x = 0; x < 28; x++) {
                const idx = (y * 28 + x) * 4;
                // Берем значение красного канала (т.к. рисуем белым по черному)
                this.pixelData[y][x] = data[idx] / 255;
            }
        }
        
        // Отображаем масштабированное изображение в результирующем канвасе
        this.resultCtx.putImageData(imageData, 0, 0);
        
        return this.pixelData;
    }
    
    async recognizeDigit() {
        try {
            const imageData = this.prepareImageData();
            
            const response = await fetch('http://localhost:8000/neural/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            const result = await response.json();
            
            if (result && result.digit !== undefined) {
                this.recognizedDigit = result.digit;
                this.confidence = result.confidence;
                
                this.digitDisplay.textContent = this.recognizedDigit;
                this.confidenceDisplay.textContent = `Уверенность: ${(this.confidence * 100).toFixed(2)}%`;
            } else {
                this.digitDisplay.textContent = 'Ошибка';
                this.confidenceDisplay.textContent = 'Не удалось распознать';
            }
        } catch (error) {
            console.error('Ошибка при распознавании:', error);
            this.digitDisplay.textContent = 'Ошибка';
            this.confidenceDisplay.textContent = 'Проверьте консоль';
        }
    }
} 