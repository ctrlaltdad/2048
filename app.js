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
        this.ui.updateDescription();
        this.ui.updateLayoutForDevice();
    }

    setupEventListeners() {
        // Mode switching buttons
        this.ui.elements.controls.play?.addEventListener('click', () => this.setMode('play'));
        this.ui.elements.controls.heuristic?.addEventListener('click', () => this.toggleEmulationPanel());
        this.ui.elements.controls.analysis?.addEventListener('click', () => this.toggleAnalysisPanel());
        this.ui.elements.controls.reset?.addEventListener('click', () => this.resetGame());
        
        // New emulation controls
        document.getElementById('btn-start-emulation')?.addEventListener('click', () => this.startEmulation());
        document.getElementById('btn-stop-emulation')?.addEventListener('click', () => this.stopEmulation());
        
        // New analysis controls
        document.getElementById('btn-start-analysis')?.addEventListener('click', () => this.startBatchAnalysis());
        document.getElementById('btn-stop-analysis')?.addEventListener('click', () => this.stopAnalysis());
        
        // Analysis tab switching
        document.querySelectorAll('.analysis-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const mode = e.target.getAttribute('data-mode');
                this.switchAnalysisTab(mode);
            });
        });
        
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
        
        // Touch controls for mobile devices
        this.setupTouchControls();
        
        // Window resize handler
        window.addEventListener('resize', () => this.ui.updateLayoutForDevice());
        
        // Close panels when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
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
                // Don't auto-start emulation, just set the mode
                this.ui.showNotification('Heuristic mode activated. Configure settings and click Start.', 'info');
                break;
            case 'analysis':
                // Don't auto-start analysis, just set the mode
                this.ui.showNotification('Analysis mode activated. Configure settings and click Start.', 'info');
                break;
        }
        
        this.ui.updateDescription();
        this.ui.drawBoard(this.game);
        
        if (this.mode !== 'analysis') {
            this.ui.updateStats('No statistics yet.');
        }
    }

    stopCurrentMode() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
            this.resetEmulationButtons();
        }
        
        if (this.analysis.getStatus().isRunning) {
            this.analysis.stopAnalysis();
            // Reset analysis button states
            const startBtn = document.getElementById('btn-start-analysis');
            const stopBtn = document.getElementById('btn-stop-analysis');
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
        }
    }

    startManualPlay() {
        this.ui.showNotification('Manual play mode activated. Use arrow keys or WASD.', 'info');
    }

    startHeuristicEmulation(delay = 300) {
        // Read from the dropdown panel elements, not the old UI elements
        const heuristicType = document.getElementById('heuristicSelect')?.value || 'monotonicity';
        const twoPhase = document.getElementById('twophase')?.checked || false;
        
        this.ui.showNotification(`Starting ${heuristicType} heuristic emulation`, 'info');
        
        this.interval = setInterval(() => {
            if (this.mode !== 'heuristic') {
                clearInterval(this.interval);
                this.interval = null;
                this.resetEmulationButtons();
                return;
            }
            
            if (this.game.gameOver) {
                clearInterval(this.interval);
                this.interval = null;
                this.ui.showNotification('Heuristic emulation finished - Game Over!', 'warning');
                this.resetEmulationButtons();
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
                this.interval = null;
                this.ui.showNotification('No valid moves - Game Over!', 'warning');
                this.resetEmulationButtons();
            }
        }, delay); // Delay in milliseconds
    }

    resetEmulationButtons() {
        const startBtn = document.getElementById('btn-start-emulation');
        const stopBtn = document.getElementById('btn-stop-emulation');
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
    }

    resetGame() {
        this.stopCurrentMode();
        this.game.initBoard();
        this.ui.drawBoard(this.game);
        this.ui.clearAnalysis();
        this.ui.showNotification('Game reset', 'info');
        
        // Restart current mode if it was heuristic emulation
        if (this.mode === 'heuristic' && this.interval) {
            // If emulation was running, restart it with the same settings
            const speed = parseFloat(document.getElementById('emulationSpeed')?.value) || 0.3;
            setTimeout(() => this.startHeuristicEmulation(speed * 1000), 500);
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
            const speed = parseFloat(document.getElementById('emulationSpeed')?.value) || 0.3;
            this.startHeuristicEmulation(speed * 1000);
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

    // Panel management methods
    toggleEmulationPanel() {
        this.hideAllPanels();
        const panel = document.getElementById('emulation-panel');
        const button = document.getElementById('btn-heuristic');
        
        if (panel && button) {
            panel.classList.toggle('hidden');
            button.classList.toggle('button-active', !panel.classList.contains('hidden'));
            this.updateControlsLayout(!panel.classList.contains('hidden'));
            
            if (!panel.classList.contains('hidden')) {
                this.ui.showNotification('Configure emulation settings below', 'info');
            }
        }
    }

    toggleAnalysisPanel() {
        this.hideAllPanels();
        const panel = document.getElementById('analysis-panel');
        const button = document.getElementById('btn-analysis');
        
        if (panel && button) {
            panel.classList.toggle('hidden');
            button.classList.toggle('button-active', !panel.classList.contains('hidden'));
            this.updateControlsLayout(!panel.classList.contains('hidden'));
            
            if (!panel.classList.contains('hidden')) {
                this.ui.showNotification('Configure analysis settings below', 'info');
            }
        }
    }

    hideAllPanels() {
        const panels = ['emulation-panel', 'analysis-panel'];
        const buttons = ['btn-heuristic', 'btn-analysis'];
        
        panels.forEach(panelId => {
            const panel = document.getElementById(panelId);
            if (panel) panel.classList.add('hidden');
        });
        
        buttons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) button.classList.remove('button-active');
        });
        
        this.updateControlsLayout(false);
    }

    updateControlsLayout(panelOpen) {
        const controls = document.getElementById('controls');
        if (controls) {
            controls.classList.toggle('panel-open', panelOpen);
        }
    }

    handleOutsideClick(e) {
        // Don't close panels during emulation or analysis
        if (this.interval || this.analysis.isRunning) {
            return;
        }
        
        const panels = document.querySelectorAll('.dropdown-panel:not(.hidden)');
        const buttons = document.querySelectorAll('#btn-heuristic, #btn-analysis');
        
        let clickedInsidePanel = false;
        let clickedButton = false;
        
        panels.forEach(panel => {
            if (panel.contains(e.target)) {
                clickedInsidePanel = true;
            }
        });
        
        buttons.forEach(button => {
            if (button.contains(e.target)) {
                clickedButton = true;
            }
        });
        
        if (!clickedInsidePanel && !clickedButton) {
            this.hideAllPanels();
        }
    }

    // Enhanced emulation methods
    startEmulation() {
        const heuristicType = document.getElementById('heuristicSelect')?.value || 'monotonicity';
        const speed = parseFloat(document.getElementById('emulationSpeed')?.value) || 0.3;
        const twoPhase = document.getElementById('twophase')?.checked || false;
        
        // Stop any running processes first
        this.stopCurrentMode();
        
        // Set mode without auto-starting
        this.mode = 'heuristic';
        this.ui.updateDescription();
        
        // Start emulation with the correct parameters
        this.startHeuristicEmulation(speed * 1000); // Convert to milliseconds
        
        // Update button states
        const startBtn = document.getElementById('btn-start-emulation');
        const stopBtn = document.getElementById('btn-stop-emulation');
        if (startBtn) startBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = false;
        
        this.ui.showNotification(`Starting ${heuristicType} emulation at ${speed}s per move`, 'info');
    }

    stopEmulation() {
        this.stopCurrentMode();
        
        // Update button states
        const startBtn = document.getElementById('btn-start-emulation');
        const stopBtn = document.getElementById('btn-stop-emulation');
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        
        this.ui.showNotification('Emulation stopped', 'warning');
    }

    // Enhanced analysis methods
    async startBatchAnalysis() {
        const analysisMode = this.getCurrentAnalysisMode();
        
        // Update button states
        const startBtn = document.getElementById('btn-start-analysis');
        const stopBtn = document.getElementById('btn-stop-analysis');
        if (startBtn) startBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = false;
        
        try {
            let results;
            if (analysisMode === 'compare') {
                results = await this.runMultipleStrategyAnalysis();
            } else if (analysisMode === 'twophase') {
                results = await this.runTwoPhaseAnalysis();
            } else {
                results = await this.runSingleStrategyAnalysis();
            }
            
            // Update statistics and show stats tab
            if (results) {
                this.updateStatisticsForMode(analysisMode, results);
                this.ui.showTab('stats');
            }
        } finally {
            // Reset button states
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
        }
    }

    async runSingleStrategyAnalysis() {
        const heuristicType = document.getElementById('analysisHeuristic')?.value || 'monotonicity';
        const runs = parseInt(document.getElementById('analysisRuns')?.value) || 20;
        
        const description = this.getAnalysisDescription();
        this.ui.showNotification(`Starting: ${description} (${runs} games)`, 'info');
        
        try {
            const results = await this.analysis.runAnalysis(heuristicType, false, runs);
            this.ui.showNotification('Single strategy analysis completed!', 'success');
            return results;
        } catch (error) {
            console.error('Analysis failed:', error);
            this.ui.showNotification('Analysis failed. Check console for details.', 'error');
        }
    }

    async runMultipleStrategyAnalysis() {
        const checkboxes = document.querySelectorAll('.strategy-checkboxes input:checked');
        const strategies = Array.from(checkboxes).map(cb => cb.value);
        const runs = parseInt(document.getElementById('analysisRuns')?.value) || 20;
        
        if (strategies.length === 0) {
            this.ui.showNotification('Please select at least one strategy to compare', 'warning');
            return;
        }
        
        if (strategies.length === 1) {
            this.ui.showNotification('Select multiple strategies for comparison, or use Single Strategy mode', 'warning');
            return;
        }
        
        const description = this.getAnalysisDescription();
        this.ui.showNotification(`Starting: ${description} (${runs} games)`, 'info');
        
        try {
            const results = await this.analysis.runComparisonAnalysis(strategies, false, runs);
            this.ui.showNotification('Multi-strategy comparison completed!', 'success');
            return results;
        } catch (error) {
            console.error('Comparison analysis failed:', error);
            this.ui.showNotification('Comparison analysis failed. Check console for details.', 'error');
        }
    }

    async runTwoPhaseAnalysis() {
        const earlyStrategy = document.getElementById('twophaseEarly')?.value || 'corner';
        const lateStrategy = document.getElementById('twophaseLate')?.value || 'expectimaxCorner';
        const threshold = parseInt(document.getElementById('twophaseThreshold')?.value) || 128;
        const runs = parseInt(document.getElementById('analysisRuns')?.value) || 20;
        
        if (earlyStrategy === lateStrategy) {
            this.ui.showNotification('Please select different strategies for early and late game', 'warning');
            return;
        }
        
        const description = this.getAnalysisDescription();
        this.ui.showNotification(`Starting: ${description} (${runs} games)`, 'info');
        
        try {
            const results = await this.analysis.runTwoPhaseAnalysis(earlyStrategy, lateStrategy, threshold, runs);
            this.ui.showNotification('Two-phase strategy analysis completed!', 'success');
            return results;
        } catch (error) {
            console.error('Two-phase analysis failed:', error);
            this.ui.showNotification('Two-phase analysis failed. Check console for details.', 'error');
        }
    }

    stopAnalysis() {
        this.analysis.stopAnalysis();
        
        // Update button states
        const startBtn = document.getElementById('btn-start-analysis');
        const stopBtn = document.getElementById('btn-stop-analysis');
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        
        this.ui.showNotification('Analysis stopped', 'warning');
    }

    // Helper method to get analysis description
    getAnalysisDescription() {
        const analysisMode = this.getCurrentAnalysisMode();
        
        if (analysisMode === 'compare') {
            const checkboxes = document.querySelectorAll('.strategy-checkboxes input:checked');
            const strategies = Array.from(checkboxes).map(cb => cb.value);
            const strategyNames = Array.from(checkboxes).map(cb => cb.nextSibling.textContent.trim());
            
            if (strategies.length === 0) {
                return 'No strategies selected for comparison';
            }
            
            return `Compare ${strategies.length} strategies: ${strategyNames.join(', ')}`;
        } else if (analysisMode === 'twophase') {
            const earlyStrategy = document.getElementById('twophaseEarly')?.value || 'corner';
            const lateStrategy = document.getElementById('twophaseLate')?.value || 'expectimaxCorner';
            const threshold = parseInt(document.getElementById('twophaseThreshold')?.value) || 128;
            
            const earlySelect = document.getElementById('twophaseEarly');
            const lateSelect = document.getElementById('twophaseLate');
            const earlyName = earlySelect?.options[earlySelect.selectedIndex]?.text || earlyStrategy;
            const lateName = lateSelect?.options[lateSelect.selectedIndex]?.text || lateStrategy;
            
            return `Two-phase: ${earlyName} → ${lateName} (switch at ${threshold})`;
        } else {
            const heuristicType = document.getElementById('analysisHeuristic')?.value || 'monotonicity';
            const select = document.getElementById('analysisHeuristic');
            const heuristicName = select?.options[select.selectedIndex]?.text || heuristicType;
            
            return `Analyze ${heuristicName}`;
        }
    }

    switchAnalysisTab(mode) {
        // Update tab buttons
        document.querySelectorAll('.analysis-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`)?.classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.analysis-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`analysis-${mode}`)?.classList.add('active');
    }

    getCurrentAnalysisMode() {
        const activeTab = document.querySelector('.analysis-tab.active');
        return activeTab?.getAttribute('data-mode') || 'single';
    }

    updateStatisticsForMode(analysisMode, results) {
        let statsContent = '';
        
        switch (analysisMode) {
            case 'compare':
                statsContent = this.formatComparisonStatistics(results);
                break;
            case 'twophase':
                statsContent = this.formatTwoPhaseStatistics(results);
                break;
            default: // single strategy
                statsContent = this.formatSingleStrategyStatistics(results);
                break;
        }
        
        this.ui.updateStats(statsContent);
    }

    formatSingleStrategyStatistics(results) {
        if (!results || !results.games) return '<p>No results available</p>';
        
        const games = results.games;
        const totalGames = games.length;
        const scores = games.map(g => g.score);
        const maxTiles = games.map(g => g.maxTile);
        const moves = games.map(g => g.moves);
        
        const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / totalGames);
        const maxScore = Math.max(...scores);
        const minScore = Math.min(...scores);
        const avgMoves = Math.round(moves.reduce((a, b) => a + b, 0) / totalGames);
        const maxTileCount = {};
        
        maxTiles.forEach(tile => {
            maxTileCount[tile] = (maxTileCount[tile] || 0) + 1;
        });
        
        const reached2048 = maxTiles.filter(tile => tile >= 2048).length;
        const winRate = ((reached2048 / totalGames) * 100).toFixed(1);
        
        return `
            <div class="statistics-content">
                <h4>📊 Single Strategy Analysis Results</h4>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h5>🎯 Performance Overview</h5>
                        <ul>
                            <li><strong>Strategy:</strong> ${results.strategy || 'Unknown'}</li>
                            <li><strong>Games Played:</strong> ${totalGames}</li>
                            <li><strong>Win Rate (2048+):</strong> ${winRate}%</li>
                            <li><strong>Success Rate:</strong> ${reached2048}/${totalGames} games</li>
                        </ul>
                    </div>
                    
                    <div class="stat-card">
                        <h5>📈 Score Statistics</h5>
                        <ul>
                            <li><strong>Average Score:</strong> ${avgScore.toLocaleString()}</li>
                            <li><strong>Highest Score:</strong> ${maxScore.toLocaleString()}</li>
                            <li><strong>Lowest Score:</strong> ${minScore.toLocaleString()}</li>
                            <li><strong>Score Range:</strong> ${(maxScore - minScore).toLocaleString()}</li>
                        </ul>
                    </div>
                    
                    <div class="stat-card">
                        <h5>🎮 Game Metrics</h5>
                        <ul>
                            <li><strong>Average Moves:</strong> ${avgMoves}</li>
                            <li><strong>Most Common Max Tile:</strong> ${Object.entries(maxTileCount).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'}</li>
                            <li><strong>Efficiency:</strong> ${(avgScore / avgMoves).toFixed(1)} pts/move</li>
                        </ul>
                    </div>
                    
                    <div class="stat-card">
                        <h5>🏆 Max Tile Distribution</h5>
                        <div class="tile-distribution">
                            ${Object.entries(maxTileCount)
                                .sort((a, b) => parseInt(b[0]) - parseInt(a[0]))
                                .map(([tile, count]) => {
                                    const percentage = ((count/totalGames)*100).toFixed(1);
                                    const barWidth = (count/totalGames)*100;
                                    return `
                                        <div class="tile-dist-item">
                                            <div class="tile-label">
                                                <strong>${tile}</strong>
                                                <span>${count} games (${percentage}%)</span>
                                            </div>
                                            <div class="tile-bar">
                                                <div class="tile-fill" style="width: ${barWidth}%"></div>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatComparisonStatistics(results) {
        if (!results || !results.results || Object.keys(results.results).length === 0) {
            return '<p>No comparison results available</p>';
        }
        
        console.log('Comparison results structure:', results);
        
        // Convert the results object to an array format for processing
        const strategyResults = Object.entries(results.results).map(([strategy, data]) => {
            console.log(`Processing strategy ${strategy}:`, data);
            
            // Calculate statistics for each strategy's data
            const stats = this.analysis.calculateStatistics(data);
            console.log(`Calculated stats for ${strategy}:`, stats);
            
            const totalGames = data.runs || data.maxTiles?.length || 0;
            
            return {
                strategy: strategy,
                avgScore: stats.avgScore || 0,
                maxScore: stats.maxScore || 0,
                minScore: stats.minScore || 0,
                avgMoves: stats.avgMoves || 0,
                totalGames: totalGames,
                gamesReached2048: stats.winCount || 0
            };
        });
        
        const sortedResults = strategyResults.sort((a, b) => b.avgScore - a.avgScore);
        
        return `
            <div class="statistics-content">
                <h4>⚔️ Strategy Comparison Results</h4>
                <div class="comparison-stats">
                    <div class="stat-card">
                        <h5>🏆 Strategy Rankings</h5>
                        <ol class="strategy-ranking">
                            ${sortedResults.map((result, index) => {
                                const winRate = ((result.gamesReached2048 / result.totalGames) * 100).toFixed(1);
                                const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🔹';
                                return `
                                    <li>
                                        <strong>${medal} ${result.strategy}</strong>
                                        <div class="strategy-details">
                                            <span>Avg Score: ${Math.round(result.avgScore).toLocaleString()}</span>
                                            <span>Win Rate: ${winRate}%</span>
                                            <span>Games: ${result.totalGames}</span>
                                        </div>
                                    </li>
                                `;
                            }).join('')}
                        </ol>
                    </div>
                    
                    <div class="stat-card">
                        <h5>📊 Detailed Comparison</h5>
                        <div class="comparison-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Strategy</th>
                                        <th>Avg Score</th>
                                        <th>Max Score</th>
                                        <th>Win Rate</th>
                                        <th>Avg Moves</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${sortedResults.map(result => {
                                        const winRate = ((result.gamesReached2048 / result.totalGames) * 100).toFixed(1);
                                        return `
                                            <tr>
                                                <td><strong>${result.strategy}</strong></td>
                                                <td>${Math.round(result.avgScore).toLocaleString()}</td>
                                                <td>${result.maxScore.toLocaleString()}</td>
                                                <td>${winRate}%</td>
                                                <td>${Math.round(result.avgMoves)}</td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <h5>🎯 Performance Insights</h5>
                        <ul>
                            <li><strong>Best Overall:</strong> ${sortedResults[0]?.strategy} (${Math.round(sortedResults[0]?.avgScore).toLocaleString()} avg score)</li>
                            <li><strong>Highest Single Game:</strong> ${Math.max(...strategyResults.map(r => r.maxScore)).toLocaleString()}</li>
                            <li><strong>Most Consistent:</strong> ${strategyResults.reduce((prev, curr) => 
                                (curr.maxScore - curr.minScore) < (prev.maxScore - prev.minScore) ? curr : prev
                            ).strategy}</li>
                            <li><strong>Most Efficient:</strong> ${strategyResults.reduce((prev, curr) => 
                                (curr.avgScore / curr.avgMoves) > (prev.avgScore / prev.avgMoves) ? curr : prev
                            ).strategy} (${((strategyResults.reduce((prev, curr) => 
                                (curr.avgScore / curr.avgMoves) > (prev.avgScore / prev.avgMoves) ? curr : prev
                            ).avgScore / strategyResults.reduce((prev, curr) => 
                                (curr.avgScore / curr.avgMoves) > (prev.avgScore / prev.avgMoves) ? curr : prev
                            ).avgMoves)).toFixed(1)} pts/move)</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    formatTwoPhaseStatistics(results) {
        if (!results || !results.games) return '<p>No two-phase results available</p>';
        
        const games = results.games;
        const totalGames = games.length;
        const scores = games.map(g => g.score);
        const maxTiles = games.map(g => g.maxTile);
        const moves = games.map(g => g.moves);
        
        const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / totalGames);
        const maxScore = Math.max(...scores);
        const reached2048 = maxTiles.filter(tile => tile >= 2048).length;
        const winRate = ((reached2048 / totalGames) * 100).toFixed(1);
        
        return `
            <div class="statistics-content">
                <h4>🔄 Two-Phase Strategy Analysis</h4>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h5>⚙️ Strategy Configuration</h5>
                        <ul>
                            <li><strong>Primary Strategy:</strong> Monotonicity</li>
                            <li><strong>Secondary Strategy:</strong> ${results.secondaryStrategy || 'Unknown'}</li>
                            <li><strong>Games Played:</strong> ${totalGames}</li>
                            <li><strong>Strategy Type:</strong> Two-Phase Adaptive</li>
                        </ul>
                    </div>
                    
                    <div class="stat-card">
                        <h5>📈 Performance Results</h5>
                        <ul>
                            <li><strong>Average Score:</strong> ${avgScore.toLocaleString()}</li>
                            <li><strong>Highest Score:</strong> ${maxScore.toLocaleString()}</li>
                            <li><strong>Win Rate (2048+):</strong> ${winRate}%</li>
                            <li><strong>Success Rate:</strong> ${reached2048}/${totalGames} games</li>
                        </ul>
                    </div>
                    
                    <div class="stat-card">
                        <h5>🎯 Two-Phase Benefits</h5>
                        <ul>
                            <li><strong>Adaptive Strategy:</strong> Switches between strategies based on game state</li>
                            <li><strong>Early Game:</strong> Focuses on monotonic tile organization</li>
                            <li><strong>Mid/Late Game:</strong> Applies secondary strategy for optimization</li>
                            <li><strong>Efficiency:</strong> ${(avgScore / (moves.reduce((a, b) => a + b, 0) / totalGames)).toFixed(1)} pts/move</li>
                        </ul>
                    </div>
                    
                    <div class="stat-card">
                        <h5>📊 Game Distribution</h5>
                        <ul>
                            ${Object.entries(maxTiles.reduce((acc, tile) => {
                                acc[tile] = (acc[tile] || 0) + 1;
                                return acc;
                            }, {}))
                            .sort((a, b) => parseInt(b[0]) - parseInt(a[0]))
                            .map(([tile, count]) => `<li><strong>${tile} Tile:</strong> ${count} games (${((count/totalGames)*100).toFixed(1)}%)</li>`)
                            .join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    setupTouchControls() {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        const minSwipeDistance = 50; // Minimum distance for a swipe
        
        const gameBoard = document.getElementById('board');
        if (!gameBoard) return;
        
        // Prevent default touch behaviors on the game board
        gameBoard.addEventListener('touchstart', (e) => {
            if (this.mode !== 'play') return;
            
            // Prevent scrolling and zooming on the game board
            e.preventDefault();
            
            const touch = e.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
        }, { passive: false });
        
        gameBoard.addEventListener('touchmove', (e) => {
            if (this.mode !== 'play') return;
            
            // Prevent scrolling while touching the game board
            e.preventDefault();
        }, { passive: false });
        
        gameBoard.addEventListener('touchend', (e) => {
            if (this.mode !== 'play') return;
            
            e.preventDefault();
            
            const touch = e.changedTouches[0];
            touchEndX = touch.clientX;
            touchEndY = touch.clientY;
            
            // Calculate swipe distances
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            const absDeltaX = Math.abs(deltaX);
            const absDeltaY = Math.abs(deltaY);
            
            // Check if it's a valid swipe (minimum distance)
            if (Math.max(absDeltaX, absDeltaY) < minSwipeDistance) {
                return; // Not a swipe, just a tap
            }
            
            let direction = null;
            
            // Determine swipe direction (prioritize the larger movement)
            if (absDeltaX > absDeltaY) {
                // Horizontal swipe
                direction = deltaX > 0 ? 'right' : 'left';
            } else {
                // Vertical swipe
                direction = deltaY > 0 ? 'down' : 'up';
            }
            
            // Execute the move
            if (direction && this.game.move(direction)) {
                this.ui.drawBoard(this.game);
                
                // Provide haptic feedback if available
                if (navigator.vibrate) {
                    navigator.vibrate(50); // Short vibration
                }
                
                if (this.game.gameOver) {
                    this.ui.showNotification('Game Over!', 'warning');
                } else if (this.game.getMaxTile() >= 2048) {
                    // Check if this is the first time reaching 2048
                    const prevMaxTile = this.game.getMaxTile();
                    if (prevMaxTile === 2048) {
                        this.ui.showNotification('Congratulations! You reached 2048!', 'success');
                        
                        // Celebrate with longer vibration
                        if (navigator.vibrate) {
                            navigator.vibrate([100, 50, 100, 50, 200]);
                        }
                    }
                }
            }
        }, { passive: false });
        
        // Add visual feedback for touch
        gameBoard.addEventListener('touchstart', () => {
            gameBoard.style.transform = 'scale(0.98)';
        });
        
        gameBoard.addEventListener('touchend', () => {
            gameBoard.style.transform = 'scale(1)';
        });
        
        gameBoard.addEventListener('touchcancel', () => {
            gameBoard.style.transform = 'scale(1)';
        });
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
