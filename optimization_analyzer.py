"""
ML Optimization Analysis and Visualization

This script provides tools to analyze and visualize the results from weight optimization
experiments, helping to understand which combinations work best for reaching 2048.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List, Optional
import argparse
from pathlib import Path

class OptimizationAnalyzer:
    """Analyzer for ML optimization results"""
    
    def __init__(self, results_file: str):
        """Load optimization results from JSON file"""
        self.results_file = results_file
        self.results = []
        self.best_result = None
        self.load_results()
    
    def load_results(self):
        """Load results from JSON file"""
        try:
            with open(self.results_file, 'r') as f:
                data = json.load(f)
            
            if 'best_result' in data:
                self.best_result = data['best_result']
            
            if 'history' in data:
                self.results = data['history']
            else:
                self.results = data  # Assume it's just a list of results
                
            print(f"Loaded {len(self.results)} optimization results")
            if self.best_result:
                print(f"Best result: Win Rate {self.best_result['win_rate']:.1f}%")
        
        except FileNotFoundError:
            print(f"Results file {self.results_file} not found")
        except Exception as e:
            print(f"Error loading results: {e}")
    
    def analyze_convergence(self, save_plot: bool = True):
        """Analyze and plot convergence over iterations"""
        if not self.results:
            print("No results to analyze")
            return
        
        # Extract win rates over time
        win_rates = [result['win_rate'] for result in self.results]
        
        # Calculate running best
        running_best = []
        best_so_far = 0
        for rate in win_rates:
            if rate > best_so_far:
                best_so_far = rate
            running_best.append(best_so_far)
        
        # Plot convergence
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(win_rates, alpha=0.7, label='Win Rate per Iteration')
        plt.plot(running_best, 'r-', linewidth=2, label='Best So Far')
        plt.xlabel('Iteration')
        plt.ylabel('Win Rate (%)')
        plt.title('Optimization Convergence')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot histogram of results
        plt.subplot(1, 2, 2)
        plt.hist(win_rates, bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Win Rate (%)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Win Rates')
        plt.axvline(np.mean(win_rates), color='r', linestyle='--', label=f'Mean: {np.mean(win_rates):.1f}%')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plot:
            plt.savefig('optimization_convergence.png', dpi=300, bbox_inches='tight')
            print("Convergence plot saved as 'optimization_convergence.png'")
        plt.show()
    
    def analyze_weights_correlation(self, save_plot: bool = True):
        """Analyze correlation between weights and performance"""
        if not self.results:
            print("No results to analyze")
            return
        
        # Create DataFrame
        data = []
        for result in self.results:
            row = result['weights'].copy()
            row['win_rate'] = result['win_rate']
            row['avg_score'] = result['avg_score']
            row['avg_max_tile'] = result['avg_max_tile']
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Correlation with win rate
        weight_columns = [col for col in df.columns if col not in ['win_rate', 'avg_score', 'avg_max_tile']]
        correlations = df[weight_columns + ['win_rate']].corr()['win_rate'].drop('win_rate')
        
        # Plot correlations
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        correlations.plot(kind='bar')
        plt.title('Weight Correlation with Win Rate')
        plt.xlabel('Heuristic Weights')
        plt.ylabel('Correlation')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Heatmap of weight correlations
        plt.subplot(2, 2, 2)
        weight_corr = df[weight_columns].corr()
        sns.heatmap(weight_corr, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        plt.title('Weight Inter-correlations')
        
        # Top performers analysis
        top_10_percent = df.nlargest(int(len(df) * 0.1), 'win_rate')
        
        plt.subplot(2, 2, 3)
        top_weights_mean = top_10_percent[weight_columns].mean()
        all_weights_mean = df[weight_columns].mean()
        
        x = range(len(weight_columns))
        width = 0.35
        plt.bar([i - width/2 for i in x], all_weights_mean, width, label='All Results', alpha=0.7)
        plt.bar([i + width/2 for i in x], top_weights_mean, width, label='Top 10%', alpha=0.7)
        plt.xlabel('Heuristic Weights')
        plt.ylabel('Average Weight Value')
        plt.title('Weight Comparison: All vs Top 10%')
        plt.xticks(x, weight_columns, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Scatter plot of key weights vs performance
        plt.subplot(2, 2, 4)
        # Find the weight with highest correlation
        best_weight = correlations.abs().idxmax()
        plt.scatter(df[best_weight], df['win_rate'], alpha=0.6)
        plt.xlabel(f'{best_weight} Weight')
        plt.ylabel('Win Rate (%)')
        plt.title(f'Win Rate vs {best_weight} Weight')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plot:
            plt.savefig('weight_correlation_analysis.png', dpi=300, bbox_inches='tight')
            print("Weight correlation plot saved as 'weight_correlation_analysis.png'")
        plt.show()
        
        return correlations
    
    def find_pareto_frontier(self):
        """Find Pareto optimal solutions (trade-off between win rate and other metrics)"""
        if not self.results:
            print("No results to analyze")
            return []
        
        pareto_solutions = []
        
        for i, result1 in enumerate(self.results):
            is_dominated = False
            
            for j, result2 in enumerate(self.results):
                if i != j:
                    # Check if result2 dominates result1
                    if (result2['win_rate'] >= result1['win_rate'] and 
                        result2['avg_score'] >= result1['avg_score'] and 
                        (result2['win_rate'] > result1['win_rate'] or result2['avg_score'] > result1['avg_score'])):
                        is_dominated = True
                        break
            
            if not is_dominated:
                pareto_solutions.append(result1)
        
        print(f"Found {len(pareto_solutions)} Pareto optimal solutions")
        return pareto_solutions
    
    def analyze_top_performers(self, top_n: int = 10):
        """Analyze characteristics of top performing weight combinations"""
        if not self.results:
            print("No results to analyze")
            return
        
        # Sort by win rate
        sorted_results = sorted(self.results, key=lambda x: x['win_rate'], reverse=True)
        top_results = sorted_results[:top_n]
        
        print(f"\n=== Top {top_n} Performing Weight Combinations ===")
        for i, result in enumerate(top_results):
            print(f"\nRank {i+1}:")
            print(f"  Win Rate: {result['win_rate']:.1f}%")
            print(f"  Avg Score: {result['avg_score']:.0f}")
            print(f"  Avg Max Tile: {result['avg_max_tile']:.0f}")
            print("  Weights:")
            for weight, value in result['weights'].items():
                if value > 0.1:  # Only show significant weights
                    print(f"    {weight}: {value:.2f}")
        
        # Analyze weight patterns in top performers
        print(f"\n=== Weight Analysis for Top {top_n} Performers ===")
        weight_sums = {}
        for result in top_results:
            for weight, value in result['weights'].items():
                if weight not in weight_sums:
                    weight_sums[weight] = []
                weight_sums[weight].append(value)
        
        for weight, values in weight_sums.items():
            mean_val = np.mean(values)
            std_val = np.std(values)
            print(f"{weight}: {mean_val:.2f} ± {std_val:.2f}")
    
    def generate_recommendations(self):
        """Generate weight recommendations based on analysis"""
        if not self.results:
            print("No results to analyze")
            return {}
        
        # Analyze top 10% of results
        sorted_results = sorted(self.results, key=lambda x: x['win_rate'], reverse=True)
        top_results = sorted_results[:max(1, len(sorted_results) // 10)]
        
        # Calculate average weights for top performers
        recommendations = {}
        weight_names = list(top_results[0]['weights'].keys())
        
        for weight in weight_names:
            values = [result['weights'][weight] for result in top_results]
            recommendations[weight] = {
                'recommended': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        
        print("\n=== Weight Recommendations (based on top 10% performers) ===")
        for weight, stats in recommendations.items():
            print(f"{weight}: {stats['recommended']:.2f} "
                  f"(range: {stats['min']:.2f}-{stats['max']:.2f}, "
                  f"std: {stats['std']:.2f})")
        
        return recommendations
    
    def save_analysis_report(self, output_file: str = "optimization_analysis_report.md"):
        """Generate a comprehensive analysis report"""
        if not self.results:
            print("No results to analyze")
            return
        
        correlations = self.analyze_weights_correlation(save_plot=False)
        recommendations = self.generate_recommendations()
        pareto_solutions = self.find_pareto_frontier()
        
        # Calculate statistics
        win_rates = [r['win_rate'] for r in self.results]
        scores = [r['avg_score'] for r in self.results]
        max_tiles = [r['avg_max_tile'] for r in self.results]
        
        report = f"""# 2048 Weight Optimization Analysis Report

