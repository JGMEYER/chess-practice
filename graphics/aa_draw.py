"""Anti-aliased drawing utilities for pygame."""

from __future__ import annotations

import math

import pygame
import pygame.gfxdraw


def circle(
    surface: pygame.Surface,
    x: int,
    y: int,
    radius: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
) -> None:
    """Draw a filled anti-aliased circle."""
    pygame.gfxdraw.filled_circle(surface, x, y, radius, color)
    pygame.gfxdraw.aacircle(surface, x, y, radius, color)


def circle_outline(
    surface: pygame.Surface,
    x: int,
    y: int,
    radius: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
    width: int = 1,
) -> None:
    """Draw an anti-aliased circle outline with the given width."""
    for i in range(width):
        r = radius - i
        if r > 0:
            pygame.gfxdraw.aacircle(surface, x, y, r, color)


def line(
    surface: pygame.Surface,
    start: tuple[int, int] | tuple[float, float],
    end: tuple[int, int] | tuple[float, float],
    color: tuple[int, int, int] | tuple[int, int, int, int],
    width: int = 1,
) -> None:
    """Draw an anti-aliased line with the given width."""
    x1, y1 = start
    x2, y2 = end

    if width == 1:
        pygame.draw.aaline(surface, color, (x1, y1), (x2, y2))
        return

    # For thick lines, draw as a filled polygon with AA edges
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)

    if length == 0:
        return

    # Perpendicular unit vector
    px = -dy / length
    py = dx / length

    # Half width offset
    hw = width / 2

    # Four corners of the thick line polygon
    points = [
        (x1 + px * hw, y1 + py * hw),
        (x1 - px * hw, y1 - py * hw),
        (x2 - px * hw, y2 - py * hw),
        (x2 + px * hw, y2 + py * hw),
    ]

    pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)
