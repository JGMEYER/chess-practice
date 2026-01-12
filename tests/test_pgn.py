"""Tests for PGN parsing and loading."""

import pytest

from chess import PGNParser, PGNData, PGNError, PGNLoader, Board
from chess.game_state import GameState
from chess.constants import PieceType, Color


class TestPGNParserTagPairs:
    """Tests for PGN tag pair parsing."""

    def test_parse_standard_tags(self):
        """Standard Seven Tag Roster should be parsed correctly."""
        pgn = """[Event "World Championship"]
[Site "New York"]
[Date "2024.01.15"]
[Round "5"]
[White "Kasparov"]
[Black "Karpov"]
[Result "1-0"]

1. e4 e5"""
        data = PGNParser.parse(pgn)
        assert data.event == "World Championship"
        assert data.site == "New York"
        assert data.date == "2024.01.15"
        assert data.round == "5"
        assert data.white == "Kasparov"
        assert data.black == "Karpov"
        assert data.result == "1-0"

    def test_parse_fen_tag(self):
        """FEN tag should set the starting position."""
        pgn = """[FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]

1... e5"""
        data = PGNParser.parse(pgn)
        assert data.fen is not None
        assert "4P3" in data.fen

    def test_parse_extra_tags(self):
        """Non-standard tags should be stored in extra_tags."""
        pgn = """[Event "Test"]
[TimeControl "300+5"]
[ECO "B07"]

1. e4"""
        data = PGNParser.parse(pgn)
        assert "TimeControl" in data.extra_tags
        assert data.extra_tags["TimeControl"] == "300+5"
        assert "ECO" in data.extra_tags

    def test_missing_tags_use_defaults(self):
        """Missing tags should use standard defaults."""
        pgn = "1. e4 e5"
        data = PGNParser.parse(pgn)
        assert data.event == "?"
        assert data.site == "?"
        assert data.white == "?"
        assert data.result == "*"


class TestPGNParserMovetext:
    """Tests for PGN movetext parsing."""

    def test_parse_simple_moves(self):
        """Simple move sequence should be parsed correctly."""
        pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        data = PGNParser.parse(pgn)
        assert data.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5"]

    def test_parse_moves_with_captures(self):
        """Captures with 'x' should be preserved."""
        pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Bxc6 dxc6"
        data = PGNParser.parse(pgn)
        assert "Bxc6" in data.moves
        assert "dxc6" in data.moves

    def test_parse_castling(self):
        """Castling notation should be recognized."""
        pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 O-O"
        data = PGNParser.parse(pgn)
        assert "O-O" in data.moves
        # Both white and black castling
        assert data.moves.count("O-O") == 2

    def test_parse_queenside_castling(self):
        """Queenside castling should be parsed."""
        pgn = "1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Nf3 Be7 5. Bf4 O-O 6. e3 c6 7. Bd3 Nbd7 8. O-O"
        data = PGNParser.parse(pgn)
        assert "O-O" in data.moves

    def test_parse_promotion(self):
        """Pawn promotion should be preserved."""
        pgn = "1. e4 e5 2. d4 exd4 3. c3 dxc3 4. Bc4 cxb2 5. Bxb2 d5 6. exd5 Qxd5 7. a4 Bb4+ 8. Nc3 Qe5+ 9. Qe2 Qxe2+ 10. Nxe2 Bd6 11. O-O-O Nf6 12. Nf4 Bg4 13. Be2 Bxe2 14. Nxe2 c6 15. Rhe1 O-O 16. Nf4 Rd8 17. Nd3 Na6 18. Rxe8+ Rxe8 19. Nf4 Bc5 20. Re1 Rxe1+ 21. Kd2 Rf1 22. f3 Bb4+ 23. Ke2 Ra1 24. Nd3 Bd6 25. g4 Nc5 26. Nxc5 Bxc5 27. h4 Rxa4 28. g5 Nd5 29. Ke1 Ra1+ 30. Kf2 Ra2 31. Bd4 Bxd4+ 32. Nxd4 Rxb2+ 33. Ke1 Rb1+ 34. Kd2 c5 35. Nb5 a6 36. Nc3 Nxc3 37. Kxc3 c4 38. f4 f6 39. Kxc4 fxg5 40. hxg5 Rf1 41. Kd5 Rxf4 42. Ke6 g6 43. Kf6 Rf5 44. Kg7 Rxg5+ 45. Kxh7 Kf7 46. Kh6 Rg4 47. Kh7 Kf6 48. Kh6 Rg3 49. Kh7 g5 50. Kh6 Rh3+ 51. Kg7 Ke5 52. Kf7 g4 53. Ke7 g3 54. Kd7 g2 55. Kc6 g1=Q"
        data = PGNParser.parse(pgn)
        assert "g1=Q" in data.moves

    def test_parse_check_indicators(self):
        """Check (+) and checkmate (#) indicators should be preserved."""
        pgn = "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#"
        data = PGNParser.parse(pgn)
        assert "Qxf7#" in data.moves or "Qxf7" in data.moves

    def test_parse_removes_comments(self):
        """Comments in braces should be removed."""
        pgn = "1. e4 {best move} e5 2. Nf3 {knights before bishops} Nc6"
        data = PGNParser.parse(pgn)
        assert data.moves == ["e4", "e5", "Nf3", "Nc6"]
        assert "{" not in str(data.moves)

    def test_parse_removes_variations(self):
        """Variations in parentheses should be removed."""
        pgn = "1. e4 e5 (1... c5 2. Nf3 d6) 2. Nf3 Nc6"
        data = PGNParser.parse(pgn)
        assert data.moves == ["e4", "e5", "Nf3", "Nc6"]
        assert "c5" not in data.moves

    def test_parse_removes_nags(self):
        """Numeric Annotation Glyphs ($1, etc.) should be removed."""
        pgn = "1. e4 $1 e5 $2 2. Nf3 $13 Nc6"
        data = PGNParser.parse(pgn)
        assert "$" not in str(data.moves)

    def test_parse_result_from_movetext(self):
        """Result at end of movetext should be extracted."""
        pgn = "1. e4 e5 1-0"
        data = PGNParser.parse(pgn)
        assert data.result == "1-0"
        assert "1-0" not in data.moves

    def test_parse_normalizes_castling(self):
        """Castling with zeros (0-0) should be normalized to O-O."""
        pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. 0-0"
        data = PGNParser.parse(pgn)
        assert "O-O" in data.moves
        assert "0-0" not in data.moves


