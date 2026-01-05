import pytest

from chess import Color, PieceType
from chess.fen import FENParser, FENData, CastlingRights, FENError


class TestFENParserPiecePlacement:
    """Tests for FEN piece placement parsing."""

    def test_starting_position_white_king(self):
        """Starting FEN should have white king at e1."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        data = FENParser.parse(fen)

        piece = data.pieces.get((4, 0))
        assert piece is not None
        assert piece.piece_type == PieceType.KING
        assert piece.color == Color.WHITE

    def test_starting_position_black_king(self):
        """Starting FEN should have black king at e8."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        data = FENParser.parse(fen)

        piece = data.pieces.get((4, 7))
        assert piece is not None
        assert piece.piece_type == PieceType.KING
        assert piece.color == Color.BLACK

    def test_starting_position_piece_count(self):
        """Starting position should have 32 pieces."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        data = FENParser.parse(fen)
        assert len(data.pieces) == 32

    def test_empty_board(self):
        """FEN with all empty ranks should produce no pieces."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)
        assert len(data.pieces) == 0

    def test_single_piece_center(self):
        """Single piece in center should parse correctly."""
        fen = "8/8/8/8/4K3/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)

        assert len(data.pieces) == 1
        piece = data.pieces.get((4, 3))  # e4
        assert piece is not None
        assert piece.piece_type == PieceType.KING
        assert piece.color == Color.WHITE

    def test_all_piece_types(self):
        """All piece types should be recognized."""
        # Position with one of each piece type for each color
        fen = "kqrbnp2/8/8/8/8/8/8/KQRBNP2 w - - 0 1"
        data = FENParser.parse(fen)

        # White pieces on rank 1
        assert data.pieces[(0, 0)].piece_type == PieceType.KING
        assert data.pieces[(1, 0)].piece_type == PieceType.QUEEN
        assert data.pieces[(2, 0)].piece_type == PieceType.ROOK
        assert data.pieces[(3, 0)].piece_type == PieceType.BISHOP
        assert data.pieces[(4, 0)].piece_type == PieceType.KNIGHT
        assert data.pieces[(5, 0)].piece_type == PieceType.PAWN

        # Black pieces on rank 8
        assert data.pieces[(0, 7)].piece_type == PieceType.KING
        assert data.pieces[(1, 7)].piece_type == PieceType.QUEEN
        assert data.pieces[(2, 7)].piece_type == PieceType.ROOK
        assert data.pieces[(3, 7)].piece_type == PieceType.BISHOP
        assert data.pieces[(4, 7)].piece_type == PieceType.KNIGHT
        assert data.pieces[(5, 7)].piece_type == PieceType.PAWN


class TestFENParserActiveColor:
    """Tests for FEN active color parsing."""

    def test_white_to_move(self):
        """'w' should set active color to WHITE."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)
        assert data.active_color == Color.WHITE

    def test_black_to_move(self):
        """'b' should set active color to BLACK."""
        fen = "8/8/8/8/8/8/8/8 b - - 0 1"
        data = FENParser.parse(fen)
        assert data.active_color == Color.BLACK


class TestFENParserCastling:
    """Tests for FEN castling rights parsing."""

    def test_all_castling_rights(self):
        """'KQkq' should enable all castling."""
        fen = "8/8/8/8/8/8/8/8 w KQkq - 0 1"
        data = FENParser.parse(fen)

        assert data.castling_rights.white_kingside is True
        assert data.castling_rights.white_queenside is True
        assert data.castling_rights.black_kingside is True
        assert data.castling_rights.black_queenside is True

    def test_no_castling_rights(self):
        """'-' should disable all castling."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)

        assert data.castling_rights.white_kingside is False
        assert data.castling_rights.white_queenside is False
        assert data.castling_rights.black_kingside is False
        assert data.castling_rights.black_queenside is False

    def test_white_kingside_only(self):
        """'K' should enable only white kingside."""
        fen = "8/8/8/8/8/8/8/8 w K - 0 1"
        data = FENParser.parse(fen)

        assert data.castling_rights.white_kingside is True
        assert data.castling_rights.white_queenside is False
        assert data.castling_rights.black_kingside is False
        assert data.castling_rights.black_queenside is False

    def test_partial_castling_Kq(self):
        """'Kq' should enable white kingside and black queenside."""
        fen = "8/8/8/8/8/8/8/8 w Kq - 0 1"
        data = FENParser.parse(fen)

        assert data.castling_rights.white_kingside is True
        assert data.castling_rights.white_queenside is False
        assert data.castling_rights.black_kingside is False
        assert data.castling_rights.black_queenside is True

    def test_castling_order_independent(self):
        """Castling characters can appear in any order."""
        fen = "8/8/8/8/8/8/8/8 w qKkQ - 0 1"
        data = FENParser.parse(fen)

        assert data.castling_rights.white_kingside is True
        assert data.castling_rights.white_queenside is True
        assert data.castling_rights.black_kingside is True
        assert data.castling_rights.black_queenside is True


