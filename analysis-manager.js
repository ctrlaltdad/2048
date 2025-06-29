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
        
        while (!this.game.gameOver && moves < maxMoves) {
            const move = this.heuristics.pickMove(this.game, heuristicType, twoPhase);
            
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
            <canvas id="distChart" width="300" height="120"></canvas>
        `;
        
        this.ui.showAnalysis(htmlContent);
        this.ui.drawDistributionChart(results.distribution);
        this.ui.updateStats(htmlContent);
        
        // Store results globally for export
        window._lastResults = {
            ...results,
            stats: stats,
            timestamp: new Date().toISOString()
        };
    }

    calculateStatistics(results) {
        const avgMaxTile = results.maxTiles.reduce((a, b) => a + b, 0) / results.maxTiles.length;
        const avgScore = results.scores.reduce((a, b) => a + b, 0) / results.scores.length;
        const avgMoves = results.movesCounts.reduce((a, b) => a + b, 0) / results.movesCounts.length;
        
        const winCount = results.maxTiles.filter(tile => tile >= 2048).length;
        const winRate = (winCount / results.runs) * 100;
        
        const maxScore = Math.max(...results.scores);
        const minScore = Math.min(...results.scores);
        const maxMaxTile = Math.max(...results.maxTiles);
        
        // Calculate standard deviations
        const scoreVariance = results.scores.reduce((sum, score) => {
            return sum + Math.pow(score - avgScore, 2);
        }, 0) / results.scores.length;
        const scoreStdDev = Math.sqrt(scoreVariance);
        
        return {
            avgMaxTile,
            avgScore,
            avgMoves,
            winRate,
            winCount,
            maxScore,
            minScore,
            maxMaxTile,
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
