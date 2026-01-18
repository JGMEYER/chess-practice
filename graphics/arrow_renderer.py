"""Arrow rendering for chess board move visualization."""

from __future__ import annotations

import math

import pygame

from . import aa_draw
from .constants import (
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
    BOARD_SIZE,
    SQUARE_SIZE,
)


class ArrowRenderer:
    """Renders directional arrows on the chess board.

    Supports three types of arrows:
    - Vertical (straight up/down)
    - Horizontal (straight left/right)
    - Knight moves (L-shaped, 2 squares then 1 square perpendicular)
    """

    # Arrow visual style - vibrant orange/yellow
    ARROW_COLOR = (245, 175, 50, 230)  # Vibrant orange-yellow
    ARROW_WIDTH = 20
    ARROWHEAD_LENGTH = 26
    ARROWHEAD_WIDTH = 42  # Much wider arrowhead

    # How far arrow starts from edge of square (larger = further from edge)
    START_EDGE_INSET = 24  # Distance from square edge where arrow starts
    # How far arrow tip is from center of target square
    END_INSET = 2

    def __init__(self) -> None:
        """Initialize the arrow renderer."""
        self._arrows: list[tuple[tuple[int, int], tuple[int, int]]] = []
        self._rotated = False

    @property
    def rotated(self) -> bool:
        """Whether the board is rotated."""
        return self._rotated

    @rotated.setter
    def rotated(self, value: bool) -> None:
        """Set board rotation state."""
        self._rotated = value

    def clear(self) -> None:
        """Remove all arrows."""
        self._arrows = []

    def add_arrow(
        self, from_sq: tuple[int, int], to_sq: tuple[int, int]
    ) -> bool:
        """Add an arrow if it's a valid type.

        Args:
            from_sq: Starting square (file, rank)
            to_sq: Ending square (file, rank)

        Returns:
            True if the arrow was added, False if invalid type
        """
        if self._is_valid_arrow(from_sq, to_sq):
            self._arrows.append((from_sq, to_sq))
            return True
        return False

    def remove_arrow(
        self, from_sq: tuple[int, int], to_sq: tuple[int, int]
    ) -> bool:
        """Remove an arrow if it exists.

        Args:
            from_sq: Starting square (file, rank)
            to_sq: Ending square (file, rank)

        Returns:
            True if the arrow was removed, False if not found
        """
        try:
            self._arrows.remove((from_sq, to_sq))
            return True
        except ValueError:
            return False

    def set_arrows(
        self, arrows: list[tuple[tuple[int, int], tuple[int, int]]]
    ) -> None:
        """Set the complete list of arrows (replacing any existing).

        Args:
            arrows: List of (from_sq, to_sq) tuples
        """
        self._arrows = [
            (from_sq, to_sq)
            for from_sq, to_sq in arrows
            if self._is_valid_arrow(from_sq, to_sq)
        ]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all arrows on the surface.

        Args:
            surface: Pygame surface to draw on
        """
        # Create a transparent surface for alpha blending
        arrow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        for from_sq, to_sq in self._arrows:
            self._draw_arrow(arrow_surface, from_sq, to_sq)

        surface.blit(arrow_surface, (0, 0))

    def _is_valid_arrow(
        self, from_sq: tuple[int, int], to_sq: tuple[int, int]
    ) -> bool:
        """Check if arrow type is valid (any movement is valid)."""
        dx = to_sq[0] - from_sq[0]
        dy = to_sq[1] - from_sq[1]

        # No movement is invalid
        if dx == 0 and dy == 0:
            return False

        return True

    def _get_arrow_type(
        self, from_sq: tuple[int, int], to_sq: tuple[int, int]
    ) -> str:
        """Determine the type of arrow."""
        dx = to_sq[0] - from_sq[0]
        dy = to_sq[1] - from_sq[1]

        if dx == 0:
            return "vertical"
        if dy == 0:
            return "horizontal"
        if (abs(dx), abs(dy)) in [(2, 1), (1, 2)]:
            return "knight"
        # Any other movement is diagonal/angled
        return "diagonal"

    def _square_to_pixel_center(
        self, file: int, rank: int
    ) -> tuple[float, float]:
        """Convert board coordinates to pixel center of square."""
        if self._rotated:
            x = BOARD_OFFSET_X + (BOARD_SIZE - 1 - file) * SQUARE_SIZE
            y = BOARD_OFFSET_Y + rank * SQUARE_SIZE
        else:
            x = BOARD_OFFSET_X + file * SQUARE_SIZE
            y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - rank) * SQUARE_SIZE

        return x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2

    def _get_edge_start_point(
        self,
        from_sq: tuple[int, int],
        to_sq: tuple[int, int],
    ) -> tuple[float, float]:
        """Get the starting point at the edge of the from_square facing toward to_square.

        The start point is on the edge of the square, centered on that edge.
        For diagonal arrows, start from the corner area.
        """
        center = self._square_to_pixel_center(*from_sq)
        dx = to_sq[0] - from_sq[0]
        dy = to_sq[1] - from_sq[1]

        half = SQUARE_SIZE // 2
        edge_dist = half - self.START_EDGE_INSET

        # For knight moves (2+1 or 1+2), use the longer direction
        is_knight = (abs(dx), abs(dy)) in [(2, 1), (1, 2)]
        if is_knight and abs(dx) == 2:
            # Horizontal is primary
            offset_x = edge_dist if dx > 0 else -edge_dist
            offset_y = 0
        elif is_knight and abs(dy) == 2:
            # Vertical is primary
            offset_x = 0
            offset_y = -edge_dist if dy > 0 else edge_dist
        elif dx == 0:
            # Vertical straight arrow
            offset_x = 0
            offset_y = -edge_dist if dy > 0 else edge_dist
        elif dy == 0:
            # Horizontal straight arrow
            offset_x = edge_dist if dx > 0 else -edge_dist
            offset_y = 0
        else:
            # Diagonal arrow - start from the actual corner of the square
            # This makes diagonals pass through square corners naturally
            corner_x = center[0] + (half if dx > 0 else -half)
            corner_y = center[1] + (-half if dy > 0 else half)

            # Apply inset along diagonal direction to match visual depth of straight arrows
            # Use START_EDGE_INSET for each axis (not divided by sqrt(2)) so it looks
            # equally inset as horizontal/vertical arrows
            inset_x = self.START_EDGE_INSET * (-1 if dx > 0 else 1)
            inset_y = self.START_EDGE_INSET * (1 if dy > 0 else -1)

            return corner_x + inset_x, corner_y + inset_y

        return center[0] + offset_x, center[1] + offset_y

    def _draw_arrow(
        self,
        surface: pygame.Surface,
        from_sq: tuple[int, int],
        to_sq: tuple[int, int],
    ) -> None:
        """Draw a single arrow."""
        arrow_type = self._get_arrow_type(from_sq, to_sq)

        if arrow_type == "knight":
            self._draw_knight_arrow(surface, from_sq, to_sq)
        else:
            self._draw_straight_arrow(surface, from_sq, to_sq)

    def _draw_straight_arrow(
        self,
        surface: pygame.Surface,
        from_sq: tuple[int, int],
        to_sq: tuple[int, int],
    ) -> None:
        """Draw a straight arrow (vertical, horizontal, or diagonal) as a unified polygon."""
        # Start from edge of square, end near center of target
        start = self._get_edge_start_point(from_sq, to_sq)
        end = self._square_to_pixel_center(*to_sq)

        # All arrows (including diagonal) end at center of target square
        # Diagonal arrows start from corner, so they naturally pass through square corners

        # Calculate direction vector
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return

        # Unit direction vector
        ux = dx / length
        uy = dy / length

        # Perpendicular unit vector
        px = -uy
        py = ux

        # End point (tip) is slightly inset from center
        end_x = end[0] - ux * self.END_INSET
        end_y = end[1] - uy * self.END_INSET

        # Start point is already at edge
        start_x, start_y = start

        # Where the shaft meets the arrowhead base
        shaft_end_x = end_x - ux * self.ARROWHEAD_LENGTH
        shaft_end_y = end_y - uy * self.ARROWHEAD_LENGTH

        # Half widths
        shaft_hw = self.ARROW_WIDTH / 2
        head_hw = self.ARROWHEAD_WIDTH / 2

        # Build unified polygon: simple shape without rounded corners
        points = [
            # Shaft left side
            (start_x + px * shaft_hw, start_y + py * shaft_hw),
            (shaft_end_x + px * shaft_hw, shaft_end_y + py * shaft_hw),
            # Arrowhead left wing
            (shaft_end_x + px * head_hw, shaft_end_y + py * head_hw),
            # Tip
            (end_x, end_y),
            # Arrowhead right wing
            (shaft_end_x - px * head_hw, shaft_end_y - py * head_hw),
            # Shaft right side
            (shaft_end_x - px * shaft_hw, shaft_end_y - py * shaft_hw),
            (start_x - px * shaft_hw, start_y - py * shaft_hw),
        ]

        aa_draw.polygon(surface, points, self.ARROW_COLOR)

    def _draw_knight_arrow(
        self,
        surface: pygame.Surface,
        from_sq: tuple[int, int],
        to_sq: tuple[int, int],
    ) -> None:
        """Draw an L-shaped knight move arrow as a unified polygon.

        The arrow goes 2 squares in the longer direction first,
        then 1 square perpendicular.
        """
        dx = to_sq[0] - from_sq[0]

        # Determine which direction has 2 squares of movement
        if abs(dx) == 2:
            # Horizontal 2, then vertical 1
            corner_sq = (to_sq[0], from_sq[1])
        else:
            # Vertical 2, then horizontal 1
            corner_sq = (from_sq[0], to_sq[1])

        # Start from edge of starting square
        start = self._get_edge_start_point(from_sq, to_sq)
        corner = self._square_to_pixel_center(*corner_sq)
        end = self._square_to_pixel_center(*to_sq)

        # First segment direction
        dx1 = corner[0] - start[0]
        dy1 = corner[1] - start[1]
        len1 = math.sqrt(dx1 * dx1 + dy1 * dy1)

        if len1 == 0:
            return

        ux1 = dx1 / len1
        uy1 = dy1 / len1
        # Perpendicular to first segment
        px1 = -uy1
        py1 = ux1

        # Second segment direction
        dx2 = end[0] - corner[0]
        dy2 = end[1] - corner[1]
        len2 = math.sqrt(dx2 * dx2 + dy2 * dy2)

        if len2 == 0:
            return

        ux2 = dx2 / len2
        uy2 = dy2 / len2
        # Perpendicular to second segment
        px2 = -uy2
        py2 = ux2

        # Half widths
        shaft_hw = self.ARROW_WIDTH / 2
        head_hw = self.ARROWHEAD_WIDTH / 2

        # Start is already at edge
        start_x, start_y = start

        # Inset end point (tip of arrow)
        end_x = end[0] - ux2 * self.END_INSET
        end_y = end[1] - uy2 * self.END_INSET

        # Where shaft meets arrowhead
        shaft_end_x = end_x - ux2 * self.ARROWHEAD_LENGTH
        shaft_end_y = end_y - uy2 * self.ARROWHEAD_LENGTH

        # Build unified L-shaped polygon with arrowhead
        # Cross product tells us turn direction
        cross = ux1 * uy2 - uy1 * ux2  # positive = left turn, negative = right turn

        # Key insight: Each corner needs ONE point, offset by BOTH perpendiculars.
        # Outer corner: offset outward from both segments
        # Inner corner: offset inward from both segments

        if cross > 0:
            # Left turn - +px side is outer, -px side is inner
            # Outer corner: corner + px1*hw + px2*hw (outward from both)
            # Inner corner: corner - px1*hw - px2*hw (inward from both)
            outer_corner = (
                corner[0] + px1 * shaft_hw + px2 * shaft_hw,
                corner[1] + py1 * shaft_hw + py2 * shaft_hw,
            )
            inner_corner = (
                corner[0] - px1 * shaft_hw - px2 * shaft_hw,
                corner[1] - py1 * shaft_hw - py2 * shaft_hw,
            )
            points = [
                # Seg1 outer edge
                (start_x + px1 * shaft_hw, start_y + py1 * shaft_hw),
                outer_corner,
                # Seg2 outer edge to arrowhead
                (shaft_end_x + px2 * shaft_hw, shaft_end_y + py2 * shaft_hw),
                # Arrowhead
                (shaft_end_x + px2 * head_hw, shaft_end_y + py2 * head_hw),
                (end_x, end_y),
                (shaft_end_x - px2 * head_hw, shaft_end_y - py2 * head_hw),
                # Seg2 inner edge
                (shaft_end_x - px2 * shaft_hw, shaft_end_y - py2 * shaft_hw),
                inner_corner,
                # Seg1 inner edge back to start
                (start_x - px1 * shaft_hw, start_y - py1 * shaft_hw),
            ]
        else:
            # Right turn - -px side is outer, +px side is inner
            # Outer corner: corner - px1*hw - px2*hw
            # Inner corner: corner + px1*hw + px2*hw
            outer_corner = (
                corner[0] - px1 * shaft_hw - px2 * shaft_hw,
                corner[1] - py1 * shaft_hw - py2 * shaft_hw,
            )
            inner_corner = (
                corner[0] + px1 * shaft_hw + px2 * shaft_hw,
                corner[1] + py1 * shaft_hw + py2 * shaft_hw,
            )
            points = [
                # Seg1 inner edge
                (start_x + px1 * shaft_hw, start_y + py1 * shaft_hw),
                inner_corner,
                # Seg2 inner edge to arrowhead
                (shaft_end_x + px2 * shaft_hw, shaft_end_y + py2 * shaft_hw),
                # Arrowhead
                (shaft_end_x + px2 * head_hw, shaft_end_y + py2 * head_hw),
                (end_x, end_y),
                (shaft_end_x - px2 * head_hw, shaft_end_y - py2 * head_hw),
                # Seg2 outer edge
                (shaft_end_x - px2 * shaft_hw, shaft_end_y - py2 * shaft_hw),
                outer_corner,
                # Seg1 outer edge back to start
                (start_x - px1 * shaft_hw, start_y - py1 * shaft_hw),
            ]

        aa_draw.polygon(surface, points, self.ARROW_COLOR)