class TestFENParserEnPassant:
    """Tests for FEN en passant parsing."""

    def test_no_en_passant(self):
        """'-' should set en passant to None."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)
        assert data.en_passant_target is None

    def test_en_passant_e3(self):
        """'e3' should indicate black pawn at e4 (rank index 3)."""
        fen = "8/8/8/8/4p3/8/8/8 w - e3 0 1"
        data = FENParser.parse(fen)
        # e3 landing square means black pawn at e4
        assert data.en_passant_target == (4, 3)

    def test_en_passant_d6(self):
        """'d6' should indicate white pawn at d5 (rank index 4)."""
        fen = "8/8/8/3P4/8/8/8/8 b - d6 0 1"
        data = FENParser.parse(fen)
        # d6 landing square means white pawn at d5
        assert data.en_passant_target == (3, 4)

    def test_en_passant_a3(self):
        """'a3' should indicate black pawn at a4."""
        fen = "8/8/8/8/p7/8/8/8 w - a3 0 1"
        data = FENParser.parse(fen)
        assert data.en_passant_target == (0, 3)

    def test_en_passant_h6(self):
        """'h6' should indicate white pawn at h5."""
        fen = "8/8/8/7P/8/8/8/8 b - h6 0 1"
        data = FENParser.parse(fen)
        assert data.en_passant_target == (7, 4)


class TestFENParserMoveCounters:
    """Tests for FEN move counter parsing."""

    def test_halfmove_clock_zero(self):
        """Halfmove clock of 0 should parse correctly."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)
        assert data.halfmove_clock == 0

    def test_halfmove_clock_nonzero(self):
        """Halfmove clock should parse correctly."""
        fen = "8/8/8/8/8/8/8/8 w - - 42 1"
        data = FENParser.parse(fen)
        assert data.halfmove_clock == 42

    def test_fullmove_number_one(self):
        """Fullmove number of 1 should parse correctly."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        data = FENParser.parse(fen)
        assert data.fullmove_number == 1

    def test_fullmove_number_large(self):
        """Large fullmove number should parse correctly."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 125"
        data = FENParser.parse(fen)
        assert data.fullmove_number == 125


class TestFENParserErrors:
    """Tests for FEN parsing error handling."""

    def test_missing_fields(self):
        """FEN with missing fields should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_too_many_fields(self):
        """FEN with too many fields should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1 extra"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_invalid_piece_char(self):
        """Invalid piece character should raise FENError."""
        fen = "rnbXkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_wrong_rank_count(self):
        """Wrong number of ranks should raise FENError."""
        fen = "8/8/8/8/8/8/8 w KQkq - 0 1"  # Only 7 ranks
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_invalid_file_count(self):
        """Rank with wrong file count should raise FENError."""
        fen = "rnbqkbnr/ppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_invalid_active_color(self):
        """Invalid active color should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 x - - 0 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_invalid_castling_char(self):
        """Invalid castling character should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w KQkX - 0 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_invalid_en_passant_file(self):
        """Invalid en passant file should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w - x3 0 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_invalid_en_passant_rank(self):
        """Invalid en passant rank should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w - e5 0 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_negative_halfmove(self):
        """Negative halfmove clock should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w - - -1 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_zero_fullmove(self):
        """Zero fullmove number should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 0"
        with pytest.raises(FENError):
            FENParser.parse(fen)

    def test_non_numeric_halfmove(self):
        """Non-numeric halfmove clock should raise FENError."""
        fen = "8/8/8/8/8/8/8/8 w - - abc 1"
        with pytest.raises(FENError):
            FENParser.parse(fen)


class TestFENDataDefaults:
    """Tests for FEN data structure defaults."""

    def test_castling_rights_default(self):
        """CastlingRights should default to all True."""
        rights = CastlingRights()
        assert rights.white_kingside is True
        assert rights.white_queenside is True
        assert rights.black_kingside is True
        assert rights.black_queenside is True

    def test_fen_data_defaults(self):
        """FENData should have sensible defaults."""
        data = FENData()
        assert data.pieces == {}
        assert data.active_color == Color.WHITE
        assert data.en_passant_target is None
        assert data.halfmove_clock == 0
        assert data.fullmove_number == 1


class TestFENParserStartingFEN:
    """Tests for the STARTING_FEN constant."""

    def test_starting_fen_is_valid(self):
        """STARTING_FEN should be a valid FEN string."""
        data = FENParser.parse(FENParser.STARTING_FEN)
        assert len(data.pieces) == 32
        assert data.active_color == Color.WHITE
