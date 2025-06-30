// Analysis Module
class AnalysisManager {
    constructor(game, heuristics, uiManager) {
        this.game = game;
        this.heuristics = heuristics;
        this.ui = uiManager;
        this.isRunning = false;
        this.currentAnalysis = null;
        this.defaultRuns = 20; // Default number of runs
    }

    async runAnalysis(heuristicType, twoPhase = false, runs = this.defaultRuns) {
        if (this.isRunning) {
            this.ui.showNotification('Analysis already running!', 'warning');
            return;
        }

        this.isRunning = true;
        this.ui.setControlsDisabled(true);

        const results = {
            heuristic: heuristicType,
            twoPhase: twoPhase,
            runs: runs,
            maxTiles: [],
            scores: [],
            movesCounts: [],
            durations: [],
            distribution: {},
            startTime: Date.now()
        };

        const paramSummary = this.createParameterSummary(heuristicType, twoPhase, runs);
        
        // Show initial status to user
        const initialDisplay = paramSummary + '<p><strong>Status:</strong> <i>Initializing...</i></p>';
        this.ui.showAnalysis(initialDisplay);
        
        // Small delay to ensure UI updates
        await this.sleep(50);
        
        for (let run = 0; run < runs; run++) {
            const runResult = await this.runSingleGame(heuristicType, twoPhase, run, runs, paramSummary);
            
            results.maxTiles.push(runResult.maxTile);
            results.scores.push(runResult.score);
            results.movesCounts.push(runResult.moves);
            results.durations.push(runResult.duration);
            
            // Update distribution
            const maxTile = runResult.maxTile;
            results.distribution[maxTile] = (results.distribution[maxTile] || 0) + 1;
        }

        results.totalTime = Date.now() - results.startTime;
        this.currentAnalysis = results;
        
        this.displayResults(results);
        this.ui.setControlsDisabled(false);
        this.isRunning = false;
        
        return results;
    }

    async runSingleGame(heuristicType, twoPhase, runIndex, totalRuns, paramSummary) {
        const startTime = Date.now();
        this.game.initBoard();
        this.ui.drawBoard(this.game);
        
        let moves = 0;
        const maxMoves = 1000;
        
        // Update progress
        this.updateProgressDisplay(runIndex, totalRuns, paramSummary);
        
        try {
            while (!this.game.gameOver && moves < maxMoves) {
                // Add timeout protection
                const moveStartTime = Date.now();
                const move = this.heuristics.pickMove(this.game, heuristicType, twoPhase);
                const moveTime = Date.now() - moveStartTime;
                
                // If move calculation took too long, skip this strategy
                if (moveTime > 5000) { // 5 second timeout
                    console.warn(`Move calculation took ${moveTime}ms for ${heuristicType}, skipping game`);
                    break;
                }
                
                if (move && this.game.move(move)) {
                    moves++;
                    
                    // Periodically update the board display
                    if (moves % 10 === 0) {
                        this.ui.drawBoard(this.game);
                        await this.sleep(1); // Small delay for UI responsiveness
                    }
                } else {
                    break; // No valid moves
                }
            }
        } catch (error) {
            console.error(`Error in game simulation for ${heuristicType}:`, error);
            // Return basic result even if there was an error
        }
        
        const duration = Date.now() - startTime;
        
        return {
            maxTile: this.game.getMaxTile(),
            score: this.game.score,
            moves: moves,
            duration: duration,
            gameOver: this.game.gameOver
        };
    }

    updateProgressDisplay(runIndex, totalRuns, paramSummary) {
        const percent = Math.floor(100 * runIndex / totalRuns);
        const progressBar = this.ui.createProgressBar(percent);
        
        const content = `
            ${paramSummary}
            ${progressBar}
            <i>Running analysis... (${runIndex}/${totalRuns})</i>
        `;
        
        this.ui.showAnalysis(content);
    }

