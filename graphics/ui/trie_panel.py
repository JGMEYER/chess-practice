"""Trie panel component for displaying the opening trie visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIDropDownMenu

try:
    from pygame_gui.elements import UICheckBox

    HAS_CHECKBOX = True
except ImportError:
    HAS_CHECKBOX = False

from graphics.trie_visualization import TrieVisualization

if TYPE_CHECKING:
    from chess.patterns.openings import OpeningTrie, TrieNode


# Panel layout constants
FILTER_BAR_HEIGHT = 35  # Height of the filter bar at the top
CENTER_BUTTON_HEIGHT = 30
CHECKBOX_HEIGHT = 25
CENTER_BUTTON_MARGIN = 10
INFO_PANEL_HEIGHT = 120  # Reduced from 180 to give more space to visualization
CONTROL_WIDTH = 160  # Width of controls in info panel

# Filter dropdown constants
DROPDOWN_HEIGHT = 28
BUTTON_WIDTH = 60
FILTER_MARGIN = 5
MIN_DROPDOWN_WIDTH = 150
MAX_OPENING_DROPDOWN_WIDTH = 350  # Max for opening names
MAX_VARIATION_DROPDOWN_WIDTH = 380  # Max for variation names (longer)
DROPDOWN_PADDING = 40  # Extra padding for dropdown arrow and margins


class TriePanel:
    """Panel containing trie visualization, center button, and info display."""

    def __init__(self, ui_manager: pygame_gui.UIManager) -> None:
        """Initialize the trie panel."""
        self._ui_manager = ui_manager
        self._trie_viz: TrieVisualization | None = None
        self._opening_trie: OpeningTrie | None = None  # Reference for filter queries
        self._center_button: UIButton | None = None
        self._focus_checkbox: UICheckBox | None = None if HAS_CHECKBOX else None
        self._font: pygame.font.Font | None = None
        self._rect: pygame.Rect | None = None
        self._visible = False

        # Filter bar UI elements
        self._opening_dropdown: UIDropDownMenu | None = None
        self._variation_dropdown: UIDropDownMenu | None = None
        self._apply_button: UIButton | None = None
        self._clear_button: UIButton | None = None

        # Filter state tracking
        self._selected_opening: str | None = None
        self._selected_variation: str | None = None
        self._all_openings: list[str] = []
        self._current_variations: list[str] = []

        # Calculated dropdown widths (set in set_trie based on content)
        self._opening_dropdown_width: int = MIN_DROPDOWN_WIDTH
        self._variation_dropdown_width: int = MIN_DROPDOWN_WIDTH

        # Track last path length to detect changes for auto-centering
        self._last_path_length: int = 0

    def set_trie(self, trie_root: TrieNode, opening_trie: OpeningTrie | None = None) -> None:
        """Initialize trie visualization with the opening trie.

        Args:
            trie_root: The root TrieNode for visualization.
            opening_trie: The OpeningTrie for filter queries (optional).
        """
        self._trie_viz = TrieVisualization(trie_root)
        self._opening_trie = opening_trie

        # Pre-fetch all openings for the dropdown
        if opening_trie:
            self._all_openings = opening_trie.get_all_openings()
            self._calculate_dropdown_widths(opening_trie)

    def _calculate_dropdown_widths(self, opening_trie: OpeningTrie) -> None:
        """Calculate dropdown widths based on longest opening/variation names."""
        # Initialize pygame font for text measurement
        measure_font = pygame.font.Font(None, 20)  # Default pygame_gui font size

        # Calculate opening dropdown width
        max_opening_width = 0
        for opening in self._all_openings:
            text_width = measure_font.size(opening)[0]
            max_opening_width = max(max_opening_width, text_width)

        # Calculate variation dropdown width (check all variations across all openings)
        max_variation_width = 0
        for opening in self._all_openings:
            variations = opening_trie.get_variations_for_opening(opening)
            for variation in variations:
                text_width = measure_font.size(variation)[0]
                max_variation_width = max(max_variation_width, text_width)

        # Add padding and enforce min/max width constraints
        self._opening_dropdown_width = min(
            MAX_OPENING_DROPDOWN_WIDTH,
            max(MIN_DROPDOWN_WIDTH, max_opening_width + DROPDOWN_PADDING)
        )
        self._variation_dropdown_width = min(
            MAX_VARIATION_DROPDOWN_WIDTH,
            max(MIN_DROPDOWN_WIDTH, max_variation_width + DROPDOWN_PADDING)
        )

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

    def _get_filter_bar_rect(self) -> pygame.Rect:
        """Get the rectangle for the filter bar at the top."""
        if self._rect is None:
            return pygame.Rect(0, 0, 0, 0)

        return pygame.Rect(
            self._rect.left + 5,
            self._rect.top + 5,
            self._rect.width - 10,
            FILTER_BAR_HEIGHT,
        )

    def _get_viz_rect(self) -> pygame.Rect:
        """Get the rectangle for the trie visualization area."""
        if self._rect is None:
            return pygame.Rect(0, 0, 0, 0)

        # Visualization starts below filter bar
        filter_height = FILTER_BAR_HEIGHT + FILTER_MARGIN
        viz_height = self._rect.height - INFO_PANEL_HEIGHT - filter_height - 10
        return pygame.Rect(
            self._rect.left + 5,
            self._rect.top + 5 + filter_height,
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
        """Create the UI elements (filter bar, center button, focus checkbox)."""
        if self._rect is None:
            return

        # Create filter bar elements
        self._create_filter_bar()

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
                text="[C] Center",
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
                text="[F] Hide other lines",
                manager=self._ui_manager,
                initial_state=True,  # Focus mode enabled by default
            )

    def _create_filter_bar(self) -> None:
        """Create the filter bar with opening/variation dropdowns."""
        filter_rect = self._get_filter_bar_rect()

        # Opening dropdown (leftmost)
        opening_options = ["Select Opening..."] + self._all_openings
        x_pos = filter_rect.left + FILTER_MARGIN
        y_pos = filter_rect.top + (FILTER_BAR_HEIGHT - DROPDOWN_HEIGHT) // 2

        self._opening_dropdown = UIDropDownMenu(
            options_list=opening_options,
            starting_option="Select Opening...",
            relative_rect=pygame.Rect(x_pos, y_pos, self._opening_dropdown_width, DROPDOWN_HEIGHT),
            manager=self._ui_manager,
        )

        # Variation dropdown (after opening dropdown)
        x_pos += self._opening_dropdown_width + FILTER_MARGIN
        # Start disabled with placeholder
        self._variation_dropdown = UIDropDownMenu(
            options_list=["Select Variation..."],
            starting_option="Select Variation...",
            relative_rect=pygame.Rect(x_pos, y_pos, self._variation_dropdown_width, DROPDOWN_HEIGHT),
            manager=self._ui_manager,
        )
        self._variation_dropdown.disable()

        # Apply button
        x_pos += self._variation_dropdown_width + FILTER_MARGIN
        self._apply_button = UIButton(
            relative_rect=pygame.Rect(x_pos, y_pos, BUTTON_WIDTH, DROPDOWN_HEIGHT),
            text="Apply",
            manager=self._ui_manager,
        )

        # Clear button (X)
        x_pos += BUTTON_WIDTH + FILTER_MARGIN
        self._clear_button = UIButton(
            relative_rect=pygame.Rect(x_pos, y_pos, 30, DROPDOWN_HEIGHT),
            text="X",
            manager=self._ui_manager,
        )

    def _destroy_ui_elements(self) -> None:
        """Destroy the UI elements."""
        if self._center_button is not None:
            self._center_button.kill()
            self._center_button = None
        if self._focus_checkbox is not None:
            self._focus_checkbox.kill()
            self._focus_checkbox = None
        # Destroy filter bar elements
        if self._opening_dropdown is not None:
            self._opening_dropdown.kill()
            self._opening_dropdown = None
        if self._variation_dropdown is not None:
            self._variation_dropdown.kill()
            self._variation_dropdown = None
        if self._apply_button is not None:
            self._apply_button.kill()
            self._apply_button = None
        if self._clear_button is not None:
            self._clear_button.kill()
            self._clear_button = None

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process events for the trie panel.

        Returns action string or None:
        - "trie_select" - node was selected
        - "trie_navigate:N" - navigate to move index N
        - "trie_center" - center button pressed
        - "reset_board" - filter applied, board should reset
        - None - no action needed
        """
        if not self._visible:
            return None

        # Handle filter bar events
        filter_action = self._process_filter_event(event)
        if filter_action:
            return filter_action

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

        # Don't forward mouse events to trie when a dropdown is expanded
        # This prevents scrolling and dragging from affecting the trie
        if self._is_dropdown_expanded():
            if event.type in (pygame.MOUSEWHEEL, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                return None

        # Forward to trie visualization
        if self._trie_viz:
            viz_rect = self._get_viz_rect()
            action = self._trie_viz.process_event(event, viz_rect)
            if action:
                return action

        return None

    def _is_dropdown_expanded(self) -> bool:
        """Check if any dropdown menu is currently expanded."""
        if self._opening_dropdown is not None:
            # UIDropDownMenu stores expansion state in current_state
            # menu_states is a dict with 'closed' and 'expanded' keys
            if hasattr(self._opening_dropdown, 'current_state') and hasattr(self._opening_dropdown, 'menu_states'):
                expanded_state = self._opening_dropdown.menu_states.get('expanded')
                if self._opening_dropdown.current_state == expanded_state:
                    return True
        if self._variation_dropdown is not None:
            if hasattr(self._variation_dropdown, 'current_state') and hasattr(self._variation_dropdown, 'menu_states'):
                expanded_state = self._variation_dropdown.menu_states.get('expanded')
                if self._variation_dropdown.current_state == expanded_state:
                    return True
        return False

    def _process_filter_event(self, event: pygame.event.Event) -> str | None:
        """Process filter bar events.

        Returns "reset_board" if filter was applied (and board should reset).
        """
        # Handle opening dropdown selection
        if (
            event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
            and self._opening_dropdown is not None
            and event.ui_element == self._opening_dropdown
        ):
            selected = event.text
            if selected == "Select Opening...":
                self._selected_opening = None
                self._selected_variation = None
                self._current_variations = []
                # Reset and disable variation dropdown
                if self._variation_dropdown:
                    self._variation_dropdown.kill()
                    filter_rect = self._get_filter_bar_rect()
                    x_pos = filter_rect.left + FILTER_MARGIN + self._opening_dropdown_width + FILTER_MARGIN
                    y_pos = filter_rect.top + (FILTER_BAR_HEIGHT - DROPDOWN_HEIGHT) // 2
                    self._variation_dropdown = UIDropDownMenu(
                        options_list=["Select Variation..."],
                        starting_option="Select Variation...",
                        relative_rect=pygame.Rect(x_pos, y_pos, self._variation_dropdown_width, DROPDOWN_HEIGHT),
                        manager=self._ui_manager,
                    )
                    self._variation_dropdown.disable()
            else:
                self._selected_opening = selected
                self._selected_variation = None
                # Populate and enable variation dropdown
                if self._opening_trie:
                    self._current_variations = self._opening_trie.get_variations_for_opening(selected)
                    # Recreate variation dropdown with new options
                    if self._variation_dropdown:
                        self._variation_dropdown.kill()
                    filter_rect = self._get_filter_bar_rect()
                    x_pos = filter_rect.left + FILTER_MARGIN + self._opening_dropdown_width + FILTER_MARGIN
                    y_pos = filter_rect.top + (FILTER_BAR_HEIGHT - DROPDOWN_HEIGHT) // 2
                    variation_options = ["All Variations"] + self._current_variations
                    self._variation_dropdown = UIDropDownMenu(
                        options_list=variation_options,
                        starting_option="All Variations",
                        relative_rect=pygame.Rect(x_pos, y_pos, self._variation_dropdown_width, DROPDOWN_HEIGHT),
                        manager=self._ui_manager,
                    )
            return None

        # Handle variation dropdown selection
        if (
            event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
            and self._variation_dropdown is not None
            and event.ui_element == self._variation_dropdown
        ):
            selected = event.text
            if selected == "All Variations" or selected == "Select Variation...":
                self._selected_variation = None
            else:
                self._selected_variation = selected
            return None

        # Handle Apply button
        if (
            event.type == pygame_gui.UI_BUTTON_PRESSED
            and self._apply_button is not None
            and event.ui_element == self._apply_button
        ):
            return self._apply_filter()

        # Handle Clear button
        if (
            event.type == pygame_gui.UI_BUTTON_PRESSED
            and self._clear_button is not None
            and event.ui_element == self._clear_button
        ):
            return self._clear_filter()

        return None

    def _apply_filter(self) -> str | None:
        """Apply the current filter selection."""
        if self._trie_viz is None:
            return None

        # Apply filter to trie visualization
        self._trie_viz.set_opening_filter(self._selected_opening, self._selected_variation)

        # Signal that board should reset if a filter was applied
        if self._selected_opening is not None:
            return "reset_board"
        return None

    def _clear_filter(self) -> str | None:
        """Clear the current filter."""
        if self._trie_viz is None:
            return None

        # Clear filter in visualization
        self._trie_viz.clear_opening_filter()

        # Reset dropdown selections
        self._selected_opening = None
        self._selected_variation = None

        # Reset dropdowns (recreate them)
        if self._opening_dropdown:
            self._opening_dropdown.kill()
        if self._variation_dropdown:
            self._variation_dropdown.kill()

        filter_rect = self._get_filter_bar_rect()
        x_pos = filter_rect.left + FILTER_MARGIN
        y_pos = filter_rect.top + (FILTER_BAR_HEIGHT - DROPDOWN_HEIGHT) // 2

        opening_options = ["Select Opening..."] + self._all_openings
        self._opening_dropdown = UIDropDownMenu(
            options_list=opening_options,
            starting_option="Select Opening...",
            relative_rect=pygame.Rect(x_pos, y_pos, self._opening_dropdown_width, DROPDOWN_HEIGHT),
            manager=self._ui_manager,
        )

        x_pos += self._opening_dropdown_width + FILTER_MARGIN
        self._variation_dropdown = UIDropDownMenu(
            options_list=["Select Variation..."],
            starting_option="Select Variation...",
            relative_rect=pygame.Rect(x_pos, y_pos, self._variation_dropdown_width, DROPDOWN_HEIGHT),
            manager=self._ui_manager,
        )
        self._variation_dropdown.disable()

        return None

    def toggle_focus_mode(self) -> None:
        """Toggle focus mode (called from keyboard shortcut)."""
        if self._focus_checkbox is not None and self._trie_viz is not None:
            new_state = not self._focus_checkbox.is_checked
            self._focus_checkbox.set_state(new_state)
            self._trie_viz.set_focus_mode(new_state)

    def center(self) -> None:
        """Center on current position (called from keyboard shortcut)."""
        if self._trie_viz is not None:
            self._trie_viz.center_on_current_position()

    def get_available_moves(self) -> list[str]:
        """Get SAN moves available from the current active node in focus mode.

        Returns:
            List of SAN move strings for visible children of active node.
            Empty list if not visible, not in focus mode, or no active node.
            Respects the current opening/variation filter.
        """
        if not self._visible:
            return []

        if self._trie_viz is None or not self._trie_viz._focus_mode:
            return []

        active_node = self._trie_viz._get_active_node()
        if active_node is None:
            return []

        # Get children that pass the filter (if active)
        moves = []
        for child in active_node.children:
            if child.san is None:
                continue
            # Check if child passes filter
            if self._trie_viz._filter_opening is not None:
                if not self._trie_viz._node_is_on_filter_path(child):
                    continue
            moves.append(child.san)
        return moves

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
