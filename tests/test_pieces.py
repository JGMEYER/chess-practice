import pytest

from chess import Color, PieceType
from chess.piece import Piece
from chess.pieces import King, Queen, Bishop, Knight, Rook, Pawn


class TestPiece:
    """Tests for the Piece base class and subclasses."""

    def test_piece_color(self):
        """Pieces should store their color correctly."""
        white_king = King(Color.WHITE)
        black_king = King(Color.BLACK)

        assert white_king.color == Color.WHITE
        assert black_king.color == Color.BLACK

    def test_piece_type(self):
        """Each piece class should have the correct piece type."""
        assert King(Color.WHITE).piece_type == PieceType.KING
        assert Queen(Color.WHITE).piece_type == PieceType.QUEEN
        assert Bishop(Color.WHITE).piece_type == PieceType.BISHOP
        assert Knight(Color.WHITE).piece_type == PieceType.KNIGHT
        assert Rook(Color.WHITE).piece_type == PieceType.ROOK
        assert Pawn(Color.WHITE).piece_type == PieceType.PAWN

    def test_piece_initial_position_none(self):
        """Pieces created without position should have None position."""
        king = King(Color.WHITE)

        assert king.position is None
        assert king.file is None
        assert king.rank is None

    def test_piece_with_position(self):
        """Pieces can be created with an initial position."""
        queen = Queen(Color.BLACK, position=(3, 7))

        assert queen.position == (3, 7)
        assert queen.file == 3
        assert queen.rank == 7

    def test_piece_repr(self):
        """Piece repr should include color and type."""
        king = King(Color.WHITE)
        assert "WHITE" in repr(king)
        assert "KING" in repr(king)

    def test_piece_repr_with_position(self):
        """Piece repr should include position if set."""
        rook = Rook(Color.BLACK, position=(0, 7))
        assert "(0, 7)" in repr(rook)

    def test_all_piece_types_exist(self):
        """All standard chess piece types should be available."""
        pieces = [
            King(Color.WHITE),
            Queen(Color.WHITE),
            Bishop(Color.WHITE),
            Knight(Color.WHITE),
            Rook(Color.WHITE),
            Pawn(Color.WHITE),
        ]

        piece_types = {p.piece_type for p in pieces}
        expected_types = {
            PieceType.KING,
            PieceType.QUEEN,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
            PieceType.PAWN,
        }

        assert piece_types == expected_types
