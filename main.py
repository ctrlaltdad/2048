import sys
from heuristics import simulate_heuristic
from ml_sim import run_parallel_simulations, run_parallel_two_phase
from game_2048 import Game2048, MOVES, MOVE_LABELS
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from visualization import plot_histogram

def interactive_play():
    print("\n=== 2048 Interactive Mode ===")
    print("Enter a sequence of moves (e.g., wasddsw) or leave blank to play manually.")
    seq_input = input("Move sequence (WASD, blank for manual): ").strip().lower()
    valid_keys = {'w', 'a', 's', 'd'}
    game = Game2048()
    game.print_board()
    if seq_input:
        seq = [m for m in seq_input if m in valid_keys]
        idx = 0
        no_move_counter = 0
        while not game.is_game_over() and not game.has_won():
            move = seq[idx % len(seq)]
            moved = game.move_tiles({'w':'up','a':'left','s':'down','d':'right'}[move])
            game.print_board()
            if moved:
                no_move_counter = 0
            else:
                no_move_counter += 1
            if game.has_won():
                print("Congratulations! You've reached 2048!")
                break
            if game.is_game_over():
                print("Game Over!")
                break
            if no_move_counter >= 2 * len(seq):
                print(f"No valid moves for {2} full cycles of the sequence. Ending game as it would never end.")
                break
            idx += 1
    else:
        while True:
            move = input("Enter move (WASD, q to quit): ").strip().lower()
            if move == 'q':
                print("Quitting manual play.")
                break
            if move not in valid_keys:
                print("Invalid move. Use W, A, S, D.")
                continue
            moved = game.move_tiles({'w':'up','a':'left','s':'down','d':'right'}[move])
            game.print_board()
            if game.has_won():
                print("Congratulations! You've reached 2048!")
                break
            if game.is_game_over():
                print("Game Over!")
                break

def main():
    mode = input("Type 'ml' for ML simulation, 'play' for interactive mode, 'ml2' for two-phase ML mode, or 'heuristic' for heuristic mode: ").strip().lower()
    if mode == 'play':
        interactive_play()
        return
    if mode == 'heuristic':
        print("Heuristic mode: choose from 'corner', 'center', or 'expectimax'.")
        heuristic = input("Heuristic (corner/center/expectimax): ").strip().lower()
        runs = input("Number of runs (default 50): ").strip()
        runs = int(runs) if runs.isdigit() else 50
        tiles, scores = simulate_heuristic(heuristic, runs)
        print(f"Heuristic: {heuristic}")
        print(f"Average top tile: {np.mean(tiles):.2f}")
        print(f"Max tile: {np.max(tiles)}")
        print(f"Percent reaching max tile: {100.0 * sum(1 for t in tiles if t == np.max(tiles)) / len(tiles):.1f}%")
        plot_histogram(tiles, f'Tile Distribution: Heuristic {heuristic}')
        return
    # ...existing code for ML and ML2 modes can be refactored in here...

if __name__ == "__main__":
    main()
