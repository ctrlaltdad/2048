# 2048

A 2048 game emulator and solution optimizer.

## Features
- Command-line playable 2048 game (manual or by move sequence)
- ML simulation to find the best fixed move sequences for high tile/score
- Parallelized simulation for speed
- Progress bars and statistical output
- Graphs of best results by sequence length

## Requirements
- Python 3.7+
- numpy, matplotlib, tqdm

## Usage

Run the main CLI:

```
python main.py
```

You will be prompted to choose a mode:

- `[h]` Heuristic simulation: Run games using a heuristic (corner, center, expectimax).
- `[s]` ML sequence simulation: Enter two move sequences and only the top X% of games from the first sequence will continue with the second sequence, to try to improve the result. You can set the switch tile, number of runs, and top percent.
- `[e]` Emulate/play: Play the game interactively or by entering a move sequence (WASD).

### Two-Phase Best Simulation Example

In simulation mode (`[s]`):
- Enter the first and second move sequences (e.g., `wasd` and `dsaw`).
- Set the switch tile (default 512), number of runs (default 50), and top percent (default 0.2 = 20%).
- The second sequence will only run for the top X% of games from the first phase.
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

## Usage Notes
- To use the new opportunistic heuristic, select `opportunistic` when prompted for a heuristic in the CLI.
- To analyze results, open `results.csv` in your preferred tool.

## File Structure

- `main.py` — CLI entry point, mode selection, and user interaction
- `game_2048.py` — Core 2048 game logic
- `heuristics.py` — Heuristic move logic and simulation
- `ml_sim.py` — ML simulation and two-phase best logic
- `visualization.py` — Plotting and visualization utilities
- `results.html` — Output HTML with embedded plots (if generated)
- `results.csv` — Output CSV file with simulation run data

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
