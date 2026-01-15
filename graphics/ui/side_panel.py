from __future__ import annotations

import pygame

from graphics.constants import (
    WINDOW_WIDTH,
    WINDOW_WIDTH_EXPANDED,
    WINDOW_HEIGHT,
    MENU_BAR_HEIGHT,
    SIDE_PANEL_WIDTH,
    SIDE_PANEL_TAB_WIDTH,
    SIDE_PANEL_TAB_HEIGHT,
    SIDEBAR_BACKGROUND,
)


class SidePanel:
    """Expandable side panel on the right edge of the window."""

    # Tab colors
    TAB_COLOR = (60, 58, 55)  # Same as sidebar background
    TAB_HOVER_COLOR = (74, 72, 69)  # Slightly lighter on hover
    TAB_ARROW_COLOR = (180, 180, 180)  # Light gray arrow

    def __init__(self):
        """Initialize the side panel in collapsed state."""
        self._expanded = False
        self._tab_hovered = False
        self._font: pygame.font.Font | None = None

    @property
    def expanded(self) -> bool:
        """Whether the panel is currently expanded."""
        return self._expanded

    def get_window_width(self) -> int:
        """Get the appropriate window width based on panel state."""
        return WINDOW_WIDTH_EXPANDED if self._expanded else WINDOW_WIDTH

    def _get_tab_rect(self) -> pygame.Rect:
        """Get the rectangle for the tab button."""
        # Tab is positioned at the right edge of the current window
        base_width = WINDOW_WIDTH_EXPANDED if self._expanded else WINDOW_WIDTH
        tab_x = base_width - SIDE_PANEL_TAB_WIDTH
        # Center the tab vertically in the window (below menu bar)
        content_height = WINDOW_HEIGHT - MENU_BAR_HEIGHT
        tab_y = MENU_BAR_HEIGHT + (content_height - SIDE_PANEL_TAB_HEIGHT) // 2
        return pygame.Rect(tab_x, tab_y, SIDE_PANEL_TAB_WIDTH, SIDE_PANEL_TAB_HEIGHT)

    def _get_panel_rect(self) -> pygame.Rect:
        """Get the rectangle for the panel content area (when expanded)."""
        panel_x = WINDOW_WIDTH
        panel_y = MENU_BAR_HEIGHT
        panel_height = WINDOW_HEIGHT - MENU_BAR_HEIGHT
        return pygame.Rect(panel_x, panel_y, SIDE_PANEL_WIDTH, panel_height)

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """
        Handle a mouse click event.

        Args:
            pos: Mouse position (x, y)

        Returns:
            True if the click was on the tab (panel state toggled), False otherwise
        """
        tab_rect = self._get_tab_rect()
        if tab_rect.collidepoint(pos):
            self._expanded = not self._expanded
            return True
        return False

    def update_hover(self, pos: tuple[int, int]) -> None:
        """
        Update hover state based on mouse position.

        Args:
            pos: Mouse position (x, y)
        """
        tab_rect = self._get_tab_rect()
        self._tab_hovered = tab_rect.collidepoint(pos)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the side panel tab and content area.

        Args:
            surface: The pygame surface to draw on
        """
        # Draw panel background if expanded
        if self._expanded:
            panel_rect = self._get_panel_rect()
            pygame.draw.rect(surface, SIDEBAR_BACKGROUND, panel_rect)
            # Draw left border for panel
            border_color = (74, 72, 69)  # Same as menu bar border
            pygame.draw.line(
                surface,
                border_color,
                (panel_rect.left, panel_rect.top),
                (panel_rect.left, panel_rect.bottom),
            )

        # Draw tab
        tab_rect = self._get_tab_rect()
        tab_color = self.TAB_HOVER_COLOR if self._tab_hovered else self.TAB_COLOR
        pygame.draw.rect(surface, tab_color, tab_rect)

        # Draw rounded left edge for tab
        corner_radius = 5
        corner_rect = pygame.Rect(
            tab_rect.left - corner_radius,
            tab_rect.top,
            corner_radius * 2,
            tab_rect.height,
        )
        pygame.draw.rect(surface, tab_color, corner_rect, border_radius=corner_radius)
        # Cover the right half of the rounded rect
        cover_rect = pygame.Rect(
            tab_rect.left,
            tab_rect.top,
            corner_radius,
            tab_rect.height,
        )
        pygame.draw.rect(surface, tab_color, cover_rect)

        # Draw arrow indicator
        arrow_size = 8
        center_x = tab_rect.centerx
        center_y = tab_rect.centery

        if self._expanded:
            # Arrow pointing left (to close)
            points = [
                (center_x + arrow_size // 2, center_y - arrow_size),
                (center_x - arrow_size // 2, center_y),
                (center_x + arrow_size // 2, center_y + arrow_size),
            ]
        else:
            # Arrow pointing right (to open)
            points = [
                (center_x - arrow_size // 2, center_y - arrow_size),
                (center_x + arrow_size // 2, center_y),
                (center_x - arrow_size // 2, center_y + arrow_size),
            ]

        pygame.draw.polygon(surface, self.TAB_ARROW_COLOR, points)
