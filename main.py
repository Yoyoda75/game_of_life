#!/usr/bin/env python3

import time

from rich.console import Console
from rich.live import Live

from game.board import Board

SIZE = 50  # 70 seems to be the max that will fit vertically


def main():
    console = Console()
    board = Board(SIZE)
    board.randomize_board()

    # repeats = 100_000
    refresh = 60
    with Live(refresh_per_second=refresh) as live:
        # with Live(auto_refresh=False) as live:
        while not board.is_stable():
            try:
                time.sleep(1 / refresh)  # Synchronizes with the refresh rate
                live.update(board.render_rich_table())
                board.next_step()
            except KeyboardInterrupt:
                break

    console.print(f"The board has become stable at step n°{board.step}")


if __name__ == "__main__":
    main()
