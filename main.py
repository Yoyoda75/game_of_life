#!/usr/bin/env python3

import time

from rich.console import Console
from rich.live import Live

from game.board import Board


SIZE = 30


def main():
    console = Console()
    board = Board(SIZE)
    board.init_random_board()

    repeats = 1_000_000
    refresh = 60
    with Live(refresh_per_second=refresh, screen=True) as live:
        for step in range(repeats):
            time.sleep(1 / refresh)
            live.update(board.render(step))
            board.next_step()


if __name__ == "__main__":
    main()
