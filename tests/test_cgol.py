import pytest
from unittest.mock import patch
from api.cgol import (
    convert_to_ascii_bitmask,
    generate_initial_live_cells,
    come_to_life,
    continue_living,
    next_generation,
    display_grid,
    check_end_conditons,
    run_game,
    ALIVE,
    DEAD,
    ROWS,
    COLUMNS,
    LIVE_CELL_HISTORY,
)

class TestConvertToAsciiBitmask:
    def test_convert_to_ascii_bitmask_basic(self):
        assert convert_to_ascii_bitmask("A") == ["01000001"]


    def test_convert_to_ascii_bitmask_multiple(self):
        assert convert_to_ascii_bitmask("AB") == ["01000001", "01000010"]


    def test_convert_to_ascii_bitmask_empty(self):
        assert convert_to_ascii_bitmask("") == []


    def test_convert_to_ascii_bitmask_max_length(self):
        word = "a" * 60
        result = convert_to_ascii_bitmask(word)
        assert len(result) == 60


    def test_convert_to_ascii_bitmask_overflow(self):
        word = "a" * 61
        result = convert_to_ascii_bitmask(word)
        assert len(result) == 0

class TestGenerateInitialLiveCells:
    def test_generate_initial_live_cells_single(self):
        bin_list = ["00000001"]
        live_cells = generate_initial_live_cells(bin_list)
        start_row = (ROWS - len(bin_list)) // 2
        start_col = (COLUMNS - 8) // 2
        assert live_cells == {(start_row, start_col + 7)}


    def test_generate_initial_live_cells_multiple(self):
        bin_list = ["10000001", "01000010"]
        live_cells = generate_initial_live_cells(bin_list)
        start_row = (ROWS - len(bin_list)) // 2
        start_col = (COLUMNS - 8) // 2
        expected = {
            (start_row, start_col),
            (start_row, start_col + 7),
            (start_row + 1, start_col + 1),
            (start_row + 1, start_col + 6),
        }
        assert live_cells == expected


    def test_generate_initial_live_cells_all_dead(self):
        bin_list = ["00000000", "00000000"]
        live_cells = generate_initial_live_cells(bin_list)
        assert live_cells == set()


    def test_generate_initial_live_cells_empty(self):
        assert generate_initial_live_cells([]) == set()

class TestNextGeneration:
    def test_next_generation_blinker(self):
        # Blinker pattern (vertical)
        live_cells = {(1, 2), (2, 2), (3, 2)}
        next_gen = next_generation(live_cells)
        assert next_gen == {(2, 1), (2, 2), (2, 3)}

    def test_continue_living_and_come_to_life(self):
        # Block pattern (still life)
        live_cells = {(1, 1), (1, 2), (2, 1), (2, 2)}
        next_gen = next_generation(live_cells)
        assert next_gen == live_cells

    def test_next_generation_single_cell(self):
        live_cells = {(1, 1)}
        next_gen = next_generation(live_cells)
        assert next_gen == set()

    def test_next_generation_empty(self):
        live_cells = set()
        next_gen = next_generation(live_cells)
        assert next_gen == set()
         
class TestContinueLiving:
    def test_continue_living_survives_with_2_or_3_neighbors(self):
        # Cell (1,1) has 2 neighbors, (2,2) has 3 neighbors
        neighbour_count = {
            (1, 1): 2,
            (2, 2): 3,
            (3, 3): 1,
            (4, 4): 4,
        }
        live_cells = {(1, 1), (2, 2), (3, 3), (4, 4)}
        result = continue_living(neighbour_count, live_cells)
        assert result == {(1, 1), (2, 2)}

    def test_continue_living_dies_with_less_than_2_or_more_than_3_neighbors(self):
        neighbour_count = {
            (1, 1): 1,
            (2, 2): 4,
            (3, 3): 0,
        }
        live_cells = {(1, 1), (2, 2), (3, 3)}
        result = continue_living(neighbour_count, live_cells)
        assert result == set()

    def test_continue_living_only_returns_live_cells(self):
        neighbour_count = {
            (1, 1): 2,
            (2, 2): 3,
            (3, 3): 2,
        }
        live_cells = {(1, 1), (2, 2)}
        result = continue_living(neighbour_count, live_cells)
        assert result == {(1, 1), (2, 2)}
        # (3,3) is not in live_cells, so not included

class TestComeToLife:
    def test_come_to_life_returns_dead_cells_with_3_neighbors(self):
        neighbour_count = {
            (1, 1): 3,
            (2, 2): 3,
            (3, 3): 2,
            (4, 4): 3,
        }
        live_cells = {(2, 2)}
        result = come_to_life(neighbour_count, live_cells)
        # (1,1) and (4,4) have 3 neighbors and are not alive
        assert result == {(1, 1), (4, 4)}

    def test_come_to_life_returns_empty_if_no_dead_cells_with_3_neighbors(self):
        neighbour_count = {
            (1, 1): 2,
            (2, 2): 4,
            (3, 3): 1,
        }
        live_cells = {(1, 1), (2, 2)}
        result = come_to_life(neighbour_count, live_cells)
        assert result == set()

    def test_come_to_life_does_not_include_current_live_cells(self):
        neighbour_count = {
            (1, 1): 3,
            (2, 2): 3,
        }
        live_cells = {(1, 1), (2, 2)}
        result = come_to_life(neighbour_count, live_cells)
        assert result == set()    

class TestDisplayGrid:
    def test_simple_display_grid(self):
        live_cells = {(0, 0), (0, 1)}
        grid = display_grid(live_cells, bounding_box=(0, 0, 1, 3))
        assert grid == f"{ALIVE}{ALIVE}{DEAD}"

class TestCheckEndConditions:
    def test_check_end_conditons_no_history(self):
        LIVE_CELL_HISTORY.clear()
        assert not check_end_conditons({(1, 1)})


    def test_check_end_conditons_single_generation_same_next_gen(self):
        LIVE_CELL_HISTORY.clear()
        gen = {(1, 1)}
        LIVE_CELL_HISTORY.append(gen)
        assert check_end_conditons(gen)

    def test_check_end_conditons_single_generation_diff_next_gen(self):
        LIVE_CELL_HISTORY.clear()
        gen = {(1, 1), (1, 2), (2, 1)}
        LIVE_CELL_HISTORY.append(gen)
        gen = next_generation(gen)
        assert not check_end_conditons(gen)

class TestRunGame:
    def test_run_game_returns_proper_output(self):
        result = run_game("A", generations=10)
        assert "generations" in result
        assert "score" in result
        assert isinstance(result["generations"], int)
        assert isinstance(result["score"], int)

    def test_run_game_no_end_conditions(self):
        with patch("api.cgol.check_end_conditons", return_value=False):
            result = run_game("A", generations=10)
            assert result["generations"] == 10
            assert result["score"] == len(generate_initial_live_cells(convert_to_ascii_bitmask("A"))) # A dies off in the next gen, bin=01000001

    def test_run_game_empty_input(self):
        result = run_game("", generations=10)
        assert result["generations"] == 0
        assert result["score"] == 0

    def test_run_game_complex_word(self):
        with patch("api.cgol.check_end_conditons", return_value=False):
            result = run_game("HELLO", generations=10)
            assert result["generations"] == 10
            assert result["score"] > 0  