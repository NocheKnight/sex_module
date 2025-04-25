class DecisionTreeVisualization {
    constructor(container) {
        this.container = container;
        this.tree = null;
        this.treeContainer = null;
        this.fileInput = null;
        this.predictionFileInput = null;
        this.predictionResult = null;
        this.predictionPath = null;
        this.currentNodeId = 0;
        this.state = 'build'; // 'build' или 'predict'
    }
    
    async initialize() {
        const visualizationContainer = document.createElement('div');
        visualizationContainer.className = 'decision-tree-container';
        this.container.innerHTML = '';
        this.container.appendChild(visualizationContainer);
        
        const controlPanel = document.createElement('div');
        controlPanel.className = 'control-panel-tree';
        
        const fileInputContainer = document.createElement('div');
        fileInputContainer.className = 'data-input-container';
        
        const fileInputLabel = document.createElement('label');
        fileInputLabel.textContent = 'Загрузите данные (CSV файл):';
        fileInputLabel.htmlFor = 'csv-file-input';
        fileInputContainer.appendChild(fileInputLabel);
        
        const formatHelp = document.createElement('div');
        formatHelp.className = 'format-help';
        formatHelp.innerHTML = `<small>Формат: CSV с заголовками, последняя колонка - целевая переменная</small>`;
        fileInputContainer.appendChild(formatHelp);
        
        const uploadContainer = document.createElement('div');
        uploadContainer.className = 'upload-container';
        
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'csv-file-input';
        fileInput.className = 'file-input';
        fileInput.accept = '.csv';
        this.fileInput = fileInput;
        uploadContainer.appendChild(fileInput);
        
        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = 'Файл не выбран';
        uploadContainer.appendChild(fileName);
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                fileName.textContent = e.target.files[0].name;
            } else {
                fileName.textContent = 'Файл не выбран';
            }
        });
        
        fileInputContainer.appendChild(uploadContainer);
        
        controlPanel.appendChild(fileInputContainer);
        
        const actionPanel = document.createElement('div');
        actionPanel.className = 'action-panel';
        
        const buildButton = document.createElement('button');
        buildButton.className = 'decision-tree-button build-button';
        buildButton.textContent = 'Построить дерево';
        buildButton.addEventListener('click', () => this.buildTree());
        actionPanel.appendChild(buildButton);
        
        const switchButton = document.createElement('button');
        switchButton.className = 'decision-tree-button switch-button';
        switchButton.textContent = 'Перейти к прогнозированию';
        switchButton.addEventListener('click', () => this.switchMode());
        actionPanel.appendChild(switchButton);
        
        const predictionInputContainer = document.createElement('div');
        predictionInputContainer.className = 'data-input-container prediction-container';
        predictionInputContainer.style.display = 'none';
        
        const predictionInputLabel = document.createElement('label');
        predictionInputLabel.textContent = 'Загрузите данные для прогноза:';
        predictionInputLabel.htmlFor = 'prediction-file-input';
        predictionInputContainer.appendChild(predictionInputLabel);
        
        const predictionFormatHelp = document.createElement('div');
        predictionFormatHelp.className = 'format-help';
        predictionFormatHelp.innerHTML = `<small>Формат: CSV с заголовками, содержащий только признаки (без целевой переменной)</small>`;
        predictionInputContainer.appendChild(predictionFormatHelp);
        
        const predictionUploadContainer = document.createElement('div');
        predictionUploadContainer.className = 'upload-container';
        
        const predictionFileInput = document.createElement('input');
        predictionFileInput.type = 'file';
        predictionFileInput.id = 'prediction-file-input';
        predictionFileInput.className = 'file-input';
        predictionFileInput.accept = '.csv';
        this.predictionFileInput = predictionFileInput;
        predictionUploadContainer.appendChild(predictionFileInput);
        
        const predictionFileName = document.createElement('div');
        predictionFileName.className = 'file-name';
        predictionFileName.textContent = 'Файл не выбран';
        predictionUploadContainer.appendChild(predictionFileName);
        
        predictionFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                predictionFileName.textContent = e.target.files[0].name;
            } else {
                predictionFileName.textContent = 'Файл не выбран';
            }
        });
        
        predictionInputContainer.appendChild(predictionUploadContainer);
        controlPanel.appendChild(predictionInputContainer);
        
        const predictButton = document.createElement('button');
        predictButton.className = 'decision-tree-button predict-button';
        predictButton.textContent = 'Прогнозировать';
        predictButton.addEventListener('click', () => this.predict());
        predictButton.style.display = 'none';
        actionPanel.appendChild(predictButton);
        
        controlPanel.appendChild(actionPanel);
        
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'results-container';
        
        const predictionResultContainer = document.createElement('div');
        predictionResultContainer.className = 'prediction-result';
        
        this.predictionResult = document.createElement('div');
        this.predictionResult.className = 'result-value';
        predictionResultContainer.appendChild(this.predictionResult);
        
        this.predictionPath = document.createElement('div');
        this.predictionPath.className = 'path-display';
        predictionResultContainer.appendChild(this.predictionPath);
        
        resultsContainer.appendChild(predictionResultContainer);
        controlPanel.appendChild(resultsContainer);
        
        const treePanel = document.createElement('div');
        treePanel.className = 'tree-panel';
        
        const treeTitle = document.createElement('h3');
        treeTitle.textContent = 'Визуализация дерева решений';
        treePanel.appendChild(treeTitle);
        
        this.treeContainer = document.createElement('div');
        this.treeContainer.className = 'tree-container';
        treePanel.appendChild(this.treeContainer);
        
        visualizationContainer.appendChild(controlPanel);
        visualizationContainer.appendChild(treePanel);
    }
    
    // Переключение между режимами построения и прогнозирования
    switchMode() {
        if (!this.tree) {
            alert('Необходимо сначала построить дерево решений! Загрузите CSV файл и нажмите "Построить дерево".');
            return;
        }
        
        const fileInputContainer = document.querySelector('.data-input-container:not(.prediction-container)');
        const predictionContainer = document.querySelector('.prediction-container');
        const buildButton = document.querySelector('.build-button');
        const predictButton = document.querySelector('.predict-button');
        const switchButton = document.querySelector('.switch-button');
        
        if (this.state === 'build') {
            this.state = 'predict';
            fileInputContainer.style.display = 'none';
            predictionContainer.style.display = 'block';
            buildButton.style.display = 'none';
            predictButton.style.display = 'block';
            switchButton.textContent = 'Вернуться к построению';
        } else {
            this.state = 'build';
            fileInputContainer.style.display = 'block';
            predictionContainer.style.display = 'none';
            buildButton.style.display = 'block';
            predictButton.style.display = 'none';
            switchButton.textContent = 'Перейти к прогнозированию';
            
            this.resetHighlightedPath();
        }
    }
    
    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }
    
    async buildTree() {
        try {
            if (!this.fileInput.files || this.fileInput.files.length === 0) {
                alert('Выберите CSV файл для построения дерева!');
                return;
            }
            
            const file = this.fileInput.files[0];
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('regression', 'false');
            formData.append('ccp_alpha', '0.01');   // Значение по умолчанию
            
            const response = await fetch('http://localhost:8000/decision/build', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.error) {
                alert(`Ошибка: ${result.error}`);
                return;
            }
            
            this.tree = result.tree;
            this.feature_names = result.feature_names;
            this.target_name = result.target_name;
            this.visualizeTree(this.tree);
            
            const switchButton = document.querySelector('.switch-button');
            switchButton.disabled = false;
            
            this.predictionResult.textContent = '';
            this.predictionPath.textContent = '';
        } catch (error) {
            console.error('Ошибка при построении дерева:', error);
            alert('Произошла ошибка при построении дерева решений. Проверьте формат данных.');
        }
    }
    
    visualizeTree(tree) {
        this.currentNodeId = 0;
        this.treeContainer.innerHTML = '';
        
        this.maxDepth = this.getTreeDepth(tree);
        
        const treeEl = this.createTreeElement(tree, 0);
        this.treeContainer.appendChild(treeEl);
    }
    
    getTreeDepth(node) {
        if (!node || node.is_leaf) {
            return 0;
        }
        return 1 + Math.max(this.getTreeDepth(node.left), this.getTreeDepth(node.right));
    }
    
    createTreeElement(node, depth) {
        const treeElement = document.createElement('div');
        treeElement.className = 'tree-node';
        
        treeElement.dataset.depth = depth;
        
        const nodeId = `node-${this.currentNodeId++}`;
        treeElement.id = nodeId;
        treeElement.dataset.path = node.path || '';
        
        const nodeContent = document.createElement('div');
        nodeContent.className = 'node-content';
        
        // Адаптируем ширину узлов в зависимости от уровня
        // Чем глубже уровень, тем уже узел
        const scaleLevel = Math.max(0.6, 1 - (depth * 0.05));
        nodeContent.style.transform = `scale(${scaleLevel})`;
        // Убираем эффект масштабирования на отступы
        nodeContent.style.margin = `${4 / scaleLevel}px`;
        
        if (node.is_leaf) {
            nodeContent.classList.add('leaf-node');
            nodeContent.innerHTML = `
                <div class="node-directions">
                </div>
                <div class="node-value">${this.target_name}: ${node.value}</div>
            `;
        } else {
            nodeContent.innerHTML = `
                <div class="node-directions">
                    <span class="direction yes">Да</span>
                    <span class="direction no">Нет</span>
                </div>
                <div class="node-split">${node.feature_name} ≤ ${node.threshold.toFixed(2)}</div>
            `;
            
            const children = document.createElement('div');
            children.className = 'node-children';
            
            const leftChild = this.createTreeElement(node.left, depth + 1);
            leftChild.classList.add('left-child');
            
            const rightChild = this.createTreeElement(node.right, depth + 1);
            rightChild.classList.add('right-child');
            
            children.appendChild(leftChild);
            children.appendChild(rightChild);
            treeElement.appendChild(children);
        }
        
        treeElement.appendChild(nodeContent);
        return treeElement;
    }
    
    async predict() {
        try {
            if (!this.predictionFileInput.files || this.predictionFileInput.files.length === 0) {
                alert('Выберите CSV файл для прогнозирования!');
                return;
            }
            
            const file = this.predictionFileInput.files[0];
            
            this.resetHighlightedPath();
            
            const formData = new FormData();
            formData.append('file', file);
            
            const treeDataStr = JSON.stringify({
                tree: this.tree,
                feature_names: this.feature_names,
                target_name: this.target_name
            });
            formData.append('tree_data', treeDataStr);
            
            const response = await fetch('http://localhost:8000/decision/predict', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.error) {
                alert(`Ошибка: ${result.error}`);
                return;
            }
            
            this.predictionResult.textContent = `Результат: ${result.prediction}`;
            this.predictionPath.textContent = `Путь: ${result.path}`;
            
            this.highlightPath(result.path);
        } catch (error) {
            console.error('Ошибка при прогнозировании:', error);
            alert('Произошла ошибка при прогнозировании. Проверьте формат данных.');
        }
    }
    
    highlightPath(path) {
        if (!path) return;
        
        this.resetHighlightedPath();
        
        const nodeElement = document.querySelector(`.tree-node[data-path="${path}"]`);
        if (nodeElement) {
            nodeElement.classList.add('highlighted-node');
            
            setTimeout(() => {
                nodeElement.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'center' 
                });
            }, 100);
        }
    }
    
    resetHighlightedPath() {
        const highlightedNodes = document.querySelectorAll('.highlighted-node');
        highlightedNodes.forEach(node => {
            node.classList.remove('highlighted-node');
        });
    }
} 