    displayResults(results) {
        const stats = this.calculateStatistics(results);
        const paramSummary = this.createParameterSummary(
            results.heuristic, 
            results.twoPhase, 
            results.runs
        );
        
        const htmlContent = `
            ${paramSummary}
            <div class="mb-4">
                <b>Analysis for ${results.heuristic}${results.twoPhase ? ' (Two-Phase)' : ''}:</b><br>
                <strong>Runs:</strong> ${results.runs}<br>
                <strong>Average Max Tile:</strong> ${stats.avgMaxTile.toFixed(2)}<br>
                <strong>Average Score:</strong> ${stats.avgScore.toFixed(0)}<br>
                <strong>Average Moves:</strong> ${stats.avgMoves.toFixed(1)}<br>
                <strong>Win Rate (2048+):</strong> ${stats.winRate.toFixed(1)}%<br>
                <strong>Total Time:</strong> ${(results.totalTime / 1000).toFixed(1)}s
            </div>
            <div class="mb-2">
                <strong>Distribution:</strong><br>
                ${this.formatDistribution(results.distribution)}
            </div>
        `;
        
        this.ui.showAnalysis(htmlContent);
        this.ui.updateStats(htmlContent);
        
        // Store results globally for export
        window._lastResults = {
            ...results,
            stats: stats,
            timestamp: new Date().toISOString()
        };
    }

    calculateStatistics(results) {
        if (!results.maxTiles || results.maxTiles.length === 0) {
            return {
                avgMaxTile: 0,
                avgScore: 0,
                avgMoves: 0,
                avgDuration: 0,
                winRate: 0,
                winCount: 0,
                maxScore: 0,
                minScore: 0,
                maxTile: 0,
                scoreStdDev: 0
            };
        }
        
        const avgMaxTile = results.maxTiles.reduce((a, b) => a + b, 0) / results.maxTiles.length;
        const avgScore = results.scores.reduce((a, b) => a + b, 0) / results.scores.length;
        const avgMoves = results.movesCounts.reduce((a, b) => a + b, 0) / results.movesCounts.length;
        const avgDuration = results.durations.reduce((a, b) => a + b, 0) / results.durations.length;
        
        const winCount = results.maxTiles.filter(tile => tile >= 2048).length;
        const winRate = (winCount / results.runs) * 100;
        
        const maxScore = Math.max(...results.scores);
        const minScore = Math.min(...results.scores);
        const maxTile = Math.max(...results.maxTiles);
        
        // Calculate standard deviations
        const scoreVariance = results.scores.reduce((sum, score) => {
            return sum + Math.pow(score - avgScore, 2);
        }, 0) / results.scores.length;
        const scoreStdDev = Math.sqrt(scoreVariance);
        
        return {
            avgMaxTile,
            avgScore,
            avgMoves,
            avgDuration,
            winRate,
            winCount,
            maxScore,
            minScore,
            maxTile,
            scoreStdDev
        };
    }

    createParameterSummary(heuristic, twoPhase, runs) {
        return `
            <div class="mb-2" style="background: #f0f0f0; padding: 8px; border-radius: 4px;">
                <b>Parameters:</b> 
                Heuristic: <b>${heuristic}</b> | 
                Two-Phase: <b>${twoPhase ? 'On' : 'Off'}</b> | 
                Runs: <b>${runs}</b>
            </div>
        `;
    }

    formatDistribution(distribution) {
        const sorted = Object.keys(distribution)
            .map(Number)
            .sort((a, b) => a - b);
        
        return sorted
            .map(tile => `${tile}: ${distribution[tile]}`)
            .join('<br>');
    }

    exportResults(format) {
        if (!this.currentAnalysis && !window._lastResults) {
            this.ui.showNotification('No analysis results to export. Run an analysis first.', 'warning');
            return;
        }
        
        const results = window._lastResults || this.currentAnalysis;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        if (format === 'csv') {
            this.exportCSV(results, timestamp);
        } else if (format === 'html') {
            this.exportHTML(results, timestamp);
        }
    }

