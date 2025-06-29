// UI Manager Module
class UIManager {
    constructor() {
        this.currentTab = 'desc';
        this.elements = this.initializeElements();
        this.setupEventListeners();
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
    }

    // Board rendering
    drawBoard(game) {
        if (!this.elements.board) return;
        
        let html = '';
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const value = game.board[i][j];
                const displayValue = value ? value : '';
                html += `<div class="tile tile-${value}">${displayValue}</div>`;
            }
        }
        
        this.elements.board.innerHTML = html;
        this.updateGameInfo(game);
    }

    updateGameInfo(game) {
        if (!this.elements.log) return;
        
        let info = `Score: ${game.score}`;
        if (game.gameOver) {
            info += ' | Game Over!';
        }
        
        this.elements.log.textContent = info;
    }

    // Tab management
    showTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab content visibility
        if (this.elements.tabContentDesc) {
            if (tabName === 'desc') {
                this.elements.tabContentDesc.classList.remove('hidden');
            } else {
                this.elements.tabContentDesc.classList.add('hidden');
            }
        }
        if (this.elements.tabContentStats) {
            if (tabName === 'stats') {
                this.elements.tabContentStats.classList.remove('hidden');
            } else {
                this.elements.tabContentStats.classList.add('hidden');
            }
        }
        if (this.elements.tabContentSettings) {
            if (tabName === 'settings') {
                this.elements.tabContentSettings.classList.remove('hidden');
            } else {
                this.elements.tabContentSettings.classList.add('hidden');
            }
        }
        
        // Update tab button styles
        if (this.elements.tabDesc) {
            this.elements.tabDesc.className = `tab-button ${tabName === 'desc' ? 'active' : ''}`;
        }
        if (this.elements.tabStats) {
            this.elements.tabStats.className = `tab-button ${tabName === 'stats' ? 'active' : ''}`;
        }
        if (this.elements.tabSettings) {
            this.elements.tabSettings.className = `tab-button ${tabName === 'settings' ? 'active' : ''}`;
        }
    }

    // Description panel updates
    updateDescription(mode = 'play') {
        const modeMap = {
            play: 'Manual Play',
            heuristic: 'Heuristic Emulation',
            analysis: 'Analysis'
        };

        const heuristicType = this.elements.heuristicSelect?.value || 'monotonicity';
        const twoPhase = this.elements.twophase?.checked || false;
        
        // Update mode
        if (this.elements.descMode) {
            this.elements.descMode.textContent = modeMap[mode] || mode;
        }
        
        // Update heuristic
        if (this.elements.descHeuristic) {
            if (mode === 'heuristic' || mode === 'analysis') {
                const heurDesc = twoPhase ? `Two-Phase ${heuristicType}` : heuristicType;
                this.elements.descHeuristic.textContent = heurDesc;
            } else {
                this.elements.descHeuristic.textContent = 'N/A';
            }
        }
        
        // Update details
        if (this.elements.descDetails) {
            if (mode === 'play') {
                this.elements.descDetails.textContent = 'Use arrow keys or WASD to play manually.';
            } else if (twoPhase) {
                this.elements.descDetails.textContent = 'Two-phase: monotonicity, then selected heuristic.';
            } else {
                const description = Heuristics.getHeuristicDescription(heuristicType);
                this.elements.descDetails.textContent = description;
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
    setControlsDisabled(disabled) {
        Object.values(this.elements.controls).forEach(button => {
            if (button) button.disabled = disabled;
        });
        
        if (this.elements.heuristicSelect) this.elements.heuristicSelect.disabled = disabled;
        if (this.elements.twophase) this.elements.twophase.disabled = disabled;
    }

    // Chart rendering
    drawDistributionChart(distribution, canvasId = 'distChart') {
        setTimeout(() => {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const values = Object.keys(distribution).map(Number).sort((a, b) => a - b);
            const maxCount = Math.max(...Object.values(distribution));
            const barWidth = (canvas.width - 20) / values.length;
            
            values.forEach((value, index) => {
                const count = distribution[value];
                const height = (count / maxCount) * (canvas.height - 40);
                const x = 10 + index * barWidth;
                const y = canvas.height - height - 20;
                
                // Draw bar
                ctx.fillStyle = '#f2b179';
                ctx.fillRect(x, y, barWidth - 2, height);
                
                // Draw label
                ctx.fillStyle = '#776e65';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(value.toString(), x + barWidth / 2, canvas.height - 5);
                
                // Draw count on top of bar
                ctx.fillText(count.toString(), x + barWidth / 2, y - 5);
            });
        }, 100);
    }

    // Notification system
    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                transition: opacity 0.3s;
            `;
            document.body.appendChild(notification);
        }
        
        // Set message and style based on type
        notification.textContent = message;
        notification.className = type;
        
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#4CAF50';
                break;
            case 'error':
                notification.style.backgroundColor = '#f44336';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ff9800';
                break;
            default:
                notification.style.backgroundColor = '#2196F3';
        }
        
        notification.style.opacity = '1';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Export functionality helpers
    triggerDownload(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showNotification(`Downloaded ${filename}`, 'success');
    }

    // Responsive design helpers
    isMobile() {
        return window.innerWidth <= 768;
    }

    updateLayoutForDevice() {
        if (this.isMobile()) {
            // Mobile-specific adjustments
            document.body.classList.add('mobile');
        } else {
            document.body.classList.remove('mobile');
        }
    }

    // Settings management
    getSettings() {
        return {
            runs: parseInt(document.getElementById('runCount')?.value) || 20,
            pauseDuration: parseFloat(document.getElementById('pauseDuration')?.value) || 0.3,
            weights: {
                monotonicity: parseFloat(document.getElementById('weightMonotonicity')?.value) || 1.0,
                corner: parseFloat(document.getElementById('weightCorner')?.value) || 1.5,
                center: parseFloat(document.getElementById('weightCenter')?.value) || 0.0,
                expectimax: parseFloat(document.getElementById('weightExpectimax')?.value) || 0.5,
                opportunistic: parseFloat(document.getElementById('weightOpportunistic')?.value) || 1.0,
                smoothness: parseFloat(document.getElementById('weightSmoothness')?.value) || 0.1,
                empty: parseFloat(document.getElementById('weightEmpty')?.value) || 2.7,
                merge: parseFloat(document.getElementById('weightMerge')?.value) || 1.0
            }
        };
    }

    setSettings(settings) {
        if (settings.runs !== undefined) {
            const runCountEl = document.getElementById('runCount');
            if (runCountEl) runCountEl.value = settings.runs;
        }
        
        if (settings.pauseDuration !== undefined) {
            const pauseDurationEl = document.getElementById('pauseDuration');
            if (pauseDurationEl) pauseDurationEl.value = settings.pauseDuration;
        }
        
        if (settings.weights) {
            Object.keys(settings.weights).forEach(key => {
                const element = document.getElementById(`weight${key.charAt(0).toUpperCase() + key.slice(1)}`);
                if (element) element.value = settings.weights[key];
            });
        }
    }

    // ML Optimization UI
    showOptimizationProgress(show = true) {
        const progressEl = document.getElementById('optimizationProgress');
        if (progressEl) {
            progressEl.style.display = show ? 'block' : 'none';
        }
    }

    updateOptimizationProgress(percent, status) {
        const progressBar = document.getElementById('optimizationProgressBar');
        const statusEl = document.getElementById('optimizationStatus');
        
        if (progressBar) progressBar.style.width = `${percent}%`;
        if (statusEl) statusEl.textContent = status;
    }

    showOptimizationResults(results) {
        const resultsEl = document.getElementById('optimizationResults');
        const weightsEl = document.getElementById('bestWeights');
        const performanceEl = document.getElementById('bestPerformance');
        
        if (resultsEl) resultsEl.style.display = 'block';
        
        if (weightsEl && results.weights) {
            weightsEl.innerHTML = Object.entries(results.weights)
                .map(([key, value]) => `${key}: ${value.toFixed(3)}`)
                .join('<br>');
        }
        
        if (performanceEl && results.performance) {
            performanceEl.textContent = `Win Rate: ${results.performance.winRate}% | Avg Score: ${results.performance.avgScore}`;
        }
    }

    hideOptimizationResults() {
        const resultsEl = document.getElementById('optimizationResults');
        if (resultsEl) resultsEl.style.display = 'none';
    }

    setOptimizationButtonsState(isRunning) {
        const startBtn = document.getElementById('btn-start-optimization');
        const stopBtn = document.getElementById('btn-stop-optimization');
        
        if (startBtn) startBtn.disabled = isRunning;
        if (stopBtn) stopBtn.disabled = !isRunning;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIManager;
}
