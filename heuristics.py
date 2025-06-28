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
    def evaluate(board):
        # Weights from ovolve/2048-AI
        smooth_weight = 0.1
        mono_weight = 1.0
        empty_weight = 2.7
        max_weight = 1.0

        def smoothness(b):
            smooth = 0
            for i in range(4):
                for j in range(4):
                    if b[i, j]:
                        v = np.log2(b[i, j])
                        for d in [(1, 0), (0, 1)]:
                            ni, nj = i + d[0], j + d[1]
                            if 0 <= ni < 4 and 0 <= nj < 4 and b[ni, nj]:
                                target = np.log2(b[ni, nj])
                                smooth -= abs(v - target)
            return smooth

        def monotonicity(b):
            totals = [0, 0, 0, 0]
            for i in range(4):
                current = 0
                next = current + 1
                while next < 4:
                    while next < 4 and b[i, next] == 0:
                        next += 1
                    if next >= 4:
                        next -= 1
                    current_value = np.log2(b[i, current]) if b[i, current] else 0
                    next_value = np.log2(b[i, next]) if b[i, next] else 0
                    if current_value > next_value:
                        totals[0] += next_value - current_value
                    elif next_value > current_value:
                        totals[1] += current_value - next_value
                    current = next
                    next += 1
            for j in range(4):
                current = 0
                next = current + 1
                while next < 4:
                    while next < 4 and b[next, j] == 0:
                        next += 1
                    if next >= 4:
                        next -= 1
                    current_value = np.log2(b[current, j]) if b[current, j] else 0
                    next_value = np.log2(b[next, j]) if b[next, j] else 0
                    if current_value > next_value:
                        totals[2] += next_value - current_value
                    elif next_value > current_value:
                        totals[3] += current_value - next_value
                    current = next
                    next += 1
            return max(totals[0], totals[1]) + max(totals[2], totals[3])

        def max_in_corner(b):
            max_tile = np.max(b)
            return 1 if max_tile in [b[0,0], b[0,3], b[3,0], b[3,3]] else 0

        b = board
        return (
            smooth_weight * smoothness(b) +
            mono_weight * monotonicity(b) +
            empty_weight * np.log2(np.count_nonzero(b == 0) + 1) +
            max_weight * max_in_corner(b)
        )

    best_move = None
    best_score = -float('inf')
    for move in MOVES:
        temp = game.copy()
        if not temp.move_tiles(move):
            continue
        score = evaluate(temp.board)
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
