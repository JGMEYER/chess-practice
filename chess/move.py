from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .piece import Piece


@dataclass
class Move:
    """Represents a chess move."""

    from_square: tuple[int, int]
    to_square: tuple[int, int]
    piece: Piece
    captured_piece: Piece | None = None
    current_en_passant_target: tuple[int, int] | None = None

    def __repr__(self) -> str:
        capture_str = f" captures {self.captured_piece}" if self.captured_piece else ""
        en_passant_str = f", new en passant target is {self.current_en_passant_target}" if self.current_en_passant_target else ""
        return f"Move({self.piece} from {self.from_square} to {self.to_square}{capture_str}{en_passant_str})"
