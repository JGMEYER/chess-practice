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
    is_en_passant: bool = False
    is_castling: bool = False
    castling_rook_from: tuple[int, int] | None = None
    castling_rook_to: tuple[int, int] | None = None

    def __repr__(self) -> str:
        capture_str = f" captures {self.captured_piece}" if self.captured_piece else ""

        if self.is_castling:
            castling_type = "O-O" if self.to_square[0] == 6 else "O-O-O"  # kingside or queenside
            special_str = f" ({castling_type})"
        elif self.is_en_passant:
            special_str = " (en passant)"
        elif self.current_en_passant_target:
            special_str = f", new en passant target is {self.current_en_passant_target}"
        else:
            special_str = ""

        return f"Move({self.piece} from {self.from_square} to {self.to_square}{capture_str}{special_str})"
