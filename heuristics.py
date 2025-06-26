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

def heuristic_move_opportunistic(game):
    # Try to find a move that will combine any tiles
    for move in MOVES:
        temp = game.copy()
        if temp.move_tiles(move):
            # If the move increases the score, it combined tiles
            _, score_before = game.get_state()
            _, score_after = temp.get_state()
            if score_after > score_before:
                return move
    # Otherwise, fall back to corner strategy
    return heuristic_move_corner(game)

def heuristic_move_monotonicity(game):
    best_move = None
    best_score = -float('inf')
    for move in MOVES:
        temp = game.copy()
        if not temp.move_tiles(move):
            continue
        board = temp.board
        max_tile = np.max(board)
        # Monotonicity (favor left and up)
        mono_left = sum(monotonicity_score(row) for row in board)
        mono_up = sum(monotonicity_score(col) for col in board.T)
        mono = 4 * (mono_left + mono_up)
        # Smoothness (penalize big differences)
        smoothness = -np.sum(np.abs(np.diff(board, axis=0))) - np.sum(np.abs(np.diff(board, axis=1)))
        # Grouping
        grouping = grouping_score(board)
        # Corner bonus/penalty
        in_corner = max_tile in [board[0,0], board[0,-1], board[-1,0], board[-1,-1]]
        corner_bonus = 40 if in_corner else -40
        # Empty tile bonus
        empty_bonus = 0.2 * np.count_nonzero(board == 0)
        # Adjacency of max and second max
        second_max = np.partition(board.flatten(), -2)[-2]
        adj_penalty = -20
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                if board[i, j] == max_tile:
                    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ni, nj = i+di, j+dj
                        if 0 <= ni < board.shape[0] and 0 <= nj < board.shape[1]:
                            if board[ni, nj] == second_max:
                                adj_penalty = 0
        # Total score
        score = mono + smoothness + grouping + corner_bonus + empty_bonus + adj_penalty
        if score > best_score:
            best_score = score
            best_move = move
    if best_move is not None:
        return best_move
    return random.choice(MOVES)

def monotonicity_score(arr):
    # Returns a score for monotonicity: higher is better
    inc = sum(arr[i] <= arr[i+1] for i in range(len(arr)-1))
    dec = sum(arr[i] >= arr[i+1] for i in range(len(arr)-1))
    return max(inc, dec)

def grouping_score(board):
    # Reward moves that keep large tiles next to each other, and small tiles together
    score = 0
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            val = board[i, j]
            if val == 0:
                continue
            # Check neighbors
            for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni, nj = i+di, j+dj
                if 0 <= ni < board.shape[0] and 0 <= nj < board.shape[1]:
                    nval = board[ni, nj]
                    if nval == 0:
                        continue
                    # Reward if both are large or both are small
                    if (val >= 128 and nval >= 128) or (val <= 8 and nval <= 8):
                        score += 1
    return score

def is_isolated_large_tile(board, threshold=256):
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            val = board[i, j]
            if val >= threshold:
                neighbors = [board[x, y] for x, y in [
                    (i-1,j), (i+1,j), (i,j-1), (i,j+1)
                ] if 0 <= x < board.shape[0] and 0 <= y < board.shape[1]]
                if all(n < threshold/2 for n in neighbors if n > 0):
                    return True
    return False

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
            elif heuristic == 'opportunistic':
                move = heuristic_move_opportunistic(game)
            elif heuristic == 'monotonicity':
                move = heuristic_move_monotonicity(game)
            else:
                move = random.choice(MOVES)
            game.move_tiles(move)
        board, score = game.get_state()
        tiles.append(np.max(board))
        scores.append(score)
    return tiles, scores

def simulate_two_phase_heuristic(heur1, heur2, runs=50, switch_tile=512):
    """
    Run each game with heur1 until a tile >= switch_tile is reached, then switch to heur2.
    Returns: list of final tiles, list of final scores
    """
    from tqdm import tqdm
    tiles = []
    scores = []
    for _ in tqdm(range(runs), desc=f"2-Phase: {heur1}->{heur2}"):
        game = Game2048()
        phase = 1
        while not game.is_game_over() and not game.has_won():
            board, _ = game.get_state()
            max_tile = np.max(board)
            if phase == 1 and max_tile >= switch_tile:
                phase = 2
            if phase == 1:
                if heur1 == 'corner':
                    move = heuristic_move_corner(game)
                elif heur1 == 'center':
                    move = heuristic_move_center(game)
                elif heur1 == 'expectimax':
                    move = heuristic_move_expectimax(game)
                elif heur1 == 'opportunistic':
                    move = heuristic_move_opportunistic(game)
                elif heur1 == 'monotonicity':
                    move = heuristic_move_monotonicity(game)
                else:
                    move = random.choice(MOVES)
            else:
                if heur2 == 'corner':
                    move = heuristic_move_corner(game)
                elif heur2 == 'center':
                    move = heuristic_move_center(game)
                elif heur2 == 'expectimax':
                    move = heuristic_move_expectimax(game)
                elif heur2 == 'opportunistic':
                    move = heuristic_move_opportunistic(game)
                elif heur2 == 'monotonicity':
                    move = heuristic_move_monotonicity(game)
                else:
                    move = random.choice(MOVES)
            game.move_tiles(move)
        board, score = game.get_state()
        tiles.append(np.max(board))
        scores.append(score)
    return tiles, scores
