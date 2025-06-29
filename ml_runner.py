"""
Simple ML Optimization Runner for 2048

This script runs weight optimization without requiring additional dependencies like pandas/seaborn.
It provides basic analysis functionality and integrates with the existing game code.
"""

import json
import time
import numpy as np
import matplotlib.pyplot as plt
from ml_optimizer import WeightOptimizer
from game_2048 import Game2048
from heuristics import HeuristicEvaluator

def run_quick_optimization():
    """Run a quick optimization session with user-friendly interface"""
    print("=== 2048 Weight Optimization Tool ===")
    print("This tool will help you find optimal weights for the 2048 game heuristics.")
    print()
    
    # Get user preferences
    method = input("Choose optimization method (random/genetic/grid): ").strip().lower()
    if method not in ['random', 'genetic', 'grid']:
        method = 'random'
        print("Using random search as default")
    
    if method == 'random':
        iterations = int(input("Number of iterations (default 30): ") or "30")
        games_per_eval = int(input("Games per evaluation (default 15): ") or "15")
    elif method == 'genetic':
        iterations = int(input("Number of generations (default 15): ") or "15")
        games_per_eval = int(input("Games per evaluation (default 10): ") or "10")
    else:  # grid
        games_per_eval = int(input("Games per evaluation (default 20): ") or "20")
        iterations = None  # Grid search determines its own iterations
    
    # Initialize optimizer
    optimizer = WeightOptimizer(games_per_eval=games_per_eval, max_workers=1)
    
    print(f"\nStarting {method} optimization...")
    print(f"Games per evaluation: {games_per_eval}")
    print("This may take several minutes...")
    print()
    
    start_time = time.time()
    
    try:
        if method == 'random':
            results = optimizer.random_search(iterations)
        elif method == 'genetic':
            results = optimizer.genetic_algorithm(generations=iterations, population_size=15)
        else:  # grid
            weight_ranges = {
                'monotonicity': [0.5, 1.0, 1.5],
                'smoothness': [0.0, 0.1, 0.2],
                'empty': [2.0, 2.7, 3.0],
                'merge': [0.5, 1.0, 1.5]
            }
            results = optimizer.grid_search(weight_ranges)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n=== Optimization Complete! ===")
        print(f"Time elapsed: {elapsed_time:.1f} seconds")
        print(f"Experiments run: {len(optimizer.history)}")
        
        if optimizer.best_result:
            print(f"\nBest configuration found:")
            print(f"Win Rate: {optimizer.best_result.win_rate:.1f}%")
            print(f"Average Score: {optimizer.best_result.avg_score:.0f}")
            print(f"Average Max Tile: {optimizer.best_result.avg_max_tile:.0f}")
            print(f"Average Moves: {optimizer.best_result.avg_moves:.0f}")
            print(f"\nOptimal weights:")
            for weight, value in optimizer.best_result.weights.items():
                if value > 0.05:  # Only show significant weights
                    print(f"  {weight}: {value:.2f}")
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"optimization_results_{method}_{timestamp}.json"
        optimizer.save_results(filename)
        print(f"\nResults saved to: {filename}")
        
        # Generate simple analysis
        analyze_results_simple(optimizer.history)
        
        return optimizer.best_result
    
    except KeyboardInterrupt:
        print("\nOptimization interrupted by user")
        if optimizer.history:
            print(f"Partial results available: {len(optimizer.history)} experiments")
            if optimizer.best_result:
                print(f"Best so far: {optimizer.best_result.win_rate:.1f}% win rate")
        return None
    except Exception as e:
        print(f"Error during optimization: {e}")
        return None

