// Main Application Controller
class App2048 {
    constructor() {
        this.game = new Game2048();
        this.heuristics = new Heuristics();
        this.ui = new UIManager();
        this.analysis = new AnalysisManager(this.game, this.heuristics, this.ui);
        
        this.mode = 'play';
        this.interval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.ui.drawBoard(this.game);
        this.ui.showTab('desc');
        this.ui.updateDescription(this.mode);
        this.ui.updateLayoutForDevice();
    }

    setupEventListeners() {
        // Mode switching buttons
        this.ui.elements.controls.play?.addEventListener('click', () => this.setMode('play'));
        this.ui.elements.controls.heuristic?.addEventListener('click', () => this.setMode('heuristic'));
        this.ui.elements.controls.analysis?.addEventListener('click', () => this.setMode('analysis'));
        this.ui.elements.controls.reset?.addEventListener('click', () => this.resetGame());
        
        // Export buttons
        this.ui.elements.controls.csv?.addEventListener('click', () => this.analysis.exportResults('csv'));
        this.ui.elements.controls.html?.addEventListener('click', () => this.analysis.exportResults('html'));
        
        // Settings buttons
        this.ui.elements.controls.applySettings?.addEventListener('click', () => this.applySettings());
        this.ui.elements.controls.startOptimization?.addEventListener('click', () => this.startOptimization());
        this.ui.elements.controls.stopOptimization?.addEventListener('click', () => this.stopOptimization());
        this.ui.elements.controls.applyOptimized?.addEventListener('click', () => this.applyOptimizedWeights());
        
        // Keyboard controls for manual play
        this.setupKeyboardControls();
        
        // Window resize handler
        window.addEventListener('resize', () => this.ui.updateLayoutForDevice());
        
        // Heuristic selection changes
        this.ui.elements.heuristicSelect?.addEventListener('change', () => {
            this.ui.updateDescription(this.mode);
        });
        
        this.ui.elements.twophase?.addEventListener('change', () => {
            this.ui.updateDescription(this.mode);
        });
    }

    setupKeyboardControls() {
        const keyHandler = (e) => {
            if (this.mode !== 'play') return;
            
            const key = e.key.toLowerCase();
            const validKeys = ['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'];
            
            if (validKeys.includes(key)) {
                e.preventDefault();
                
                let direction = null;
                if (key === 'arrowup' || key === 'w') direction = 'up';
                if (key === 'arrowdown' || key === 's') direction = 'down';
                if (key === 'arrowleft' || key === 'a') direction = 'left';
                if (key === 'arrowright' || key === 'd') direction = 'right';
                
                if (direction && this.game.move(direction)) {
                    this.ui.drawBoard(this.game);
                    
                    if (this.game.gameOver) {
                        this.ui.showNotification('Game Over!', 'warning');
                    } else if (this.game.getMaxTile() >= 2048) {
                        // Check if this is the first time reaching 2048
                        const prevMaxTile = this.game.getMaxTile();
                        if (prevMaxTile === 2048) {
                            this.ui.showNotification('Congratulations! You reached 2048!', 'success');
                        }
                    }
                }
            }
        };
        
        // Remove existing listener and add new one
        document.removeEventListener('keydown', keyHandler);
        document.addEventListener('keydown', keyHandler);
    }

    setMode(newMode) {
        // Stop any running processes
        this.stopCurrentMode();
        
        this.mode = newMode;
        this.ui.clearAnalysis();
        
        switch (newMode) {
            case 'play':
                this.startManualPlay();
                break;
            case 'heuristic':
                this.startHeuristicEmulation();
                break;
            case 'analysis':
                this.startAnalysis();
                break;
        }
        
        this.ui.updateDescription(this.mode);
        this.ui.drawBoard(this.game);
        
        if (this.mode !== 'analysis') {
            this.ui.updateStats('No statistics yet.');
        }
    }

