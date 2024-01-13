#!/usr/bin/env python3

import time

from rich.console import Console
from rich.live import Live

from game.board import Board

SIZE = 30


def main():
    console = Console()
    board = Board(SIZE)
    board.randomize_board()

    repeats = 100_000
    refresh = 60
    with Live(refresh_per_second=refresh, screen=True) as live:
        while not board.is_stable():
            time.sleep(1 / refresh)
            live.update(board.render_rich_table())
            board.next_step()

    console.print(f"The board has become stable at step n°{board.step}")

if __name__ == "__main__":
    main()
