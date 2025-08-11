"""Main game logic
This module implements Conway's Game of Life logic, including functions for
converting words to bitmasks, generating initial live cells, computing generations,
and running the game loop. It also provides utilities for displaying the grid and
checking end conditions.
"""

from collections import defaultdict, deque

ALIVE = "🟩"
DEAD = "⬜"
DEAD = "‧"
ROWS = 60
COLUMNS = 40
LIVE_CELL_HISTORY = deque()
CELL_NEIGHBOURS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def convert_to_ascii_bitmask(word: str) -> list[str]:
    """
    Converts a word into a list of 8-bit binary strings representing each character's ASCII value.

    Args:
        word (str): The input word to convert.

    Returns:
        list[str]: List of 8-character binary strings, one for each letter in the word.
                   Returns an empty list if the word is longer than 60 characters.
    """
    result = []
    if len(word) <= 60:
        for letter in word:
            ascii_bin = bin(ord(letter))[2:].zfill(8)
            result.append(ascii_bin)
    return result


def generate_initial_live_cells(bin_list: list[str]) -> set[tuple[int, int]]:
    """
    Generates the initial set of live cells from a list of binary strings, centering them in the grid.

    Args:
        bin_list (list[str]): List of binary strings representing the initial pattern.

    Returns:
        set[tuple[int, int]]: Set of (row, column) tuples for live cells.
    """

    start_row = (ROWS - len(bin_list)) // 2
    start_col = (COLUMNS - 8) // 2
    live_cells = set()

    for i, row in enumerate(bin_list):
        for j, col in enumerate(row):
            if int(col) == 1:
                x = start_row + i
                y = start_col + j
                cell = (x, y)
                live_cells.add(cell)

    return live_cells


def next_generation(live_cells: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """
    Computes the next generation of live cells according to Conway's Game of Life rules.

    Args:
        live_cells (set[tuple[int, int]]): Current set of live cells.

    Returns:
        set[tuple[int, int]]: Set of live cells for the next generation.
    """
    neighbour_count = defaultdict(int)

    for row, col in live_cells:
        for cnrow, cncol in CELL_NEIGHBOURS:
            neighbour_count[(row + cnrow, col + cncol)] += 1

    stay_alive = continue_living(neighbour_count, live_cells)
    come_alive = come_to_life(neighbour_count, live_cells)

    new_generation = stay_alive | come_alive
    return new_generation


def continue_living(
    neighbour_count: dict[tuple, int], live_cells
) -> set[tuple[int, int]]:
    """
    Determines which live cells survive to the next generation.

    Args:
        neighbour_count (dict[tuple, int]): Mapping of cell positions to neighbor counts.
        live_cells (set[tuple[int, int]]): Current set of live cells.

    Returns:
        set[tuple[int, int]]: Set of cells that remain alive.
    """
    living_cells = {
        cell for cell, count in neighbour_count.items() if count in {2, 3}
    } & live_cells

    return living_cells


def come_to_life(neighbour_count: dict[tuple, int], live_cells) -> set[tuple[int, int]]:
    """
    Determines which dead cells become alive in the next generation.

    Args:
        neighbour_count (dict[tuple, int]): Mapping of cell positions to neighbor counts.
        live_cells (set[tuple[int, int]]): Current set of live cells.

    Returns:
        set[tuple[int, int]]: Set of cells that become alive.
    """
    resurrected_cells = {
        cell for cell, count in neighbour_count.items() if count == 3
    } - live_cells

    return resurrected_cells


def display_grid(live_cells: set[tuple[int, int]], bounding_box: tuple = (0, 0, ROWS, COLUMNS))->str:
    """
    Returns a string representation of the grid for display.

    Args:
        live_cells (set[tuple[int, int]]): Set of live cell positions.
        bounding_box (tuple): (start_row, start_col, end_row, end_col) for display area.

    Returns:
        str: Multiline string representing the grid.
    """
    start_row, start_col, end_row, end_col = bounding_box
    grid = []
    for row in range(start_row, end_row):
        display_row = [
            ALIVE if (row, col) in live_cells else DEAD
            for col in range(start_col, end_col)
        ]
        grid.append("".join(display_row))
    return "\n".join(grid)


def check_end_conditons(curr_generation: set[tuple[int, int]]) -> bool:
    """
    Checks if the game should end based on the current generation and history.

    Args:
        curr_generation (set[tuple[int, int]]): The current set of live cells.

    Returns:
        bool: True if the game should end, False otherwise.
    """
    if len(LIVE_CELL_HISTORY) == 0:
        LIVE_CELL_HISTORY.append(curr_generation)
        return False
    if (
        len(curr_generation) == 0
        or curr_generation in LIVE_CELL_HISTORY
        or curr_generation == LIVE_CELL_HISTORY[-1]
    ):
        return True

    # else add to queue
    else:
        if len(LIVE_CELL_HISTORY) == 10:
            LIVE_CELL_HISTORY.popleft()
        LIVE_CELL_HISTORY.append(curr_generation)
        return False


def run_game(word: str, generations: int = 1000)-> dict[str, int]:
    """
    Runs Conway's Game of Life for a given word and returns the number of generations and score.

    Args:
        word (str): The word to convert into the initial pattern.
        generations (int, optional): Maximum number of generations to run. Defaults to 1000.

    Returns:
        dict[str, int]: Dictionary with keys 'generations' and 'score'.
    """
    curr_gen_number = 0
    total_cells_spawned = 0
    ascii_bits = convert_to_ascii_bitmask(word)
    curr_gen = generate_initial_live_cells(ascii_bits)

    while curr_gen_number < generations:
        should_end = check_end_conditons(curr_gen)
        if should_end:
            break
        total_cells_spawned += len(curr_gen)
        next_gen = next_generation(curr_gen)
        curr_gen = next_gen
        curr_gen_number += 1

    return {"generations": curr_gen_number, "score": total_cells_spawned}


if __name__ == "__main__":
    print(run_game("monument"))