    exportCSV(results, timestamp) {
        let csv = 'Heuristic,TwoPhase,Run,MaxTile,Score,Moves,Duration\n';
        
        for (let i = 0; i < results.runs; i++) {
            csv += `${results.heuristic},${results.twoPhase},${i + 1},${results.maxTiles[i]},${results.scores[i]},${results.movesCounts[i]},${results.durations[i]}\n`;
        }
        
        const filename = `2048_analysis_${results.heuristic}_${results.twoPhase ? 'twophase_' : ''}${timestamp}.csv`;
        this.ui.triggerDownload(csv, filename, 'text/csv');
    }

    exportHTML(results, timestamp) {
        const stats = results.stats || this.calculateStatistics(results);
        
        const html = `
<!DOCTYPE html>
<html>
<head>
    <title>2048 Analysis Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #faf8ef; }
        .header { background: #bbada0; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .distribution { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>2048 Analysis Results</h1>
        <p>Generated on: ${new Date().toLocaleString()}</p>
    </div>
    
    <div class="stats">
        <h2>Configuration</h2>
        <p><strong>Heuristic:</strong> ${results.heuristic}</p>
        <p><strong>Two-Phase:</strong> ${results.twoPhase ? 'Enabled' : 'Disabled'}</p>
        <p><strong>Number of Runs:</strong> ${results.runs}</p>
        <p><strong>Total Analysis Time:</strong> ${(results.totalTime / 1000).toFixed(1)} seconds</p>
        
        <h2>Performance Statistics</h2>
        <p><strong>Average Max Tile:</strong> ${stats.avgMaxTile.toFixed(2)}</p>
        <p><strong>Average Score:</strong> ${stats.avgScore.toFixed(0)}</p>
        <p><strong>Average Moves:</strong> ${stats.avgMoves.toFixed(1)}</p>
        <p><strong>Win Rate (2048+):</strong> ${stats.winRate.toFixed(1)}% (${stats.winCount}/${results.runs} games)</p>
        <p><strong>Highest Score:</strong> ${stats.maxScore}</p>
        <p><strong>Highest Tile:</strong> ${stats.maxMaxTile}</p>
        <p><strong>Score Standard Deviation:</strong> ${stats.scoreStdDev.toFixed(0)}</p>
        
        <div class="distribution">
            <h2>Max Tile Distribution</h2>
            <table>
                <tr><th>Max Tile</th><th>Count</th><th>Percentage</th></tr>
                ${Object.keys(results.distribution)
                    .map(Number)
                    .sort((a, b) => a - b)
                    .map(tile => {
                        const count = results.distribution[tile];
                        const percentage = ((count / results.runs) * 100).toFixed(1);
                        return `<tr><td>${tile}</td><td>${count}</td><td>${percentage}%</td></tr>`;
                    })
                    .join('')}
            </table>
        </div>
    </div>
</body>
</html>`;
        
        const filename = `2048_analysis_${results.heuristic}_${results.twoPhase ? 'twophase_' : ''}${timestamp}.html`;
        this.ui.triggerDownload(html, filename, 'text/html');
    }

