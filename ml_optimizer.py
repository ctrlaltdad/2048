"""
Machine Learning Weight Optimizer for 2048 Game

This module implements various optimization algorithms to find the best weight combinations
for the weighted combo heuristic to maximize the probability of reaching 2048.
"""

import numpy as np
import json
import time
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import random
from dataclasses import dataclass
from game_2048 import Game2048
from heuristics import HeuristicEvaluator

@dataclass
class OptimizationResult:
    """Results from a weight optimization run"""
    weights: Dict[str, float]
    win_rate: float
    avg_score: float
    avg_max_tile: float
    avg_moves: float
    games_played: int
    
    def __str__(self):
        return f"Win Rate: {self.win_rate:.1f}%, Avg Score: {self.avg_score:.0f}, Avg Max Tile: {self.avg_max_tile:.0f}"

class WeightOptimizer:
    """
    Main optimizer class that implements various ML techniques to find optimal weights
    """
    
    def __init__(self, games_per_eval: int = 50, max_workers: int = 4):
        self.games_per_eval = games_per_eval
        self.max_workers = max_workers
        self.heuristic_names = [
            'monotonicity', 'corner', 'center', 'expectimax', 
            'opportunistic', 'smoothness', 'empty', 'merge'
        ]
        self.best_result = None
        self.history = []
        
    def evaluate_weights(self, weights: Dict[str, float]) -> OptimizationResult:
        """Evaluate a specific weight configuration"""
        evaluator = HeuristicEvaluator()
        
        results = []
        for _ in range(self.games_per_eval):
            game = Game2048()
            moves = 0
            
            while not game.is_game_over() and moves < 2000:
                move = evaluator.pick_weighted_move(game.board, weights)
                if move and game.move(move):
                    moves += 1
                else:
                    break
            
            max_tile = np.max(game.board)
            won = max_tile >= 2048
            
            results.append({
                'won': won,
                'score': game.score,
                'max_tile': max_tile,
                'moves': moves
            })
        
        # Calculate statistics
        win_rate = sum(r['won'] for r in results) / len(results) * 100
        avg_score = np.mean([r['score'] for r in results])
        avg_max_tile = np.mean([r['max_tile'] for r in results])
        avg_moves = np.mean([r['moves'] for r in results])
        
        result = OptimizationResult(
            weights=weights.copy(),
            win_rate=win_rate,
            avg_score=avg_score,
            avg_max_tile=avg_max_tile,
            avg_moves=avg_moves,
            games_played=len(results)
        )
        
        if self.best_result is None or result.win_rate > self.best_result.win_rate:
            self.best_result = result
            print(f"New best result: {result}")
        
        return result
    
    def random_search(self, iterations: int = 100) -> List[OptimizationResult]:
        """Random search optimization"""
        print(f"Starting random search with {iterations} iterations...")
        results = []
        
        for i in range(iterations):
            # Generate random weights
            weights = {}
            for name in self.heuristic_names:
                weights[name] = random.uniform(0, 5.0)
            
            result = self.evaluate_weights(weights)
            results.append(result)
            self.history.append(result)
            
            print(f"Iteration {i+1}/{iterations}: {result}")
        
        return results
    
    def grid_search(self, weight_ranges: Dict[str, List[float]]) -> List[OptimizationResult]:
        """Grid search over specified weight ranges"""
        print("Starting grid search...")
        
        # Generate all combinations
        import itertools
        
        keys = list(weight_ranges.keys())
        values = [weight_ranges[key] for key in keys]
        combinations = list(itertools.product(*values))
        
        print(f"Testing {len(combinations)} weight combinations...")
        
        results = []
        for i, combo in enumerate(combinations):
            weights = dict(zip(keys, combo))
            # Set unspecified weights to 0
            for name in self.heuristic_names:
                if name not in weights:
                    weights[name] = 0.0
            
            result = self.evaluate_weights(weights)
            results.append(result)
            self.history.append(result)
            
            print(f"Combination {i+1}/{len(combinations)}: {result}")
        
        return results
    
    def genetic_algorithm(self, population_size: int = 20, generations: int = 50, 
                         mutation_rate: float = 0.1, elite_size: int = 4) -> List[OptimizationResult]:
        """Genetic algorithm optimization"""
        print(f"Starting genetic algorithm: {population_size} individuals, {generations} generations...")
        
        # Initialize population
        population = []
        for _ in range(population_size):
            weights = {}
            for name in self.heuristic_names:
                weights[name] = random.uniform(0, 5.0)
            population.append(weights)
        
        best_results = []
        
        for generation in range(generations):
            print(f"Generation {generation + 1}/{generations}")
            
            # Evaluate population
            results = []
            for weights in population:
                result = self.evaluate_weights(weights)
                results.append(result)
                self.history.append(result)
            
            # Sort by fitness (win rate)
            results.sort(key=lambda x: x.win_rate, reverse=True)
            best_results.append(results[0])
            
            print(f"  Best: {results[0]}")
            print(f"  Avg:  Win Rate: {np.mean([r.win_rate for r in results]):.1f}%")
            
            # Create next generation
            new_population = []
            
            # Keep elite
            for i in range(elite_size):
                new_population.append(results[i].weights.copy())
            
            # Crossover and mutation
            while len(new_population) < population_size:
                # Tournament selection
                parent1 = self._tournament_selection(results)
                parent2 = self._tournament_selection(results)
                
                # Crossover
                child = self._crossover(parent1.weights, parent2.weights)
                
                # Mutation
                if random.random() < mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population
        
        return best_results
    
    def _tournament_selection(self, results: List[OptimizationResult], tournament_size: int = 3):
        """Tournament selection for genetic algorithm"""
        tournament = random.sample(results, min(tournament_size, len(results)))
        return max(tournament, key=lambda x: x.win_rate)
    
    def _crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Dict[str, float]:
        """Crossover operation for genetic algorithm"""
        child = {}
        for name in self.heuristic_names:
            if random.random() < 0.5:
                child[name] = parent1[name]
            else:
                child[name] = parent2[name]
        return child
    
    def _mutate(self, weights: Dict[str, float], mutation_strength: float = 0.5) -> Dict[str, float]:
        """Mutation operation for genetic algorithm"""
        mutated = weights.copy()
        for name in self.heuristic_names:
            if random.random() < 0.3:  # 30% chance to mutate each weight
                mutated[name] += random.gauss(0, mutation_strength)
                mutated[name] = max(0, mutated[name])  # Keep non-negative
        return mutated
    
    def bayesian_optimization(self, iterations: int = 50):
        """Bayesian optimization using Gaussian Process (simplified version)"""
        print(f"Starting Bayesian optimization with {iterations} iterations...")
        
        # Start with some random samples
        n_initial = 10
        for i in range(n_initial):
            weights = {}
            for name in self.heuristic_names:
                weights[name] = random.uniform(0, 5.0)
            
            result = self.evaluate_weights(weights)
            self.history.append(result)
            print(f"Initial sample {i+1}/{n_initial}: {result}")
        
        # For remaining iterations, use simple exploration-exploitation strategy
        for i in range(n_initial, iterations):
            if random.random() < 0.3:  # 30% exploration
                weights = {}
                for name in self.heuristic_names:
                    weights[name] = random.uniform(0, 5.0)
            else:  # 70% exploitation - modify best weights
                weights = self.best_result.weights.copy()
                # Add some noise
                for name in self.heuristic_names:
                    weights[name] += random.gauss(0, 0.3)
                    weights[name] = max(0, weights[name])
            
            result = self.evaluate_weights(weights)
            self.history.append(result)
            print(f"Iteration {i+1}/{iterations}: {result}")
        
        return self.history[-iterations:]
    
    def save_results(self, filename: str):
        """Save optimization history to JSON file"""
        data = {
            'best_result': {
                'weights': self.best_result.weights,
                'win_rate': self.best_result.win_rate,
                'avg_score': self.best_result.avg_score,
                'avg_max_tile': self.best_result.avg_max_tile,
                'avg_moves': self.best_result.avg_moves,
                'games_played': self.best_result.games_played
            },
            'history': []
        }
        
        for result in self.history:
            data['history'].append({
                'weights': result.weights,
                'win_rate': result.win_rate,
                'avg_score': result.avg_score,
                'avg_max_tile': result.avg_max_tile,
                'avg_moves': result.avg_moves,
                'games_played': result.games_played
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Results saved to {filename}")
    
    def load_results(self, filename: str):
        """Load optimization history from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load best result
        best_data = data['best_result']
        self.best_result = OptimizationResult(
            weights=best_data['weights'],
            win_rate=best_data['win_rate'],
            avg_score=best_data['avg_score'],
            avg_max_tile=best_data['avg_max_tile'],
            avg_moves=best_data['avg_moves'],
            games_played=best_data['games_played']
        )
        
        # Load history
        self.history = []
        for result_data in data['history']:
            result = OptimizationResult(
                weights=result_data['weights'],
                win_rate=result_data['win_rate'],
                avg_score=result_data['avg_score'],
                avg_max_tile=result_data['avg_max_tile'],
                avg_moves=result_data['avg_moves'],
                games_played=result_data['games_played']
            )
            self.history.append(result)
        
        print(f"Loaded {len(self.history)} results from {filename}")
        print(f"Best result: {self.best_result}")

def main():
    """Example usage of the optimizer"""
    optimizer = WeightOptimizer(games_per_eval=30)
    
    print("=== 2048 Weight Optimization ===")
    print("Choose optimization method:")
    print("1. Random Search")
    print("2. Grid Search")
    print("3. Genetic Algorithm")
    print("4. Bayesian Optimization")
    print("5. Load previous results")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        iterations = int(input("Number of iterations (default 50): ") or "50")
        optimizer.random_search(iterations)
    
    elif choice == "2":
        print("Grid search on key weights...")
        weight_ranges = {
            'monotonicity': [0.5, 1.0, 1.5, 2.0],
            'smoothness': [0.0, 0.1, 0.2, 0.3],
            'empty': [1.0, 2.0, 2.7, 3.0, 4.0],
            'merge': [0.5, 1.0, 1.5, 2.0]
        }
        optimizer.grid_search(weight_ranges)
    
    elif choice == "3":
        generations = int(input("Number of generations (default 20): ") or "20")
        optimizer.genetic_algorithm(generations=generations)
    
    elif choice == "4":
        iterations = int(input("Number of iterations (default 30): ") or "30")
        optimizer.bayesian_optimization(iterations)
    
    elif choice == "5":
        filename = input("Filename to load: ").strip()
        optimizer.load_results(filename)
    
    # Save results
    save_file = input("Save results to file (default: optimization_results.json): ").strip()
    if not save_file:
        save_file = "optimization_results.json"
    
    optimizer.save_results(save_file)
    
    print(f"\n=== Final Results ===")
    print(f"Best configuration found:")
    print(f"Weights: {optimizer.best_result.weights}")
    print(f"Performance: {optimizer.best_result}")

if __name__ == "__main__":
    main()
