import random
import os

class Game2048:
    def __init__(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 4 if random.random() < 0.1 else 2

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
        before = [row[:] for row in self.board]
        if direction in ['left', 'right']:
            reverse = (direction == 'right')
            self.board = [self.merge(row, reverse) for row in self.board]
        else:  # up or down
            reverse = (direction == 'down')
            # Transpose the board
            self.board = list(map(list, zip(*self.board)))
            # Merge each row
            self.board = [self.merge(row, reverse) for row in self.board]
            # Transpose back
            self.board = list(map(list, zip(*self.board)))
        
        if before != self.board:
            self.add_new_tile()
            return True
        return False

    def merge(self, row, reverse=False):
        # Remove zeros and create new row
        row = [x for x in row if x != 0]
        if reverse:
            row.reverse()
        # Merge adjacent equal numbers
        i = 0
        while i < len(row) - 1:
            if row[i] == row[i + 1]:
                row[i] *= 2
                self.score += row[i]
                row.pop(i + 1)
            i += 1
        # Add zeros to maintain size (always to the end)
        while len(row) < 4:
            row.append(0)
        if reverse:
            row.reverse()
        return row

    def is_game_over(self):
        # Check if there are any empty cells
        if any(0 in row for row in self.board):
            return False
        
        # Check if any adjacent cells are equal
        for i in range(4):
            for j in range(4):
                current = self.board[i][j]
                # Check right neighbor
                if j < 3 and current == self.board[i][j + 1]:
                    return False
                # Check bottom neighbor
                if i < 3 and current == self.board[i + 1][j]:
                    return False
        return True

    def has_won(self):
        return any(2048 in row for row in self.board)

    def copy(self):
        new_game = Game2048()
        new_game.board = [row[:] for row in self.board]
        new_game.score = self.score
        return new_game

    def get_state(self):
        return [row[:] for row in self.board], self.score

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
