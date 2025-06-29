// 2048 Heuristics Module
class Heuristics {
    constructor() {
        this.cache = new Map();
    }

    // Main entry point for picking moves
    pickMove(game, heuristicType, twoPhase = false) {
        if (twoPhase) {
            return this.pickTwoPhaseMove(game, heuristicType);
        }
        
        switch (heuristicType) {
            case 'monotonicity':
                return this.pickMonotonicityMove(game);
            case 'corner':
                return this.pickCornerMove(game);
            case 'center':
                return this.pickCenterMove(game);
            case 'expectimax':
                return this.pickExpectimaxMove(game);
            case 'expectimaxCorner':
                return this.pickBestMove(game, 'expectimaxCorner');
            case 'gradientDescent':
                return this.pickBestMove(game, 'gradientDescent');
            case 'opportunistic':
                return this.pickOpportunisticMove(game);
            case 'smoothness':
                return this.pickSmoothnessMove(game);
            case 'adaptive':
                return this.pickAdaptiveMove(game);
            case 'ultraAdaptive':
                return this.pickUltraAdaptiveMove(game);
            case 'advancedMinimax':
                return this.pickAdvancedMinimaxMove(game);
            case 'weighted':
                return this.pickWeightedMove(game);
            case 'mlsim':
                return this.pickMLSimMove(game);
            default:
                return this.pickRandomMove(game);
        }
    }

    pickTwoPhaseMove(game, heuristicType) {
        // First try monotonicity, if no good move found, use selected heuristic
        let move = this.pickMonotonicityMove(game);
        if (!move || this.evaluateMove(game, move, 'monotonicity') < 50) {
            move = this.pickMove(game, heuristicType, false);
        }
        return move;
    }

    // Monotonicity Heuristic
    evaluateMonotonicity(board) {
        let score = 0;
        
        // Check rows for monotonicity
        for (let i = 0; i < 4; i++) {
            let increasing = true, decreasing = true;
            for (let j = 0; j < 3; j++) {
                if (board[i][j] > board[i][j + 1]) increasing = false;
                if (board[i][j] < board[i][j + 1]) decreasing = false;
            }
            if (increasing || decreasing) score += 100;
        }
        
        // Check columns for monotonicity
        for (let j = 0; j < 4; j++) {
            let increasing = true, decreasing = true;
            for (let i = 0; i < 3; i++) {
                if (board[i][j] > board[i + 1][j]) increasing = false;
                if (board[i][j] < board[i + 1][j]) decreasing = false;
            }
            if (increasing || decreasing) score += 100;
        }
        
        return score;
    }

    pickMonotonicityMove(game) {
        return this.pickBestMove(game, 'monotonicity');
    }

    // Corner Heuristic
    evaluateCorner(board) {
        const maxTile = Math.max(...board.flat());
        const corners = [board[0][0], board[0][3], board[3][0], board[3][3]];
        
        let score = 0;
        if (corners.includes(maxTile)) {
            score += 1000;
        }
        
        // Bonus for keeping larger tiles near corners
        const cornerPositions = [[0,0], [0,3], [3,0], [3,3]];
        const adjacentPositions = [
            [[0,1], [1,0]], [[0,2], [1,3]], 
            [[2,0], [3,1]], [[2,3], [3,2]]
        ];
        
        cornerPositions.forEach((corner, idx) => {
            const [ci, cj] = corner;
            const cornerValue = board[ci][cj];
            if (cornerValue > 0) {
                score += cornerValue * 2;
                
                // Check adjacent positions
                adjacentPositions[idx].forEach(([ai, aj]) => {
                    if (board[ai][aj] > 0 && board[ai][aj] <= cornerValue) {
                        score += board[ai][aj];
                    }
                });
            }
        });
        
        return score;
    }

    pickCornerMove(game) {
        return this.pickBestMove(game, 'corner');
    }

    // Center Heuristic
    evaluateCenter(board) {
        const centerTiles = [board[1][1], board[1][2], board[2][1], board[2][2]];
        let score = centerTiles.reduce((sum, tile) => sum + tile * 2, 0);
        
        // Additional bonus for larger tiles in center
        centerTiles.forEach(tile => {
            if (tile >= 128) score += tile;
        });
        
        return score;
    }

