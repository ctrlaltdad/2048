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

## File Structure

- `main.py` — CLI entry point, mode selection, and user interaction
- `game_2048.py` — Core 2048 game logic
- `heuristics.py` — Heuristic move logic and simulation
- `ml_sim.py` — ML simulation and two-phase best logic
- `visualization.py` — Plotting and visualization utilities
- `results.html` — Output HTML with embedded plots (if generated)

## Requirements

- Python 3.7+
- numpy
- matplotlib
- tqdm

Install requirements with:

```
pip install numpy matplotlib tqdm
```

## License
Apache License 2.0
