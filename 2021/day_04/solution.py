#!/usr/bin/env python3

import numpy as np

# A bingo board.
class Board:
    def __init__(self, board):
        self.board = np.array(board)
        self.stamps = np.zeros(self.board.shape, dtype=bool)
        
    def __str__(self):
        s = ""
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
        for line in input_file:
            line = line.strip()
            print(line)
            if not line:
                # blank line => new board
                if board:
                    boards.append(Board(board))
                board = []
            else:
                board.append([int(x) for x in line.split()])

        # When we run out of lines, we should have one complete board left to
        # append to our list.
        boards.append(Board(board)) 

    print(f"Draws = {draws}")
    print("Boards = ")
    for b in boards:
        print(b)

    # Find the winning board by playing all draws.
    last_draw = None
    winning_board = None
    for draw in draws:
        if winning_board:
            break

        last_draw = draw
        print(f"Playing draw: {draw}")

        for board in boards:
            board.play(draw)
            if board.is_winning():
                print("Found winning board!")
                winning_board = board

    # we either won or ran out of draws
    print(f"Last draw was: {last_draw}")
    if winning_board:
        # print score
        print(f"Winning board is:\n{winning_board}")
        print(f"Winning board has score: {winning_board.score(last_draw)}")
    else:
        print(f"No winning board!")

if __name__ == "__main__":
    main()
