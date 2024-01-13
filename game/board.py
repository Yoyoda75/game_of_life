import numpy as np
import scipy
from rich.align import Align
from rich.panel import Panel
from rich.table import Table

DEFAULT_SIZE = 20


class Board(np.ndarray):
    """
    A board object that represents the Game of Life's board.
    """

    def __new__(cls, size=DEFAULT_SIZE):
        """Initialize an array of zeros"""
        obj = np.zeros((size, size), dtype=np.uint8).view(cls)
        obj._size = size
        return obj

    def __array_finalize__(self, obj):
        """Set or update attributes"""
        if obj is None:
            return
        self._size = getattr(obj, "_size", DEFAULT_SIZE)

    @property
    def kernel(self):
        kernel = np.ones((3, 3), dtype=np.uint8)
        kernel[1, 1] = 0
        return kernel

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: int):
        if value < 0:
            return ValueError("Size cannot be negative")
        self._size = value

    @property
    def neighbors(self):
        """Returns a convolution of the board using the 3 by 3 kernel."""
        # return scipy.signal.convolve2d(self.copy(), self.kernel, mode="same", boundary="wrap")
        return scipy.signal.convolve2d(np.copy(self), self.kernel, mode="same", boundary="wrap")

    def is_empty(self) -> bool:
        """Checks if the board is empty (full of 0s)."""
        return np.count_nonzero(self) == 0

    def clear(self):
        self[:] = 0

    def init_random_board(self):
        """
        Initialises a board filled with randoms 1s and 0s.
        """
        # self[:] = np.random.randint(0, 2, size=(self.size, self.size))
        # Modify the values in p to change the distribution's uniformity
        self[:] = np.random.choice(a=[0, 1], size=(self.size, self.size), p=[0.5, 0.5])

    def next_step(self):
        """
        Apply the rules of the game of life based on the number of neighbors and the current state of the board.
        This counts as one evolution, this method is then meant to be reused for every step.

        Rules:
        1. Underpopulation: a live cell with fewer than 2 neighbors dies
        2. Survival: a live cell with 2 or 3 neighbors stays alive
        3. Overpopulation: a live cell with more than 3 neighbors dies
        4. Reproduction: a dead cell with exactly 3 neighbors becomes alive
        """
        # Creating an array of True and False representing the 1s and 0s of the original board
        population = self.astype(np.bool_)
        # Settings the rules with numpy logical operators
        dies = np.logical_or(
            self.neighbors < 2, self.neighbors > 3
        )  # Underpopulation and overpopulation together (rules 1 & 3)
        stays_alive = np.logical_and(
            population, np.logical_or(self.neighbors == 2, self.neighbors == 3)
        )  # Survival (rule 2)
        becomes_alive = np.logical_and(~population, self.neighbors >= 3)  # Reproduction (rule 4)

        # Applying the rules to the current board without having to create a new one
        self[:] = np.where(dies, 0, np.where(stays_alive, 1, np.where(becomes_alive, 1, self)))

    def render_rich_table(self, step: int = 0) -> Table:
        def format_cell(cell):
            return "██" if cell else "  "

        table = Table(show_header=False, show_footer=False, show_edge=False, box=None)
        table.padding = (0, 0)
        table.pad_edge = False

        vectorized_format_cell = np.vectorize(format_cell)
        formatted_board = vectorized_format_cell(self)

        for row in formatted_board:
            table.add_row(*row)

        table = Panel.fit(table, title="Game of Life", padding=(0, 0), subtitle=f"Step n°{step}")
        table = Align.center(table)
        return table
