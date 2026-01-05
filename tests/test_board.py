import pytest

from chess import Board, Color, PieceType, FENLoader
from chess.game_state import GameState
from chess.pieces import King, Queen, Rook, Pawn


def _load_starting_position(board: Board) -> None:
    """Helper to load the starting position via FENLoader."""
    game_state = GameState()
    loader = FENLoader(board, game_state)
    loader.load_starting_position()


class TestBoard:
    """Tests for the Board class."""

    def test_empty_board(self):
        """A new board should be empty."""
        board = Board()
        for file, rank, piece in board:
            assert piece is None

    def test_set_and_get_piece(self):
        """Should be able to place and retrieve pieces."""
        board = Board()
        king = King(Color.WHITE)

        board.set_piece(4, 0, king)

        assert board.get_piece(4, 0) is king
        assert king.position == (4, 0)

    def test_set_piece_updates_position(self):
        """Setting a piece should update its position attribute."""
        board = Board()
        rook = Rook(Color.BLACK)

        board.set_piece(7, 7, rook)

        assert rook.file == 7
        assert rook.rank == 7

    def test_clear_square(self):
        """Should be able to clear a square by setting None."""
        board = Board()
        pawn = Pawn(Color.WHITE)

        board.set_piece(0, 1, pawn)
        board.set_piece(0, 1, None)

        assert board.get_piece(0, 1) is None

    def test_clear_board(self):
        """Clear should remove all pieces."""
        board = Board()
        board.set_piece(0, 0, King(Color.WHITE))
        board.set_piece(7, 7, King(Color.BLACK))

        board.clear()

        for file, rank, piece in board:
            assert piece is None

    def test_invalid_position_raises(self):
        """Invalid positions should raise ValueError."""
        board = Board()

        with pytest.raises(ValueError):
            board.get_piece(-1, 0)

        with pytest.raises(ValueError):
            board.get_piece(8, 0)

        with pytest.raises(ValueError):
            board.set_piece(0, 8, King(Color.WHITE))

    def test_initial_position_white_pieces(self):
        """Initial position should have white pieces on ranks 0 and 1."""
        board = Board()
        _load_starting_position(board)

        # Check white back rank
        assert board.get_piece(0, 0).piece_type == PieceType.ROOK
        assert board.get_piece(1, 0).piece_type == PieceType.KNIGHT
        assert board.get_piece(2, 0).piece_type == PieceType.BISHOP
        assert board.get_piece(3, 0).piece_type == PieceType.QUEEN
        assert board.get_piece(4, 0).piece_type == PieceType.KING
        assert board.get_piece(5, 0).piece_type == PieceType.BISHOP
        assert board.get_piece(6, 0).piece_type == PieceType.KNIGHT
        assert board.get_piece(7, 0).piece_type == PieceType.ROOK

        # All back rank pieces should be white
        for file in range(8):
            assert board.get_piece(file, 0).color == Color.WHITE

        # Check white pawns
        for file in range(8):
            piece = board.get_piece(file, 1)
            assert piece.piece_type == PieceType.PAWN
            assert piece.color == Color.WHITE

    def test_initial_position_black_pieces(self):
        """Initial position should have black pieces on ranks 6 and 7."""
        board = Board()
        _load_starting_position(board)

        # Check black back rank
        assert board.get_piece(0, 7).piece_type == PieceType.ROOK
        assert board.get_piece(4, 7).piece_type == PieceType.KING

        # All back rank pieces should be black
        for file in range(8):
            assert board.get_piece(file, 7).color == Color.BLACK

        # Check black pawns
        for file in range(8):
            piece = board.get_piece(file, 6)
            assert piece.piece_type == PieceType.PAWN
            assert piece.color == Color.BLACK

    def test_initial_position_empty_middle(self):
        """Initial position should have empty squares in the middle."""
        board = Board()
        _load_starting_position(board)

        for rank in range(2, 6):
            for file in range(8):
                assert board.get_piece(file, rank) is None

    def test_file_to_letter(self):
        """Should convert file index to letter correctly."""
        assert Board.file_to_letter(0) == "a"
        assert Board.file_to_letter(4) == "e"
        assert Board.file_to_letter(7) == "h"

    def test_rank_to_number(self):
        """Should convert rank index to number correctly."""
        assert Board.rank_to_number(0) == "1"
        assert Board.rank_to_number(3) == "4"
        assert Board.rank_to_number(7) == "8"
