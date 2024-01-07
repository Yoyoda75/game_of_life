#!/usr/bin/env python

import time

import numpy as np
import scipy
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from game.board import Board

SIZE = 50


def update_table(board: Board) -> Table:
    table = Table(title="Game of Life", show_header=False, show_footer=False, show_edge=False, box=None)
    table.padding = (0, 0)
    table.pad_edge = False

    columns = board.shape[1]
    for column in range(columns):
        table.add_column(no_wrap=True, justify="center", vertical="middle")

    for row in board:
        formatted_row = ["■" if element else " " for element in row]
        table.add_row(*formatted_row)

    return table


def main():
    console = Console()
    board = Board(SIZE)
    board.init_random_board()

    # print(board)
    # print(board.neighbors)
    repeats = 100000
    refresh = 50
    with Live(refresh_per_second=refresh, screen=True) as live:
        for _ in range(repeats):
            time.sleep(1 / refresh)
            table = Align.center(update_table(board), vertical="middle")
            live.update(table)
            board.next_step()


if __name__ == "__main__":
    main()
