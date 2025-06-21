import itertools
from game_2048 import Game2048
import matplotlib.pyplot as plt
import numpy as np

MOVES = ['up', 'down', 'left', 'right']
MOVE_LABELS = {'up': 'w', 'down': 's', 'left': 'a', 'right': 'd'}

def simulate_sequence(seq):
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
            if move_count % 100 == 0:
                print(f"After {move_count} moves for sequence {[MOVE_LABELS[m] for m in seq]}:")
                game.print_board()
        else:
            invalid_moves += 1
            if invalid_moves >= 4:
                print(f"No valid moves for sequence {[MOVE_LABELS[m] for m in seq]}. Ending simulation.")
                break
        seq_idx += 1
    board, score = game.get_state()
    max_tile = max(max(row) for row in board)
    return max_tile, score, seq, move_count

def main():
    print("Starting 2048 ML simulation for sequence lengths 5 to 8...")
    runs_per_seq = 50
    best_avg_tiles_by_length = []
    best_seqs_by_length = []
    lengths = [5, 6, 7, 8]
    for seq_len in lengths:
        print(f"\n--- Testing sequence length {seq_len} ---")
        best_avg_tile = 0
        best_tile_seq = []
        for idx, seq in enumerate(itertools.product(MOVES, repeat=seq_len), 1):
            scores = []
            tiles = []
            for run in range(runs_per_seq):
                max_tile, score, moves, move_count = simulate_sequence(seq)
                scores.append(score)
                tiles.append(max_tile)
            avg_tile = np.mean(tiles)
            if avg_tile > best_avg_tile:
                best_avg_tile = avg_tile
                best_tile_seq = seq
            if idx % 50 == 0:
                print(f"SeqLen {seq_len} Sim {idx:4d}: AvgTile={avg_tile:6.2f} | Sequence={[MOVE_LABELS[m] for m in seq]}")
        best_avg_tiles_by_length.append(best_avg_tile)
        best_seqs_by_length.append(best_tile_seq)
        print(f"Best average tile for length {seq_len}: {best_avg_tile}")
        print(f"Best sequence: {[MOVE_LABELS[m] for m in best_tile_seq]}")
    # Plot best average tile vs. sequence length
    plt.figure(figsize=(8, 5))
    plt.plot(lengths, best_avg_tiles_by_length, marker='o')
    plt.title(f'2048: Best Avg Highest Tile vs. Sequence Length ({runs_per_seq} runs each)')
    plt.xlabel('Sequence Length')
    plt.ylabel('Best Avg Highest Tile')
    plt.xticks(lengths)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    # Print summary
    for l, t, s in zip(lengths, best_avg_tiles_by_length, best_seqs_by_length):
        print(f"Length {l}: Best Avg Tile={t:.2f} | Sequence={[MOVE_LABELS[m] for m in s]}")

if __name__ == "__main__":
    main()
