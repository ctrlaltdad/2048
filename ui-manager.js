// UI Manager for 2048 game interface
class UIManager {
    constructor() {
        this.currentTab = 'desc';
        this.elements = this.initializeElements();
        this.setupEventListeners();
        // Show default content on load
        this.updateDescriptionContent('overview');
    }

    initializeElements() {
        return {
            board: document.getElementById('board'),
            log: document.getElementById('log'),
            analysis: document.getElementById('analysis'),
            heuristicSelect: document.getElementById('heuristicSelect'),
            twophase: document.getElementById('twophase'),
            descMode: document.getElementById('desc-mode'),
            descHeuristic: document.getElementById('desc-heuristic'),
            descDetails: document.getElementById('desc-details'),
            statsContent: document.getElementById('stats-content'),
            tabDesc: document.getElementById('tab-desc'),
            tabStats: document.getElementById('tab-stats'),
            tabSettings: document.getElementById('tab-settings'),
            tabContentDesc: document.getElementById('tab-content-desc'),
            tabContentStats: document.getElementById('tab-content-stats'),
            tabContentSettings: document.getElementById('tab-content-settings'),
            controls: {
                play: document.getElementById('btn-play'),
                heuristic: document.getElementById('btn-heuristic'),
                analysis: document.getElementById('btn-analysis'),
                reset: document.getElementById('btn-reset'),
                csv: document.getElementById('btn-csv'),
                html: document.getElementById('btn-html'),
                applySettings: document.getElementById('btn-apply-settings'),
                startOptimization: document.getElementById('btn-start-optimization'),
                stopOptimization: document.getElementById('btn-stop-optimization'),
                applyOptimized: document.getElementById('btn-apply-optimized')
            }
        };
    }

    setupEventListeners() {
        // Tab switching
        this.elements.tabDesc?.addEventListener('click', () => this.showTab('desc'));
        this.elements.tabStats?.addEventListener('click', () => this.showTab('stats'));
        this.elements.tabSettings?.addEventListener('click', () => this.showTab('settings'));
        
        // Heuristic selection changes
        this.elements.heuristicSelect?.addEventListener('change', () => this.updateDescription());
        this.elements.twophase?.addEventListener('change', () => this.updateDescription());
        
        // Description system setup
        this.setupDescriptionSystem();
    }

    setupDescriptionSystem() {
        const descTopicSelect = document.getElementById('desc-topic');
        if (descTopicSelect) {
            descTopicSelect.addEventListener('change', (e) => {
                this.updateDescriptionContent(e.target.value);
            });
        }
    }

    showTab(tabName) {
        // Hide all tab contents
        ['desc', 'stats', 'settings'].forEach(tab => {
            const content = document.getElementById(`tab-content-${tab}`);
            const tabButton = document.getElementById(`tab-${tab}`);
            if (content) content.style.display = 'none';
            if (tabButton) tabButton.classList.remove('active');
        });

        // Show selected tab
        const selectedContent = document.getElementById(`tab-content-${tabName}`);
        const selectedTab = document.getElementById(`tab-${tabName}`);
        if (selectedContent) selectedContent.style.display = 'block';
        if (selectedTab) selectedTab.classList.add('active');
        
        this.currentTab = tabName;
    }

    updateDescription() {
        const heuristic = this.elements.heuristicSelect?.value;
        const isTwoPhase = this.elements.twophase?.checked;
        
        if (this.elements.descHeuristic) {
            this.elements.descHeuristic.textContent = heuristic || 'None selected';
        }
        
        if (this.elements.descMode) {
            this.elements.descMode.textContent = isTwoPhase ? 'Two-phase' : 'Single-phase';
        }
        
        // Update details based on heuristic
        let details = '';
        switch (heuristic) {
            case 'monotonicity':
                details = 'Maintains ordered sequences in rows/columns for better tile organization. Focuses on keeping tiles in monotonic order to build larger tiles systematically.';
                break;
            case 'corner':
                details = 'Keeps the highest tile in a corner position. This prevents the largest tile from being trapped and allows for better merging opportunities.';
                break;
            case 'center':
                details = 'Focuses on building large tiles toward the center of the board. Useful for creating merge opportunities from multiple directions.';
                break;
            case 'expectimax':
                details = 'Uses probabilistic search to evaluate future game states. Considers the random tile placement and calculates expected outcomes.';
                break;
            case 'expectimaxCorner':
                details = 'Enhanced expectimax specifically optimized for corner strategy. Combines probabilistic search with corner positioning for superior performance. ⭐ Recommended';
                break;
            case 'gradientDescent':
                details = 'Uses mathematical optimization to find the best move direction. Continuously improves decision-making through gradient-based learning. ⭐ Recommended';
                break;
            case 'opportunistic':
                details = 'Adapts strategy based on current board state. Switches between different approaches depending on available opportunities.';
                break;
            case 'smoothness':
                details = 'Minimizes tile value differences between adjacent cells. Creates more uniform board states that are easier to manage and merge.';
                break;
            case 'adaptive':
                details = 'Dynamically adjusts strategy based on game progression. Changes behavior in early, mid, and late game phases for optimal performance.';
                break;
            case 'ultraAdaptive':
                details = 'Advanced adaptive strategy with more sophisticated phase detection. Uses multiple metrics to determine the best approach for each game state.';
                break;
            case 'advancedMinimax':
                details = 'Enhanced minimax algorithm with deeper search and better evaluation. Looks further ahead to make more informed decisions.';
                break;
            case 'weighted':
                details = 'Combines multiple heuristics with weighted importance. Balances different strategies to leverage the strengths of each approach.';
                break;
            case 'mlsim':
                details = 'Machine learning simulation that mimics successful gameplay patterns. Uses pattern recognition to make human-like strategic decisions. ⭐ Recommended';
                break;
            default:
                details = 'Select a heuristic to see its description.';
        }
        
        if (this.elements.descDetails) {
            this.elements.descDetails.textContent = details;
        }
    }

