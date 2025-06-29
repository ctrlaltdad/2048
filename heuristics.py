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
            elif heuristic == 'adaptive':
                move = heuristic_move_adaptive(game)
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
                elif heur1 == 'adaptive':
                    move = heuristic_move_adaptive(game)
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
                elif heur2 == 'adaptive':
                    move = heuristic_move_adaptive(game)
                else:
                    move = random.choice(MOVES)
            game.move_tiles(move)
        board, score = game.get_state()
        tiles.append(np.max(board))
        scores.append(score)
    return tiles, scores

class HeuristicEvaluator:
    """
    Evaluator class that provides various heuristic evaluation functions
    and weighted combination strategies for ML optimization.
    """
    
    def __init__(self):
        self.default_weights = {
            'monotonicity': 1.0,
            'corner': 0.0,
            'center': 0.0,
            'expectimax': 0.0,
            'opportunistic': 0.0,
            'smoothness': 0.1,
            'empty': 2.7,
            'merge': 1.0
        }
    
    def eval_monotonicity(self, board):
        """Evaluate monotonicity of the board"""
        score = 0
        
        # Check row monotonicity (both increasing and decreasing)
        for i in range(4):
            row = board[i]
            
            # Check if row is monotonically increasing or decreasing
            increasing = True
            decreasing = True
            
            for j in range(3):
                if row[j] != 0 and row[j+1] != 0:
                    if row[j] > row[j+1]:
                        increasing = False
                    if row[j] < row[j+1]:
                        decreasing = False
            
            # Reward monotonic rows
            if increasing or decreasing:
                score += 100
                # Extra reward for fully filled monotonic rows
                if np.all(row != 0):
                    score += 200
        
        # Check column monotonicity
        for j in range(4):
            col = board[:, j]
            
            increasing = True
            decreasing = True
            
            for i in range(3):
                if col[i] != 0 and col[i+1] != 0:
                    if col[i] > col[i+1]:
                        increasing = False
                    if col[i] < col[i+1]:
                        decreasing = False
            
            if increasing or decreasing:
                score += 100
                if np.all(col != 0):
                    score += 200
        
        return score
    
    def eval_corner(self, board):
        """Evaluate corner strategy"""
        corners = [board[0,0], board[0,3], board[3,0], board[3,3]]
        max_corner = np.max(corners)
        return (max_corner * 2) if max_corner > 0 else 10
    
    def eval_center(self, board):
        """Evaluate center strategy"""
        score = 0
        for i in range(4):
            for j in range(4):
                if i in [1, 2] and j in [1, 2]:
                    score += board[i, j] if board[i, j] > 0 else 5
        return score
    
    def eval_expectimax(self, board):
        """Simplified expectimax evaluation"""
        score = 0
        # Check horizontal merges
        for i in range(4):
            for j in range(3):
                if board[i, j] > 0 and board[i, j] == board[i, j+1]:
                    score += board[i, j] * 2
        
        # Check vertical merges
        for j in range(4):
            for i in range(3):
                if board[i, j] > 0 and board[i, j] == board[i+1, j]:
                    score += board[i, j] * 2
        
        return score
    
    def eval_opportunistic(self, board):
        """Evaluate opportunistic merging"""
        score = 0
        # Check horizontal merges
        for i in range(4):
            for j in range(3):
                if board[i, j] > 0 and board[i, j] == board[i, j+1]:
                    score += board[i, j]
        
        # Check vertical merges
        for j in range(4):
            for i in range(3):
                if board[i, j] > 0 and board[i, j] == board[i+1, j]:
                    score += board[i, j]
        
        return score
    
    def eval_smoothness(self, board):
        """Evaluate smoothness (based on ovolve/2048-AI)"""
        smoothness = 0
        
        for x in range(4):
            for y in range(4):
                if board[x, y] != 0:
                    value = np.log2(board[x, y])
                    
                    # Check right direction
                    right_y = y + 1
                    while right_y < 4 and board[x, right_y] == 0:
                        right_y += 1
                    if right_y < 4:
                        target_value = np.log2(board[x, right_y])
                        smoothness -= abs(value - target_value)
                    
                    # Check down direction
                    down_x = x + 1
                    while down_x < 4 and board[down_x, y] == 0:
                        down_x += 1
                    if down_x < 4:
                        target_value = np.log2(board[down_x, y])
                        smoothness -= abs(value - target_value)
        
        return smoothness
    
    def eval_empty(self, board):
        """Evaluate empty tiles"""
        return np.sum(board == 0) * 100
    
    def eval_merge(self, board):
        """Evaluate merge opportunities"""
        score = 0
        # Check horizontal merges
        for i in range(4):
            for j in range(3):
                if board[i, j] > 0 and board[i, j] == board[i, j+1]:
                    score += board[i, j]
        
        # Check vertical merges
        for j in range(4):
            for i in range(3):
                if board[i, j] > 0 and board[i, j] == board[i+1, j]:
                    score += board[i, j]
        
        return score
    
    def eval_weighted_combo(self, board, weights=None):
        """Evaluate using weighted combination of all heuristics"""
        if weights is None:
            weights = self.default_weights
        
        total_score = 0
        
        # Only calculate scores for heuristics with weight > 0 (efficiency)
        if weights.get('monotonicity', 0) > 0:
            total_score += self.eval_monotonicity(board) * weights['monotonicity']
        
        if weights.get('corner', 0) > 0:
            total_score += self.eval_corner(board) * weights['corner']
        
        if weights.get('center', 0) > 0:
            total_score += self.eval_center(board) * weights['center']
        
        if weights.get('expectimax', 0) > 0:
            total_score += self.eval_expectimax(board) * weights['expectimax']
        
        if weights.get('opportunistic', 0) > 0:
            total_score += self.eval_opportunistic(board) * weights['opportunistic']
        
        if weights.get('smoothness', 0) > 0:
            total_score += self.eval_smoothness(board) * weights['smoothness']
        
        if weights.get('empty', 0) > 0:
            total_score += self.eval_empty(board) * weights['empty']
        
        if weights.get('merge', 0) > 0:
            total_score += self.eval_merge(board) * weights['merge']
        
        return total_score
    
    def pick_weighted_move(self, board, weights=None):
        """Pick the best move using weighted combination of heuristics"""
        if weights is None:
            weights = self.default_weights
        
        best_move = None
        best_score = -float('inf')
        
        for move in MOVES:
            # Simulate the move
            temp_board = board.copy()
            moved = self._simulate_move(temp_board, move)
            
            if moved:
                score = self.eval_weighted_combo(temp_board, weights)
                if score > best_score:
                    best_score = score
                    best_move = move
        
        return best_move
    
    def _simulate_move(self, board, direction):
        """Simulate a move on the board and return if it was valid"""
        old_board = board.copy()
        
        if direction == 'left':
            for i in range(4):
                row = board[i, :]
                new_row = self._merge_line(row)
                board[i, :] = new_row
        elif direction == 'right':
            for i in range(4):
                row = board[i, :]
                new_row = self._merge_line(row[::-1])[::-1]
                board[i, :] = new_row
        elif direction == 'up':
            for j in range(4):
                col = board[:, j]
                new_col = self._merge_line(col)
                board[:, j] = new_col
        elif direction == 'down':
            for j in range(4):
                col = board[:, j]
                new_col = self._merge_line(col[::-1])[::-1]
                board[:, j] = new_col
        
        return not np.array_equal(old_board, board)
    
    def _merge_line(self, line):
        """Merge a single line (used in move simulation)"""
        # Remove zeros
        filtered = line[line != 0]
        
        # Merge adjacent equal tiles
        merged = []
        i = 0
        while i < len(filtered):
            if i < len(filtered) - 1 and filtered[i] == filtered[i + 1]:
                merged.append(filtered[i] * 2)
                i += 2
            else:
                merged.append(filtered[i])
                i += 1
        
        # Pad with zeros to maintain length
        result = np.array(merged + [0] * (4 - len(merged)))
        return result