    async runComparisonAnalysis(strategies, twoPhase = false, runs = this.defaultRuns) {
        if (this.isRunning) {
            this.ui.showNotification('Analysis already running!', 'warning');
            return;
        }

        this.isRunning = true;
        this.ui.setControlsDisabled(true);

        const comparisonResults = {
            strategies: strategies,
            twoPhase: twoPhase,
            runs: runs,
            results: {},
            startTime: Date.now()
        };

        // Show initial status to user
        const initialSummary = `<h4>Strategy Comparison Analysis</h4>
            <p><strong>Strategies to test:</strong> ${strategies.join(', ')}</p>
            <p><strong>Games per strategy:</strong> ${runs}${twoPhase ? ' | <strong>Two-Phase Mode</strong>' : ''}</p>
            <p><strong>Status:</strong> <i>Initializing...</i></p>`;
        this.ui.showAnalysis(initialSummary);
        
        // Small delay to ensure UI updates
        await this.sleep(50);

        for (let strategyIndex = 0; strategyIndex < strategies.length; strategyIndex++) {
            const strategy = strategies[strategyIndex];
            
            if (!this.isRunning) break; // Check if stopped
            
            const results = {
                heuristic: strategy,
                twoPhase: twoPhase,
                runs: runs,
                maxTiles: [],
                scores: [],
                movesCounts: [],
                durations: [],
                distribution: {}
            };

            for (let run = 0; run < runs; run++) {
                if (!this.isRunning) break; // Check if stopped
                
                try {
                    const paramSummary = `<h4>Strategy Comparison Analysis</h4>
                        <p><strong>Current:</strong> ${strategy} (${strategyIndex + 1}/${strategies.length})</p>
                        <p><strong>All Strategies:</strong> ${strategies.join(', ')}</p>
                        <p><strong>Games per strategy:</strong> ${runs}${twoPhase ? ' | <strong>Two-Phase Mode</strong>' : ''}</p>`;
                    
                    const runResult = await this.runSingleGame(strategy, twoPhase, run, runs, paramSummary);
                    
                    results.maxTiles.push(runResult.maxTile);
                    results.scores.push(runResult.score);
                    results.movesCounts.push(runResult.moves);
                    results.durations.push(runResult.duration);
                    
                    // Update distribution
                    const maxTile = runResult.maxTile;
                    results.distribution[maxTile] = (results.distribution[maxTile] || 0) + 1;
                } catch (error) {
                    console.error(`Error in comparison analysis run ${run} for strategy ${strategy}:`, error);
                    // Skip this run and continue
                    continue;
                }
            }

            comparisonResults.results[strategy] = results;
        }

        comparisonResults.totalTime = Date.now() - comparisonResults.startTime;
        this.currentAnalysis = comparisonResults;
        
        this.isRunning = false;
        this.ui.setControlsDisabled(false);
        
        this.displayComparisonResults(comparisonResults);
        return comparisonResults;
    }

    displayComparisonResults(results) {
        let output = '<div class="comparison-results">';
        output += `<h3>Strategy Comparison Results</h3>`;
        output += `<p><strong>Games per strategy:</strong> ${results.runs} | <strong>Total time:</strong> ${(results.totalTime / 1000).toFixed(1)}s</p>`;
        
        // Create summary table
        output += '<table class="comparison-table">';
        output += '<tr><th>Strategy</th><th>2048+ Rate</th><th>Avg Score</th><th>Avg Moves</th><th>Max Tile</th></tr>';
        
        const summaries = [];
        
        Object.entries(results.results).forEach(([strategy, data]) => {
            const summary = this.calculateStatistics(data);
            summaries.push({ strategy, ...summary });
            
            const winRate = ((data.maxTiles.filter(tile => tile >= 2048).length / data.maxTiles.length) * 100).toFixed(1);
            const maxTileAchieved = Math.max(...data.maxTiles);
            
            output += `<tr>
                <td><strong>${strategy}</strong></td>
                <td>${winRate}%</td>
                <td>${summary.avgScore.toFixed(0)}</td>
                <td>${summary.avgMoves.toFixed(0)}</td>
                <td>${maxTileAchieved}</td>
            </tr>`;
        });
        
        output += '</table>';
        
        // Find best performing strategy
        const bestStrategy = summaries.reduce((best, current) => {
            const currentWinRate = (results.results[current.strategy].maxTiles.filter(tile => tile >= 2048).length / results.results[current.strategy].maxTiles.length);
            const bestWinRate = (results.results[best.strategy].maxTiles.filter(tile => tile >= 2048).length / results.results[best.strategy].maxTiles.length);
            return currentWinRate > bestWinRate ? current : best;
        });
        
        output += `<div class="best-strategy">
            <h4>🏆 Best Performing Strategy: ${bestStrategy.strategy}</h4>
            <p>Recommended for reaching 2048 consistently.</p>
        </div>`;
        
        output += '</div>';
        
        this.ui.updateStats(output);
        this.ui.showNotification(`Comparison complete! Best strategy: ${bestStrategy.strategy}`, 'success');
    }