    pickCenterMove(game) {
        return this.pickBestMove(game, 'center');
    }

    // Expectimax Heuristic
    evaluateExpectimax(board, depth = 2) {
        if (depth === 0) return this.evaluateBoard(board);
        
        const moves = ['up', 'down', 'left', 'right'];
        let bestScore = -Infinity;
        
        for (let moveDir of moves) {
            const tempGame = new Game2048();
            tempGame.board = board.map(row => [...row]);
            
            if (tempGame.move(moveDir)) {
                // Remove the auto-added tile for expectimax calculation
                const emptyPositions = [];
                for (let i = 0; i < 4; i++) {
                    for (let j = 0; j < 4; j++) {
                        if (tempGame.board[i][j] === 0) {
                            emptyPositions.push([i, j]);
                        }
                    }
                }
                
                if (emptyPositions.length > 0) {
                    let expectedScore = 0;
                    emptyPositions.forEach(([i, j]) => {
                        // Try placing 2 (90% probability)
                        tempGame.board[i][j] = 2;
                        expectedScore += 0.9 * this.evaluateExpectimax(tempGame.board, depth - 1);
                        
                        // Try placing 4 (10% probability)
                        tempGame.board[i][j] = 4;
                        expectedScore += 0.1 * this.evaluateExpectimax(tempGame.board, depth - 1);
                        
                        tempGame.board[i][j] = 0;
                    });
                    expectedScore /= emptyPositions.length;
                    bestScore = Math.max(bestScore, expectedScore);
                }
            }
        }
        
        return bestScore;
    }

    pickExpectimaxMove(game) {
        return this.pickBestMove(game, 'expectimax');
    }

    // High-performance proven strategy: Expectimax with corner bias
    evaluateExpectimaxCorner(board, depth = 2) {
        if (depth === 0) {
            return this.evaluateCornerOptimized(board);
        }
        
        const moves = ['up', 'down', 'left', 'right'];
        let bestScore = -Infinity;
        
        for (let moveDir of moves) {
            const tempGame = new Game2048();
            tempGame.board = board.map(row => [...row]);
            
            if (tempGame.move(moveDir)) {
                // Simulate tile placement more efficiently - only test a few positions
                const emptyPositions = [];
                for (let i = 0; i < 4; i++) {
                    for (let j = 0; j < 4; j++) {
                        if (tempGame.board[i][j] === 0) {
                            emptyPositions.push([i, j]);
                        }
                    }
                }
                
                if (emptyPositions.length > 0) {
                    let expectedScore = 0;
                    // Limit to maximum 4 positions to test for performance
                    const positionsToTest = emptyPositions.slice(0, Math.min(4, emptyPositions.length));
                    
                    positionsToTest.forEach(([i, j]) => {
                        // 90% chance of 2, 10% chance of 4
                        tempGame.board[i][j] = 2;
                        expectedScore += 0.9 * this.evaluateExpectimaxCorner(tempGame.board, depth - 1);
                        
                        tempGame.board[i][j] = 4;
                        expectedScore += 0.1 * this.evaluateExpectimaxCorner(tempGame.board, depth - 1);
                        
                        tempGame.board[i][j] = 0;
                    });
                    
                    expectedScore /= positionsToTest.length;
                    bestScore = Math.max(bestScore, expectedScore);
                }
            }
        }
        
        return bestScore;
    }

    evaluateCornerOptimized(board) {
        let score = 0;
        
        // Heavily favor keeping max tile in corner
        const maxTile = Math.max(...board.flat());
        const corners = [board[0][0], board[0][3], board[3][0], board[3][3]];
        if (corners.includes(maxTile)) {
            score += maxTile * 10;
        }
        
        // Prefer bottom-left corner specifically (proven effective)
        if (board[3][0] === maxTile) {
            score += maxTile * 5;
        }
        
        // Snake pattern bonus (left-to-right on bottom, right-to-left on top)
        score += this.evaluateSnakeOptimized(board) * 1000;
        
        // Empty cell bonus
        const emptyCount = board.flat().filter(x => x === 0).length;
        score += emptyCount * 135;
        
        // Monotonicity bonus
        score += this.evaluateMonotonicity(board) * 10;
        
        // Smoothness bonus
        score += this.evaluateSmoothness(board) * 3;
        
        return score;
    }

