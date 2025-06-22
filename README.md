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

### Interactive Play
Run:
```
python ml_2048.py
```
Choose `play` mode. You can:
- Enter a sequence of moves (e.g., `wasddsw`) to see it repeated until the game ends
- Or leave blank to play move-by-move (WASD keys)

### ML Simulation
Run:
```
python ml_2048.py
```
Choose `ml` mode. The script will:
- Test all possible move sequences of length 5, 6, 7, and 8
- Run each sequence 50 times in parallel
- Report the best average and top tile for each length, with the sequence and % of runs that achieved the top tile
- Show a graph of results

## Files
- `game_2048.py`: Core 2048 game logic
- `ml_2048.py`: ML simulation and interactive CLI

## Customization
- You can change the number of runs per sequence in `ml_2048.py` (`runs_per_seq`)
- You can adjust the tested sequence lengths in the `lengths` list

## License
Apache License 2.0
