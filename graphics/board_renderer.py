from __future__ import annotations

import pygame

from .constants import (
    LIGHT_SQUARE,
    DARK_SQUARE,
    BACKGROUND,
    LABEL_COLOR,
    SQUARE_SIZE,
    BOARD_SIZE,
    LABEL_MARGIN,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
)


class BoardRenderer:
    """Renders the chess board squares and labels."""

    def __init__(self):
        """Initialize the board renderer."""
        self._font: pygame.font.Font | None = None

    def _ensure_font(self) -> None:
        """Initialize the font if not already done."""
        if self._font is None:
            pygame.font.init()
            self._font = pygame.font.SysFont("Arial", 14, bold=True)

    def draw_board(self, surface: pygame.Surface) -> None:
        """
        Draw the chess board squares.

        Args:
            surface: The pygame surface to draw on
        """
        for file in range(BOARD_SIZE):
            for rank in range(BOARD_SIZE):
                # Determine square color (light if file+rank is even)
                is_light = (file + rank) % 2 == 1
                color = LIGHT_SQUARE if is_light else DARK_SQUARE

                # Calculate pixel position
                x = BOARD_OFFSET_X + file * SQUARE_SIZE
                # Flip rank so rank 0 (white's first rank) is at bottom
                y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - rank) * SQUARE_SIZE

                pygame.draw.rect(surface, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    def draw_labels(self, surface: pygame.Surface) -> None:
        """
        Draw rank and file labels in the margins.

        Args:
            surface: The pygame surface to draw on
        """
        self._ensure_font()

        # File labels (a-h) along the bottom
        for file in range(BOARD_SIZE):
            letter = chr(ord("a") + file)
            text = self._font.render(letter, True, LABEL_COLOR)
            x = BOARD_OFFSET_X + file * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
            y = BOARD_OFFSET_Y + BOARD_SIZE * SQUARE_SIZE + 4
            surface.blit(text, (x, y))

        # Rank labels (1-8) along the left
        for rank in range(BOARD_SIZE):
            number = str(rank + 1)
            text = self._font.render(number, True, LABEL_COLOR)
            x = (LABEL_MARGIN - text.get_width()) // 2
            # Flip so rank 1 is at bottom
            y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - rank) * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
            surface.blit(text, (x, y))

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the complete board with labels.

        Args:
            surface: The pygame surface to draw on
        """
        surface.fill(BACKGROUND)
        self.draw_board(surface)
        self.draw_labels(surface)
