import copy

import hc
import pytest
import utils


def test_hill_climbing_reduces_cost_on_simple_line_map():
    board = [[utils.OBJECT_HOSPITAL, None, None, None, utils.OBJECT_HOUSE]]
    before = copy.deepcopy(board)
    initial_cost = utils.cost(board)

    solved = hc.hill_climbing(board)

    assert board == before
    assert utils.cost(solved) < initial_cost
    assert solved == [[None, None, None, utils.OBJECT_HOSPITAL, utils.OBJECT_HOUSE]]


def test_hill_climbing_stops_at_local_optimum():
    board = [
        [None, utils.OBJECT_HOUSE, None],
        [utils.OBJECT_HOUSE, utils.OBJECT_HOSPITAL, utils.OBJECT_HOUSE],
        [None, utils.OBJECT_HOUSE, None],
    ]

    solved = hc.hill_climbing(copy.deepcopy(board))
    solved_cost = utils.cost(solved)

    for hospital in utils.find_objects(solved, utils.OBJECT_HOSPITAL):
        for candidate_move in utils.actions(solved, hospital):
            candidate_map = utils.result(solved, hospital, candidate_move)
            assert utils.cost(candidate_map) >= solved_cost


def test_hill_climbing_does_not_mutate_input_map_when_improvement_exists():
    board = [[utils.OBJECT_HOSPITAL, None, utils.OBJECT_HOUSE]]
    before = copy.deepcopy(board)

    solved = hc.hill_climbing(board)

    assert board == before
    assert solved != before


def test_simulated_annealing_accepts_improving_move_without_mutating_input(
    monkeypatch,
):
    board = [[utils.OBJECT_HOSPITAL, None, None, None, utils.OBJECT_HOUSE]]
    before = copy.deepcopy(board)

    def fake_choice(options):
        return options[0]

    monkeypatch.setattr(hc.random, "choice", fake_choice)

    solved = hc.simulated_annealing(board, T_min=0.5, T_initial=1.0, cooling_rate=0.4)

    assert board == before
    assert utils.cost(solved) < utils.cost(before)
    assert solved == [[None, utils.OBJECT_HOSPITAL, None, None, utils.OBJECT_HOUSE]]


@pytest.mark.parametrize(
    ("random_value", "expected_board"),
    [
        (
            0.0,
            [
                [utils.OBJECT_HOUSE, None, utils.OBJECT_HOUSE],
                [None, utils.OBJECT_HOSPITAL, None],
            ],
        ),
        (
            1.0,
            [
                [utils.OBJECT_HOUSE, utils.OBJECT_HOSPITAL, utils.OBJECT_HOUSE],
                [None, None, None],
            ],
        ),
    ],
)
def test_simulated_annealing_handles_worse_moves_probabilistically(
    monkeypatch, random_value, expected_board
):
    board = [
        [utils.OBJECT_HOUSE, utils.OBJECT_HOSPITAL, utils.OBJECT_HOUSE],
        [None, None, None],
    ]
    before = copy.deepcopy(board)

    def fake_choice(options):
        return options[0]

    monkeypatch.setattr(hc.random, "choice", fake_choice)
    monkeypatch.setattr(hc.random, "random", lambda: random_value)

    solved = hc.simulated_annealing(board, T_min=0.5, T_initial=1.0, cooling_rate=0.4)

    assert board == before
    assert solved == expected_board


def test_simulated_annealing_returns_current_grid_when_no_hospitals_can_move():
    board = [
        [utils.OBJECT_HOUSE, utils.OBJECT_HOUSE, utils.OBJECT_HOUSE],
        [utils.OBJECT_HOUSE, utils.OBJECT_HOSPITAL, utils.OBJECT_HOUSE],
        [utils.OBJECT_HOUSE, utils.OBJECT_HOUSE, utils.OBJECT_HOUSE],
    ]

    solved = hc.simulated_annealing(
        board, T_min=0.5, T_initial=1.0, cooling_rate=0.4
    )

    assert solved == board
