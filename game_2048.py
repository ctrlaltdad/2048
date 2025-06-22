import numpy as np
import random
import os

class Game2048:
    def __init__(self):
        self.board = np.zeros((4, 4), dtype=np.int32)
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty = np.argwhere(self.board == 0)
        if len(empty) > 0:
            i, j = empty[random.randrange(len(empty))]
            self.board[i, j] = 4 if random.random() < 0.1 else 2

    def print_board(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Score: {self.score}")
        print("-" * 25)
        for row in self.board:
            print("|", end=" ")
            for cell in row:
                if cell == 0:
                    print(".".center(4), end=" ")
                else:
                    print(str(cell).center(4), end=" ")
            print("|")
        print("-" * 25)

    def move_tiles(self, direction):
        before = self.board.copy()
        if direction in ['left', 'right']:
            reverse = (direction == 'right')
            for i in range(4):
                self.board[i] = self.merge(self.board[i], reverse)
        else:  # up or down
            reverse = (direction == 'down')
            self.board = self.board.T
            for i in range(4):
                self.board[i] = self.merge(self.board[i], reverse)
            self.board = self.board.T
        if not np.array_equal(before, self.board):
            self.add_new_tile()
            return True
        return False

    def merge(self, row, reverse=False):
        # row: 1D numpy array
        nonzero = row[row != 0]
        if reverse:
            nonzero = nonzero[::-1]
        merged = []
        skip = False
        i = 0
        while i < len(nonzero):
            if not skip and i + 1 < len(nonzero) and nonzero[i] == nonzero[i + 1]:
                merged_val = nonzero[i] * 2
                self.score += merged_val
                merged.append(merged_val)
                skip = True
            else:
                if not skip:
                    merged.append(nonzero[i])
                skip = False
            i += 1
            if skip:
                i += 1
                skip = False
        merged = np.array(merged, dtype=np.int32)
        # Pad with zeros
        if len(merged) < 4:
            merged = np.concatenate([merged, np.zeros(4 - len(merged), dtype=np.int32)])
        if reverse:
            merged = merged[::-1]
        return merged

    def is_game_over(self):
        if np.any(self.board == 0):
            return False
        for i in range(4):
            for j in range(4):
                current = self.board[i, j]
                if j < 3 and current == self.board[i, j + 1]:
                    return False
                if i < 3 and current == self.board[i + 1, j]:
                    return False
        return True

    def has_won(self):
        return np.any(self.board == 2048)

    def copy(self):
        new_game = Game2048()
        new_game.board = self.board.copy()
        new_game.score = self.score
        return new_game

    def get_state(self):
        return self.board.copy(), self.score

def main():
    game = Game2048()
    move_dict = {
        'w': 'up',
        's': 'down',
        'a': 'left',
        'd': 'right'
    }

    print("Welcome to 2048!")
    print("Use WASD keys to move the tiles:")
    print("w: up")
    print("s: down")
    print("a: left")
    print("d: right")
    print("q: quit")
    input("Press Enter to start...")

    while True:
        game.print_board()
        
        if game.has_won():
            print("Congratulations! You've reached 2048!")
            break
            
        if game.is_game_over():
            print("Game Over!")
            break
            
        move = input("Enter your move (WASD): ").lower()
        
        if move == 'q':
            print("Thanks for playing!")
            break
            
        if move in move_dict:
            game.move_tiles(move_dict[move])
        else:
            print("Invalid move! Use WASD keys.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
