from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import Color, PieceType
from .move import Move
from .piece import Piece

if TYPE_CHECKING:
    from .fen import CastlingRights, FENData


class GameState:
    """Tracks the state of a chess game."""

    def __init__(self):
        """Initialize a new game state."""
        self.move_history: list[Move] = []
        self.redo_history: list[Move] = []
        self.current_turn: Color = Color.WHITE
        self._castling_rights: CastlingRights | None = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        self._initial_en_passant_target: tuple[int, int] | None = None

    @property
    def castling_rights(self) -> CastlingRights:
        """Get castling rights, creating default if not set."""
        if self._castling_rights is None:
            from .fen import CastlingRights
            self._castling_rights = CastlingRights()
        return self._castling_rights

    @castling_rights.setter
    def castling_rights(self, value: CastlingRights) -> None:
        """Set castling rights."""
        self._castling_rights = value

    @property
    def last_move(self) -> Move | None:
        """Get the last move played, or None if no moves yet."""
        return self.move_history[-1] if self.move_history else None
    
    @property
    def current_en_passant_target(self) -> tuple[int, int] | None:
        """Get the current en passant target, or None if no target."""
        if self.move_history:
            return self.move_history[-1].current_en_passant_target
        return self._initial_en_passant_target
    
    @property
    def current_en_passant_taking_square(self) -> tuple[int, int] | None:
        """Get the current en passant taking square, or None if no target."""
        en_passant_target = self.current_en_passant_target
        forward_offset = 1 if self.current_turn == Color.WHITE else -1

        if not en_passant_target:
            return None

        target_file, target_rank = en_passant_target
        return (target_file, target_rank+forward_offset)

    def record_move(self, move: Move) -> None:
        """
        Record a move and switch turns.

        Args:
            move: The move to record
        """
        self.move_history.append(move)
        self.current_turn = (
            Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        )

    @property
    def captured_pieces(self) -> list[Piece]:
        """Get all captured pieces in order of capture."""
        return [
            move.captured_piece
            for move in self.move_history
            if move.captured_piece is not None
        ]

    @property
    def move_count(self) -> int:
        """Get the total number of moves played."""
        return len(self.move_history)

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.move_history) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_history) > 0

    def reset(self) -> None:
        """Reset to initial state."""
        self.move_history.clear()
        self.redo_history.clear()
        self.current_turn = Color.WHITE
        self._castling_rights = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self._initial_en_passant_target = None

    def load_from_fen_data(self, fen_data: FENData) -> None:
        """
        Load game state from parsed FEN data.

        Args:
            fen_data: Parsed FEN data containing game state
        """
        self.reset()
        self.current_turn = fen_data.active_color
        self.castling_rights = fen_data.castling_rights
        self.halfmove_clock = fen_data.halfmove_clock
        self.fullmove_number = fen_data.fullmove_number
        self._initial_en_passant_target = fen_data.en_passant_target