    updateDescriptionContent(topic) {
        const contentDiv = document.getElementById('desc-content');
        if (!contentDiv) return;
        
        const content = this.getDescriptionContent(topic);
        contentDiv.innerHTML = content;
    }

    getDescriptionContent(topic) {
        switch (topic) {
            case 'overview':
                return `<h4>🎮 Welcome to the 2048 Analysis Tool</h4>
                    <p>This tool helps you analyze and improve your 2048 gameplay using various AI strategies and analysis modes.</p>
                    <h4>🚀 Getting Started</h4>
                    <ul>
                        <li><strong>Play Mode:</strong> Use arrow keys or WASD to play manually</li>
                        <li><strong>Emulation Mode:</strong> Watch AI strategies play automatically</li>
                        <li><strong>Analysis Mode:</strong> Compare strategies and find the best approach</li>
                    </ul>`;
                
            case 'analysis-modes':
                return `<h4>📊 Analysis Modes</h4>
                    <p>Choose the right analysis mode for your needs:</p>
                    <ul>
                        <li><strong>Single Strategy:</strong> Test one strategy across multiple games</li>
                        <li><strong>Strategy Comparison:</strong> Compare multiple strategies head-to-head</li>
                        <li><strong>Parameter Optimization:</strong> Find the best parameters for a strategy</li>
                    </ul>
                    <p>Each mode provides detailed statistics and performance metrics.</p>`;
                
            case 'heuristics':
                return `<h4>🧠 Strategy Heuristics</h4>
                    <p>Understanding the different AI strategies available:</p>
                    <div class="heuristics-grid">
                        <div class="heuristic-item">
                            <h5>Monotonicity</h5>
                            <p>Maintains ordered sequences in rows/columns for better tile organization. Focuses on keeping tiles in monotonic order to build larger tiles systematically.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Corner Strategy</h5>
                            <p>Keeps the highest tile in a corner position. This prevents the largest tile from being trapped and allows for better merging opportunities.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Center Strategy</h5>
                            <p>Focuses on building large tiles toward the center of the board. Useful for creating merge opportunities from multiple directions.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Expectimax</h5>
                            <p>Uses probabilistic search to evaluate future game states. Considers the random tile placement and calculates expected outcomes.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Expectimax Corner ⭐</h5>
                            <p>Enhanced expectimax specifically optimized for corner strategy. Combines probabilistic search with corner positioning for superior performance.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Gradient Descent ⭐</h5>
                            <p>Uses mathematical optimization to find the best move direction. Continuously improves decision-making through gradient-based learning.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Opportunistic</h5>
                            <p>Adapts strategy based on current board state. Switches between different approaches depending on available opportunities.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Smoothness</h5>
                            <p>Minimizes tile value differences between adjacent cells. Creates more uniform board states that are easier to manage and merge.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Adaptive</h5>
                            <p>Dynamically adjusts strategy based on game progression. Changes behavior in early, mid, and late game phases for optimal performance.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Ultra-Adaptive</h5>
                            <p>Advanced adaptive strategy with more sophisticated phase detection. Uses multiple metrics to determine the best approach for each game state.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Advanced Minimax</h5>
                            <p>Enhanced minimax algorithm with deeper search and better evaluation. Looks further ahead to make more informed decisions.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>Weighted Combo</h5>
                            <p>Combines multiple heuristics with weighted importance. Balances different strategies to leverage the strengths of each approach.</p>
                        </div>
                        <div class="heuristic-item">
                            <h5>ML Sim ⭐</h5>
                            <p>Machine learning simulation that mimics successful gameplay patterns. Uses pattern recognition to make human-like strategic decisions.</p>
                        </div>
                    </div>
                    <p><strong>⭐ Recommended:</strong> These strategies typically perform best and are recommended for serious analysis.</p>
                    <p><strong>Two-Phase:</strong> All strategies can be combined with monotonicity in a two-phase approach for potentially better results.</p>`;
                
            case 'tips':
                return `<h4>💡 Tips & Best Practices</h4>
                    <ul>
                        <li><strong>Start with comparisons:</strong> Use strategy comparison to find the best approach</li>
                        <li><strong>Run multiple games:</strong> Use at least 10 games for reliable statistics</li>
                        <li><strong>Try two-phase strategies:</strong> Often more effective than single-phase</li>
                        <li><strong>Watch emulations:</strong> Learn from AI moves and patterns</li>
                        <li><strong>Optimize parameters:</strong> Fine-tune strategies for better performance</li>
                        <li><strong>Export results:</strong> Save your analysis for future reference</li>
                    </ul>
                    <p>Remember: The best strategy depends on your goals - highest score, reaching 2048, or consistent performance.</p>`;
                
            default:
                return '<p>Select a topic to learn more about the 2048 Analysis Tool.</p>';
        }
    }

