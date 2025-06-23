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
    from ml_sim import run_parallel_simulations, run_parallel_two_phase
    from visualization import plot_histogram
    print("2048 CLI Modes:")
    print("  [h] Heuristic simulation")
    print("  [s] Sequence simulation")
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
        print("ML simulation mode: [ml] for single-phase, [ml2] for two-phase.")
        sim_mode = input("Type 'ml' for ML simulation or 'ml2' for two-phase ML mode: ").strip().lower()
        if sim_mode == 'ml':
            print("Starting 2048 ML simulation for sequence lengths 5 to 8...")
            # ...insert ML simulation code here or call a function...
            print("[ML simulation not yet implemented in this stub]")
            return
        elif sim_mode == 'ml2':
            print("Two-phase ML mode: test strategies that switch move sequence at a given tile.")
            # ...insert ML2 simulation code here or call a function...
            print("[ML2 simulation not yet implemented in this stub]")
            return
        else:
            print("Invalid simulation mode.")
            return
    print("Invalid mode. Please choose 'h', 's', or 'e'.")

if __name__ == "__main__":
    main()
