from __future__ import annotations

from .constants import Color, PieceType
from .move import Move
from .piece import Piece


class GameState:
    """Tracks the state of a chess game."""

    def __init__(self):
        """Initialize a new game state."""
        self.move_history: list[Move] = []
        self.current_turn: Color = Color.WHITE

    @property
    def last_move(self) -> Move | None:
        """Get the last move played, or None if no moves yet."""
        return self.move_history[-1] if self.move_history else None
    
    @property
    def current_en_passant_target(self) -> tuple[int, int] | None:
        """Get the current en passant target, or None if no target."""
        return (
            self.move_history[-1].current_en_passant_target
            if self.move_history else None
        )
    
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
