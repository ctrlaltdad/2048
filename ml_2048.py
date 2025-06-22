import itertools
from game_2048 import Game2048
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import base64
from io import BytesIO
import matplotlib.animation as animation
import random

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

def simulate_two_phase_sequence(seq1, seq2, switch_tile):
    """
    Simulate a single game of 2048 using seq1 until switch_tile is reached, then seq2 for the rest.
    Returns the highest tile, final score, the sequences, and the number of moves made.
    """
    game = Game2048()
    move_count = 0
    seq1_idx = 0
    seq2_idx = 0
    phase = 1
    invalid_moves = 0
    while not game.is_game_over() and not game.has_won():
        board, _ = game.get_state()
        max_tile = max(max(row) for row in board)
        if phase == 1 and max_tile >= switch_tile:
            phase = 2
        if phase == 1:
            move = seq1[seq1_idx % len(seq1)]
            seq1_idx += 1
        else:
            move = seq2[seq2_idx % len(seq2)]
            seq2_idx += 1
        moved = game.move_tiles(move)
        if moved:
            move_count += 1
            invalid_moves = 0
        else:
            invalid_moves += 1
            if invalid_moves >= 4:
                break
    board, score = game.get_state()
    max_tile = max(max(row) for row in board)
    return max_tile, score, seq1, seq2, move_count

def simulate_two_phase_sequence_unpack(args):
    return simulate_two_phase_sequence(*args)

