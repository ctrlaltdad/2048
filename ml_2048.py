import itertools
from game_2048 import Game2048
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

MOVES = ['up', 'down', 'left', 'right']
MOVE_LABELS = {'up': 'w', 'down': 's', 'left': 'a', 'right': 'd'}

def simulate_sequence(seq):
    """
    Simulate a single game of 2048 using a repeating move sequence until the game ends.
    Returns the highest tile, final score, the sequence, and the number of moves made.
    """
    game = Game2048()
    move_count = 0
    seq_idx = 0
    invalid_moves = 0
    while not game.is_game_over() and not game.has_won():
        move = seq[seq_idx % len(seq)]
        moved = game.move_tiles(move)
        if moved:
            move_count += 1
            invalid_moves = 0
        else:
            invalid_moves += 1
            if invalid_moves >= 4:
                break
        seq_idx += 1
    board, score = game.get_state()
    max_tile = max(max(row) for row in board)
    return max_tile, score, seq, move_count

def run_parallel_simulations(seq, runs_per_seq, executor=None):
    """
    Run multiple simulations of a given move sequence in parallel.
    Returns lists of highest tiles and scores for each run.
    """
    if executor is not None:
        results = list(executor.map(simulate_sequence, [seq]*runs_per_seq))
    else:
        with ProcessPoolExecutor() as local_executor:
            results = list(local_executor.map(simulate_sequence, [seq]*runs_per_seq))
    tiles = [result[0] for result in results]
    scores = [result[1] for result in results]
    return tiles, scores

def interactive_play():
    """
    Interactive mode for playing 2048 manually or by entering a move sequence.
    """
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
    """
    Main entry point for running ML simulation or interactive play.
    """
    mode = input("Type 'ml' for ML simulation, or 'play' for interactive mode: ").strip().lower()
    if mode == 'play':
        interactive_play()
        return
    print("Starting 2048 ML simulation for sequence lengths 5 to 8...")
    runs_per_seq = 50
    best_avg_tiles_by_length = []
    best_seqs_by_length = []
    best_max_tiles_by_length = []
    best_max_tile_seqs_by_length = []
    best_max_tile_percents = []
    lengths = [5, 6, 7, 8]
    with ProcessPoolExecutor() as executor:
        for seq_len in lengths:
            print(f"\n--- Testing sequence length {seq_len} ---")
            best_avg_tile = 0
            best_tile_seq = []
            best_max_tile = 0
            best_max_tile_seq = []
            best_max_tile_count = 0
            total_seqs = 4 ** seq_len
            for idx, seq in enumerate(tqdm(itertools.product(MOVES, repeat=seq_len), total=total_seqs, desc=f"{seq_len}-move sequences"), 1):
                tiles, scores = run_parallel_simulations(seq, runs_per_seq, executor)
                avg_tile = np.mean(tiles)
                max_tile = np.max(tiles)
                max_tile_count = sum(1 for t in tiles if t == max_tile)
                if avg_tile > best_avg_tile:
                    best_avg_tile = avg_tile
                    best_tile_seq = seq
                if max_tile > best_max_tile or (max_tile == best_max_tile and max_tile_count > best_max_tile_count):
                    best_max_tile = max_tile
                    best_max_tile_seq = seq
                    best_max_tile_count = max_tile_count
            best_avg_tiles_by_length.append(best_avg_tile)
            best_seqs_by_length.append(best_tile_seq)
            best_max_tiles_by_length.append(best_max_tile)
            best_max_tile_seqs_by_length.append(best_max_tile_seq)
            percent = 100.0 * best_max_tile_count / runs_per_seq
            best_max_tile_percents.append(percent)
            print(f"Best average tile for length {seq_len}: {best_avg_tile}")
            print(f"Best sequence by average: {[MOVE_LABELS[m] for m in best_tile_seq]}")
            print(f"Top tile achieved for length {seq_len}: {best_max_tile}")
            print(f"Sequence for top tile: {[MOVE_LABELS[m] for m in best_max_tile_seq]}")
            print(f"Percent of runs for top tile: {percent:.1f}%")
    # Plot best average tile and best max tile vs. sequence length
    plt.figure(figsize=(8, 5))
    plt.plot(lengths, best_avg_tiles_by_length, marker='o', label='Best Avg Highest Tile')
    plt.plot(lengths, best_max_tiles_by_length, marker='s', label='Top Tile Achieved')
    plt.title(f'2048: Best Avg and Top Tile vs. Sequence Length ({runs_per_seq} runs each)')
    plt.xlabel('Sequence Length')
    plt.ylabel('Tile Value')
    plt.xticks(lengths)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    # Print summary
    print("\n===== SUMMARY =====")
    for l, avg_t, avg_s, max_t, max_s, pct in zip(lengths, best_avg_tiles_by_length, best_seqs_by_length, best_max_tiles_by_length, best_max_tile_seqs_by_length, best_max_tile_percents):
        print(f"Length {l}:")
        print(f"  Best Avg Tile={avg_t:.2f} | Sequence={[MOVE_LABELS[m] for m in avg_s]}")
        print(f"  Top Tile={max_t} | Sequence={[MOVE_LABELS[m] for m in max_s]} | Percent of runs: {pct:.1f}%")

if __name__ == "__main__":
    main()
