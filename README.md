# 2048 Web Game

A comprehensive 2048 web-based game with advanced AI strategies and analytics.

## Features
- **Interactive Web Interface**: Complete web-based 2048 game with multiple play modes
- **Advanced AI Strategies**: Multiple heuristics including Expectimax Corner, Gradient Descent, ML Sim, and more
- **Real-time Analysis**: Statistical analysis with exportable results (CSV/HTML)
- **ML Weight Optimization**: Advanced machine learning algorithms to find optimal strategy weights
- **Customizable Settings**: Adjustable parameters for all strategies and optimization methods
- **Modern UI**: Clean, responsive design with tabbed interface

## Quick Start

Simply open `web_2048.html` in your web browser for the complete interactive experience!

## How to Use

### Game Modes

1. **Manual Play**: Use arrow keys or WASD to play manually
2. **Heuristic Emulation**: Watch AI strategies play automatically
3. **Batch Analysis**: Run multiple games to test strategy performance

### AI Strategies (Recommended for reaching 2048)

- **⭐ Expectimax Corner**: Advanced expectimax with corner bias (best for 2048+)
- **⭐ ML Sim**: Machine learning optimized feature combination
- **⭐ Gradient Descent**: Position-weighted scoring strategy
- **Ultra-Adaptive**: Adapts strategy based on game phase
- **Advanced Minimax**: Deep lookahead with alpha-beta pruning

### Settings & Optimization

1. Click the **Settings** tab in the side panel
2. Adjust strategy weights and run parameters
3. Use **ML Weight Optimization** to automatically find best weights:
   - Choose optimization method (Random, Genetic, Grid, Bayesian)
   - Set iterations and games per evaluation
   - Click "Start Optimization" and wait for results

### Analysis & Export

- **Statistics Tab**: View detailed performance metrics
- **Export Options**: Save results as CSV or HTML reports
- **Real-time Progress**: Track optimization and analysis progress

## Strategy Performance

Expected success rates for reaching 2048:
- **Expectimax Corner**: 70-90% success rate
- **ML Sim**: 60-80% success rate  
- **Gradient Descent**: 50-70% success rate
- **Ultra-Adaptive**: 40-60% success rate

## Tips for Success

1. **Try Expectimax Corner first** - it's the most sophisticated strategy
2. **Use ML Optimization** to find custom weights for your preferences
3. **Run Batch Analysis** to compare different strategies statistically
4. **Keep the largest tile in a corner** (most strategies work this way)
5. **Monitor empty cell count** - more empty cells = more options

## File Structure

- `web_2048.html` — Main game interface
- `styles.css` — Game styling and UI
- `game-logic.js` — Core 2048 game mechanics
- `heuristics.js` — AI strategy implementations
- `ui-manager.js` — User interface management
- `analysis-manager.js` — Statistics and batch analysis
- `app.js` — Main application controller

## Browser Compatibility

Works in all modern web browsers. No installation required!
- Results and histograms for both phases will be shown.

### Heuristic Mode Example

In heuristic mode (`[h]`):
- Choose a heuristic (`corner`, `center`, or `expectimax`).
- Set the number of runs.
- See statistics and a histogram of results.

### Emulation Mode Example

In emulation mode (`[e]`):
- Enter a move sequence (WASD) to play automatically, or press Enter for turn-by-turn manual play.

## New Features (2025)

### Opportunistic Heuristic
- Added a new heuristic: `opportunistic`. This strategy will always make a move that combines two tiles if possible; otherwise, it falls back to the `corner` strategy. Selectable in all heuristic-based simulation modes.

### Results CSV Logging
- Every simulation run now appends a row to `results.csv` with:
  - Timestamp
  - Unique run ID
  - Simulation type
  - Parameters
  - Highest tile achieved
  - Percent of runs achieving highest tile
  - Standard deviation
  - Simulation duration (seconds)
- This allows for easy analysis and benchmarking of all runs. You can open or import `results.csv` in any data analysis tool (Excel, pandas, etc).

### 2-Phase Heuristic Simulation
- In simulation mode, you can now select a 2-phase heuristic: choose two heuristics and a switch tile (e.g., 512). The simulation will use the first heuristic until the switch tile is reached, then switch to the second.
- Results are reported in both the HTML and CSV outputs, including the heuristic pair and all relevant statistics.

