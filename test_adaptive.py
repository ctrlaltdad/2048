#!/usr/bin/env python3
"""
Test script to verify the adaptive heuristic is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_2048 import Game2048
from heuristics import heuristic_move_adaptive, simulate_heuristic
import numpy as np

def test_adaptive_heuristic():
    """Test that the adaptive heuristic works and makes sensible moves."""
    print("Testing adaptive heuristic...")
    
    # Test 1: Early game behavior
    print("\n=== Test 1: Early Game ===")
    game = Game2048()
    game.board = np.array([
        [2, 4, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])
    
    move = heuristic_move_adaptive(game)
    print(f"Early game board:\n{game.board}")
    print(f"Adaptive move choice: {move}")
    
    # Test 2: Mid game behavior
    print("\n=== Test 2: Mid Game ===")
    game.board = np.array([
        [128, 64, 32, 16],
        [256, 128, 64, 32],
        [2, 4, 8, 16],
        [0, 2, 4, 8]
    ])
    
    move = heuristic_move_adaptive(game)
    print(f"Mid game board:\n{game.board}")
    print(f"Adaptive move choice: {move}")
    
    # Test 3: Late game behavior
    print("\n=== Test 3: Late Game ===")
    game.board = np.array([
        [1024, 512, 256, 128],
        [512, 256, 128, 64],
        [256, 128, 64, 32],
        [128, 64, 32, 16]
    ])
    
    move = heuristic_move_adaptive(game)
    print(f"Late game board:\n{game.board}")
    print(f"Adaptive move choice: {move}")
    
    # Test 4: Run a few games to see performance
    print("\n=== Test 4: Performance Test ===")
    print("Running 10 games with adaptive heuristic...")
    
    tiles, scores = simulate_heuristic('adaptive', runs=10)
    
    print(f"Final tiles: {tiles}")
    print(f"Max tile achieved: {max(tiles)}")
    print(f"Average final tile: {np.mean(tiles):.1f}")
    print(f"Average score: {np.mean(scores):.1f}")
    
    # Count achievements
    tile_1024_count = sum(1 for t in tiles if t >= 1024)
    tile_512_count = sum(1 for t in tiles if t >= 512)
    tile_256_count = sum(1 for t in tiles if t >= 256)
    
    print(f"Games reaching 1024: {tile_1024_count}/10")
    print(f"Games reaching 512: {tile_512_count}/10")
    print(f"Games reaching 256: {tile_256_count}/10")
    
    print("\n✅ Adaptive heuristic test completed!")

if __name__ == "__main__":
    test_adaptive_heuristic()
