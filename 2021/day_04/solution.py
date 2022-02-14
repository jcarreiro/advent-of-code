#!/usr/bin/env python3

import numpy as np

# A bingo board.
class Board:
    def __init__(self, board_num, board):
        self.board_num = board_num
        self.board = np.array(board)
        self.stamps = np.zeros(self.board.shape, dtype=bool)
        
    def __str__(self):
        s = f"Board {self.board_num}\n"
        rows, cols = self.board.shape
        for r in range(rows):
            for c in range(cols):
                if self.stamps[r][c]:
                    s += f" *{self.board[r][c]:2}* "
                else:
                    s += f"  {self.board[r][c]:2}  "
            s += "\n"
        return s

    def play(self, number):
        self.stamps |= self.board == number

    def is_winning(self):
        return np.any(np.hstack((np.all(self.stamps, axis=0), np.all(self.stamps, axis=1))))

    def score(self, last_draw):
        return last_draw * np.sum(self.board[~self.stamps])

def main():
    draws = None
    boards = None
    with open("input.txt") as input_file:
        # The first line is the list of draws.
        line = input_file.readline()
        print(line)
        draws = [int(x) for x in line.split(",")]

        boards = []
        board = None
        board_num = 0
        for line in input_file:
            line = line.strip()
            print(line)
            if not line:
                # blank line => new board
                if board:
                    boards.append(Board(board_num, board))
                board = []
                board_num += 1
            else:
                board.append([int(x) for x in line.split()])

        # When we run out of lines, we should have one complete board left to
        # append to our list.
        boards.append(Board(board_num, board)) 

    print(f"Draws = {draws}")
    print("Boards = ")
    for b in boards:
        print(b)

    # Find the winning board by playing all draws.
    #
    # In part 1, we need to find the first board that wins; in part 2, the last
    # board.
    winning_boards = []
    for t in range(len(draws)):
        if len(winning_boards) == len(boards):
            print("All boards are winning now!")
            break

        draw = draws[t]
        print(f"Playing draw {draw} on timestep {t}.")
        for board in boards:
            # Once a board is winning, don't play it anymore.
            if not board.is_winning():
                board.play(draw)
                if board.is_winning():
                    print(f"Board {board.board_num} won on timestep {t}!")
                    winning_boards.append((board, t, draw))

    # Print score for first winning board and last winning board.
    if winning_boards:
        def print_score(name, board, t, last_draw):
            print(f"{name} winning board scored {board.score(draw)}! Board:\n{board}")

        print_score("First", *winning_boards[0])
        if winning_boards[0] != winning_boards[-1]:
            print_score("Last", *winning_boards[-1])
    else:
        print(f"No winning boards!")

if __name__ == "__main__":
    main()
