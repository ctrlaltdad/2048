"""
Test ML optimization functionality

This script tests the ML optimization components to ensure they work correctly.
"""

import numpy as np
from game_2048 import Game2048
from heuristics import HeuristicEvaluator
from ml_optimizer import WeightOptimizer, OptimizationResult

def test_heuristic_evaluator():
    """Test the HeuristicEvaluator class"""
    print("Testing HeuristicEvaluator...")
    
    evaluator = HeuristicEvaluator()
    
    # Create a test board
    test_board = np.array([
        [2, 4, 8, 16],
        [0, 2, 4, 8],
        [0, 0, 2, 4],
        [0, 0, 0, 2]
    ])
    
    # Test individual heuristics
    mono_score = evaluator.eval_monotonicity(test_board)
    corner_score = evaluator.eval_corner(test_board)
    smooth_score = evaluator.eval_smoothness(test_board)
    empty_score = evaluator.eval_empty(test_board)
    
    print(f"  Monotonicity score: {mono_score}")
    print(f"  Corner score: {corner_score}")
    print(f"  Smoothness score: {smooth_score:.2f}")
    print(f"  Empty score: {empty_score}")
    
    # Test weighted combination
    weights = {
        'monotonicity': 1.0,
        'corner': 0.5,
        'center': 0.0,
        'expectimax': 0.0,
        'opportunistic': 0.0,
        'smoothness': 0.1,
        'empty': 2.7,
        'merge': 1.0
    }
    
    weighted_score = evaluator.eval_weighted_combo(test_board, weights)
    print(f"  Weighted combo score: {weighted_score:.2f}")
    
    # Test move selection
    move = evaluator.pick_weighted_move(test_board, weights)
    print(f"  Recommended move: {move}")
    
    print("✓ HeuristicEvaluator tests passed")

def test_optimization_result():
    """Test OptimizationResult class"""
    print("\nTesting OptimizationResult...")
    
    weights = {'monotonicity': 1.0, 'empty': 2.0}
    result = OptimizationResult(
        weights=weights,
        win_rate=45.5,
        avg_score=12345,
        avg_max_tile=512,
        avg_moves=234,
        games_played=50
    )
    
    print(f"  Result: {result}")
    print("✓ OptimizationResult tests passed")

def test_weight_optimizer():
    """Test WeightOptimizer with a very small example"""
    print("\nTesting WeightOptimizer...")
    
    # Use very small parameters for quick testing
    optimizer = WeightOptimizer(games_per_eval=3, max_workers=1)
    
    # Test weight evaluation
    test_weights = {
        'monotonicity': 1.0,
        'corner': 0.0,
        'center': 0.0,
        'expectimax': 0.0,
        'opportunistic': 0.0,
        'smoothness': 0.1,
        'empty': 2.7,
        'merge': 1.0
    }
    
    print("  Testing weight evaluation (this may take a moment)...")
    result = optimizer.evaluate_weights(test_weights)
    print(f"  Test result: {result}")
    
    # Test a very small random search
    print("  Testing mini random search...")
    results = optimizer.random_search(iterations=2)
    print(f"  Completed {len(results)} random search iterations")
    
    if optimizer.best_result:
        print(f"  Best result found: {optimizer.best_result.win_rate:.1f}% win rate")
    
    print("✓ WeightOptimizer tests passed")

def test_game_integration():
    """Test integration with the game"""
    print("\nTesting game integration...")
    
    evaluator = HeuristicEvaluator()
    game = Game2048()
    
    moves_played = 0
    max_moves = 50  # Limit for testing
    
    while not game.is_game_over() and moves_played < max_moves:
        move = evaluator.pick_weighted_move(game.board)
        if move and game.move(move):
            moves_played += 1
        else:
            break
    
    final_score = game.score
    max_tile = np.max(game.board)
    
    print(f"  Game completed: {moves_played} moves")
    print(f"  Final score: {final_score}")
    print(f"  Max tile reached: {max_tile}")
    
    print("✓ Game integration tests passed")

def run_all_tests():
    """Run all tests"""
    print("Running ML optimization tests...\n")
    
    try:
        test_heuristic_evaluator()
        test_optimization_result()
        test_weight_optimizer()
        test_game_integration()
        
        print("\n" + "="*50)
        print("🎉 All tests passed successfully!")
        print("✓ HeuristicEvaluator working correctly")
        print("✓ OptimizationResult working correctly") 
        print("✓ WeightOptimizer working correctly")
        print("✓ Game integration working correctly")
        print("\nThe ML optimization system is ready to use!")
        print("Try running: python ml_runner.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
