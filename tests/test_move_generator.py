import pytest

from chess import Board, Color
from chess.pieces import Knight, Rook
from chess.move_generator import MoveGenerator


@pytest.fixture
def move_gen():
    return MoveGenerator()


@pytest.fixture
def empty_board():
    return Board()


class TestKnightMoves:
    """Tests for knight move generation."""

    def test_knight_moves_from_center(self, move_gen, empty_board):
        """Knight in center should have 8 possible moves."""
        knight = Knight(Color.WHITE)
        empty_board.set_piece(4, 4, knight)  # e5

        moves = move_gen.get_valid_moves(empty_board, knight)

        assert len(moves) == 8
        expected = [
            (6, 5), (6, 3),  # Right 2, up/down 1
            (2, 5), (2, 3),  # Left 2, up/down 1
            (5, 6), (5, 2),  # Right 1, up/down 2
            (3, 6), (3, 2),  # Left 1, up/down 2
        ]
        assert set(moves) == set(expected)

    def test_knight_moves_from_corner(self, move_gen, empty_board):
        """Knight in corner should have 2 possible moves."""
        knight = Knight(Color.WHITE)
        empty_board.set_piece(0, 0, knight)  # a1

        moves = move_gen.get_valid_moves(empty_board, knight)

        assert len(moves) == 2
        expected = [(2, 1), (1, 2)]
        assert set(moves) == set(expected)

    def test_knight_blocked_by_friendly(self, move_gen, empty_board):
        """Knight cannot land on friendly piece."""
        knight = Knight(Color.WHITE)
        friendly_rook = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, knight)
        empty_board.set_piece(6, 5, friendly_rook)  # Block one destination

        moves = move_gen.get_valid_moves(empty_board, knight)

        assert len(moves) == 7
        assert (6, 5) not in moves

    def test_knight_can_capture_enemy(self, move_gen, empty_board):
        """Knight can capture enemy piece."""
        knight = Knight(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)
        empty_board.set_piece(4, 4, knight)
        empty_board.set_piece(6, 5, enemy_rook)

        moves = move_gen.get_valid_moves(empty_board, knight)

        assert len(moves) == 8
        assert (6, 5) in moves  # Can capture


class TestRookMoves:
    """Tests for rook move generation."""

    def test_rook_moves_on_empty_board(self, move_gen, empty_board):
        """Rook on empty board should have 14 possible moves."""
        rook = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, rook)  # e5

        moves = move_gen.get_valid_moves(empty_board, rook)

        # 7 squares in each direction (horizontal + vertical) = 14 total
        assert len(moves) == 14

    def test_rook_blocked_by_friendly(self, move_gen, empty_board):
        """Rook stops before friendly piece."""
        rook = Rook(Color.WHITE)
        friendly = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, rook)
        empty_board.set_piece(4, 6, friendly)  # Block upward

        moves = move_gen.get_valid_moves(empty_board, rook)

        # Can move to rank 5, but not 6 or 7
        assert (4, 5) in moves
        assert (4, 6) not in moves
        assert (4, 7) not in moves

    def test_rook_captures_enemy(self, move_gen, empty_board):
        """Rook can capture enemy but stops there."""
        rook = Rook(Color.WHITE)
        enemy = Rook(Color.BLACK)
        empty_board.set_piece(4, 4, rook)
        empty_board.set_piece(4, 6, enemy)  # Enemy upward

        moves = move_gen.get_valid_moves(empty_board, rook)

        # Can move to rank 5 and capture on 6, but not 7
        assert (4, 5) in moves
        assert (4, 6) in moves  # Can capture
        assert (4, 7) not in moves  # Can't go past

    def test_rook_blocked_multiple_directions(self, move_gen, empty_board):
        """Rook blocked in multiple directions."""
        rook = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, rook)
        empty_board.set_piece(4, 5, Rook(Color.WHITE))  # Block up
        empty_board.set_piece(4, 3, Rook(Color.WHITE))  # Block down
        empty_board.set_piece(5, 4, Rook(Color.WHITE))  # Block right
        empty_board.set_piece(3, 4, Rook(Color.WHITE))  # Block left

        moves = move_gen.get_valid_moves(empty_board, rook)

        assert len(moves) == 0


class TestGetAllMoves:
    """Tests for getting all moves for a color."""

    def test_get_all_moves_returns_pieces_with_moves(self, move_gen, empty_board):
        """get_all_moves returns dict of pieces to their moves."""
        knight = Knight(Color.WHITE)
        rook = Rook(Color.WHITE)
        empty_board.set_piece(0, 0, knight)
        empty_board.set_piece(7, 7, rook)

        all_moves = move_gen.get_all_moves(empty_board, Color.WHITE)

        assert knight in all_moves
        assert rook in all_moves
        assert len(all_moves[knight]) == 2  # Corner knight
        assert len(all_moves[rook]) == 14  # Open rook

    def test_get_all_moves_ignores_other_color(self, move_gen, empty_board):
        """get_all_moves only returns moves for specified color."""
        white_knight = Knight(Color.WHITE)
        black_knight = Knight(Color.BLACK)
        empty_board.set_piece(4, 4, white_knight)
        empty_board.set_piece(0, 0, black_knight)

        white_moves = move_gen.get_all_moves(empty_board, Color.WHITE)

        assert white_knight in white_moves
        assert black_knight not in white_moves
