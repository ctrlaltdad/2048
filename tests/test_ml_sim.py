"""
Automated tests for ml_sim.py (2048 simulation logic)
Run with: pytest tests/test_ml_sim.py
"""
import pytest
import numpy as np
from ml_sim import simulate_sequence, run_parallel_simulations, simulate_two_phase_sequence, run_parallel_two_phase, simulate_two_phase_best, MOVES

def test_simulate_sequence_basic():
    """Test that simulate_sequence returns a valid tile, score, sequence, and move count for a simple sequence."""
    seq = ['up', 'down', 'left', 'right']
    max_tile, score, used_seq, move_count = simulate_sequence(seq)
    assert isinstance(max_tile, (int, np.integer))
    assert isinstance(score, (int, np.integer))
    assert used_seq == seq
    assert move_count > 0

def test_run_parallel_simulations_consistency():
    """Test that running the same sequence multiple times returns the correct number of results."""
    seq = ['up', 'down', 'left', 'right']
    runs = 5
    tiles, scores = run_parallel_simulations(seq, runs)
    assert len(tiles) == runs
    assert len(scores) == runs
    assert all(isinstance(t, (int, np.integer)) for t in tiles)
    assert all(isinstance(s, (int, np.integer)) for s in scores)

def test_simulate_two_phase_sequence_switch():
    """Test two-phase simulation switches to second sequence at the correct tile value."""
    seq1 = ['up'] * 2
    seq2 = ['down'] * 2
    switch_tile = 4  # Should switch after first merge
    max_tile, score, used_seq1, used_seq2, move_count = simulate_two_phase_sequence(seq1, seq2, switch_tile)
    assert isinstance(max_tile, (int, np.integer))
    assert used_seq1 == seq1
    assert used_seq2 == seq2
    assert move_count > 0

def test_run_parallel_two_phase_length():
    """Test that run_parallel_two_phase returns correct number of results."""
    seq1 = ['up'] * 2
    seq2 = ['down'] * 2
    switch_tile = 4
    runs = 3
    tiles, scores = run_parallel_two_phase(seq1, seq2, switch_tile, runs)
    assert len(tiles) == runs
    assert len(scores) == runs

def test_simulate_two_phase_best_top_percent():
    """Test that simulate_two_phase_best returns correct number of improved results for top percent."""
    seq1 = ['up'] * 2
    seq2 = ['down'] * 2
    switch_tile = 4
    runs = 10
    top_percent = 0.3
    tiles, scores, improved_tiles, improved_scores = simulate_two_phase_best(seq1, seq2, switch_tile, runs, top_percent)
    n_top = max(1, int(top_percent * runs))
    assert len(tiles) == runs
    assert len(scores) == runs
    assert len(improved_tiles) == n_top
    assert len(improved_scores) == n_top

def test_simulate_sequence_invalid_moves():
    """Test that simulate_sequence terminates if only invalid moves are given."""
    seq = ['up'] * 10  # Eventually will be stuck
    max_tile, score, used_seq, move_count = simulate_sequence(seq)
    assert move_count <= 40  # Should not loop forever
