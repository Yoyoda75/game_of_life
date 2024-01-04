#!/usr/bin/env python

import time

import numpy as np
import scipy
from rich.console import Console

from game.board import Board

SIZE = 100


def main():
    console = Console()
    kernel = np.ones((3, 3), dtype=np.uint8)
    kernel[1, 1] = 0
    board = Board(kernel, SIZE)
    board.init_random_board()
    print(board)

    steps = board.evolution(100)
    for step in steps:
        if step.is_empty():
            break
        console.print(step)


if __name__ == "__main__":
    main()
