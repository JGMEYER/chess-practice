from __future__ import annotations

from .constants import PieceType, Color


class Piece:
    """Base class for all chess pieces."""

    piece_type: PieceType  # To be set by subclasses
    move_offsets: list[tuple[int, int]] = []  # Movement pattern offsets
    is_sliding: bool = False  # True for rook, bishop, queen

    def __init__(self, color: Color, position: tuple[int, int] | None = None):
        """
        Initialize a chess piece.

        Args:
            color: The color of the piece (WHITE or BLACK)
            position: Optional (file, rank) tuple where file and rank are 0-7
        """
        self.color = color
        self.position = position

    def __repr__(self) -> str:
        pos_str = f" at {self.position}" if self.position else ""
        return f"{self.color.name} {self.piece_type.name}{pos_str}"

    @property
    def file(self) -> int | None:
        """Return the file (column) of the piece, 0-7 or None if not on board."""
        return self.position[0] if self.position else None

    @property
    def rank(self) -> int | None:
        """Return the rank (row) of the piece, 0-7 or None if not on board."""
        return self.position[1] if self.position else None
