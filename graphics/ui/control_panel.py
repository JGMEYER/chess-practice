from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from graphics.constants import (
    SIDEBAR_X,
    SIDEBAR_Y,
    CONTROL_BUTTON_SIZE,
    CONTROL_ICON_SIZE,
    CONTROL_BUTTON_SPACING,
)

if TYPE_CHECKING:
    from graphics.icon_loader import IconLoader


class ControlPanel:
    """Right sidebar control panel with undo/redo/flip buttons."""

    def __init__(self, manager: pygame_gui.UIManager, icon_loader: IconLoader):
        """
        Initialize the control panel.

        Args:
            manager: The pygame_gui UI manager
            icon_loader: Icon loader with loaded control icons
        """
        self.manager = manager

        # Calculate button positions (centered in 200px sidebar)
        start_x = SIDEBAR_X + 30  # 30px left margin for centering
        button_y = SIDEBAR_Y + 10  # 10px from top

        # Create undo button
        self.undo_button = UIButton(
            relative_rect=pygame.Rect(
                (start_x, button_y),
                (CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE)
            ),
            text="",
            manager=manager,
            object_id="#control_button",
        )

        # Create redo button
        redo_x = start_x + CONTROL_BUTTON_SIZE + CONTROL_BUTTON_SPACING
        self.redo_button = UIButton(
            relative_rect=pygame.Rect(
                (redo_x, button_y),
                (CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE)
            ),
            text="",
            manager=manager,
            object_id="#control_button",
        )

        # Create flip button
        flip_x = start_x + 2 * (CONTROL_BUTTON_SIZE + CONTROL_BUTTON_SPACING)
        self.flip_button = UIButton(
            relative_rect=pygame.Rect(
                (flip_x, button_y),
                (CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE)
            ),
            text="",
            manager=manager,
            object_id="#control_button",
        )

        # Store icons and buttons for custom rendering
        self.undo_icon = icon_loader.get_icon("undo")
        self.redo_icon = icon_loader.get_icon("redo")
        self.flip_icon = icon_loader.get_icon("flip")

        # Calculate padding to center icons within buttons
        self.icon_padding = (CONTROL_BUTTON_SIZE - CONTROL_ICON_SIZE) // 2

        # Create disabled (dimmed) versions of icons
        self.undo_icon_disabled = self._create_disabled_icon(self.undo_icon)
        self.redo_icon_disabled = self._create_disabled_icon(self.redo_icon)

        # Track button states (start disabled)
        self._undo_enabled = False
        self._redo_enabled = False
        self.undo_button.disable()
        self.redo_button.disable()

    def _create_disabled_icon(self, icon: pygame.Surface) -> pygame.Surface:
        """Create a dimmed version of an icon for disabled state."""
        disabled = icon.copy()
        disabled.set_alpha(80)
        return disabled

    def update_button_states(self, can_undo: bool, can_redo: bool) -> None:
        """
        Update the enabled/disabled state of undo and redo buttons.

        Args:
            can_undo: Whether undo is available
            can_redo: Whether redo is available
        """
        if can_undo != self._undo_enabled:
            self._undo_enabled = can_undo
            if can_undo:
                self.undo_button.enable()
            else:
                self.undo_button.disable()

        if can_redo != self._redo_enabled:
            self._redo_enabled = can_redo
            if can_redo:
                self.redo_button.enable()
            else:
                self.redo_button.disable()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw icons centered on top of buttons.

        Args:
            screen: The pygame surface to draw on
        """
        padding = self.icon_padding

        # Draw undo icon (use dimmed version if disabled)
        undo_rect = self.undo_button.rect
        undo_icon = self.undo_icon if self._undo_enabled else self.undo_icon_disabled
        screen.blit(undo_icon, (undo_rect.x + padding, undo_rect.y + padding))

        # Draw redo icon (use dimmed version if disabled)
        redo_rect = self.redo_button.rect
        redo_icon = self.redo_icon if self._redo_enabled else self.redo_icon_disabled
        screen.blit(redo_icon, (redo_rect.x + padding, redo_rect.y + padding))

        # Draw flip icon (centered in button)
        flip_rect = self.flip_button.rect
        screen.blit(self.flip_icon, (flip_rect.x + padding, flip_rect.y + padding))

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process UI events.

        Args:
            event: A pygame event

        Returns:
            Action string: "undo", "redo", "flip", or None
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.undo_button:
                return "undo"
            elif event.ui_element == self.redo_button:
                return "redo"
            elif event.ui_element == self.flip_button:
                return "flip"
        return None