def run_parallel_two_phase(seq1, seq2, switch_tile, runs_per_seq, executor=None):
    """
    Run multiple two-phase simulations in parallel.
    Returns lists of highest tiles and scores for each run.
    """
    args = [(seq1, seq2, switch_tile)] * runs_per_seq
    if executor is not None:
        results = list(executor.map(simulate_two_phase_sequence_unpack, args))
    else:
        with ProcessPoolExecutor() as local_executor:
            results = list(local_executor.map(simulate_two_phase_sequence_unpack, args))
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
    mode = input("Type 'ml' for ML simulation, 'play' for interactive mode, or 'ml2' for two-phase ML mode: ").strip().lower()
    if mode == 'play':
        interactive_play()
        return
    if mode == 'ml2':
        print("Two-phase ML mode: test strategies that switch move sequence at a given tile.")
        runs_per_seq = 10  # Reduced from 50 for faster testing
        lengths = [3, 4, 5]  # Now using 3, 4, 5
        sample_pairs = 500  # Number of random (seq1, seq2) pairs to test per length
        switch_tile = int(input("Enter switch tile (e.g., 512): ").strip())
        best_results = []
        with ProcessPoolExecutor() as executor:
            for l in lengths:
                print(f"\n--- Testing seq1/seq2 length {l} (random {sample_pairs} pairs) ---")
                best_avg_tile = 0
                best_seqs = ([], [])
                best_max_tile = 0
                best_max_tile_seqs = ([], [])
                best_max_tile_count = 0
                best_seq_tiles = []
                all_seqs = list(itertools.product(MOVES, repeat=l))
                total_seqs = len(all_seqs)
                # Randomly sample pairs (with replacement if needed)
                pairs = [ (random.choice(all_seqs), random.choice(all_seqs)) for _ in range(sample_pairs) ]
                outer = tqdm(pairs, total=sample_pairs, desc=f"seq1/seq2-{l}")
                for seq1, seq2 in outer:
                    tiles, scores = run_parallel_two_phase(seq1, seq2, switch_tile, runs_per_seq, executor)
                    avg_tile = np.mean(tiles)
                    max_tile = np.max(tiles)
                    max_tile_count = sum(1 for t in tiles if t == max_tile)
                    if avg_tile > best_avg_tile:
                        best_avg_tile = avg_tile
                        best_seqs = (seq1, seq2)
                    if max_tile > best_max_tile or (max_tile == best_max_tile and max_tile_count > best_max_tile_count):
                        best_max_tile = max_tile
                        best_max_tile_seqs = (seq1, seq2)
                        best_max_tile_count = max_tile_count
                        best_seq_tiles = tiles.copy()
                percent = 100.0 * best_max_tile_count / runs_per_seq
                print(f"Best avg tile: {best_avg_tile}")
                print(f"Best seqs by avg: {[MOVE_LABELS[m] for m in best_seqs[0]]} -> {[MOVE_LABELS[m] for m in best_seqs[1]]}")
                print(f"Top tile: {best_max_tile}")
                print(f"Seqs for top tile: {[MOVE_LABELS[m] for m in best_max_tile_seqs[0]]} -> {[MOVE_LABELS[m] for m in best_max_tile_seqs[1]]}")
                print(f"Percent of runs for top tile: {percent:.1f}%")
                best_results.append({
                    'l1': l, 'l2': l,
                    'best_avg_tile': best_avg_tile,
                    'best_seqs': best_seqs,
                    'best_max_tile': best_max_tile,
                    'best_max_tile_seqs': best_max_tile_seqs,
                    'percent': percent,
                    'best_seq_tiles': best_seq_tiles
                })
        # Visualization and HTML output for two-phase mode
        with open('results.html', 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>2048 Two-Phase ML Results</title></head><body>')
            f.write(f'<h1>2048 Two-Phase ML Results (Switch at {switch_tile})</h1>')
            for res in best_results:
                l1, l2 = res['l1'], res['l2']
                seq1, seq2 = res['best_max_tile_seqs']
                tiles = res['best_seq_tiles']
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.hist(tiles, bins=range(min(tiles), max(tiles)+2), edgecolor='black', alpha=0.7)
                ax.set_title(f'Tile Distribution: seq1-{l1} → seq2-{l2}')
                ax.set_xlabel('Tile Value')
                ax.set_ylabel('Frequency')
                ax.grid(True, axis='y', linestyle='--', alpha=0.5)
                buf = BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format='png')
                plt.close(fig)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                f.write(f'<h2>seq1-{l1}: {[MOVE_LABELS[m] for m in seq1]} → seq2-{l2}: {[MOVE_LABELS[m] for m in seq2]}</h2>')
                f.write(f'<img src="data:image/png;base64,{img_base64}"/><br/>')
                f.write(f'<p>Best Avg Tile: {res["best_avg_tile"]:.2f} | Top Tile: {res["best_max_tile"]} | % of runs: {res["percent"]:.1f}%</p>')
            f.write('</body></html>')
        print("\n===== TWO-PHASE SUMMARY =====")
        for res in best_results:
            l1, l2 = res['l1'], res['l2']
            print(f"seq1-{l1} → seq2-{l2}:")
            print(f"  Best Avg Tile={res['best_avg_tile']:.2f} | seq1={[MOVE_LABELS[m] for m in res['best_seqs'][0]]} | seq2={[MOVE_LABELS[m] for m in res['best_seqs'][1]]}")
            print(f"  Top Tile={res['best_max_tile']} | seq1={[MOVE_LABELS[m] for m in res['best_max_tile_seqs'][0]]} | seq2={[MOVE_LABELS[m] for m in res['best_max_tile_seqs'][1]]} | % of runs: {res['percent']:.1f}%")
        return
    print("Starting 2048 ML simulation for sequence lengths 5 to 8...")
    runs_per_seq = 50
    best_avg_tiles_by_length = []
    best_seqs_by_length = []
    best_max_tiles_by_length = []
    best_max_tile_seqs_by_length = []
    best_max_tile_percents = []
    lengths = [5, 6, 7, 8]
    html_plots = []
    heatmap_data = []
    heatmap_tile_labels = set()
    animated_hist_data = None
    animated_hist_seq = None
    animated_hist_moves = None
    with ProcessPoolExecutor() as executor:
        for seq_len in lengths:
            print(f"\n--- Testing sequence length {seq_len} ---")
            best_avg_tile = 0
            best_tile_seq = []
            best_max_tile = 0
            best_max_tile_seq = []
            best_max_tile_count = 0
            best_seq_tiles = []
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
                    best_seq_tiles = tiles.copy()
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
            # Create and save histogram for this sequence length
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(best_seq_tiles, bins=range(min(best_seq_tiles), max(best_seq_tiles)+2), edgecolor='black', alpha=0.7)
            ax.set_title(f'Tile Distribution for Best {seq_len}-Move Sequence')
            ax.set_xlabel('Tile Value')
            ax.set_ylabel('Frequency')
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            # Save to base64 and embed in HTML
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            html_plots.append(f'<h2>{seq_len}-Move Sequence: {[MOVE_LABELS[m] for m in best_max_tile_seq]}</h2><img src="data:image/png;base64,{img_base64}"/><br/>')
            # Collect data for heatmap
            tile_counts = {}
            for t in best_seq_tiles:
                tile_counts[t] = tile_counts.get(t, 0) + 1
            total = len(best_seq_tiles)
            heatmap_row = []
            for tile in range(2, max(best_seq_tiles)+1, 2):
                heatmap_row.append(tile_counts.get(tile, 0) / total)
                heatmap_tile_labels.add(tile)
            heatmap_data.append(heatmap_row)
            # Collect data for animated histogram (for the longest sequence only)
            if seq_len == lengths[-1]:
                # For animation, run a single game and record tile distribution after every 10 moves
                animated_hist_seq = best_max_tile_seq
                animated_hist_moves = []
                animated_hist_data = []
                game = Game2048()
                move_idx = 0
                move_history = []
                while not game.is_game_over() and not game.has_won():
                    move = animated_hist_seq[move_idx % len(animated_hist_seq)]
                    moved = game.move_tiles({'w':'up','a':'left','s':'down','d':'right'}[move])
                    move_history.append(moved)
                    if (move_idx+1) % 10 == 0 or game.is_game_over() or game.has_won():
                        flat = [cell for row in game.board for cell in row if cell > 0]
                        animated_hist_data.append(flat.copy())
                        animated_hist_moves.append(move_idx+1)
                    move_idx += 1
    # --- Heatmap Plot ---
    heatmap_tile_labels = sorted(list(heatmap_tile_labels))
    heatmap_matrix = np.zeros((len(heatmap_tile_labels), len(lengths)))
    for col, row in enumerate(heatmap_data):
        for row_idx, val in enumerate(row):
            heatmap_matrix[row_idx, col] = val
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(heatmap_matrix, aspect='auto', cmap='YlOrRd', origin='lower')
    ax.set_xticks(np.arange(len(lengths)))
    ax.set_xticklabels(lengths)
    ax.set_yticks(np.arange(len(heatmap_tile_labels)))
    ax.set_yticklabels(heatmap_tile_labels)
    ax.set_xlabel('Sequence Length')
    ax.set_ylabel('Tile Value')
    ax.set_title('Heatmap: Probability of Achieving Each Tile')
    fig.colorbar(im, ax=ax, label='Probability')
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    heatmap_img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    # --- Animated Histogram ---
    if animated_hist_data:
        fig, ax = plt.subplots(figsize=(8, 5))
        bins = range(2, max([max(d) for d in animated_hist_data])+2, 2)
        def update_hist(i):
            ax.clear()
            ax.hist(animated_hist_data[i], bins=bins, edgecolor='black', alpha=0.7)
            ax.set_title(f'Tile Distribution after {animated_hist_moves[i]} Moves\n(Sequence: {[MOVE_LABELS[m] for m in animated_hist_seq]})')
            ax.set_xlabel('Tile Value')
            ax.set_ylabel('Frequency')
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
        ani = animation.FuncAnimation(fig, update_hist, frames=len(animated_hist_data), repeat=False)
        gif_buf = BytesIO()
        ani.save(gif_buf, writer='pillow', format='gif')
        plt.close(fig)
        gif_buf.seek(0)
        animated_gif_base64 = base64.b64encode(gif_buf.read()).decode('utf-8')
    # --- Write to HTML ---
    with open('results.html', 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>2048 ML Simulation Results</title></head><body>')
        f.write('<h1>2048 ML Simulation Results</h1>')
        f.write('<p>Distribution of top tile results for each sequence length.</p>')
        for plot_html in html_plots:
            f.write(plot_html)
        f.write('<h2>Heatmap: Probability of Achieving Each Tile</h2>')
        f.write(f'<img src="data:image/png;base64,{heatmap_img_base64}"/><br/>')
        if animated_hist_data:
            f.write('<h2>Animated Histogram: Tile Distribution Evolution (Longest Sequence)</h2>')
            f.write(f'<img src="data:image/gif;base64,{animated_gif_base64}"/><br/>')
        f.write('</body></html>')
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