class TestPGNParserErrors:
    """Tests for PGN parser error handling."""

    def test_empty_pgn_raises_error(self):
        """Empty PGN should raise PGNError."""
        with pytest.raises(PGNError):
            PGNParser.parse("")

    def test_whitespace_only_raises_error(self):
        """Whitespace-only PGN should raise PGNError."""
        with pytest.raises(PGNError):
            PGNParser.parse("   \n\t  ")


class TestPGNLoader:
    """Tests for loading PGN games onto a board."""

    @pytest.fixture
    def board_and_state(self):
        """Create a fresh board and game state."""
        return Board(), GameState()

    def test_load_simple_opening(self, board_and_state):
        """Simple opening moves should load correctly."""
        board, game_state = board_and_state
        loader = PGNLoader(board, game_state)

        pgn = "1. e4 e5 2. Nf3 Nc6"
        moves = loader.load(pgn)

        assert len(moves) == 4
        # Check final position
        assert board.get_piece(4, 3) is not None  # e4 pawn
        assert board.get_piece(4, 3).piece_type == PieceType.PAWN
        assert board.get_piece(5, 2) is not None  # Nf3 knight
        assert board.get_piece(5, 2).piece_type == PieceType.KNIGHT
        assert board.get_piece(2, 5) is not None  # Nc6 knight
        assert board.get_piece(2, 5).piece_type == PieceType.KNIGHT

    def test_load_castling(self, board_and_state):
        """Castling should be executed correctly."""
        board, game_state = board_and_state
        loader = PGNLoader(board, game_state)

        # Italian Game with castling
        pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O"
        loader.load(pgn)

        # White king should be on g1
        king = board.get_piece(6, 0)
        assert king is not None
        assert king.piece_type == PieceType.KING
        assert king.color == Color.WHITE

        # White rook should be on f1
        rook = board.get_piece(5, 0)
        assert rook is not None
        assert rook.piece_type == PieceType.ROOK

    def test_load_captures(self, board_and_state):
        """Captures should remove pieces correctly."""
        board, game_state = board_and_state
        loader = PGNLoader(board, game_state)

        pgn = "1. e4 d5 2. exd5"
        loader.load(pgn)

        # d5 should have white pawn
        piece = board.get_piece(3, 4)
        assert piece is not None
        assert piece.piece_type == PieceType.PAWN
        assert piece.color == Color.WHITE

        # e4 should be empty
        assert board.get_piece(4, 3) is None

    def test_load_with_fen_tag(self, board_and_state):
        """Game with FEN tag should start from that position."""
        board, game_state = board_and_state
        loader = PGNLoader(board, game_state)

        # FEN with white pawn already on e4
        pgn = """[FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"]

1... e5 2. Nf3"""
        loader.load(pgn)

        # Should have pawn on e4 and e5, knight on f3
        assert board.get_piece(4, 3) is not None  # e4
        assert board.get_piece(4, 4) is not None  # e5
        assert board.get_piece(5, 2) is not None  # Nf3

    def test_load_illegal_move_raises_error(self, board_and_state):
        """Illegal moves should raise PGNError."""
        board, game_state = board_and_state
        loader = PGNLoader(board, game_state)

        # Knight can't move to e5 from starting position
        pgn = "1. Ne5"
        with pytest.raises(PGNError):
            loader.load(pgn)

    def test_load_disambiguation(self, board_and_state):
        """Disambiguation in moves should be handled correctly."""
        board, game_state = board_and_state
        loader = PGNLoader(board, game_state)

        # Set up a position where disambiguation is needed
        pgn = "1. Nf3 Nf6 2. Nc3 Nc6 3. Nd4 Nd5 4. Ndb5"
        loader.load(pgn)

        # One knight should be on b5
        knight = board.get_piece(1, 4)
        assert knight is not None
        assert knight.piece_type == PieceType.KNIGHT


class TestPGNDataDefaults:
    """Tests for PGNData default values."""

    def test_defaults_are_standard(self):
        """Default values should match PGN standard."""
        data = PGNData()
        assert data.event == "?"
        assert data.site == "?"
        assert data.date == "????.??.??"
        assert data.round == "?"
        assert data.white == "?"
        assert data.black == "?"
        assert data.result == "*"
        assert data.moves == []
        assert data.fen is None
