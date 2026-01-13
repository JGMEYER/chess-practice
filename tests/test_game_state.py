"""Tests for GameState - tracking game state and move history."""

import pytest

from chess import Color
from chess.game_state import GameState
from chess.move import Move
from chess.pieces import Pawn, Rook, Queen
from chess.fen import CastlingRights, FENData


@pytest.fixture
def game_state():
    return GameState()


class TestGameStateInitialization:
    """Tests for initial game state."""

    def test_initial_turn_is_white(self, game_state):
        """Game starts with white to move."""
        assert game_state.current_turn == Color.WHITE

    def test_initial_move_history_empty(self, game_state):
        """Move history starts empty."""
        assert len(game_state.move_history) == 0

    def test_initial_redo_history_empty(self, game_state):
        """Redo history starts empty."""
        assert len(game_state.redo_history) == 0

    def test_initial_halfmove_clock(self, game_state):
        """Halfmove clock starts at 0."""
        assert game_state.halfmove_clock == 0

    def test_initial_fullmove_number(self, game_state):
        """Fullmove number starts at 1."""
        assert game_state.fullmove_number == 1

    def test_default_castling_rights(self, game_state):
        """Default castling rights are all available."""
        rights = game_state.castling_rights
        assert rights.white_kingside is True
        assert rights.white_queenside is True
        assert rights.black_kingside is True
        assert rights.black_queenside is True


class TestRecordMove:
    """Tests for recording moves."""

    def test_record_move_adds_to_history(self, game_state):
        """Recording a move adds it to history."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)

        game_state.record_move(move)

        assert len(game_state.move_history) == 1
        assert game_state.move_history[0] == move

    def test_record_move_switches_turn(self, game_state):
        """Recording a move switches the turn."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)

        game_state.record_move(move)

        assert game_state.current_turn == Color.BLACK

    def test_record_multiple_moves(self, game_state):
        """Recording multiple moves alternates turns."""
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)

        move1 = Move(from_square=(4, 1), to_square=(4, 3), piece=white_pawn)
        move2 = Move(from_square=(4, 6), to_square=(4, 4), piece=black_pawn)

        game_state.record_move(move1)
        game_state.record_move(move2)

        assert len(game_state.move_history) == 2
        assert game_state.current_turn == Color.WHITE


class TestLastMove:
    """Tests for last_move property."""

    def test_last_move_returns_none_when_empty(self, game_state):
        """last_move returns None when no moves."""
        assert game_state.last_move is None

    def test_last_move_returns_most_recent(self, game_state):
        """last_move returns the most recent move."""
        pawn = Pawn(Color.WHITE)
        move1 = Move(from_square=(4, 1), to_square=(4, 2), piece=pawn)
        move2 = Move(from_square=(4, 2), to_square=(4, 3), piece=pawn)

        game_state.record_move(move1)
        game_state.record_move(move2)

        assert game_state.last_move == move2


class TestEnPassantTarget:
    """Tests for en passant target tracking."""

    def test_en_passant_from_initial_setting(self, game_state):
        """En passant target returns initial setting when no moves."""
        game_state._initial_en_passant_target = (4, 3)
        assert game_state.current_en_passant_target == (4, 3)

    def test_en_passant_from_last_move(self, game_state):
        """En passant target returns from last move."""
        pawn = Pawn(Color.WHITE)
        move = Move(
            from_square=(4, 1),
            to_square=(4, 3),
            piece=pawn,
            current_en_passant_target=(4, 3),
        )
        game_state.record_move(move)

        assert game_state.current_en_passant_target == (4, 3)

    def test_en_passant_taking_square_for_white(self, game_state):
        """En passant taking square is one rank ahead for white."""
        game_state.current_turn = Color.WHITE
        pawn = Pawn(Color.BLACK)
        move = Move(
            from_square=(4, 6),
            to_square=(4, 4),
            piece=pawn,
            current_en_passant_target=(4, 4),
        )
        game_state.record_move(move)
        game_state.current_turn = Color.WHITE  # Reset for test

        # Taking square should be e5 + 1 rank = e6
        assert game_state.current_en_passant_taking_square == (4, 5)

    def test_en_passant_taking_square_none_when_no_target(self, game_state):
        """En passant taking square is None when no target."""
        assert game_state.current_en_passant_taking_square is None


