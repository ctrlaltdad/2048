# main.py: Entry point for 2048 CLI and simulation modes
# All imports are now local to avoid circular dependencies and unnecessary imports

def interactive_play(seq_input=None):
    from game_2048 import Game2048
    print("\n=== 2048 Interactive Mode ===")
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

# Define MOVES and MOVE_LABELS here for CLI and visualization
MOVES = ['up', 'down', 'left', 'right']
MOVE_LABELS = {'up': 'w', 'down': 's', 'left': 'a', 'right': 'd'}

def main():
    import numpy as np
    from heuristics import simulate_heuristic
    from ml_sim import run_parallel_simulations, run_parallel_two_phase, simulate_two_phase_best
    from visualization import plot_histogram
    print("2048 CLI Modes:")
    print("  [h] Heuristic simulation")
    print("  [s] ML sequence simulation")
    print("  [e] Emulate/play the game")
    mode = input("Choose mode ([h]euristic, [s]imulate, [e]mulate): ").strip().lower()
    if mode == 'e':
        print("Emulation mode: play 2048 interactively or with a move sequence.")
        seq_input = input("Enter move sequence (WASD, blank for manual play): ").strip().lower()
        interactive_play(seq_input if seq_input else None)
        return
    if mode == 'h':
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
    if mode == 's':
        print("Two-phase best ML simulation: Only top X% of first sequence get second sequence.")
        seq1 = input("Enter first move sequence (e.g. 'wasd'): ").strip().lower()
        seq2 = input("Enter second move sequence (e.g. 'dsaw'): ").strip().lower()
        switch_tile = input("Switch tile (default 512): ").strip()
        switch_tile = int(switch_tile) if switch_tile.isdigit() else 512
        runs = input("Number of runs (default 50): ").strip()
        runs = int(runs) if runs.isdigit() else 50
        top_percent = input("Top percent to continue (0.2 = 20%, default): ").strip()
        top_percent = float(top_percent) if top_percent else 0.2
        # Convert WASD to directions
        keymap = {'w':'up','a':'left','s':'down','d':'right'}
        seq1_moves = [keymap[c] for c in seq1 if c in keymap]
        seq2_moves = [keymap[c] for c in seq2 if c in keymap]
        tiles, scores, improved_tiles, improved_scores = simulate_two_phase_best(seq1_moves, seq2_moves, switch_tile, runs, top_percent)
        print(f"First phase: avg tile={np.mean(tiles):.2f}, max tile={np.max(tiles)}")
        print(f"Second phase (top {int(top_percent*100)}%): avg tile={np.mean(improved_tiles):.2f}, max tile={np.max(improved_tiles)}")
        plot_histogram(tiles, 'First Phase Tile Distribution')
        plot_histogram(improved_tiles, 'Second Phase (Top) Tile Distribution')
        return
    print("Invalid mode. Please choose 'h', 's', or 'e'.")

if __name__ == "__main__":
    main()