    // Board display methods
    drawBoard(game) {
        this.updateBoard(game.board);
        this.updateScore(game.score);
    }

    updateBoard(board) {
        if (!this.elements.board) return;
        
        const boardElement = this.elements.board;
        boardElement.innerHTML = '';
        
        for (let r = 0; r < 4; r++) {
            for (let c = 0; c < 4; c++) {
                const cell = document.createElement('div');
                cell.className = 'tile';
                
                const value = board[r][c];
                if (value > 0) {
                    cell.textContent = value;
                    cell.classList.add(`tile-${value}`);
                } else {
                    cell.classList.add('tile-0');
                }
                
                boardElement.appendChild(cell);
            }
        }
    }

    updateScore(score) {
        const scoreElement = document.getElementById('score');
        if (scoreElement) {
            scoreElement.textContent = this.formatScore(score);
        }
    }

    updateLayoutForDevice() {
        // Mobile-responsive adjustments
        const isMobile = window.innerWidth <= 768;
        const board = this.elements.board;
        
        if (board) {
            if (isMobile) {
                board.classList.add('mobile-board');
            } else {
                board.classList.remove('mobile-board');
            }
        }
    }

    // Analysis display
    showAnalysis(content) {
        if (this.elements.analysis) {
            this.elements.analysis.innerHTML = content;
            this.elements.analysis.style.display = 'block';
            this.elements.analysis.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    clearAnalysis() {
        if (this.elements.analysis) {
            this.elements.analysis.innerHTML = '';
        }
    }

    // Statistics updates
    updateStats(content) {
        if (this.elements.statsContent) {
            this.elements.statsContent.innerHTML = content;
        }
    }

    // Progress bar
    createProgressBar(percent) {
        return `
            <div class="progress-bar mb-2">
                <div class="progress-fill" style="width: ${percent}%"></div>
            </div>
        `;
    }

    // Control management
    setButtonState(buttonId, enabled) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = !enabled;
        }
    }

    // Update button states for different modes
    setEmulationMode(isRunning) {
        this.setButtonState('btn-play', !isRunning);
        this.setButtonState('btn-heuristic', isRunning);
        this.setButtonState('btn-analysis', !isRunning);
        this.setButtonState('btn-reset', !isRunning);
    }

    setAnalysisMode(isRunning) {
        this.setButtonState('btn-play', !isRunning);
        this.setButtonState('btn-heuristic', !isRunning);
        this.setButtonState('btn-analysis', isRunning);
        this.setButtonState('btn-reset', !isRunning);
    }

    setControlsDisabled(disabled) {
        // Disable/enable main control buttons during analysis
        this.setButtonState('btn-play', !disabled);
        this.setButtonState('btn-heuristic', !disabled);
        this.setButtonState('btn-analysis', !disabled);
        this.setButtonState('btn-reset', !disabled);
        this.setButtonState('btn-csv', !disabled);
        this.setButtonState('btn-html', !disabled);
        
        // Also disable analysis controls
        this.setButtonState('btn-start-single', !disabled);
        this.setButtonState('btn-start-comparison', !disabled);
        this.setButtonState('btn-start-optimization', !disabled);
        
        // Disable form elements
        const formElements = [
            'heuristicSelect',
            'numGames',
            'analysisMode',
            'optimizationTarget'
        ];
        
        formElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.disabled = disabled;
        });
        
        // Disable strategy checkboxes
        const checkboxes = document.querySelectorAll('.strategy-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.disabled = disabled;
        });
    }

    // Log messages
    log(message, type = 'info') {
        if (this.elements.log) {
            const timestamp = new Date().toLocaleTimeString();
            const logClass = type === 'error' ? 'text-danger' : 
                           type === 'success' ? 'text-success' : 
                           type === 'warning' ? 'text-warning' : '';
            
            this.elements.log.innerHTML += `
                <div class="log-entry">
                    <span class="text-muted">[${timestamp}]</span> 
                    <span class="${logClass}">${message}</span>
                </div>
            `;
            this.elements.log.scrollTop = this.elements.log.scrollHeight;
        }
    }

    clearLog() {
        if (this.elements.log) {
            this.elements.log.innerHTML = '';
        }
    }

    showNotification(message, type = 'info') {
        // Show notification message
        this.log(message, type);
        
        // Also show as a temporary toast notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ffc107';
                notification.style.color = '#000';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            default:
                notification.style.backgroundColor = '#007bff';
        }
        
        document.body.appendChild(notification);
        
        // Fade in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);
        
        // Fade out and remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIManager;
}
