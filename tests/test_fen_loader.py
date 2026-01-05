import pytest

from chess import Board, Color, PieceType
from chess.game_state import GameState
from chess.fen_loader import FENLoader
from chess.fen import FENParser, FENError


class TestFENLoaderBasic:
    """Basic tests for FEN loading."""

    def test_load_starting_position_piece_count(self):
        """Loading starting FEN should place 32 pieces."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load_starting_position()

        piece_count = sum(1 for _, _, piece in board if piece is not None)
        assert piece_count == 32

    def test_load_starting_position_white_king(self):
        """Loading starting FEN should place white king at e1."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load_starting_position()

        piece = board.get_piece(4, 0)
        assert piece is not None
        assert piece.piece_type == PieceType.KING
        assert piece.color == Color.WHITE

    def test_load_starting_position_black_king(self):
        """Loading starting FEN should place black king at e8."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load_starting_position()

        piece = board.get_piece(4, 7)
        assert piece is not None
        assert piece.piece_type == PieceType.KING
        assert piece.color == Color.BLACK

    def test_load_empty_board(self):
        """Loading empty FEN should result in empty board."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/8/8/8/8 w - - 0 1")

        piece_count = sum(1 for _, _, piece in board if piece is not None)
        assert piece_count == 0


class TestFENLoaderGameState:
    """Tests for game state configuration via FEN loading."""

    def test_load_sets_white_turn(self):
        """Loading FEN with 'w' should set white to move."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/8/8/8/8 w - - 0 1")

        assert game_state.current_turn == Color.WHITE

    def test_load_sets_black_turn(self):
        """Loading FEN with 'b' should set black to move."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/8/8/8/8 b - - 0 1")

        assert game_state.current_turn == Color.BLACK

    def test_load_clears_move_history(self):
        """Loading FEN should clear move history."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        # Simulate some moves happened
        game_state.move_history.append(None)  # Dummy move

        loader.load("8/8/8/8/8/8/8/8 w - - 0 1")

        assert len(game_state.move_history) == 0

    def test_load_sets_castling_rights(self):
        """Loading FEN should set castling rights."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/8/8/8/8 w Kq - 0 1")

        assert game_state.castling_rights.white_kingside is True
        assert game_state.castling_rights.white_queenside is False
        assert game_state.castling_rights.black_kingside is False
        assert game_state.castling_rights.black_queenside is True

    def test_load_sets_en_passant_target(self):
        """Loading FEN with en passant should set target."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/4p3/8/8/8 w - e3 0 1")

        # e3 landing square means pawn at e4 (index 3)
        assert game_state.current_en_passant_target == (4, 3)

    def test_load_sets_halfmove_clock(self):
        """Loading FEN should set halfmove clock."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/8/8/8/8 w - - 42 1")

        assert game_state.halfmove_clock == 42

    def test_load_sets_fullmove_number(self):
        """Loading FEN should set fullmove number."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load("8/8/8/8/8/8/8/8 w - - 0 25")

        assert game_state.fullmove_number == 25


class TestFENLoaderErrors:
    """Tests for FEN loading error handling."""

    def test_invalid_fen_raises_error(self):
        """Invalid FEN should raise FENError."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        with pytest.raises(FENError):
            loader.load("invalid fen string")

    def test_incomplete_fen_raises_error(self):
        """Incomplete FEN should raise FENError."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        with pytest.raises(FENError):
            loader.load("8/8/8/8/8/8/8/8 w")


class TestFENLoaderPiecePositions:
    """Tests for correct piece positioning via FEN loading."""

    def test_pieces_have_correct_positions(self):
        """Loaded pieces should have correct position attributes."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        loader.load_starting_position()

        # Check white king position attribute
        white_king = board.get_piece(4, 0)
        assert white_king.position == (4, 0)

        # Check black queen position attribute
        black_queen = board.get_piece(3, 7)
        assert black_queen.position == (3, 7)

    def test_load_custom_position(self):
        """Loading custom position should place pieces correctly."""
        board = Board()
        game_state = GameState()
        loader = FENLoader(board, game_state)

        # Famous position: "The Opera Game" final position
        loader.load("1n2kb1r/p4ppp/4q3/4p1B1/4P3/8/PPP2PPP/2KR4 b k - 1 17")

        # Check specific pieces
        assert board.get_piece(1, 7).piece_type == PieceType.KNIGHT  # b8
        assert board.get_piece(4, 7).piece_type == PieceType.KING    # e8
        assert board.get_piece(5, 7).piece_type == PieceType.BISHOP  # f8
        assert board.get_piece(7, 7).piece_type == PieceType.ROOK    # h8
        assert board.get_piece(4, 5).piece_type == PieceType.QUEEN   # e6
        assert board.get_piece(6, 4).piece_type == PieceType.BISHOP  # g5 (white)
        assert board.get_piece(3, 0).piece_type == PieceType.ROOK    # d1 (white)
        assert board.get_piece(2, 0).piece_type == PieceType.KING    # c1 (white)

        # Verify colors
        assert board.get_piece(1, 7).color == Color.BLACK
        assert board.get_piece(6, 4).color == Color.WHITE
        assert board.get_piece(2, 0).color == Color.WHITE

        # Verify it's black to move
        assert game_state.current_turn == Color.BLACK

        # Verify only black kingside castling available
        assert game_state.castling_rights.black_kingside is True
        assert game_state.castling_rights.black_queenside is False
        assert game_state.castling_rights.white_kingside is False
        assert game_state.castling_rights.white_queenside is False
