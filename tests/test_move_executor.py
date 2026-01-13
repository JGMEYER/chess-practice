"""Tests for MoveExecutor - executing, undoing, and redoing moves."""

import pytest

from chess import Board, Color
from chess.game_state import GameState
from chess.move_executor import MoveExecutor
from chess.fen_loader import FENLoader
from chess.constants import PieceType
from chess.pieces import Pawn, Rook, Knight, Bishop, Queen, King


@pytest.fixture
def board():
    return Board()


@pytest.fixture
def game_state():
    return GameState()


@pytest.fixture
def executor(board, game_state):
    return MoveExecutor(board, game_state)


class TestBasicMoveExecution:
    """Tests for basic move execution."""

    def test_execute_simple_move(self, board, game_state, executor):
        """Execute a simple piece move."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        # Move e2-e4
        move = executor.execute_move((4, 1), (4, 3))

        assert board.get_piece(4, 1) is None  # e2 empty
        assert board.get_piece(4, 3) is not None  # e4 has pawn
        assert board.get_piece(4, 3).piece_type == PieceType.PAWN
        assert game_state.current_turn == Color.BLACK

    def test_execute_capture(self, board, game_state, executor):
        """Execute a capture move."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

        # Capture with pawn: exd5
        move = executor.execute_move((4, 3), (3, 4))

        assert board.get_piece(4, 3) is None  # e4 empty
        assert board.get_piece(3, 4).color == Color.WHITE  # d5 has white pawn
        assert move.captured_piece is not None
        assert move.captured_piece.piece_type == PieceType.PAWN

    def test_move_updates_piece_position(self, board, game_state, executor):
        """Piece's internal position is updated after move."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        # Move knight Ng1-f3
        executor.execute_move((6, 0), (5, 2))

        knight = board.get_piece(5, 2)
        assert knight.position == (5, 2)


class TestCastlingExecution:
    """Tests for castling move execution."""

    def test_kingside_castling(self, board, game_state, executor):
        """Execute kingside castling."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        # Kingside castle: O-O (e1-g1)
        move = executor.execute_move((4, 0), (6, 0))

        assert move.is_castling is True
        assert board.get_piece(4, 0) is None  # e1 empty
        assert board.get_piece(6, 0).piece_type == PieceType.KING  # g1 has king
        assert board.get_piece(7, 0) is None  # h1 empty
        assert board.get_piece(5, 0).piece_type == PieceType.ROOK  # f1 has rook

    def test_queenside_castling(self, board, game_state, executor):
        """Execute queenside castling."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        # Queenside castle: O-O-O (e1-c1)
        move = executor.execute_move((4, 0), (2, 0))

        assert move.is_castling is True
        assert board.get_piece(4, 0) is None  # e1 empty
        assert board.get_piece(2, 0).piece_type == PieceType.KING  # c1 has king
        assert board.get_piece(0, 0) is None  # a1 empty
        assert board.get_piece(3, 0).piece_type == PieceType.ROOK  # d1 has rook

    def test_castling_removes_castling_rights(self, board, game_state, executor):
        """Castling removes castling rights for that color."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        executor.execute_move((4, 0), (6, 0))  # O-O

        assert game_state.castling_rights.white_kingside is False
        assert game_state.castling_rights.white_queenside is False


