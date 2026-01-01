from __future__ import annotations

import pygame

from chess.board import Board
from .sprites import SpriteLoader
from .constants import (
    SQUARE_SIZE,
    BOARD_SIZE,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
)


class PieceRenderer:
    """Renders chess pieces on the board."""

    def __init__(self, sprite_loader: SpriteLoader):
        """
        Initialize the piece renderer.

        Args:
            sprite_loader: The sprite loader containing piece images
        """
        self._sprite_loader = sprite_loader

    def draw_pieces(self, surface: pygame.Surface, board: Board) -> None:
        """
        Draw all pieces on the board.

        Args:
            surface: The pygame surface to draw on
            board: The chess board containing piece positions
        """
        for file, rank, piece in board:
            if piece is not None:
                sprite = self._sprite_loader.get_sprite(piece.color, piece.piece_type)

                # Calculate pixel position
                x = BOARD_OFFSET_X + file * SQUARE_SIZE
                # Flip rank so rank 0 (white's first rank) is at bottom
                y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - rank) * SQUARE_SIZE

                surface.blit(sprite, (x, y))
