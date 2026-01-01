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
    SELECTED_SQUARE,
    VALID_MOVE_DOT,
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

    def draw_board(
        self,
        surface: pygame.Surface,
        selected_square: tuple[int, int] | None = None,
    ) -> None:
        """
        Draw the chess board squares.

        Args:
            surface: The pygame surface to draw on
            selected_square: Optional (file, rank) of selected square to highlight
        """
        for file in range(BOARD_SIZE):
            for rank in range(BOARD_SIZE):
                # Determine square color
                if selected_square and (file, rank) == selected_square:
                    color = SELECTED_SQUARE
                elif (file + rank) % 2 == 1:
                    color = LIGHT_SQUARE
                else:
                    color = DARK_SQUARE

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

    def draw_valid_moves(
        self,
        surface: pygame.Surface,
        valid_moves: list[tuple[int, int]],
    ) -> None:
        """
        Draw dots on valid move squares.

        Args:
            surface: The pygame surface to draw on
            valid_moves: List of (file, rank) tuples for valid destinations
        """
        dot_radius = SQUARE_SIZE // 6

        for file, rank in valid_moves:
            # Calculate center of square
            x = BOARD_OFFSET_X + file * SQUARE_SIZE + SQUARE_SIZE // 2
            y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - rank) * SQUARE_SIZE + SQUARE_SIZE // 2

            # Draw semi-transparent dot
            dot_surface = pygame.Surface((dot_radius * 2, dot_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, VALID_MOVE_DOT, (dot_radius, dot_radius), dot_radius)
            surface.blit(dot_surface, (x - dot_radius, y - dot_radius))

    def draw(
        self,
        surface: pygame.Surface,
        selected_square: tuple[int, int] | None = None,
        valid_moves: list[tuple[int, int]] | None = None,
    ) -> None:
        """
        Draw the complete board with labels and highlights.

        Args:
            surface: The pygame surface to draw on
            selected_square: Optional (file, rank) of selected square
            valid_moves: Optional list of valid move squares to highlight
        """
        surface.fill(BACKGROUND)
        self.draw_board(surface, selected_square)
        self.draw_labels(surface)
        if valid_moves:
            self.draw_valid_moves(surface, valid_moves)
