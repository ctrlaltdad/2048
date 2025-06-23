import itertools
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from game_2048 import Game2048, MOVES

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
