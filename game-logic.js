// 2048 Game Logic Module
class Game2048 {
    constructor() {
        this.board = [];
        this.score = 0;
        this.gameOver = false;
        this.initBoard();
    }

    initBoard() {
        this.board = Array.from({length: 4}, () => Array(4).fill(0));
        this.score = 0;
        this.gameOver = false;
        this.addTile();
        this.addTile();
    }

    addTile() {
        const empty = [];
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                if (this.board[i][j] === 0) {
                    empty.push([i, j]);
                }
            }
        }
        
        if (empty.length === 0) return false;
        
        const [i, j] = empty[Math.floor(Math.random() * empty.length)];
        this.board[i][j] = Math.random() < 0.1 ? 4 : 2;
        return true;
    }

    move(direction) {
        const oldBoard = this.board.map(row => [...row]);
        const oldScore = this.score;
        let moved = false;

        switch (direction) {
            case 'up':
                moved = this.moveUp();
                break;
            case 'down':
                moved = this.moveDown();
                break;
            case 'left':
                moved = this.moveLeft();
                break;
            case 'right':
                moved = this.moveRight();
                break;
        }

        if (moved) {
            this.addTile();
            this.checkGameOver();
        }

        return moved;
    }

    moveLeft() {
        let moved = false;
        for (let i = 0; i < 4; i++) {
            const row = this.board[i].filter(cell => cell !== 0);
            
            // Merge tiles
            for (let j = 0; j < row.length - 1; j++) {
                if (row[j] === row[j + 1]) {
                    row[j] *= 2;
                    this.score += row[j];
                    row[j + 1] = 0;
                }
            }
            
            // Remove zeros after merging
            const newRow = row.filter(cell => cell !== 0);
            while (newRow.length < 4) {
                newRow.push(0);
            }
            
            // Check if row changed
            for (let j = 0; j < 4; j++) {
                if (this.board[i][j] !== newRow[j]) {
                    moved = true;
                }
            }
            
            this.board[i] = newRow;
        }
        return moved;
    }

    moveRight() {
        let moved = false;
        for (let i = 0; i < 4; i++) {
            const row = this.board[i].slice().reverse().filter(cell => cell !== 0);
            
            // Merge tiles
            for (let j = 0; j < row.length - 1; j++) {
                if (row[j] === row[j + 1]) {
                    row[j] *= 2;
                    this.score += row[j];
                    row[j + 1] = 0;
                }
            }
            
            // Remove zeros after merging
            const newRow = row.filter(cell => cell !== 0);
            while (newRow.length < 4) {
                newRow.push(0);
            }
            
            const finalRow = newRow.reverse();
            
            // Check if row changed
            for (let j = 0; j < 4; j++) {
                if (this.board[i][j] !== finalRow[j]) {
                    moved = true;
                }
            }
            
            this.board[i] = finalRow;
        }
        return moved;
    }

    moveUp() {
        this.transpose();
        const moved = this.moveLeft();
        this.transpose();
        return moved;
    }

    moveDown() {
        this.transpose();
        const moved = this.moveRight();
        this.transpose();
        return moved;
    }

    transpose() {
        const newBoard = Array.from({length: 4}, () => Array(4).fill(0));
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                newBoard[j][i] = this.board[i][j];
            }
        }
        this.board = newBoard;
    }

    checkGameOver() {
        // Check for empty cells
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                if (this.board[i][j] === 0) {
                    this.gameOver = false;
                    return false;
                }
            }
        }

        // Check for possible merges
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 3; j++) {
                if (this.board[i][j] === this.board[i][j + 1]) {
                    this.gameOver = false;
                    return false;
                }
            }
        }

        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 3; i++) {
                if (this.board[i][j] === this.board[i + 1][j]) {
                    this.gameOver = false;
                    return false;
                }
            }
        }

        this.gameOver = true;
        return true;
    }

    getMaxTile() {
        return Math.max(...this.board.flat());
    }

    getEmptyCount() {
        return this.board.flat().filter(cell => cell === 0).length;
    }

    clone() {
        const clonedGame = new Game2048();
        clonedGame.board = this.board.map(row => [...row]);
        clonedGame.score = this.score;
        clonedGame.gameOver = this.gameOver;
        return clonedGame;
    }

    toJSON() {
        return {
            board: this.board,
            score: this.score,
            gameOver: this.gameOver,
            maxTile: this.getMaxTile(),
            emptyCount: this.getEmptyCount()
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Game2048;
}