    async runTwoPhaseAnalysis(earlyStrategy, lateStrategy, threshold, runs = this.defaultRuns) {
        if (this.isRunning) {
            this.ui.showNotification('Analysis already running!', 'warning');
            return;
        }

        this.isRunning = true;
        this.ui.setControlsDisabled(true);

        const results = {
            type: 'twophase',
            earlyStrategy: earlyStrategy,
            lateStrategy: lateStrategy,
            threshold: threshold,
            runs: runs,
            maxTiles: [],
            scores: [],
            movesCounts: [],
            durations: [],
            switchPoints: [], // Track when strategy switched
            distribution: {},
            startTime: Date.now()
        };

        const paramSummary = this.createTwoPhaseParameterSummary(earlyStrategy, lateStrategy, threshold, runs);
        
        // Show initial status to user
        const initialDisplay = paramSummary + '<p><strong>Status:</strong> <i>Initializing...</i></p>';
        this.ui.showAnalysis(initialDisplay);
        
        // Small delay to ensure UI updates
        await this.sleep(50);
        
        for (let run = 0; run < runs; run++) {
            const runResult = await this.runTwoPhaseSingleGame(earlyStrategy, lateStrategy, threshold, run, runs, paramSummary);
            
            results.maxTiles.push(runResult.maxTile);
            results.scores.push(runResult.score);
            results.movesCounts.push(runResult.moves);
            results.durations.push(runResult.duration);
            results.switchPoints.push(runResult.switchPoint);
            
            // Update distribution
            const maxTile = runResult.maxTile;
            results.distribution[maxTile] = (results.distribution[maxTile] || 0) + 1;
        }

        results.totalTime = Date.now() - results.startTime;
        this.currentAnalysis = results;
        
        this.displayTwoPhaseResults(results);
        
        this.isRunning = false;
        this.ui.setControlsDisabled(false);
        
        return results;
    }

    async runTwoPhaseSingleGame(earlyStrategy, lateStrategy, threshold, runIndex, totalRuns, paramSummary) {
        const startTime = Date.now();
        this.game.initBoard();
        this.ui.drawBoard(this.game);
        
        let moves = 0;
        let switchPoint = -1;
        let currentStrategy = earlyStrategy;
        const maxMoves = 1000;
        
        // Update progress
        this.updateProgressDisplay(runIndex, totalRuns, paramSummary);
        
        while (!this.game.gameOver && moves < maxMoves) {
            // Check if we should switch strategies
            const maxTile = this.game.getMaxTile();
            if (switchPoint === -1 && maxTile >= threshold) {
                currentStrategy = lateStrategy;
                switchPoint = moves;
            }
            
            const move = this.heuristics.pickMove(this.game, currentStrategy, false);
            
            if (move && this.game.move(move)) {
                moves++;
                
                // Periodically update the board display
                if (moves % 10 === 0) {
                    this.ui.drawBoard(this.game);
                    await this.sleep(1); // Small delay for UI responsiveness
                }
            } else {
                break; // No valid moves
            }
        }
        
        const duration = Date.now() - startTime;
        
        return {
            maxTile: this.game.getMaxTile(),
            score: this.game.score,
            moves: moves,
            duration: duration,
            switchPoint: switchPoint,
            gameOver: this.game.gameOver
        };
    }

    createTwoPhaseParameterSummary(earlyStrategy, lateStrategy, threshold, runs) {
        return `<h4>Two-Phase Analysis</h4>
            <p><strong>Early Strategy:</strong> ${earlyStrategy}</p>
            <p><strong>Late Strategy:</strong> ${lateStrategy}</p>
            <p><strong>Switch Threshold:</strong> ${threshold}</p>
            <p><strong>Number of runs:</strong> ${runs}</p>`;
    }