    evaluateSnakeOptimized(board) {
        // Bottom-left snake pattern (highly effective for 2048)
        const snakeOrder = [
            [3,0], [3,1], [3,2], [3,3],  // Bottom row: left to right
            [2,3], [2,2], [2,1], [2,0],  // Third row: right to left
            [1,0], [1,1], [1,2], [1,3],  // Second row: left to right
            [0,3], [0,2], [0,1], [0,0]   // Top row: right to left
        ];
        
        let score = 0;
        let prevValue = Infinity;
        
        for (let [i, j] of snakeOrder) {
            const value = board[i][j];
            if (value > 0) {
                // Prefer decreasing values along snake
                if (value <= prevValue) {
                    score += Math.log2(value + 1) * value;
                } else {
                    score -= Math.log2(value + 1) * value * 0.5;
                }
                prevValue = value;
            }
        }
        
        return score;
    }

    // Gradient descent strategy
    evaluateGradientDescent(board) {
        let score = 0;
        
        // Prefer larger values in specific corner (bottom-left optimized weights)
        const weights = [
            [2,  1, 0.5, 0.25],
            [4,  2, 1,   0.5],
            [8,  4, 2,   1],
            [16, 8, 4,   2]
        ];
        
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                if (board[i][j] > 0) {
                    score += board[i][j] * weights[i][j];
                }
            }
        }
        
        // Additional bonuses
        score += this.evaluateMonotonicity(board) * 100;
        const emptyCount = board.flat().filter(x => x === 0).length;
        score += emptyCount * 150;
        
        return score;
    }

    // Opportunistic Heuristic
    evaluateOpportunistic(board) {
        let score = 0;
        
        // Count potential horizontal merges
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 3; j++) {
                if (board[i][j] === board[i][j + 1] && board[i][j] > 0) {
                    score += board[i][j] * 2;
                }
            }
        }
        
        // Count potential vertical merges
        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 3; i++) {
                if (board[i][j] === board[i + 1][j] && board[i][j] > 0) {
                    score += board[i][j] * 2;
                }
            }
        }
        
        // Bonus for empty spaces
        const emptyCount = board.flat().filter(cell => cell === 0).length;
        score += emptyCount * 50;
        
        return score;
    }

    pickOpportunisticMove(game) {
        return this.pickBestMove(game, 'opportunistic');
    }

    // Smoothness Heuristic
    evaluateSmoothness(board) {
        let smoothness = 0;
        
        // Calculate smoothness for rows
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 3; j++) {
                if (board[i][j] !== 0 && board[i][j + 1] !== 0) {
                    smoothness -= Math.abs(Math.log2(board[i][j]) - Math.log2(board[i][j + 1]));
                }
            }
        }
        
        // Calculate smoothness for columns
        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 3; i++) {
                if (board[i][j] !== 0 && board[i + 1][j] !== 0) {
                    smoothness -= Math.abs(Math.log2(board[i][j]) - Math.log2(board[i + 1][j]));
                }
            }
        }
        
        return smoothness * 10; // Scale factor
    }

    pickSmoothnessMove(game) {
        return this.pickBestMove(game, 'smoothness');
    }

    // Adaptive Heuristic (changes strategy based on game phase)
    evaluateAdaptive(board) {
        const maxTile = Math.max(...board.flat());
        const emptyCount = board.flat().filter(x => x === 0).length;
        
        let score = 0;
        
        // Early game (max tile < 128): focus on merging
        if (maxTile < 128) {
            score += this.evaluateOpportunistic(board) * 2;
            score += emptyCount * 50;
        }
        // Mid game (128 <= max tile < 1024): balance merging and positioning
        else if (maxTile < 1024) {
            score += this.evaluateMonotonicity(board) * 1.5;
            score += this.evaluateCorner(board) * 0.8;
            score += this.evaluateOpportunistic(board) * 1.2;
        }
        // Late game (max tile >= 1024): focus on corner and monotonicity
        else {
            score += this.evaluateMonotonicity(board) * 2;
            score += this.evaluateCorner(board) * 2;
            score += this.evaluateSmoothness(board) * 0.5;
        }
        
        return score;
    }

    pickAdaptiveMove(game) {
        return this.pickBestMove(game, 'adaptive');
    }

    // Ultra-Adaptive Heuristic (advanced phase detection)
    evaluateUltraAdaptive(board) {
        const maxTile = Math.max(...board.flat());
        const emptyCount = board.flat().filter(x => x === 0).length;
        
        let score = 0;
        
        // Determine game phase based on multiple factors
        const earlyPhase = maxTile < 64 || emptyCount > 10;
        const midPhase = (maxTile >= 64 && maxTile < 512) || (emptyCount <= 10 && emptyCount > 4);
        const latePhase = maxTile >= 512 || emptyCount <= 4;
        const endGamePhase = maxTile >= 1024 || emptyCount <= 2;
        
        if (earlyPhase) {
            // Focus on building and maintaining options
            score += this.evaluateOpportunistic(board) * 2.5;
            score += emptyCount * 100;
            score += this.evaluateCenter(board) * 0.5;
        } else if (midPhase) {
            // Transition to structured play
            score += this.evaluateMonotonicity(board) * 1.8;
            score += this.evaluateOpportunistic(board) * 1.5;
            score += this.evaluateCorner(board) * 1.2;
            score += this.evaluateSmoothness(board) * 0.8;
        } else if (latePhase && !endGamePhase) {
            // Structured play with corner strategy
            score += this.evaluateCorner(board) * 2.5;
            score += this.evaluateMonotonicity(board) * 2.0;
            score += this.evaluateSmoothness(board) * 1.0;
            score += emptyCount * 150;
        } else if (endGamePhase) {
            // Survival mode
            score += this.evaluateCorner(board) * 3.0;
            score += this.evaluateMonotonicity(board) * 2.5;
            score += emptyCount * 200;
            // Add expectimax for critical decisions
            score += this.evaluateExpectimax(board, 1) * 0.5;
        }
        
        return score;
    }

    pickUltraAdaptiveMove(game) {
        return this.pickBestMove(game, 'ultraAdaptive');
    }

    // Advanced Minimax with alpha-beta pruning
    evaluateAdvancedMinimax(board, depth = 3, alpha = -Infinity, beta = Infinity, maximizingPlayer = true) {
        if (depth === 0) {
            return this.evaluateAdvancedPosition(board);
        }
        
        if (maximizingPlayer) {
            let maxEval = -Infinity;
            const moves = ['up', 'down', 'left', 'right'];
            
            for (let move of moves) {
                const tempGame = new Game2048();
                tempGame.board = board.map(row => [...row]);
                
                if (tempGame.move(move)) {
                    let evaluation = this.evaluateAdvancedMinimax(tempGame.board, depth - 1, alpha, beta, false);
                    maxEval = Math.max(maxEval, evaluation);
                    alpha = Math.max(alpha, evaluation);
                    if (beta <= alpha) break; // Alpha-beta pruning
                }
            }
            return maxEval;
        } else {
            let minEval = Infinity;
            // Simulate random tile placement
            const emptyPositions = [];
            for (let i = 0; i < 4; i++) {
                for (let j = 0; j < 4; j++) {
                    if (board[i][j] === 0) {
                        emptyPositions.push([i, j]);
                    }
                }
            }
            
            for (let [i, j] of emptyPositions) {
                // Try placing 2 (90% probability) and 4 (10% probability)
                for (let value of [2, 4]) {
                    const newBoard = board.map(row => [...row]);
                    newBoard[i][j] = value;
                    
                    let evaluation = this.evaluateAdvancedMinimax(newBoard, depth - 1, alpha, beta, true);
                    if (value === 2) evaluation *= 0.9;
                    else evaluation *= 0.1;
                    
                    minEval = Math.min(minEval, evaluation);
                    beta = Math.min(beta, evaluation);
                    if (beta <= alpha) break;
                }
                if (beta <= alpha) break;
            }
            return minEval;
        }
    }

    evaluateAdvancedPosition(board) {
        let score = 0;
        
        // Snake pattern evaluation
        score += this.evaluateSnakePattern(board) * 1000;
        
        // Standard metrics
        score += this.evaluateMonotonicity(board) * 100;
        score += this.evaluateCorner(board) * 50;
        score += this.evaluateSmoothness(board) * 30;
        
        // Empty tiles
        const emptyCount = board.flat().filter(x => x === 0).length;
        score += emptyCount * 100;
        
        return score;
    }

    evaluateSnakePattern(board) {
        // Check for snake-like patterns (alternating directions)
        const patterns = [
            // Top-left to bottom-right snake
            [[0,0],[0,1],[0,2],[0,3],[1,3],[1,2],[1,1],[1,0],[2,0],[2,1],[2,2],[2,3],[3,3],[3,2],[3,1],[3,0]],
            // Top-right to bottom-left snake
            [[0,3],[0,2],[0,1],[0,0],[1,0],[1,1],[1,2],[1,3],[2,3],[2,2],[2,1],[2,0],[3,0],[3,1],[3,2],[3,3]]
        ];
        
        let bestScore = 0;
        
        for (let pattern of patterns) {
            let score = 0;
            let prevValue = 0;
            
            for (let [i, j] of pattern) {
                const value = board[i][j];
                if (value > 0) {
                    if (prevValue === 0 || value <= prevValue) {
                        score += Math.log2(value + 1);
                    } else {
                        score -= Math.log2(value + 1) * 0.5; // Penalty for increasing values
                    }
                    prevValue = value;
                }
            }
            
            bestScore = Math.max(bestScore, score);
        }
        
        return bestScore;
    }

    pickAdvancedMinimaxMove(game) {
        return this.pickBestMove(game, 'advancedMinimax');
    }

    // Weighted Combination Strategy
    evaluateWeighted(board, customWeights = null) {
        const weights = customWeights || this.getDefaultWeights();
        
        let totalScore = 0;
        
        if (weights.monotonicity > 0) {
            totalScore += this.evaluateMonotonicity(board) * weights.monotonicity;
        }
        
        if (weights.corner > 0) {
            totalScore += this.evaluateCorner(board) * weights.corner;
        }
        
        if (weights.center > 0) {
            totalScore += this.evaluateCenter(board) * weights.center;
        }
        
        if (weights.expectimax > 0) {
            totalScore += this.evaluateExpectimax(board, 1) * weights.expectimax;
        }
        
        if (weights.opportunistic > 0) {
            totalScore += this.evaluateOpportunistic(board) * weights.opportunistic;
        }
        
        if (weights.smoothness > 0) {
            totalScore += this.evaluateSmoothness(board) * weights.smoothness;
        }
        
        if (weights.empty > 0) {
            const emptyCount = board.flat().filter(x => x === 0).length;
            totalScore += emptyCount * 100 * weights.empty;
        }
        
        if (weights.merge > 0) {
            let mergeScore = 0;
            for (let i = 0; i < 4; i++) {
                for (let j = 0; j < 3; j++) {
                    if (board[i][j] && board[i][j] === board[i][j + 1]) {
                        mergeScore += board[i][j];
                    }
                    if (board[j][i] && board[j][i] === board[j + 1] && board[j + 1]) {
                        mergeScore += board[j][i];
                    }
                }
            }
            totalScore += mergeScore * weights.merge;
        }
        
        return totalScore;
    }

    getDefaultWeights() {
        return {
            monotonicity: 1.0,
            corner: 1.5,
            center: 0.0,
            expectimax: 0.5,
            opportunistic: 1.0,
            smoothness: 0.1,
            empty: 2.7,
            merge: 1.0
        };
    }

    setCustomWeights(weights) {
        this.customWeights = weights;
    }

    pickWeightedMove(game) {
        return this.pickBestMove(game, 'weighted');
    }

    // ML Sim Heuristic - Weighted feature combination optimized for 2048
    evaluateMLSim(board) {
        let score = 0;
        
        // Feature 1: Maximum tile value (heavily weighted)
        const maxTile = Math.max(...board.flat());
        score += Math.log2(maxTile) * 1000;
        
        // Feature 2: Number of empty cells
        const emptyCount = board.flat().filter(x => x === 0).length;
        score += emptyCount * 270;
        
        // Feature 3: Monotonicity score
        score += this.evaluateMonotonicity(board) * 47;
        
        // Feature 4: Smoothness (difference between adjacent tiles)
        score += this.evaluateSmoothness(board) * 11;
        
        // Feature 5: Corner strategy
        score += this.evaluateCorner(board) * 5;
        
        // Feature 6: Merge potential
        let mergeScore = 0;
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 3; j++) {
                if (board[i][j] && board[i][j] === board[i][j + 1]) {
                    mergeScore += board[i][j];
                }
                if (board[j][i] && board[j][i] === board[j + 1] && board[j + 1]) {
                    mergeScore += board[j][i];
                }
            }
        }
        score += mergeScore * 13;
        
        return score;
    }

    pickMLSimMove(game) {
        return this.pickBestMove(game, 'mlsim');
    }

    // Generic move picker
    pickBestMove(game, heuristicType) {
        const moves = ['up', 'down', 'left', 'right'];
        let bestMove = null;
        let bestScore = -Infinity;
        
        for (let moveDir of moves) {
            const tempGame = game.clone();
            if (tempGame.move(moveDir)) {
                const score = this.evaluateMove(tempGame, moveDir, heuristicType);
                if (score > bestScore) {
                    bestScore = score;
                    bestMove = moveDir;
                }
            }
        }
        
        return bestMove;
    }

    evaluateMove(game, move, heuristicType) {
        switch (heuristicType) {
            case 'monotonicity':
                return this.evaluateMonotonicity(game.board);
            case 'corner':
                return this.evaluateCorner(game.board);
            case 'center':
                return this.evaluateCenter(game.board);
            case 'expectimax':
                return this.evaluateExpectimax(game.board);
            case 'expectimaxCorner':
                return this.evaluateExpectimaxCorner(game.board);
            case 'gradientDescent':
                return this.evaluateGradientDescent(game.board);
            case 'opportunistic':
                return this.evaluateOpportunistic(game.board);
            case 'smoothness':
                return this.evaluateSmoothness(game.board);
            case 'adaptive':
                return this.evaluateAdaptive(game.board);
            case 'ultraAdaptive':
                return this.evaluateUltraAdaptive(game.board);
            case 'advancedMinimax':
                return this.evaluateAdvancedMinimax(game.board);
            case 'weighted':
                return this.evaluateWeighted(game.board, this.customWeights);
            case 'mlsim':
                return this.evaluateMLSim(game.board);
            default:
                return this.evaluateBoard(game.board);
        }
    }

    evaluateBoard(board) {
        return board.flat().reduce((sum, tile) => sum + tile, 0);
    }

    pickRandomMove(game) {
        const moves = ['up', 'down', 'left', 'right'];
        const validMoves = moves.filter(move => {
            const tempGame = game.clone();
            return tempGame.move(move);
        });
        
        if (validMoves.length === 0) return null;
        return validMoves[Math.floor(Math.random() * validMoves.length)];
    }

    // Utility method to get heuristic descriptions
    static getHeuristicDescription(heuristicType) {
        const descriptions = {
            monotonicity: 'Monotonicity: Favors boards where rows/columns are strictly increasing or decreasing.',
            corner: 'Corner: Tries to keep the largest tile in a corner.',
            center: 'Center: Favors moves toward the center.',
            expectimax: 'Expectimax: Looks ahead using expected value.',
            expectimaxCorner: 'Expectimax Corner: Advanced expectimax with corner bias and snake patterns.',
            gradientDescent: 'Gradient Descent: Uses weighted position values favoring bottom-left corner.',
            opportunistic: 'Opportunistic: Combines tiles whenever possible.',
            smoothness: 'Smoothness: Prefers boards where neighboring tiles have similar values.',
            adaptive: 'Adaptive: Changes strategy based on game phase (early/mid/late game).',
            ultraAdaptive: 'Ultra-Adaptive: Advanced phase detection with minimax integration.',
            advancedMinimax: 'Advanced Minimax: Deep lookahead with alpha-beta pruning and snake patterns.',
            weighted: 'Weighted Combo: Combines multiple strategies with customizable weights.',
            mlsim: 'ML Sim: Weighted feature-based move selection optimized for 2048.'
        };
        return descriptions[heuristicType] || 'Unknown heuristic';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Heuristics;
}