class TestEnPassantExecution:
    """Tests for en passant move execution."""

    def test_en_passant_capture(self, board, game_state, executor):
        """Execute en passant capture."""
        fen_loader = FENLoader(board, game_state)
        # White pawn on e5, black pawn just moved d7-d5
        fen_loader.load("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")

        # En passant: exd6
        move = executor.execute_move((4, 4), (3, 5))

        assert move.is_en_passant is True
        assert board.get_piece(4, 4) is None  # e5 empty
        assert board.get_piece(3, 5).piece_type == PieceType.PAWN  # d6 has white pawn
        assert board.get_piece(3, 4) is None  # d5 empty (captured pawn removed)
        assert move.captured_piece is not None

    def test_pawn_double_move_sets_en_passant_target(self, board, game_state, executor):
        """Pawn double move sets up en passant target."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        # e2-e4
        move = executor.execute_move((4, 1), (4, 3))

        assert move.current_en_passant_target == (4, 3)


class TestPromotionExecution:
    """Tests for pawn promotion execution."""

    def test_promotion_to_queen(self, board, game_state, executor):
        """Execute pawn promotion to queen."""
        fen_loader = FENLoader(board, game_state)
        # White pawn on e7, ready to promote
        fen_loader.load("4k3/4P3/8/8/8/8/8/4K3 w - - 0 1")

        move = executor.execute_move((4, 6), (4, 7), PieceType.QUEEN)

        assert move.is_promotion is True
        assert board.get_piece(4, 7).piece_type == PieceType.QUEEN
        assert board.get_piece(4, 7).color == Color.WHITE

    def test_promotion_to_knight(self, board, game_state, executor):
        """Execute pawn promotion to knight (underpromotion)."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("4k3/4P3/8/8/8/8/8/4K3 w - - 0 1")

        move = executor.execute_move((4, 6), (4, 7), PieceType.KNIGHT)

        assert move.is_promotion is True
        assert move.promoted_to.piece_type == PieceType.KNIGHT
        assert board.get_piece(4, 7).piece_type == PieceType.KNIGHT

    def test_promotion_with_capture(self, board, game_state, executor):
        """Execute pawn promotion with capture."""
        fen_loader = FENLoader(board, game_state)
        # White pawn on e7, black rook on d8
        fen_loader.load("3rk3/4P3/8/8/8/8/8/4K3 w - - 0 1")

        move = executor.execute_move((4, 6), (3, 7), PieceType.QUEEN)

        assert move.is_promotion is True
        assert move.captured_piece is not None
        assert move.captured_piece.piece_type == PieceType.ROOK
        assert board.get_piece(3, 7).piece_type == PieceType.QUEEN


class TestUndoMove:
    """Tests for undoing moves."""

    def test_undo_simple_move(self, board, game_state, executor):
        """Undo a simple move restores board state."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        pawn = board.get_piece(4, 1)
        executor.execute_move((4, 1), (4, 3))
        executor.undo_move()

        assert board.get_piece(4, 1) == pawn  # Pawn back on e2
        assert board.get_piece(4, 3) is None  # e4 empty
        assert game_state.current_turn == Color.WHITE

    def test_undo_capture_restores_piece(self, board, game_state, executor):
        """Undo capture restores captured piece."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

        black_pawn = board.get_piece(3, 4)  # d5 pawn
        executor.execute_move((4, 3), (3, 4))  # exd5
        executor.undo_move()

        assert board.get_piece(3, 4) == black_pawn  # Black pawn restored
        assert board.get_piece(4, 3) is not None  # White pawn back

    def test_undo_castling(self, board, game_state, executor):
        """Undo castling restores king and rook."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        executor.execute_move((4, 0), (6, 0))  # O-O
        executor.undo_move()

        assert board.get_piece(4, 0).piece_type == PieceType.KING  # King on e1
        assert board.get_piece(7, 0).piece_type == PieceType.ROOK  # Rook on h1
        assert board.get_piece(6, 0) is None  # g1 empty
        assert board.get_piece(5, 0) is None  # f1 empty

    def test_undo_en_passant(self, board, game_state, executor):
        """Undo en passant restores both pawns."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")

        executor.execute_move((4, 4), (3, 5))  # exd6 e.p.
        executor.undo_move()

        assert board.get_piece(4, 4).piece_type == PieceType.PAWN  # White pawn on e5
        assert board.get_piece(3, 4).piece_type == PieceType.PAWN  # Black pawn on d5
        assert board.get_piece(3, 5) is None  # d6 empty

    def test_undo_promotion(self, board, game_state, executor):
        """Undo promotion restores pawn."""
        fen_loader = FENLoader(board, game_state)
        # e8 is free for promotion
        fen_loader.load("k7/4P3/8/8/8/8/8/4K3 w - - 0 1")

        executor.execute_move((4, 6), (4, 7), PieceType.QUEEN)
        executor.undo_move()

        assert board.get_piece(4, 6).piece_type == PieceType.PAWN  # Pawn back on e7
        assert board.get_piece(4, 7) is None  # e8 empty

    def test_undo_returns_none_when_no_history(self, board, game_state, executor):
        """Undo returns None when no moves to undo."""
        result = executor.undo_move()
        assert result is None


