from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton


class MenuBar:
    """Top menu bar with File menu."""

    def __init__(self, manager: pygame_gui.UIManager, width: int):
        """
        Initialize the menu bar.

        Args:
            manager: The pygame_gui UI manager
            width: Width of the menu bar (typically window width)
        """
        self.manager = manager
        self.width = width
        self.menu_height = 30

        # Create File menu button
        self.file_button = UIButton(
            relative_rect=pygame.Rect((0, 0), (60, self.menu_height)),
            text="File",
            manager=manager,
            object_id="#file_menu_button",
        )

        # Dropdown state
        self.dropdown_visible = False
        self.load_fen_button: UIButton | None = None

    def show_dropdown(self) -> None:
        """Show the File dropdown menu."""
        if not self.dropdown_visible:
            # Position dropdown directly below the File button
            button_bottom = self.file_button.relative_rect.bottom
            self.load_fen_button = UIButton(
                relative_rect=pygame.Rect((0, button_bottom), (150, 28)),
                text="Load from FEN...",
                manager=self.manager,
                object_id="#load_fen_button",
            )
            self.dropdown_visible = True

    def hide_dropdown(self) -> None:
        """Hide the File dropdown menu."""
        if self.dropdown_visible and self.load_fen_button:
            self.load_fen_button.kill()
            self.load_fen_button = None
            self.dropdown_visible = False

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process UI events.

        Args:
            event: A pygame event

        Returns:
            Action string if an action was triggered, None otherwise.
            Possible actions: "load_fen"
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.file_button:
                if self.dropdown_visible:
                    self.hide_dropdown()
                else:
                    self.show_dropdown()
            elif event.ui_element == self.load_fen_button:
                self.hide_dropdown()
                return "load_fen"

        # Hide dropdown when clicking elsewhere
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.dropdown_visible:
                # Check if click is outside menu elements
                mouse_pos = event.pos
                file_rect = self.file_button.relative_rect
                dropdown_rect = (
                    self.load_fen_button.relative_rect
                    if self.load_fen_button
                    else pygame.Rect(0, 0, 0, 0)
                )
                if not file_rect.collidepoint(
                    mouse_pos
                ) and not dropdown_rect.collidepoint(mouse_pos):
                    self.hide_dropdown()

        return None
