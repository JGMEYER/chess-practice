"""Renders the move list in the sidebar."""

from __future__ import annotations

import pygame

from .constants import (
    SIDEBAR_X,
    MOVE_LIST_TOP_Y,
    MOVE_LIST_BOTTOM_Y,
    MOVE_LIST_LINE_HEIGHT,
    MOVE_NUMBER_WIDTH,
    MOVE_COLUMN_WIDTH,
)


class MoveListRenderer:
    """Renders a scrollable move list in the sidebar."""

    def __init__(self):
        """Initialize the move list renderer."""
        self._font = pygame.font.SysFont("Consolas", 13)
        self._scroll_offset = 0
        self._max_visible_lines = (
            MOVE_LIST_BOTTOM_Y - MOVE_LIST_TOP_Y
        ) // MOVE_LIST_LINE_HEIGHT

    def draw(
        self,
        surface: pygame.Surface,
        san_moves: list[str],
        current_index: int | None = None,
    ) -> None:
        """
        Draw the move list.

        Args:
            surface: Pygame surface to draw on
            san_moves: List of SAN notation strings
            current_index: Index of the current position (for highlighting)
        """
        if not san_moves:
            return

        # Pair moves: [(1, "e4", "e5"), (2, "Nf3", "Nc6"), ...]
        pairs = self._pair_moves(san_moves)

        # Auto-scroll to show current move
        if current_index is not None:
            self._auto_scroll(current_index, len(pairs))

        # Draw visible rows
        y = MOVE_LIST_TOP_Y
        for i in range(self._scroll_offset, len(pairs)):
            if y + MOVE_LIST_LINE_HEIGHT > MOVE_LIST_BOTTOM_Y:
                break

            move_num, white_move, black_move = pairs[i]
            x = SIDEBAR_X + 10

            # Move number (gray)
            self._draw_text(surface, f"{move_num}.", x, y, (120, 120, 120))
            x += MOVE_NUMBER_WIDTH

            # White move
            white_highlighted = self._is_current(current_index, i, 0)
            white_color = (255, 255, 255) if white_highlighted else (200, 200, 200)
            self._draw_text(surface, white_move, x, y, white_color)
            x += MOVE_COLUMN_WIDTH

            # Black move (if exists)
            if black_move:
                black_highlighted = self._is_current(current_index, i, 1)
                black_color = (255, 255, 255) if black_highlighted else (200, 200, 200)
                self._draw_text(surface, black_move, x, y, black_color)

            y += MOVE_LIST_LINE_HEIGHT

    def _draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        """Render text at the given position."""
        text_surface = self._font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def _pair_moves(
        self, moves: list[str]
    ) -> list[tuple[int, str, str | None]]:
        """
        Group moves into (move_number, white_move, black_move) tuples.

        Args:
            moves: List of SAN moves

        Returns:
            List of tuples (move_num, white_move, black_move or None)
        """
        pairs = []
        for i in range(0, len(moves), 2):
            move_num = i // 2 + 1
            white_move = moves[i]
            black_move = moves[i + 1] if i + 1 < len(moves) else None
            pairs.append((move_num, white_move, black_move))
        return pairs

    def _is_current(
        self, current_index: int | None, pair_index: int, sub_index: int
    ) -> bool:
        """
        Check if this move is the current position.

        Args:
            current_index: Overall move index (0-based)
            pair_index: Index of the move pair
            sub_index: 0 for white, 1 for black

        Returns:
            True if this move should be highlighted
        """
        if current_index is None:
            return False
        return current_index == pair_index * 2 + sub_index

    def _auto_scroll(self, current_index: int, total_pairs: int) -> None:
        """
        Adjust scroll to keep current move visible.

        Args:
            current_index: Current move index
            total_pairs: Total number of move pairs
        """
        pair_index = current_index // 2

        # Scroll up if current move is above visible area
        if pair_index < self._scroll_offset:
            self._scroll_offset = pair_index

        # Scroll down if current move is below visible area
        elif pair_index >= self._scroll_offset + self._max_visible_lines:
            self._scroll_offset = pair_index - self._max_visible_lines + 1

    def handle_scroll(self, delta: int, total_moves: int) -> None:
        """
        Handle mouse wheel scrolling.

        Args:
            delta: Scroll amount (positive = up, negative = down)
            total_moves: Total number of moves
        """
        total_pairs = (total_moves + 1) // 2
        max_scroll = max(0, total_pairs - self._max_visible_lines)

        # delta is positive for scroll up (move view up = earlier moves)
        # delta is negative for scroll down (move view down = later moves)
        self._scroll_offset = max(0, min(max_scroll, self._scroll_offset - delta))

    def reset_scroll(self) -> None:
        """Reset scroll position to the beginning."""
        self._scroll_offset = 0