    displayTwoPhaseResults(results) {
        const stats = this.calculateStatistics(results);
        const switchStats = this.calculateSwitchStatistics(results);
        const paramSummary = this.createTwoPhaseParameterSummary(
            results.earlyStrategy, 
            results.lateStrategy, 
            results.threshold,
            results.runs
        );
        
        const htmlContent = `
            ${paramSummary}
            <div class="mb-4">
                <b>Two-Phase Analysis Results:</b><br>
                ${results.earlyStrategy} → ${results.lateStrategy} (switch at ${results.threshold})<br><br>
                
                <b>Performance Statistics:</b><br>
                Max tile achieved: <b>${stats.maxTile}</b><br>
                Average max tile: <b>${stats.avgMaxTile.toFixed(1)}</b><br>
                Average score: <b>${stats.avgScore.toFixed(0)}</b><br>
                Average moves: <b>${stats.avgMoves.toFixed(1)}</b><br>
                Average duration: <b>${stats.avgDuration.toFixed(0)}ms</b><br><br>
                
                <b>Strategy Switch Statistics:</b><br>
                Games that switched: <b>${switchStats.switchedGames}/${results.runs} (${switchStats.switchPercentage.toFixed(1)}%)</b><br>
                Average switch point: <b>${switchStats.avgSwitchPoint.toFixed(1)} moves</b><br><br>
                
                ${this.createDistributionTable(results.distribution)}
            </div>
        `;
        
        this.ui.showAnalysis(htmlContent);
    }

    calculateSwitchStatistics(results) {
        if (!results.switchPoints || results.switchPoints.length === 0) {
            return {
                switchedGames: 0,
                switchPercentage: 0,
                avgSwitchPoint: 0
            };
        }
        
        const validSwitches = results.switchPoints.filter(sp => sp !== -1);
        return {
            switchedGames: validSwitches.length,
            switchPercentage: (validSwitches.length / results.runs) * 100,
            avgSwitchPoint: validSwitches.length > 0 ? validSwitches.reduce((a, b) => a + b, 0) / validSwitches.length : 0
        };
    }

    createDistributionTable(distribution) {
        if (!distribution || Object.keys(distribution).length === 0) {
            return '<p><i>No distribution data available</i></p>';
        }
        
        const total = Object.values(distribution).reduce((a, b) => a + b, 0);
        
        let html = '<div><strong>Max Tile Distribution:</strong><br>';
        html += '<table style="border-collapse: collapse; margin-top: 8px;">';
        html += '<tr><th style="border: 1px solid #ddd; padding: 4px 8px;">Tile</th><th style="border: 1px solid #ddd; padding: 4px 8px;">Count</th><th style="border: 1px solid #ddd; padding: 4px 8px;">%</th></tr>';
        
        Object.keys(distribution)
            .map(Number)
            .sort((a, b) => a - b)
            .forEach(tile => {
                const count = distribution[tile];
                const percentage = ((count / total) * 100).toFixed(1);
                html += `<tr><td style="border: 1px solid #ddd; padding: 4px 8px;">${tile}</td><td style="border: 1px solid #ddd; padding: 4px 8px;">${count}</td><td style="border: 1px solid #ddd; padding: 4px 8px;">${percentage}%</td></tr>`;
            });
        
        html += '</table></div>';
        return html;
    }

    // Utility function for async delays
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Stop current analysis
    stopAnalysis() {
        this.isRunning = false;
        this.ui.setControlsDisabled(false);
        this.ui.showNotification('Analysis stopped', 'info');
    }

    // Get current analysis status
    getStatus() {
        return {
            isRunning: this.isRunning,
            hasResults: !!this.currentAnalysis
        };
    }

    // Set default number of runs for analysis
    setDefaultRuns(runs) {
        this.defaultRuns = runs;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnalysisManager;
}
