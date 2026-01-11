from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel

from graphics.constants import MENU_BUTTON_HEIGHT


class MenuBar:
    """Top menu bar with File and Help menus."""

    def __init__(self, manager: pygame_gui.UIManager, width: int):
        """
        Initialize the menu bar.

        Args:
            manager: The pygame_gui UI manager
            width: Width of the menu bar (typically window width)
        """
        self.manager = manager
        self.width = width
        self.menu_height = MENU_BUTTON_HEIGHT

        # Create File menu button
        self.file_button = UIButton(
            relative_rect=pygame.Rect((0, 0), (60, self.menu_height)),
            text="File",
            manager=manager,
            object_id="#file_menu_button",
        )

        # Create Help menu button
        self.help_button = UIButton(
            relative_rect=pygame.Rect((60, 0), (60, self.menu_height)),
            text="Help",
            manager=manager,
            object_id="#help_menu_button",
        )

        # Dropdown state
        self.active_menu: str | None = None
        self.dropdown_panel: UIPanel | None = None
        self.load_fen_button: UIButton | None = None
        self.credits_button: UIButton | None = None

    def show_file_dropdown(self) -> None:
        """Show the File dropdown menu."""
        self.hide_dropdown()
        button_bottom = self.file_button.relative_rect.bottom

        # Create panel container for dropdown
        self.dropdown_panel = UIPanel(
            relative_rect=pygame.Rect((0, button_bottom), (150, 28)),
            manager=self.manager,
            object_id="#dropdown_panel",
        )

        # Create Load from FEN button
        self.load_fen_button = UIButton(
            relative_rect=pygame.Rect((0, 0), (150, 28)),
            text="Load from FEN...",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )
        self.active_menu = "file"

    def show_help_dropdown(self) -> None:
        """Show the Help dropdown menu."""
        self.hide_dropdown()
        button_bottom = self.help_button.relative_rect.bottom

        # Create panel container for dropdown
        self.dropdown_panel = UIPanel(
            relative_rect=pygame.Rect((60, button_bottom), (150, 28)),
            manager=self.manager,
            object_id="#dropdown_panel",
        )

        # Create Credits button
        self.credits_button = UIButton(
            relative_rect=pygame.Rect((0, 0), (150, 28)),
            text="Credits",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )
        self.active_menu = "help"

    def hide_dropdown(self) -> None:
        """Hide any open dropdown menu."""
        if self.dropdown_panel:
            self.dropdown_panel.kill()
            self.dropdown_panel = None
        self.load_fen_button = None
        self.credits_button = None
        self.active_menu = None

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process UI events.

        Args:
            event: A pygame event

        Returns:
            Action string if an action was triggered, None otherwise.
            Possible actions: "load_fen", "show_credits"
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.file_button:
                if self.active_menu == "file":
                    self.hide_dropdown()
                else:
                    self.show_file_dropdown()
            elif event.ui_element == self.help_button:
                if self.active_menu == "help":
                    self.hide_dropdown()
                else:
                    self.show_help_dropdown()
            elif event.ui_element == self.load_fen_button:
                self.hide_dropdown()
                return "load_fen"
            elif event.ui_element == self.credits_button:
                self.hide_dropdown()
                return "show_credits"

        # Hide dropdown when clicking elsewhere
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active_menu is not None:
                # Check if click is outside menu elements
                mouse_pos = event.pos
                file_rect = self.file_button.relative_rect
                help_rect = self.help_button.relative_rect
                dropdown_rect = (
                    self.dropdown_panel.relative_rect
                    if self.dropdown_panel
                    else pygame.Rect(0, 0, 0, 0)
                )
                if (
                    not file_rect.collidepoint(mouse_pos)
                    and not help_rect.collidepoint(mouse_pos)
                    and not dropdown_rect.collidepoint(mouse_pos)
                ):
                    self.hide_dropdown()

        return None