class TestRedoMove:
    """Tests for redoing moves."""

    def test_redo_undone_move(self, board, game_state, executor):
        """Redo restores undone move."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        executor.execute_move((4, 1), (4, 3))  # e4
        executor.undo_move()
        executor.redo_move()

        assert board.get_piece(4, 1) is None  # e2 empty
        assert board.get_piece(4, 3) is not None  # e4 has pawn
        assert game_state.current_turn == Color.BLACK

    def test_redo_castling(self, board, game_state, executor):
        """Redo castling."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        executor.execute_move((4, 0), (6, 0))  # O-O
        executor.undo_move()
        executor.redo_move()

        assert board.get_piece(6, 0).piece_type == PieceType.KING  # King on g1
        assert board.get_piece(5, 0).piece_type == PieceType.ROOK  # Rook on f1

    def test_redo_returns_none_when_no_history(self, board, game_state, executor):
        """Redo returns None when no moves to redo."""
        result = executor.redo_move()
        assert result is None

    def test_new_move_clears_redo_history(self, board, game_state, executor):
        """Making a new move clears redo history."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        executor.execute_move((4, 1), (4, 3))  # e4
        executor.undo_move()
        executor.execute_move((3, 1), (3, 3))  # d4 - different move

        assert len(game_state.redo_history) == 0
        result = executor.redo_move()
        assert result is None


class TestCastlingRightsUpdates:
    """Tests for castling rights being updated correctly."""

    def test_king_move_removes_both_castling_rights(self, board, game_state, executor):
        """Moving king removes both castling rights for that color."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        executor.execute_move((4, 0), (4, 1))  # Ke1-e2

        assert game_state.castling_rights.white_kingside is False
        assert game_state.castling_rights.white_queenside is False

    def test_kingside_rook_move_removes_kingside_right(self, board, game_state, executor):
        """Moving kingside rook removes only kingside castling."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        executor.execute_move((7, 0), (7, 1))  # Rh1-h2

        assert game_state.castling_rights.white_kingside is False
        assert game_state.castling_rights.white_queenside is True

    def test_queenside_rook_move_removes_queenside_right(self, board, game_state, executor):
        """Moving queenside rook removes only queenside castling."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        executor.execute_move((0, 0), (0, 1))  # Ra1-a2

        assert game_state.castling_rights.white_kingside is True
        assert game_state.castling_rights.white_queenside is False


class TestIsPromotionMove:
    """Tests for is_promotion_move check."""

    def test_white_pawn_promotion_rank(self, board, game_state, executor):
        """White pawn moving to rank 8 is promotion."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("4k3/4P3/8/8/8/8/8/4K3 w - - 0 1")

        assert executor.is_promotion_move((4, 6), (4, 7)) is True

    def test_black_pawn_promotion_rank(self, board, game_state, executor):
        """Black pawn moving to rank 1 is promotion."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("4k3/8/8/8/8/8/4p3/4K3 b - - 0 1")

        assert executor.is_promotion_move((4, 1), (4, 0)) is True

    def test_pawn_not_reaching_back_rank_not_promotion(self, board, game_state, executor):
        """Pawn not reaching back rank is not promotion."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()

        assert executor.is_promotion_move((4, 1), (4, 3)) is False

    def test_non_pawn_not_promotion(self, board, game_state, executor):
        """Non-pawn piece is never promotion."""
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("4k3/4R3/8/8/8/8/8/4K3 w - - 0 1")

        assert executor.is_promotion_move((4, 6), (4, 7)) is False