class TestCapturedPieces:
    """Tests for captured pieces tracking."""

    def test_captured_pieces_empty_initially(self, game_state):
        """No captured pieces at start."""
        assert len(game_state.captured_pieces) == 0

    def test_captured_pieces_returns_captures(self, game_state):
        """captured_pieces returns all captured pieces."""
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        black_rook = Rook(Color.BLACK)

        move1 = Move(
            from_square=(4, 3),
            to_square=(3, 4),
            piece=white_pawn,
            captured_piece=black_pawn,
        )
        move2 = Move(
            from_square=(3, 4),
            to_square=(3, 7),
            piece=white_pawn,
            captured_piece=black_rook,
        )

        game_state.record_move(move1)
        game_state.record_move(move2)

        captured = game_state.captured_pieces
        assert len(captured) == 2
        assert black_pawn in captured
        assert black_rook in captured

    def test_captured_pieces_excludes_non_captures(self, game_state):
        """Non-capture moves don't add to captured pieces."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)

        game_state.record_move(move)

        assert len(game_state.captured_pieces) == 0


class TestMoveCount:
    """Tests for move count property."""

    def test_move_count_zero_initially(self, game_state):
        """Move count is 0 initially."""
        assert game_state.move_count == 0

    def test_move_count_increments(self, game_state):
        """Move count increments with each move."""
        pawn = Pawn(Color.WHITE)

        for i in range(5):
            move = Move(from_square=(4, i), to_square=(4, i + 1), piece=pawn)
            game_state.record_move(move)

        assert game_state.move_count == 5


class TestUndoRedo:
    """Tests for undo/redo capability checks."""

    def test_can_undo_false_when_no_history(self, game_state):
        """Cannot undo when no moves."""
        assert game_state.can_undo() is False

    def test_can_undo_true_when_moves_exist(self, game_state):
        """Can undo when moves exist."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)
        game_state.record_move(move)

        assert game_state.can_undo() is True

    def test_can_redo_false_when_no_redo_history(self, game_state):
        """Cannot redo when no redo history."""
        assert game_state.can_redo() is False

    def test_can_redo_true_when_redo_exists(self, game_state):
        """Can redo when redo history exists."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)
        game_state.redo_history.append(move)

        assert game_state.can_redo() is True


class TestReset:
    """Tests for reset functionality."""

    def test_reset_clears_move_history(self, game_state):
        """Reset clears move history."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)
        game_state.record_move(move)

        game_state.reset()

        assert len(game_state.move_history) == 0

    def test_reset_clears_redo_history(self, game_state):
        """Reset clears redo history."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)
        game_state.redo_history.append(move)

        game_state.reset()

        assert len(game_state.redo_history) == 0

    def test_reset_restores_white_turn(self, game_state):
        """Reset restores white to move."""
        game_state.current_turn = Color.BLACK

        game_state.reset()

        assert game_state.current_turn == Color.WHITE

    def test_reset_restores_counters(self, game_state):
        """Reset restores halfmove and fullmove counters."""
        game_state.halfmove_clock = 50
        game_state.fullmove_number = 25

        game_state.reset()

        assert game_state.halfmove_clock == 0
        assert game_state.fullmove_number == 1


class TestLoadFromFENData:
    """Tests for loading state from FEN data."""

    def test_load_sets_active_color(self, game_state):
        """Loading FEN sets active color."""
        fen_data = FENData(active_color=Color.BLACK)

        game_state.load_from_fen_data(fen_data)

        assert game_state.current_turn == Color.BLACK

    def test_load_sets_castling_rights(self, game_state):
        """Loading FEN sets castling rights."""
        castling = CastlingRights(
            white_kingside=True,
            white_queenside=False,
            black_kingside=False,
            black_queenside=True,
        )
        fen_data = FENData(castling_rights=castling)

        game_state.load_from_fen_data(fen_data)

        assert game_state.castling_rights.white_kingside is True
        assert game_state.castling_rights.white_queenside is False
        assert game_state.castling_rights.black_kingside is False
        assert game_state.castling_rights.black_queenside is True

    def test_load_sets_en_passant_target(self, game_state):
        """Loading FEN sets en passant target."""
        fen_data = FENData(en_passant_target=(4, 2))

        game_state.load_from_fen_data(fen_data)

        assert game_state._initial_en_passant_target == (4, 2)

    def test_load_sets_counters(self, game_state):
        """Loading FEN sets halfmove and fullmove counters."""
        fen_data = FENData(halfmove_clock=10, fullmove_number=15)

        game_state.load_from_fen_data(fen_data)

        assert game_state.halfmove_clock == 10
        assert game_state.fullmove_number == 15

    def test_load_clears_histories(self, game_state):
        """Loading FEN clears move histories."""
        pawn = Pawn(Color.WHITE)
        move = Move(from_square=(4, 1), to_square=(4, 3), piece=pawn)
        game_state.record_move(move)
        game_state.redo_history.append(move)

        fen_data = FENData()
        game_state.load_from_fen_data(fen_data)

        assert len(game_state.move_history) == 0
        assert len(game_state.redo_history) == 0
