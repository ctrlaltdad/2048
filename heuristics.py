import random
import numpy as np
from game_2048 import Game2048

MOVES = ['up', 'down', 'left', 'right']

def heuristic_move_corner(game):
    for move in ['down', 'left', 'right', 'up']:
        temp = game.copy()
        if temp.move_tiles(move):
            return move
    return random.choice(MOVES)

def heuristic_move_center(game):
    for move in ['down', 'right', 'up', 'left']:
        temp = game.copy()
        if temp.move_tiles(move):
            return move
    return random.choice(MOVES)

def heuristic_move_expectimax(game):
    best_move = None
    best_score = -float('inf')
    for move in MOVES:
        temp = game.copy()
        if not temp.move_tiles(move):
            continue
        empty = np.argwhere(temp.board == 0)
        if len(empty) == 0:
            score = np.max(temp.board)
        else:
            score = 0
            for i, j in empty:
                for val, prob in [(2, 0.9), (4, 0.1)]:
                    temp2 = temp.copy()
                    temp2.board[i, j] = val
                    score += prob * np.max(temp2.board)
            score /= len(empty)
        if score > best_score:
            best_score = score
            best_move = move
    if best_move is not None:
        return best_move
    return random.choice(MOVES)

def simulate_heuristic(heuristic, runs=50):
    from tqdm import tqdm
    tiles = []
    scores = []
    for _ in tqdm(range(runs), desc=f"Heuristic: {heuristic}"):
        game = Game2048()
        while not game.is_game_over() and not game.has_won():
            if heuristic == 'corner':
                move = heuristic_move_corner(game)
            elif heuristic == 'center':
                move = heuristic_move_center(game)
            elif heuristic == 'expectimax':
                move = heuristic_move_expectimax(game)
            else:
                move = random.choice(MOVES)
            game.move_tiles(move)
        board, score = game.get_state()
        tiles.append(np.max(board))
        scores.append(score)
    return tiles, scores