    stopCurrentMode() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        
        if (this.analysis.getStatus().isRunning) {
            this.analysis.stopAnalysis();
        }
    }

    startManualPlay() {
        this.ui.showNotification('Manual play mode activated. Use arrow keys or WASD.', 'info');
    }

    startHeuristicEmulation(delay = 300) {
        const heuristicType = this.ui.elements.heuristicSelect?.value || 'monotonicity';
        const twoPhase = this.ui.elements.twophase?.checked || false;
        
        this.ui.showNotification(`Starting ${heuristicType} heuristic emulation`, 'info');
        
        this.interval = setInterval(() => {
            if (this.mode !== 'heuristic') {
                clearInterval(this.interval);
                return;
            }
            
            if (this.game.gameOver) {
                clearInterval(this.interval);
                this.ui.showNotification('Heuristic emulation finished - Game Over!', 'warning');
                return;
            }
            
            const move = this.heuristics.pickMove(this.game, heuristicType, twoPhase);
            
            if (move && this.game.move(move)) {
                this.ui.drawBoard(this.game);
                
                // Check for 2048 achievement
                if (this.game.getMaxTile() >= 2048) {
                    this.ui.showNotification(`Heuristic reached ${this.game.getMaxTile()}!`, 'success');
                }
            } else {
                clearInterval(this.interval);
                this.ui.showNotification('No valid moves - Game Over!', 'warning');
            }
        }, delay); // Delay in milliseconds
    }

    async startAnalysis() {
        const heuristicType = this.ui.elements.heuristicSelect?.value || 'monotonicity';
        const twoPhase = this.ui.elements.twophase?.checked || false;
        const settings = this.ui.getSettings();
        const runs = settings.runs;
        
        this.ui.showNotification(`Starting analysis with ${runs} runs`, 'info');
        
        try {
            const results = await this.analysis.runAnalysis(heuristicType, twoPhase, runs);
            this.ui.showNotification('Analysis completed successfully!', 'success');
            return results;
        } catch (error) {
            console.error('Analysis failed:', error);
            this.ui.showNotification('Analysis failed. Check console for details.', 'error');
        }
    }

    resetGame() {
        this.stopCurrentMode();
        this.game.initBoard();
        this.ui.drawBoard(this.game);
        this.ui.clearAnalysis();
        this.ui.showNotification('Game reset', 'info');
        
        // Restart current mode if it was heuristic emulation
        if (this.mode === 'heuristic') {
            setTimeout(() => this.startHeuristicEmulation(), 500);
        }
    }

    // Settings management
    applySettings() {
        const settings = this.ui.getSettings();
        
        // Apply custom weights to heuristics
        this.heuristics.setCustomWeights(settings.weights);
        
        // Update analysis runs
        this.analysis.setDefaultRuns(settings.runs);
        
        // Update emulation speed if currently running
        if (this.interval) {
            clearInterval(this.interval);
            this.startHeuristicEmulation(settings.pauseDuration * 1000);
        }
        
        this.ui.showNotification('Settings applied successfully!', 'success');
    }

    // ML Optimization functionality (placeholder for future implementation)
    async startOptimization() {
        this.ui.showNotification('Starting ML optimization...', 'info');
        this.ui.setOptimizationButtonsState(true);
        this.ui.showOptimizationProgress(true);
        this.ui.hideOptimizationResults();
        
        const optimizationMethod = document.getElementById('optimizationMethod')?.value || 'random';
        const iterations = parseInt(document.getElementById('optimizationIterations')?.value) || 20;
        const gamesPerEval = parseInt(document.getElementById('gamesPerEvaluation')?.value) || 10;
        
        try {
            // Placeholder optimization logic - in a real implementation, 
            // this would connect to the ML optimization algorithms
            const results = await this.runSimulatedOptimization(optimizationMethod, iterations, gamesPerEval);
            
            this.ui.showOptimizationResults(results);
            this.ui.showNotification('Optimization completed!', 'success');
        } catch (error) {
            console.error('Optimization failed:', error);
            this.ui.showNotification('Optimization failed. Check console for details.', 'error');
        } finally {
            this.ui.setOptimizationButtonsState(false);
            this.ui.showOptimizationProgress(false);
        }
    }

    stopOptimization() {
        this.ui.showNotification('Optimization stopped', 'warning');
        this.ui.setOptimizationButtonsState(false);
        this.ui.showOptimizationProgress(false);
    }

    applyOptimizedWeights() {
        const bestWeights = this.extractBestWeights();
        if (bestWeights) {
            this.ui.setSettings({ weights: bestWeights });
            this.applySettings();
            this.ui.showNotification('Optimized weights applied!', 'success');
        }
    }

    extractBestWeights() {
        // Extract weights from the optimization results display
        const weightsEl = document.getElementById('bestWeights');
        if (!weightsEl) return null;
        
        const weightsText = weightsEl.textContent;
        const weights = {};
        
        weightsText.split('\n').forEach(line => {
            const [key, value] = line.split(':').map(s => s.trim());
            if (key && value) {
                weights[key] = parseFloat(value);
            }
        });
        
        return Object.keys(weights).length > 0 ? weights : null;
    }

    // Simulated optimization for demonstration
    async runSimulatedOptimization(method, iterations, gamesPerEval) {
        const weights = this.ui.getSettings().weights;
        let bestWeights = { ...weights };
        let bestPerformance = { winRate: 0, avgScore: 0 };
        
        for (let i = 0; i < iterations; i++) {
            // Update progress
            this.ui.updateOptimizationProgress(
                (i / iterations) * 100,
                `${method} optimization: ${i + 1}/${iterations}`
            );
            
            // Simulate some computation time
            await this.sleep(100);
            
            // Generate random weight variations
            const testWeights = {};
            Object.keys(weights).forEach(key => {
                testWeights[key] = Math.max(0, weights[key] + (Math.random() - 0.5) * 0.5);
            });
            
            // Simulate performance evaluation
            const performance = {
                winRate: Math.random() * 100,
                avgScore: 10000 + Math.random() * 20000
            };
            
            if (performance.winRate > bestPerformance.winRate) {
                bestPerformance = performance;
                bestWeights = { ...testWeights };
            }
        }
        
        return {
            weights: bestWeights,
            performance: {
                winRate: bestPerformance.winRate.toFixed(1),
                avgScore: Math.round(bestPerformance.avgScore)
            }
        };
    }

    // Utility function for async delays
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Public API methods for external use
    getCurrentGame() {
        return this.game.toJSON();
    }

    setCustomWeights(weights) {
        // Future enhancement: allow custom heuristic weights
        console.log('Custom weights:', weights);
    }

    getAnalysisResults() {
        return this.analysis.currentAnalysis;
    }

    // Development/Debug methods
    setBoard(boardState) {
        if (Array.isArray(boardState) && boardState.length === 4) {
            this.game.board = boardState;
            this.ui.drawBoard(this.game);
        }
    }

    simulateMove(direction) {
        const tempGame = this.game.clone();
        return tempGame.move(direction);
    }

    // Performance monitoring
    measurePerformance(heuristicType, iterations = 100) {
        const startTime = performance.now();
        
        for (let i = 0; i < iterations; i++) {
            const tempGame = this.game.clone();
            this.heuristics.pickMove(tempGame, heuristicType);
        }
        
        const endTime = performance.now();
        const avgTime = (endTime - startTime) / iterations;
        
        console.log(`Average time for ${heuristicType}: ${avgTime.toFixed(2)}ms`);
        return avgTime;
    }
}

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Make app globally available for debugging
    window.app2048 = new App2048();
    
    // Add some development shortcuts
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Development mode detected. Available commands:');
        console.log('- app2048.setBoard(board) - Set custom board state');
        console.log('- app2048.measurePerformance(heuristic) - Measure heuristic performance');
        console.log('- app2048.getCurrentGame() - Get current game state');
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App2048;
}