def analyze_results_simple(history):
    """Simple analysis without external dependencies"""
    if not history:
        print("No results to analyze")
        return
    
    win_rates = [r.win_rate for r in history]
    scores = [r.avg_score for r in history]
    max_tiles = [r.avg_max_tile for r in history]
    
    print(f"\n=== Simple Analysis ===")
    print(f"Win rate statistics:")
    print(f"  Best: {max(win_rates):.1f}%")
    print(f"  Average: {np.mean(win_rates):.1f}%")
    print(f"  Worst: {min(win_rates):.1f}%")
    print(f"  Standard deviation: {np.std(win_rates):.1f}%")
    
    print(f"\nScore statistics:")
    print(f"  Best: {max(scores):.0f}")
    print(f"  Average: {np.mean(scores):.0f}")
    print(f"  Standard deviation: {np.std(scores):.0f}")
    
    # Find top 10% performers
    top_count = max(1, len(history) // 10)
    top_performers = sorted(history, key=lambda x: x.win_rate, reverse=True)[:top_count]
    
    print(f"\nTop {top_count} performer(s) weight analysis:")
    weight_sums = {}
    for result in top_performers:
        for weight, value in result.weights.items():
            if weight not in weight_sums:
                weight_sums[weight] = []
            weight_sums[weight].append(value)
    
    for weight, values in weight_sums.items():
        mean_val = np.mean(values)
        if mean_val > 0.05:  # Only show significant weights
            print(f"  {weight}: {mean_val:.2f} (±{np.std(values):.2f})")

def test_configuration(weights, num_games=50):
    """Test a specific weight configuration"""
    print(f"\nTesting configuration with {num_games} games...")
    
    evaluator = HeuristicEvaluator()
    
    wins = 0
    scores = []
    max_tiles = []
    moves_list = []
    
    for i in range(num_games):
        game = Game2048()
        moves = 0
        
        while not game.is_game_over() and moves < 2000:
            move = evaluator.pick_weighted_move(game.board, weights)
            if move and game.move(move):
                moves += 1
            else:
                break
        
        max_tile = np.max(game.board)
        if max_tile >= 2048:
            wins += 1
        
        scores.append(game.score)
        max_tiles.append(max_tile)
        moves_list.append(moves)
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{num_games} games")
    
    win_rate = (wins / num_games) * 100
    avg_score = np.mean(scores)
    avg_max_tile = np.mean(max_tiles)
    avg_moves = np.mean(moves_list)
    
    print(f"\nTest Results:")
    print(f"Win Rate: {win_rate:.1f}% ({wins}/{num_games})")
    print(f"Average Score: {avg_score:.0f}")
    print(f"Average Max Tile: {avg_max_tile:.0f}")
    print(f"Average Moves: {avg_moves:.0f}")
    
    return {
        'win_rate': win_rate,
        'avg_score': avg_score,
        'avg_max_tile': avg_max_tile,
        'avg_moves': avg_moves
    }

def compare_configurations():
    """Compare different weight configurations"""
    print("=== Configuration Comparison ===")
    
    # Reference configuration (from ovolve/2048-AI)
    reference_weights = {
        'monotonicity': 1.0,
        'corner': 0.0,
        'center': 0.0,
        'expectimax': 0.0,
        'opportunistic': 0.0,
        'smoothness': 0.1,
        'empty': 2.7,
        'merge': 1.0
    }
    
    # Alternative configurations to test
    configurations = {
        'Reference (ovolve/2048-AI)': reference_weights,
        'Monotonicity Focus': {
            'monotonicity': 2.0, 'corner': 0.0, 'center': 0.0, 'expectimax': 0.0,
            'opportunistic': 0.0, 'smoothness': 0.1, 'empty': 1.5, 'merge': 0.5
        },
        'Balanced Approach': {
            'monotonicity': 1.0, 'corner': 0.5, 'center': 0.0, 'expectimax': 0.5,
            'opportunistic': 0.3, 'smoothness': 0.2, 'empty': 2.0, 'merge': 1.0
        },
        'Empty-Heavy': {
            'monotonicity': 0.8, 'corner': 0.0, 'center': 0.0, 'expectimax': 0.0,
            'opportunistic': 0.0, 'smoothness': 0.1, 'empty': 4.0, 'merge': 0.8
        }
    }
    
    results = {}
    for name, weights in configurations.items():
        print(f"\nTesting: {name}")
        results[name] = test_configuration(weights, num_games=30)
    
    print(f"\n=== Comparison Summary ===")
    print(f"{'Configuration':<25} {'Win Rate':<10} {'Avg Score':<12} {'Avg Max Tile':<15}")
    print("-" * 65)
    
    for name, result in results.items():
        print(f"{name:<25} {result['win_rate']:>7.1f}% {result['avg_score']:>10.0f} {result['avg_max_tile']:>13.0f}")

def main():
    """Main menu for the optimization tool"""
    while True:
        print("\n" + "="*50)
        print("2048 ML Weight Optimization Tool")
        print("="*50)
        print("1. Run optimization")
        print("2. Test specific configuration")
        print("3. Compare standard configurations")
        print("4. Load and analyze previous results")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            run_quick_optimization()
        
        elif choice == '2':
            print("\nEnter weights for each heuristic (0-5, press Enter for 0):")
            weights = {}
            heuristics = ['monotonicity', 'corner', 'center', 'expectimax', 'opportunistic', 'smoothness', 'empty', 'merge']
            
            for heuristic in heuristics:
                value = input(f"{heuristic}: ").strip()
                weights[heuristic] = float(value) if value else 0.0
            
            num_games = int(input("Number of test games (default 30): ") or "30")
            test_configuration(weights, num_games)
        
        elif choice == '3':
            compare_configurations()
        
        elif choice == '4':
            filename = input("Enter results filename: ").strip()
            try:
                optimizer = WeightOptimizer()
                optimizer.load_results(filename)
                analyze_results_simple(optimizer.history)
            except Exception as e:
                print(f"Error loading results: {e}")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
