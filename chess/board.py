from __future__ import annotations

from typing import TYPE_CHECKING

from .piece import Piece

if TYPE_CHECKING:
    from .fen import FENData


class Board:
    """Represents the chess board and piece positions."""

    def __init__(self):
        """Initialize an empty 8x8 board."""
        # 8x8 grid, indexed as [file][rank] where file=0-7 (a-h), rank=0-7 (1-8)
        self._grid: list[list[Piece | None]] = [
            [None for _ in range(8)] for _ in range(8)
        ]

    def get_piece(self, file: int, rank: int) -> Piece | None:
        """
        Get the piece at the given position.

        Args:
            file: Column index 0-7 (a-h)
            rank: Row index 0-7 (1-8)

        Returns:
            The piece at that position, or None if empty
        """
        if not (0 <= file < 8 and 0 <= rank < 8):
            raise ValueError(f"Invalid position: file={file}, rank={rank}")
        return self._grid[file][rank]

    def set_piece(self, file: int, rank: int, piece: Piece | None) -> None:
        """
        Place a piece at the given position.

        Args:
            file: Column index 0-7 (a-h)
            rank: Row index 0-7 (1-8)
            piece: The piece to place, or None to clear the square
        """
        if not (0 <= file < 8 and 0 <= rank < 8):
            raise ValueError(f"Invalid position: file={file}, rank={rank}")
        self._grid[file][rank] = piece
        if piece is not None:
            piece.position = (file, rank)

    def clear(self) -> None:
        """Remove all pieces from the board."""
        for file in range(8):
            for rank in range(8):
                self._grid[file][rank] = None

    def load_from_fen_data(self, fen_data: FENData) -> None:
        """
        Load board position from parsed FEN data.

        Args:
            fen_data: Parsed FEN data containing piece positions
        """
        self.clear()
        for (file, rank), piece in fen_data.pieces.items():
            self.set_piece(file, rank, piece)

    def __iter__(self):
        """Iterate over all squares, yielding (file, rank, piece) tuples."""
        for file in range(8):
            for rank in range(8):
                yield file, rank, self._grid[file][rank]

    @staticmethod
    def file_to_letter(file: int) -> str:
        """Convert file index (0-7) to letter (a-h)."""
        return chr(ord("a") + file)

    @staticmethod
    def rank_to_number(rank: int) -> str:
        """Convert rank index (0-7) to number string (1-8)."""
        return str(rank + 1)
