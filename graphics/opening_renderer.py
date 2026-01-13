"""Renders the current opening name in the sidebar."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UITooltip

from .constants import OPENING_NAME_Y, OPENING_NAME_X, OPENING_NAME_MAX_WIDTH

if TYPE_CHECKING:
    from chess.patterns import Opening


class OpeningRenderer:
    """Renders the current opening name in the sidebar."""

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize the opening renderer.

        Args:
            ui_manager: The pygame_gui UI manager for tooltips
        """
        self._font = pygame.font.SysFont("Consolas", 11)
        self._ellipsis_width = self._font.size("...")[0]
        self._ui_manager = ui_manager
        self._tooltip: UITooltip | None = None
        self._current_opening_name: str | None = None
        self._is_truncated = False
        self._text_rect: pygame.Rect | None = None

    def _truncate_text(self, text: str) -> tuple[str, bool]:
        """
        Truncate text to fit within max width, breaking at delimiters or words.

        Args:
            text: The full text to potentially truncate

        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        # Check if text already fits
        text_width = self._font.size(text)[0]
        if text_width <= OPENING_NAME_MAX_WIDTH:
            return text, False

        # We need to truncate - account for ellipsis width
        available_width = OPENING_NAME_MAX_WIDTH - self._ellipsis_width

        # Try truncating at " - " delimiters first (keeps logical chunks)
        parts = text.split(" - ")
        truncated = ""
        for i, part in enumerate(parts):
            test_text = " - ".join(parts[: i + 1])
            if self._font.size(test_text)[0] <= available_width:
                truncated = test_text
            else:
                break

        # If we got at least one part, use delimiter-based truncation
        if truncated:
            return truncated + "...", True

        # Fall back to word-by-word truncation
        words = text.split()
        truncated = ""
        for i, word in enumerate(words):
            test_text = " ".join(words[: i + 1])
            if self._font.size(test_text)[0] <= available_width:
                truncated = test_text
            else:
                break

        if truncated:
            return truncated + "...", True

        # Last resort: character-by-character truncation
        for i in range(len(text), 0, -1):
            if self._font.size(text[:i])[0] <= available_width:
                return text[:i] + "...", True

        return "...", True

    def update(self) -> None:
        """Update tooltip visibility based on mouse hover."""
        if not self._is_truncated or self._text_rect is None:
            # No truncation, kill any existing tooltip
            if self._tooltip is not None:
                self._tooltip.kill()
                self._tooltip = None
            return

        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self._text_rect.collidepoint(mouse_pos)

        if is_hovering and self._tooltip is None and self._current_opening_name:
            # Show tooltip
            self._tooltip = UITooltip(
                html_text=self._current_opening_name,
                hover_distance=(0, 15),
                manager=self._ui_manager,
            )
        elif not is_hovering and self._tooltip is not None:
            # Hide tooltip
            self._tooltip.kill()
            self._tooltip = None

    def draw(self, surface: pygame.Surface, opening: Opening | None) -> None:
        """
        Draw the opening name if one is detected.

        Args:
            surface: Pygame surface to draw on
            opening: The current opening, or None if no match
        """
        # Track opening changes to clear tooltip when opening changes
        new_name = opening.name if opening else None
        if new_name != self._current_opening_name:
            self._current_opening_name = new_name
            if self._tooltip is not None:
                self._tooltip.kill()
                self._tooltip = None

        if opening is None:
            self._is_truncated = False
            self._text_rect = None
            return

        display_text, self._is_truncated = self._truncate_text(opening.name)
        text_surface = self._font.render(display_text, True, (140, 140, 140))

        # Store text rect for hover detection
        self._text_rect = pygame.Rect(
            OPENING_NAME_X,
            OPENING_NAME_Y,
            text_surface.get_width(),
            text_surface.get_height(),
        )

        surface.blit(text_surface, (OPENING_NAME_X, OPENING_NAME_Y))
