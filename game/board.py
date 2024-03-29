import numpy as np
import scipy
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from typing import List

DEFAULT_SIZE = 20
MAX_PREVIOUS_BOARDS = 10


class Board(np.ndarray):
    """
    A board object that represents the Game of Life's board.
    """

    def __new__(cls, size=DEFAULT_SIZE):
        """Initialize an array of zeros"""
        obj = np.zeros((size, size), dtype=np.uint8).view(cls)
        obj._size: int = size
        obj._previous_boards: List = []
        obj._step = 0
        return obj

    def __array_finalize__(self, obj):
        """Set or update attributes"""
        if obj is None:
            return
        self._size = getattr(obj, "_size", DEFAULT_SIZE)
        self._previous_boards = getattr(obj, "_previous_boards", [])
        self._step = getattr(obj, "_step", 0)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value: int):
        self._step += value

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
            raise ValueError("Size cannot be negative")
        self._size = value

    @property
    def previous_boards(self):
        return self._previous_boards

    @previous_boards.setter
    def previous_boards(self, array: np.ndarray):
        if len(self._previous_boards) > MAX_PREVIOUS_BOARDS:
            del self._previous_boards[0]

        # Converting the array to a sparse matrix and then to a hashable type
        self._previous_boards.append(array)

    @property
    def neighbors(self):
        """Returns a convolution of the board using the 3 by 3 kernel."""
        # return scipy.signal.convolve2d(self.copy(), self.kernel, mode="same", boundary="wrap")
        return scipy.signal.convolve2d(np.copy(self), self.kernel, mode="same", boundary="wrap")

    def is_stable(self) -> bool:
        """
        Returns True if the current board has already been seen in one the MAX_PREVIOUS_BOARDS number of boards.
        This helps identify a stable board that goes back and forth between 2 states.
        """
        if len(self.previous_boards) >= MAX_PREVIOUS_BOARDS:
            return any(np.array_equal(self.copy(), board) for board in self.previous_boards)
        return False

    def is_empty(self) -> bool:
        """Checks if the board is empty (full of 0s)."""
        return np.count_nonzero(self) == 0

    def clear(self):
        self[:] = 0

    def randomize_board(self):
        """
        Initialises a board filled with randoms 1s and 0s.
        """
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
        self.previous_boards = self.copy()
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

    def render_rich_table(self) -> Table:
        def format_cell(cell):
            return "██" if cell else "  "

        table = Table(show_header=False, show_footer=False, show_edge=False, box=None)
        table.padding = (0, 0)
        table.pad_edge = False

        vectorized_format_cell = np.vectorize(format_cell)
        formatted_board = vectorized_format_cell(self)

        for row in formatted_board:
            table.add_row(*row)

        table = Panel.fit(table, title="Game of Life", padding=(0, 0), subtitle=f"Step n°{self.step}")
        table = Align.center(table, vertical="middle")

        # Incrementing the step by one (see step.setter)
        self.step = 1
        return table

    def make_glider(self):
        """Creates a glider shape and insert it in the main board."""
        glider = np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1]])  # define the glider shape
        glider = np.pad(glider, pad_width=1, mode="constant", constant_values=0)  # pad the glider shape with zeros

        # Choose a random 90 degrees rotation and applies it to the glider
        rotation = np.random.choice(a=[0, 1, 2, 3])
        glider = np.rot90(glider, k=rotation)

        # Choose a random starting point for the glider within the boundaries of the board (-4)
        start = np.random.randint(0, self.size - 4)
        self[start : start + 5, start : start + 5] = glider
