from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from graphics.constants import (
    SIDEBAR_X,
    SIDEBAR_Y,
    CONTROL_BUTTON_SIZE,
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

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw icons on top of buttons.

        Args:
            screen: The pygame surface to draw on
        """
        # Draw undo icon
        undo_rect = self.undo_button.rect
        icon_pos = (undo_rect.x, undo_rect.y)
        screen.blit(self.undo_icon, icon_pos)

        # Draw redo icon
        redo_rect = self.redo_button.rect
        icon_pos = (redo_rect.x, redo_rect.y)
        screen.blit(self.redo_icon, icon_pos)

        # Draw flip icon
        flip_rect = self.flip_button.rect
        icon_pos = (flip_rect.x, flip_rect.y)
        screen.blit(self.flip_icon, icon_pos)

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
