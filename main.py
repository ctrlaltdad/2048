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
    from heuristics import simulate_heuristic, simulate_two_phase_heuristic
    from ml_sim import run_parallel_simulations, run_parallel_two_phase, simulate_two_phase_best
    from visualization import plot_histogram, show_heatmap_from_tiles, save_visuals_to_html
    import uuid
    import time
    import os
    import csv
    from datetime import datetime
    csv_file = 'results.csv'
    def append_csv_row(sim_type, params, top_tile, percent_top, std, sim_duration_sec):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_id = str(uuid.uuid4())
        row = [timestamp, run_id, sim_type, params, top_tile, percent_top, std, sim_duration_sec]
        file_exists = os.path.exists(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.stat(csv_file).st_size == 0:
                writer.writerow(['timestamp','run_id','sim_type','parameters','top_tile','percent_top','std','sim_duration_sec'])
            writer.writerow(row)
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
        import time
        start_time = time.time()
        tiles, scores = simulate_heuristic(heuristic, runs)
        sim_duration_sec = time.time() - start_time
        top_tile = np.max(tiles)
        top_count = sum(1 for t in tiles if t == top_tile)
        print(f"Heuristic: {heuristic}")
        print(f"Top tile: {top_tile} | Percent: {100.0 * top_count / len(tiles):.1f}%")
        print(f"Average top tile: {np.mean(tiles):.2f}")
        visuals = []
        visuals.append(plot_histogram(tiles, f'Tile Distribution: Heuristic {heuristic}', show=False, return_html=True))
        visuals.append(show_heatmap_from_tiles(tiles, f'Heatmap: Heuristic {heuristic}', show=False, return_html=True))
        solutions = [{
            'name': f'Heuristic: {heuristic}',
            'avg': float(np.mean(tiles)),
            'std': float(np.std(tiles)),
            'top': int(top_tile),
            'percent': 100.0 * top_count / len(tiles),
            'plots': visuals
        }]
        save_visuals_to_html(solutions, filename='results.html', run_title=f'Heuristic: {heuristic}')
        # CSV logging
        append_csv_row(
            sim_type='heuristic',
            params=f'heuristic={heuristic},runs={runs}',
            top_tile=int(top_tile),
            percent_top=100.0 * top_count / len(tiles),
            std=float(np.std(tiles)),
            sim_duration_sec=sim_duration_sec
        )
        return
    if mode == 's':
        print("Simulation options:")
        print("  [1] Find best fixed sequence (length 4, 5, or 6)")
        print("  [2] Find best split sequence (length 4, 5, or 6, split at tile 512, only top X% continue)")
        print("  [3] Find best heuristic")
        print("  [4] 2-Phase Heuristic Simulation (switch heuristics at a target tile)")
        sim_opt = input("Choose simulation option [1/2/3/4]: ").strip()
        if sim_opt == '1':
            from itertools import product
            runs = input("Number of runs per sequence (default 20): ").strip()
            runs = int(runs) if runs.isdigit() else 20
            all_solutions = []
            for l in [4, 5, 6]:
                print(f"Testing all {l}-move sequences...")
                best_solutions = []
                for seq in product(MOVES, repeat=l):
                    # Repeat the sequence to ensure the full length is used in simulation
                    def full_seq_sim(s):
                        # Repeat the sequence to at least 100 moves
                        repeat_seq = list(s) * (100 // len(s) + 1)
                        return repeat_seq[:100]
                    tiles, _ = run_parallel_simulations(full_seq_sim(seq), runs)
                    avg = np.mean(tiles)
                    top_tile = np.max(tiles)
                    top_pct = 100.0 * sum(1 for t in tiles if t == top_tile) / len(tiles)
                    best_solutions.append({
                        'name': f'Sequence: {seq}',
                        'avg': float(avg),
                        'std': float(np.std(tiles)),
                        'top': int(top_tile),
                        'percent': top_pct,
                        'plots': [
                            plot_histogram(tiles, f'Histogram: {seq}', show=False, return_html=True),
                            show_heatmap_from_tiles(tiles, f'Heatmap: {seq}', show=False, return_html=True)
                        ]
                    })
                # Sort and keep top 5
                best_solutions.sort(key=lambda s: s['avg'], reverse=True)
                top5 = best_solutions[:5]
                print(f"Top 5 {l}-move sequences:")
                for i, sol in enumerate(top5):
                    print(f"  {i+1}. {sol['name']} (avg: {sol['avg']:.2f}, top: {sol['top']}, percent: {sol['percent']:.1f}%)")
                save_visuals_to_html(top5, filename='results.html', run_title=f'Best {l}-Move Sequences')
                # CSV logging for each top sequence
                for sol in top5:
                    append_csv_row(
                        sim_type='fixed_sequence',
                        params=f'sequence={sol["name"]},runs={runs}',
                        top_tile=sol['top'],
                        percent_top=sol['percent'],
                        std=sol['std'],
                        sim_duration_sec=0  # Placeholder for duration
                    )
            return
        elif sim_opt == '2':
            from itertools import product
            runs = input("Number of runs per sequence (default 20): ").strip()
            runs = int(runs) if runs.isdigit() else 20
            top_percent = input("Top percent to continue (0.2 = 20%, default): ").strip()
            top_percent = float(top_percent) if top_percent else 0.2
            best_avg = 0
            best_seq1 = None
            best_seq2 = None
            best_tiles = []
            best_improved = []
            best_top = 0
            best_top_pct = 0
            best_top2 = 0
            best_top2_pct = 0
            for l in [4, 5, 6]:
                print(f"Testing all split {l}-move sequences...")
                for seq1 in product(MOVES, repeat=l):
                    for seq2 in product(MOVES, repeat=l):
                        tiles, _, improved_tiles, _ = simulate_two_phase_best(seq1, seq2, 512, runs, top_percent)
                        avg = np.mean(improved_tiles) if improved_tiles else 0
                        top_tile = np.max(improved_tiles) if improved_tiles else 0
                        top_pct = 100.0 * sum(1 for t in improved_tiles if t == top_tile) / len(improved_tiles) if improved_tiles else 0
                        if avg > best_avg:
                            best_avg = avg
                            best_seq1 = seq1
                            best_seq2 = seq2
                            best_tiles = tiles
                            best_improved = improved_tiles
                            best_top = np.max(tiles)
                            best_top_pct = 100.0 * sum(1 for t in tiles if t == best_top) / len(tiles)
                            best_top2 = top_tile
                            best_top2_pct = top_pct
                print(f"Best split {l}-move: {best_seq1} -> {best_seq2} (avg improved tile: {best_avg:.2f}, top tile: {best_top2}, percent: {best_top2_pct:.1f}%)")
                visuals = []
                visuals.append(plot_histogram(best_tiles, f'First Phase {l}-Move', show=False, return_html=True))
                visuals.append(plot_histogram(best_improved, f'Second Phase {l}-Move (Top)', show=False, return_html=True))
                visuals.append(show_heatmap_from_tiles(best_improved, f'Heatmap: Second Phase {l}-Move (Top)', show=False, return_html=True))
                save_visuals_to_html(visuals, 'results.html', title=f'Best Split {l}-Move Sequence')
                # CSV logging for best split sequence
                append_csv_row(
                    sim_type='split_sequence',
                    params=f'seq1={best_seq1},seq2={best_seq2},runs={runs},top_percent={top_percent}',
                    top_tile=best_top2,
                    percent_top=best_top2_pct,
                    std=float(np.std(best_improved)) if best_improved else 0,
                    sim_duration_sec=0  # Placeholder for duration
                )
            return
        elif sim_opt == '3':
            heuristics = ['corner', 'center', 'expectimax', 'opportunistic']
            runs = input("Number of runs per heuristic (default 20): ").strip()
            runs = int(runs) if runs.isdigit() else 20
            all_solutions = []
            for h in heuristics:
                tiles, _ = simulate_heuristic(h, runs)
                avg = np.mean(tiles)
                top_tile = np.max(tiles)
                top_pct = 100.0 * sum(1 for t in tiles if t == top_tile) / len(tiles)
                all_solutions.append({
                    'name': f'Heuristic: {h}',
                    'avg': float(avg),
                    'std': float(np.std(tiles)),
                    'top': int(top_tile),
                    'percent': top_pct,
                    'plots': [
                        plot_histogram(tiles, f'Histogram: {h}', show=False, return_html=True),
                        show_heatmap_from_tiles(tiles, f'Heatmap: {h}', show=False, return_html=True)
                    ]
                })
                print(f"Heuristic {h}: avg tile {avg:.2f}, top tile {top_tile}, percent {top_pct:.1f}%")
            # Sort and keep top 5
            all_solutions.sort(key=lambda s: s['avg'], reverse=True)
            top5 = all_solutions[:5]
            print(f"Best heuristic: {top5[0]['name']} (avg tile: {top5[0]['avg']:.2f}, top tile: {top5[0]['top']}, percent: {top5[0]['percent']:.1f}%)")
            # CSV logging for each top heuristic
            import time
            start_time = time.time()
            for sol in top5:
                append_csv_row(
                    sim_type='heuristic_compare',
                    params=f'heuristic={sol["name"]},runs={runs}',
                    top_tile=sol['top'],
                    percent_top=sol['percent'],
                    std=sol['std'],
                    sim_duration_sec=sim_duration_sec
                )
            return
        elif sim_opt == '4':
            heuristics = ['corner', 'center', 'expectimax']
            print("Available heuristics:", ', '.join(heuristics))
            heur1 = input("First phase heuristic: ").strip().lower()
            heur2 = input("Second phase heuristic: ").strip().lower()
            if heur1 not in heuristics or heur2 not in heuristics:
                print("Invalid heuristic(s). Choose from:", ', '.join(heuristics))
                return
            runs = input("Number of runs (default 50): ").strip()
            runs = int(runs) if runs.isdigit() else 50
            switch_tile = input("Switch to second heuristic at which tile? (default 512): ").strip()
            switch_tile = int(switch_tile) if switch_tile.isdigit() else 512
            import time
            start_time = time.time()
            tiles, scores = simulate_two_phase_heuristic(heur1, heur2, runs, switch_tile)
            sim_duration_sec = time.time() - start_time
            avg = float(np.mean(tiles))
            std = float(np.std(tiles))
            top_tile = int(np.max(tiles))
            top_count = sum(1 for t in tiles if t == top_tile)
            percent = 100.0 * top_count / len(tiles)
            name = f"2-Phase: {heur1}→{heur2} @ {switch_tile}"
            visuals = [
                plot_histogram(tiles, f'Tile Distribution: {name}', show=False, return_html=True),
                show_heatmap_from_tiles(tiles, f'Heatmap: {name}', show=False, return_html=True)
            ]
            solutions = [{
                'name': name,
                'avg': avg,
                'std': std,
                'top': top_tile,
                'percent': percent,
                'plots': visuals
            }]
            print(f"2-Phase Heuristic: {heur1}→{heur2} @ {switch_tile}")
            print(f"Top tile: {top_tile} | Percent: {percent:.1f}% | Avg: {avg:.2f} | Std: {std:.2f}")
            save_visuals_to_html(solutions, filename='results.html', run_title=name)
            # CSV logging for 2-phase heuristic
            append_csv_row(
                sim_type='2phase_heuristic',
                params=f'heur1={heur1},heur2={heur2},runs={runs},switch_tile={switch_tile}',
                top_tile=top_tile,
                percent_top=percent,
                std=std,
                sim_duration_sec=sim_duration_sec
            )
            return
        else:
            print("Invalid simulation option.")
            return
    print("Invalid mode. Please choose 'h', 's', or 'e'.")

if __name__ == "__main__":
    main()