def heuristic_move_adaptive(game):
    """
    Advanced adaptive heuristic that changes strategy based on game state.
    Uses different strategies for early, mid, and late game phases.
    """
    board, score = game.get_state()
    max_tile = np.max(board)
    empty_count = np.sum(board == 0)
    
    # Determine game phase based on max tile and board density
    if max_tile <= 64:
        # Early game: focus on building and corner positioning
        phase = "early"
    elif max_tile <= 512:
        # Mid game: balance monotonicity and opportunities
        phase = "mid"
    else:
        # Late game: strict monotonicity and preservation
        phase = "late"
    
    # Different strategy per phase
    if phase == "early":
        # Early game: prioritize corner strategy with opportunistic merges
        best_move = None
        best_score = -float('inf')
        
        for move in MOVES:
            temp = game.copy()
            if not temp.move_tiles(move):
                continue
            
            # Score based on corner positioning and merge opportunities
            temp_board, temp_score = temp.get_state()
            score = 0
            
            # Favor keeping largest tile in corner
            corners = [temp_board[0,0], temp_board[0,3], temp_board[3,0], temp_board[3,3]]
            max_corner = np.max(corners)
            if max_corner == np.max(temp_board):
                score += 500
            
            # Reward immediate merges
            if temp_score > game.get_state()[1]:
                score += (temp_score - game.get_state()[1]) * 2
            
            # Prefer moves that maintain empty spaces
            score += np.sum(temp_board == 0) * 50
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else heuristic_move_corner(game)
    
    elif phase == "mid":
        # Mid game: weighted combination with dynamic adjustment
        def evaluate_mid_game(board):
            # Dynamic weights based on current state
            empty_ratio = np.sum(board == 0) / 16.0
            
            # More emphasis on monotonicity as board fills up
            mono_weight = 1.0 + (1.0 - empty_ratio) * 2.0
            smooth_weight = 0.2
            empty_weight = 3.0 * empty_ratio  # Less important when board is full
            merge_weight = 1.5
            
            def monotonicity_advanced(b):
                scores = []
                
                # Check all four directions for monotonicity
                for direction in range(4):
                    score = 0
                    if direction < 2:  # Horizontal
                        for i in range(4):
                            row = b[i] if direction == 0 else b[i][::-1]
                            prev = 0
                            for val in row:
                                if val != 0:
                                    if prev != 0 and val <= prev:
                                        score += 1
                                    prev = val
                    else:  # Vertical
                        for j in range(4):
                            col = b[:, j] if direction == 2 else b[:, j][::-1]
                            prev = 0
                            for val in col:
                                if val != 0:
                                    if prev != 0 and val <= prev:
                                        score += 1
                                    prev = val
                    scores.append(score)
                
                return max(scores)
            
            def smoothness_score(b):
                smooth = 0
                for i in range(4):
                    for j in range(4):
                        if b[i, j] != 0:
                            val = np.log2(b[i, j])
                            for di, dj in [(0, 1), (1, 0)]:
                                ni, nj = i + di, j + dj
                                if 0 <= ni < 4 and 0 <= nj < 4 and b[ni, nj] != 0:
                                    target = np.log2(b[ni, nj])
                                    smooth -= abs(val - target)
                return smooth
            
            def merge_opportunities(b):
                merges = 0
                for i in range(4):
                    for j in range(3):
                        if b[i, j] != 0 and b[i, j] == b[i, j+1]:
                            merges += b[i, j]
                for j in range(4):
                    for i in range(3):
                        if b[i, j] != 0 and b[i, j] == b[i+1, j]:
                            merges += b[i, j]
                return merges
            
            return (
                mono_weight * monotonicity_advanced(board) +
                smooth_weight * smoothness_score(board) +
                empty_weight * np.sum(board == 0) +
                merge_weight * merge_opportunities(board)
            )
        
        best_move = None
        best_score = -float('inf')
        for move in MOVES:
            temp = game.copy()
            if not temp.move_tiles(move):
                continue
            score = evaluate_mid_game(temp.board)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else heuristic_move_monotonicity(game)
    
    else:  # Late game
        # Late game: strict monotonicity with careful preservation
        def evaluate_late_game(board):
            # Very conservative evaluation for endgame
            def strict_monotonicity(b):
                # Check if largest tile is in corner and surrounded properly
                max_val = np.max(b)
                max_positions = np.argwhere(b == max_val)
                
                if len(max_positions) > 1:
                    return -1000  # Multiple max tiles is bad
                
                max_pos = max_positions[0]
                corner_bonus = 0
                
                # Strongly prefer corners
                if tuple(max_pos) in [(0,0), (0,3), (3,0), (3,3)]:
                    corner_bonus = 1000
                
                # Check monotonic decrease from max tile
                mono_score = 0
                i, j = max_pos
                
                # Check all directions from max tile
                directions = [(0,1), (1,0), (0,-1), (-1,0)]
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 4 and 0 <= nj < 4:
                        if b[ni, nj] != 0 and b[ni, nj] <= max_val:
                            mono_score += 100
                        elif b[ni, nj] > max_val:
                            mono_score -= 500  # Penalty for larger neighbor
                
                return corner_bonus + mono_score
            
            def preservation_score(b):
                # Penalty for isolated large tiles
                large_threshold = np.max(b) // 4
                penalty = 0
                
                for i in range(4):
                    for j in range(4):
                        if b[i, j] >= large_threshold:
                            neighbors = []
                            for di, dj in [(0,1), (1,0), (0,-1), (-1,0)]:
                                ni, nj = i + di, j + dj
                                if 0 <= ni < 4 and 0 <= nj < 4:
                                    neighbors.append(b[ni, nj])
                            
                            # Penalty if large tile has no large neighbors
                            if not any(n >= large_threshold//2 for n in neighbors if n > 0):
                                penalty -= 200
                
                return penalty
            
            return (
                strict_monotonicity(board) * 3.0 +
                preservation_score(board) +
                np.sum(board == 0) * 100  # Empty spaces still valuable
            )
        
        best_move = None
        best_score = -float('inf')
        for move in MOVES:
            temp = game.copy()
            if not temp.move_tiles(move):
                continue
            score = evaluate_late_game(temp.board)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else heuristic_move_monotonicity(game)
