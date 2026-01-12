"""Renders the current opening name in the sidebar."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .constants import OPENING_NAME_Y, SIDEBAR_X

if TYPE_CHECKING:
    from chess.patterns import Opening


class OpeningRenderer:
    """Renders the current opening name in the sidebar."""

    def __init__(self):
        """Initialize the opening renderer."""
        self._font = pygame.font.SysFont("Consolas", 11)

    def draw(self, surface: pygame.Surface, opening: Opening | None) -> None:
        """
        Draw the opening name if one is detected.

        Args:
            surface: Pygame surface to draw on
            opening: The current opening, or None if no match
        """
        if opening is None:
            return

        text_surface = self._font.render(opening.name, True, (140, 140, 140))
        surface.blit(text_surface, (SIDEBAR_X + 10, OPENING_NAME_Y))
