from constants import *
from IDA_star import IDAStarSolver
from sokoban_game import SokobanGame
from ultils import parse_level


def assert_rectangular(board):
    width = len(board[0])
    assert all(len(row) == width for row in board), "Board is not rectangular"


def test_basic_bound_check():
    board = parse_level(0)
    game = SokobanGame(board)
    assert game.position_on_board(0, 0)
    assert not game.position_on_board(-1, 0)
    assert not game.position_on_board(len(board), 0)


def test_level_zero_solution():
    board = parse_level(0)
    solver = IDAStarSolver(board)
    solver.solve()

    assert solver.end_node is not None, "Level 0 should be solvable"
    solution = solver.get_solution()
    assert len(solution) >= 2, "Solution path should contain at least start and end"
    assert solution[-1] is not None


if __name__ == "__main__":
    board = parse_level(0)
    assert_rectangular(board)
    test_basic_bound_check()
    test_level_zero_solution()
    print("All tests passed")