## ML Weight Optimization

This project now includes advanced machine learning algorithms to automatically find optimal weight combinations for the heuristic strategies:

### Available Optimization Methods

1. **Random Search**: Explores the weight space randomly to find good configurations
2. **Genetic Algorithm**: Evolves populations of weight configurations over generations
3. **Grid Search**: Systematically tests predefined weight combinations
4. **Bayesian Optimization**: Uses Gaussian processes for intelligent exploration-exploitation

### Using ML Optimization

#### Web Interface (Easiest)
1. Open `web_2048.html` in your browser
2. Go to Settings tab
3. Scroll to "ML Weight Optimization" section
4. Choose optimization method and parameters
5. Click "Start Optimization"
6. Apply the best weights found automatically

#### Command Line
```bash
# Run the ML optimization tool
python ml_runner.py

# Or use the advanced optimizer directly
python ml_optimizer.py

# Analyze previous optimization results
python optimization_analyzer.py results.json --all
```

### Weight Optimization Results

The system optimizes 8 different heuristic weights:
- **Monotonicity**: Rewards monotonic rows/columns
- **Corner**: Keeps largest tiles in corners  
- **Center**: Favors center positioning
- **Expectimax**: Looks ahead with expected values
- **Opportunistic**: Prioritizes immediate merges
- **Smoothness**: Prefers similar adjacent tiles
- **Empty**: Values empty tile count
- **Merge**: Rewards merge opportunities

### Performance Metrics

The optimizer tracks multiple performance indicators:
- **Win Rate**: Percentage of games reaching 2048
- **Average Score**: Mean final score across games
- **Average Max Tile**: Mean highest tile achieved
- **Average Moves**: Mean number of moves per game

### Example Optimization Session

```bash
$ python ml_runner.py
=== 2048 Weight Optimization Tool ===
Choose optimization method (random/genetic/grid): genetic
Number of generations (default 15): 20
Games per evaluation (default 10): 15

Starting genetic optimization...
Generation 1/20: Best: 23.3% win rate
Generation 5/20: Best: 41.2% win rate  
Generation 10/20: Best: 58.7% win rate
Generation 20/20: Best: 67.3% win rate

=== Optimization Complete! ===
Best configuration found:
Win Rate: 67.3%
Optimal weights:
  monotonicity: 1.85
  smoothness: 0.23
  empty: 3.42
  merge: 1.15
```

### Integration with Existing Code

The ML optimizer seamlessly integrates with the existing heuristic system:

```python
from heuristics import HeuristicEvaluator
from ml_optimizer import WeightOptimizer

# Use optimized weights
evaluator = HeuristicEvaluator()
optimized_weights = {'monotonicity': 1.85, 'smoothness': 0.23, ...}
best_move = evaluator.pick_weighted_move(board, optimized_weights)
```

## File Structure

- `main.py` — CLI entry point, mode selection, and user interaction
- `game_2048.py` — Core 2048 game logic
- `heuristics.py` — Heuristic move logic and simulation
- `ml_sim.py` — ML simulation and two-phase best logic
- `visualization.py` — Plotting and visualization utilities
- `results.html` — Output HTML with embedded plots (if generated)
- `results.csv` — Output CSV file with simulation run data
- `ml_optimizer.py` — Core ML optimization algorithms  
- `ml_runner.py` — User-friendly optimization tool
- `optimization_analyzer.py` — Advanced results analysis

## Requirements

- Python 3.7+
- numpy
- matplotlib
- tqdm

Install requirements with:

```
pip install numpy matplotlib tqdm
```

## Automated Testing

This project includes a test suite for the simulation logic in `ml_sim.py` using `pytest`.

To run the tests:

```
pip install pytest
pytest tests/test_ml_sim.py
```

See `TESTING.md` for a full list of test cases and their descriptions.

## Output and Results

- All simulation and heuristic results (histograms, heatmaps) are saved to `results.html`.
- Each run is appended as a new section with a timestamp and run title.
- You can open `results.html` in your browser to review all results and graphs from all runs.
- Additionally, all runs are logged in `results.csv` for analysis.

## License
Apache License 2.0
