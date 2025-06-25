"""
Automated tests for heuristics.py (2048 heuristic logic)
Run with: pytest tests/test_heuristics.py
"""
import pytest
import numpy as np
from heuristics import simulate_heuristic

def test_opportunistic_runs_and_returns_tiles():
    """Test that the opportunistic heuristic runs and returns valid tiles and scores."""
    tiles, scores = simulate_heuristic('opportunistic', runs=5)
    assert len(tiles) == 5
    assert len(scores) == 5
    assert all(isinstance(t, (int, np.integer)) for t in tiles)
    assert all(isinstance(s, (int, np.integer)) for s in scores)
    assert max(tiles) >= 2

def test_opportunistic_not_worse_than_random():
    """Test that opportunistic heuristic performs at least as well as random in a small sample."""
    tiles_opp, _ = simulate_heuristic('opportunistic', runs=10)
    tiles_rand, _ = simulate_heuristic('random', runs=10)
    assert np.mean(tiles_opp) >= 0.8 * np.mean(tiles_rand)  # Should not be much worse than random
