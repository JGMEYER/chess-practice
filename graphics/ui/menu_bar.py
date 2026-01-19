from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel

from graphics.constants import MENU_BUTTON_HEIGHT

# Menu bar dimensions
MENU_BUTTON_WIDTH = 60
DROPDOWN_WIDTH = 150
DROPDOWN_ITEM_HEIGHT = 28


class MenuBar:
    """Top menu bar with File, Game, and Help menus."""

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
            relative_rect=pygame.Rect((0, 0), (MENU_BUTTON_WIDTH, self.menu_height)),
            text="File",
            manager=manager,
            object_id="#menu_button",
        )

        # Create Game menu button
        self.game_button = UIButton(
            relative_rect=pygame.Rect(
                (MENU_BUTTON_WIDTH, 0), (MENU_BUTTON_WIDTH, self.menu_height)
            ),
            text="Game",
            manager=manager,
            object_id="#menu_button",
        )

        # Create Help menu button
        self.help_button = UIButton(
            relative_rect=pygame.Rect(
                (MENU_BUTTON_WIDTH * 2, 0), (MENU_BUTTON_WIDTH, self.menu_height)
            ),
            text="Help",
            manager=manager,
            object_id="#menu_button",
        )

        # Dropdown state
        self.active_menu: str | None = None
        self.dropdown_panel: UIPanel | None = None
        self.load_fen_button: UIButton | None = None
        self.load_pgn_button: UIButton | None = None
        self.copy_fen_button: UIButton | None = None
        self.copy_pgn_button: UIButton | None = None
        self.reset_game_button: UIButton | None = None
        self.settings_button: UIButton | None = None
        self.credits_button: UIButton | None = None

    def show_file_dropdown(self) -> None:
        """Show the File dropdown menu."""
        self.hide_dropdown()
        button_bottom = self.file_button.relative_rect.bottom

        # Create panel container for dropdown (4 items)
        num_items = 4
        panel_height = num_items * DROPDOWN_ITEM_HEIGHT
        self.dropdown_panel = UIPanel(
            relative_rect=pygame.Rect((0, button_bottom), (DROPDOWN_WIDTH, panel_height)),
            manager=self.manager,
            object_id="#dropdown_panel",
        )

        # Create menu items
        item_size = (DROPDOWN_WIDTH, DROPDOWN_ITEM_HEIGHT)

        self.copy_fen_button = UIButton(
            relative_rect=pygame.Rect((0, 0 * DROPDOWN_ITEM_HEIGHT), item_size),
            text="Copy FEN",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )

        self.copy_pgn_button = UIButton(
            relative_rect=pygame.Rect((0, 1 * DROPDOWN_ITEM_HEIGHT), item_size),
            text="Copy PGN",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )

        self.load_fen_button = UIButton(
            relative_rect=pygame.Rect((0, 2 * DROPDOWN_ITEM_HEIGHT), item_size),
            text="Load from FEN...",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )

        self.load_pgn_button = UIButton(
            relative_rect=pygame.Rect((0, 3 * DROPDOWN_ITEM_HEIGHT), item_size),
            text="Load from PGN...",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )

        self.active_menu = "file"

    def show_game_dropdown(self) -> None:
        """Show the Game dropdown menu."""
        self.hide_dropdown()
        button_bottom = self.game_button.relative_rect.bottom

        # Create panel container for dropdown (2 items)
        num_items = 2
        panel_height = num_items * DROPDOWN_ITEM_HEIGHT
        self.dropdown_panel = UIPanel(
            relative_rect=pygame.Rect(
                (MENU_BUTTON_WIDTH, button_bottom), (DROPDOWN_WIDTH, panel_height)
            ),
            manager=self.manager,
            object_id="#dropdown_panel",
        )

        item_size = (DROPDOWN_WIDTH, DROPDOWN_ITEM_HEIGHT)

        # Create Reset button
        self.reset_game_button = UIButton(
            relative_rect=pygame.Rect((0, 0), item_size),
            text="Reset",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )

        # Create Settings button
        self.settings_button = UIButton(
            relative_rect=pygame.Rect((0, DROPDOWN_ITEM_HEIGHT), item_size),
            text="Settings...",
            manager=self.manager,
            container=self.dropdown_panel,
            object_id="#file_menu_item",
        )

        self.active_menu = "game"

    def show_help_dropdown(self) -> None:
        """Show the Help dropdown menu."""
        self.hide_dropdown()
        button_bottom = self.help_button.relative_rect.bottom

        # Create panel container for dropdown (1 item)
        num_items = 1
        panel_height = num_items * DROPDOWN_ITEM_HEIGHT
        self.dropdown_panel = UIPanel(
            relative_rect=pygame.Rect(
                (MENU_BUTTON_WIDTH * 2, button_bottom), (DROPDOWN_WIDTH, panel_height)
            ),
            manager=self.manager,
            object_id="#dropdown_panel",
        )

        # Create Credits button
        self.credits_button = UIButton(
            relative_rect=pygame.Rect((0, 0), (DROPDOWN_WIDTH, DROPDOWN_ITEM_HEIGHT)),
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
        self.load_pgn_button = None
        self.copy_fen_button = None
        self.copy_pgn_button = None
        self.reset_game_button = None
        self.settings_button = None
        self.credits_button = None
        self.active_menu = None

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process UI events.

        Args:
            event: A pygame event

        Returns:
            Action string if an action was triggered, None otherwise.
            Possible actions: "load_fen", "load_pgn", "copy_fen", "copy_pgn",
                            "reset_game", "show_settings", "show_credits"
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.file_button:
                if self.active_menu == "file":
                    self.hide_dropdown()
                else:
                    self.show_file_dropdown()
            elif event.ui_element == self.game_button:
                if self.active_menu == "game":
                    self.hide_dropdown()
                else:
                    self.show_game_dropdown()
            elif event.ui_element == self.help_button:
                if self.active_menu == "help":
                    self.hide_dropdown()
                else:
                    self.show_help_dropdown()
            elif event.ui_element == self.load_fen_button:
                self.hide_dropdown()
                return "load_fen"
            elif event.ui_element == self.load_pgn_button:
                self.hide_dropdown()
                return "load_pgn"
            elif event.ui_element == self.copy_fen_button:
                self.hide_dropdown()
                return "copy_fen"
            elif event.ui_element == self.copy_pgn_button:
                self.hide_dropdown()
                return "copy_pgn"
            elif event.ui_element == self.reset_game_button:
                self.hide_dropdown()
                return "reset_game"
            elif event.ui_element == self.settings_button:
                self.hide_dropdown()
                return "show_settings"
            elif event.ui_element == self.credits_button:
                self.hide_dropdown()
                return "show_credits"

        # Hide dropdown when clicking elsewhere
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active_menu is not None:
                # Check if click is outside menu elements
                mouse_pos = event.pos
                file_rect = self.file_button.relative_rect
                game_rect = self.game_button.relative_rect
                help_rect = self.help_button.relative_rect
                dropdown_rect = (
                    self.dropdown_panel.relative_rect
                    if self.dropdown_panel
                    else pygame.Rect(0, 0, 0, 0)
                )
                if (
                    not file_rect.collidepoint(mouse_pos)
                    and not game_rect.collidepoint(mouse_pos)
                    and not help_rect.collidepoint(mouse_pos)
                    and not dropdown_rect.collidepoint(mouse_pos)
                ):
                    self.hide_dropdown()

        return None
