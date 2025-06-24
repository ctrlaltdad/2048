import itertools
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from game_2048 import Game2048

MOVES = ['up', 'down', 'left', 'right']

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
        else:
            invalid_moves += 1
            if invalid_moves >= 4:
                break
        seq_idx += 1
    board, score = game.get_state()
    max_tile = np.max(board)
    return max_tile, score, seq, move_count

def run_parallel_simulations(seq, runs_per_seq, executor=None):
    if executor is not None:
        results = list(executor.map(simulate_sequence, [seq]*runs_per_seq))
    else:
        with ProcessPoolExecutor() as local_executor:
            results = list(local_executor.map(simulate_sequence, [seq]*runs_per_seq))
    tiles = [result[0] for result in results]
    scores = [result[1] for result in results]
    return tiles, scores

def simulate_two_phase_sequence(seq1, seq2, switch_tile):
    game = Game2048()
    move_count = 0
    seq1_idx = 0
    seq2_idx = 0
    phase = 1
    invalid_moves = 0
    while not game.is_game_over() and not game.has_won():
        board, _ = game.get_state()
        max_tile = np.max(board)
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
    max_tile = np.max(board)
    return max_tile, score, seq1, seq2, move_count

def simulate_two_phase_sequence_unpack(args):
    return simulate_two_phase_sequence(*args)

def run_parallel_two_phase(seq1, seq2, switch_tile, runs_per_seq, executor=None):
    args = [(seq1, seq2, switch_tile)] * runs_per_seq
    if executor is not None:
        results = list(executor.map(simulate_two_phase_sequence_unpack, args))
    else:
        with ProcessPoolExecutor() as local_executor:
            results = list(local_executor.map(simulate_two_phase_sequence_unpack, args))
    tiles = [result[0] for result in results]
    scores = [result[1] for result in results]
    return tiles, scores

def simulate_two_phase_best(seq1, seq2, switch_tile, runs_per_seq, top_percent=0.2):
    """
    Run the first sequence for all runs, then for the top X% highest-tile games,
    continue with the second sequence from the saved state at switch_tile or higher.
    Returns: (tiles, scores, improved_tiles, improved_scores)
    """
    from game_2048 import Game2048
    import numpy as np
    import copy
    # First phase: run seq1 for all runs
    states = []
    results = []
    for _ in range(runs_per_seq):
        game = Game2048()
        move_count = 0
        seq1_idx = 0
        phase = 1
        invalid_moves = 0
        # Play until switch_tile or game over
        while not game.is_game_over() and not game.has_won():
            board, _ = game.get_state()
            max_tile = np.max(board)
            if phase == 1 and max_tile >= switch_tile:
                break
            move = seq1[seq1_idx % len(seq1)]
            seq1_idx += 1
            moved = game.move_tiles(move)
            if moved:
                move_count += 1
                invalid_moves = 0
            else:
                invalid_moves += 1
                if invalid_moves >= 4:
                    break
        board, score = game.get_state()
        max_tile = np.max(board)
        # Save state for possible second phase
        states.append((copy.deepcopy(game), seq1_idx))
        results.append((max_tile, score))
    # Select top X% by tile (and score as tiebreaker)
    n_top = max(1, int(top_percent * runs_per_seq))
    sorted_idx = sorted(range(len(results)), key=lambda i: (results[i][0], results[i][1]), reverse=True)
    top_indices = sorted_idx[:n_top]
    # Second phase: continue with seq2 from saved state
    improved_tiles = []
    improved_scores = []
    for i in top_indices:
        game, seq1_idx = states[i]
        seq2_idx = 0
        invalid_moves = 0
        while not game.is_game_over() and not game.has_won():
            move = seq2[seq2_idx % len(seq2)]
            seq2_idx += 1
            moved = game.move_tiles(move)
            if moved:
                invalid_moves = 0
            else:
                invalid_moves += 1
                if invalid_moves >= 4:
                    break
        board, score = game.get_state()
        improved_tiles.append(np.max(board))
        improved_scores.append(score)
    # Return all first-phase results and improved second-phase results
    return [r[0] for r in results], [r[1] for r in results], improved_tiles, improved_scores