## Summary Statistics
- Total experiments: {len(self.results)}
- Best win rate: {max(win_rates):.1f}%
- Average win rate: {np.mean(win_rates):.1f}% ± {np.std(win_rates):.1f}%
- Best average score: {max(scores):.0f}
- Average score: {np.mean(scores):.0f} ± {np.std(scores):.0f}
- Best average max tile: {max(max_tiles):.0f}

## Weight Correlations with Win Rate
"""
        
        for weight, corr in correlations.items():
            report += f"- {weight}: {corr:.3f}\n"
        
        report += f"""
## Recommended Weights
Based on analysis of top 10% performers:

"""
        
        for weight, stats in recommendations.items():
            report += f"- **{weight}**: {stats['recommended']:.2f} (std: {stats['std']:.2f})\n"
        
        report += f"""
## Key Findings
- Found {len(pareto_solutions)} Pareto optimal solutions
- Weight with highest correlation to win rate: {correlations.abs().idxmax()} ({correlations[correlations.abs().idxmax()]:.3f})
- Weight with lowest correlation to win rate: {correlations.abs().idxmin()} ({correlations[correlations.abs().idxmin()]:.3f})

## Best Configuration
"""
        
        if self.best_result:
            report += f"- Win Rate: {self.best_result['win_rate']:.1f}%\n"
            report += f"- Average Score: {self.best_result['avg_score']:.0f}\n"
            report += f"- Weights:\n"
            for weight, value in self.best_result['weights'].items():
                report += f"  - {weight}: {value:.2f}\n"
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"Analysis report saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze 2048 weight optimization results')
    parser.add_argument('results_file', help='JSON file containing optimization results')
    parser.add_argument('--convergence', action='store_true', help='Generate convergence analysis')
    parser.add_argument('--correlation', action='store_true', help='Generate correlation analysis')
    parser.add_argument('--top', type=int, default=10, help='Number of top performers to analyze')
    parser.add_argument('--report', action='store_true', help='Generate comprehensive report')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    
    args = parser.parse_args()
    
    if not Path(args.results_file).exists():
        print(f"Error: Results file '{args.results_file}' not found")
        return
    
    analyzer = OptimizationAnalyzer(args.results_file)
    
    if args.all or args.convergence:
        analyzer.analyze_convergence()
    
    if args.all or args.correlation:
        analyzer.analyze_weights_correlation()
    
    if args.all or args.top:
        analyzer.analyze_top_performers(args.top)
    
    if args.all or args.report:
        analyzer.save_analysis_report()
    
    # Always show recommendations
    analyzer.generate_recommendations()

if __name__ == "__main__":
    main()
