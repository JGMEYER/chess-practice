"""Trie panel component for displaying the opening trie visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton

try:
    from pygame_gui.elements import UICheckBox

    HAS_CHECKBOX = True
except ImportError:
    HAS_CHECKBOX = False

from graphics.trie_visualization import TrieVisualization

if TYPE_CHECKING:
    from chess.patterns.openings import TrieNode


# Panel layout constants
CENTER_BUTTON_HEIGHT = 30
CHECKBOX_HEIGHT = 25
CENTER_BUTTON_MARGIN = 10
INFO_PANEL_HEIGHT = 120  # Reduced from 180 to give more space to visualization
CONTROL_WIDTH = 160  # Width of controls in info panel


class TriePanel:
    """Panel containing trie visualization, center button, and info display."""

    def __init__(self, ui_manager: pygame_gui.UIManager) -> None:
        """Initialize the trie panel."""
        self._ui_manager = ui_manager
        self._trie_viz: TrieVisualization | None = None
        self._center_button: UIButton | None = None
        self._focus_checkbox: UICheckBox | None = None if HAS_CHECKBOX else None
        self._font: pygame.font.Font | None = None
        self._rect: pygame.Rect | None = None
        self._visible = False

        # Track last path length to detect changes for auto-centering
        self._last_path_length: int = 0

    def set_trie(self, trie_root: TrieNode) -> None:
        """Initialize trie visualization with the opening trie."""
        self._trie_viz = TrieVisualization(trie_root)

    def update(self, san_history: list[str], current_move_count: int) -> None:
        """Update visualization state based on game state."""
        if self._trie_viz:
            self._trie_viz.update_current_path(san_history, current_move_count)

            # Auto-center and select active node when move count changes
            if current_move_count != self._last_path_length:
                self._trie_viz.center_on_current_position()
                self._trie_viz.select_current_position()
                self._last_path_length = current_move_count

    def set_visible(self, visible: bool, rect: pygame.Rect | None = None) -> None:
        """Set panel visibility and create/destroy UI elements accordingly."""
        if visible and not self._visible:
            # Becoming visible
            self._rect = rect
            self._create_ui_elements()
        elif not visible and self._visible:
            # Becoming hidden
            self._destroy_ui_elements()
            self._rect = None

        self._visible = visible

    def set_rect(self, rect: pygame.Rect) -> None:
        """Update the panel's rectangle (used when window resizes)."""
        if self._rect != rect:
            self._rect = rect
            # Recreate UI elements at new position
            if self._visible:
                self._destroy_ui_elements()
                self._create_ui_elements()

    def _get_viz_rect(self) -> pygame.Rect:
        """Get the rectangle for the trie visualization area."""
        if self._rect is None:
            return pygame.Rect(0, 0, 0, 0)

        # Visualization now starts at top of panel (controls moved to info panel)
        viz_height = self._rect.height - INFO_PANEL_HEIGHT - 10
        return pygame.Rect(
            self._rect.left + 5,
            self._rect.top + 5,
            self._rect.width - 10,
            max(viz_height, 100),  # Minimum height
        )

    def _get_info_rect(self) -> pygame.Rect:
        """Get the rectangle for the opening info panel."""
        if self._rect is None:
            return pygame.Rect(0, 0, 0, 0)

        return pygame.Rect(
            self._rect.left + 5,
            self._rect.bottom - INFO_PANEL_HEIGHT,
            self._rect.width - 10,
            INFO_PANEL_HEIGHT - 5,
        )

    def _create_ui_elements(self) -> None:
        """Create the UI elements (center button and focus checkbox) in info panel."""
        if self._rect is None:
            return

        info_rect = self._get_info_rect()

        # Create center button (right side of info panel)
        if self._center_button is None:
            button_rect = pygame.Rect(
                info_rect.right - CONTROL_WIDTH - 5,
                info_rect.top + 5,
                CONTROL_WIDTH,
                CENTER_BUTTON_HEIGHT,
            )
            self._center_button = UIButton(
                relative_rect=button_rect,
                text="Center",
                manager=self._ui_manager,
            )

        # Create focus mode checkbox (below button)
        # Use position tuple only - let pygame_gui auto-size for proper checkbox appearance
        if HAS_CHECKBOX and self._focus_checkbox is None:
            checkbox_pos = (
                info_rect.right - CONTROL_WIDTH - 5,
                info_rect.top + CENTER_BUTTON_HEIGHT + 12,
            )
            self._focus_checkbox = UICheckBox(
                relative_rect=checkbox_pos,
                text="Hide other lines",
                manager=self._ui_manager,
                initial_state=True,  # Focus mode enabled by default
            )

    def _destroy_ui_elements(self) -> None:
        """Destroy the UI elements."""
        if self._center_button is not None:
            self._center_button.kill()
            self._center_button = None
        if self._focus_checkbox is not None:
            self._focus_checkbox.kill()
            self._focus_checkbox = None

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process events for the trie panel.

        Returns action string or None:
        - "trie_select" - node was selected
        - "trie_navigate:N" - navigate to move index N
        - "trie_center" - center button pressed
        - None - no action needed
        """
        if not self._visible:
            return None

        # Handle center button
        if (
            event.type == pygame_gui.UI_BUTTON_PRESSED
            and self._center_button is not None
            and event.ui_element == self._center_button
        ):
            if self._trie_viz:
                self._trie_viz.center_on_current_position()
            return "trie_center"

        # Handle focus mode checkbox
        if HAS_CHECKBOX and self._focus_checkbox is not None:
            if (
                event.type == pygame_gui.UI_CHECK_BOX_CHECKED
                and event.ui_element == self._focus_checkbox
            ):
                if self._trie_viz:
                    self._trie_viz.set_focus_mode(True)
                return None
            elif (
                event.type == pygame_gui.UI_CHECK_BOX_UNCHECKED
                and event.ui_element == self._focus_checkbox
            ):
                if self._trie_viz:
                    self._trie_viz.set_focus_mode(False)
                return None

        # Forward to trie visualization
        if self._trie_viz:
            viz_rect = self._get_viz_rect()
            action = self._trie_viz.process_event(event, viz_rect)
            if action:
                return action

        return None

    def update_hover(self, pos: tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        if not self._visible or self._trie_viz is None:
            return

        viz_rect = self._get_viz_rect()
        self._trie_viz.update_hover(pos, viz_rect)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the trie panel contents."""
        if not self._visible or self._rect is None:
            return

        # Draw trie visualization
        if self._trie_viz:
            viz_rect = self._get_viz_rect()
            self._trie_viz.draw(surface, viz_rect)

        # Draw info panel for selected node
        self._draw_info_panel(surface)

    def _draw_info_panel(self, surface: pygame.Surface) -> None:
        """Draw the opening info panel for selected node."""
        if self._trie_viz is None:
            return

        info_rect = self._get_info_rect()

        # Draw background
        pygame.draw.rect(surface, (50, 50, 50), info_rect)
        pygame.draw.rect(surface, (70, 70, 70), info_rect, 1)

        # Initialize font if needed
        if self._font is None:
            self._font = pygame.font.Font(None, 18)

        # Text area width (leave space for controls on right)
        text_max_x = info_rect.right - CONTROL_WIDTH - 15

        selected = self._trie_viz.selected_node
        if selected is None:
            # No selection - show hint (centered in text area, not full panel)
            hint_text = "Click a node to see opening info"
            text_surface = self._font.render(hint_text, True, (120, 120, 120))
            text_rect = text_surface.get_rect(
                center=(info_rect.left + (text_max_x - info_rect.left) // 2, info_rect.centery)
            )
            surface.blit(text_surface, text_rect)
            return

        # Show opening info for selected node
        y_offset = info_rect.top + 10
        x_offset = info_rect.left + 10
        line_height = 18

        # Node label
        if selected.san:
            label = f"Move: {selected.san}"
        else:
            label = "Starting Position"
        text_surface = self._font.render(label, True, (200, 200, 200))
        surface.blit(text_surface, (x_offset, y_offset))
        y_offset += line_height + 5

        # Reserve space at bottom for path hint if on path
        path_hint_height = 20 if selected.path_index is not None else 0

        # Show openings at this node
        openings = list(selected.trie_node.openings)
        if openings:
            # Get unique opening names
            names = sorted(set(o.display_name for o in openings))

            # Limit display to fit in panel (accounting for header and path hint)
            available_height = info_rect.height - 35 - path_hint_height
            max_lines = max(1, available_height // line_height)
            for i, name in enumerate(names[:max_lines]):
                if i == max_lines - 1 and len(names) > max_lines:
                    text = f"... and {len(names) - max_lines + 1} more"
                else:
                    text = name
                text_surface = self._font.render(text, True, (180, 180, 180))
                surface.blit(text_surface, (x_offset, y_offset))
                y_offset += line_height
        else:
            text_surface = self._font.render("No opening data", True, (120, 120, 120))
            surface.blit(text_surface, (x_offset, y_offset))

        # Show if on current path (clickable hint)
        if selected.path_index is not None:
            path_text = f"On path (move {selected.path_index}) - click to go"
            text_surface = self._font.render(path_text, True, (100, 160, 100))
            surface.blit(text_surface, (x_offset, info_rect.bottom - 20))
