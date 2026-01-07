from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine
from pygame_gui.windows import UIMessageWindow


class FENDialog(pygame_gui.elements.UIWindow):
    """Modal dialog for entering FEN strings."""

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        window_size: tuple[int, int],
    ):
        """
        Initialize the FEN dialog.

        Args:
            manager: The pygame_gui UI manager
            window_size: Size of the main window (for centering)
        """
        dialog_width = 500
        dialog_height = 150

        # Center the dialog
        x = (window_size[0] - dialog_width) // 2
        y = (window_size[1] - dialog_height) // 2

        super().__init__(
            rect=pygame.Rect((x, y), (dialog_width, dialog_height)),
            manager=manager,
            window_display_title="Load FEN Position",
            object_id="#fen_dialog",
        )

        # Label
        self.label = UILabel(
            relative_rect=pygame.Rect((10, 10), (dialog_width - 40, 25)),
            text="Enter FEN string:",
            manager=manager,
            container=self,
        )

        # Text input
        self.text_entry = UITextEntryLine(
            relative_rect=pygame.Rect((10, 40), (dialog_width - 40, 35)),
            manager=manager,
            container=self,
        )
        # Set default starting position FEN
        self.text_entry.set_text(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )

        # OK button
        self.ok_button = UIButton(
            relative_rect=pygame.Rect((dialog_width - 180, 85), (75, 30)),
            text="OK",
            manager=manager,
            container=self,
        )

        # Cancel button
        self.cancel_button = UIButton(
            relative_rect=pygame.Rect((dialog_width - 95, 85), (75, 30)),
            text="Cancel",
            manager=manager,
            container=self,
        )

    def get_fen_string(self) -> str:
        """Get the entered FEN string."""
        return self.text_entry.get_text()


def show_error_dialog(
    manager: pygame_gui.UIManager,
    window_size: tuple[int, int],
    message: str,
) -> UIMessageWindow:
    """
    Show an error dialog.

    Args:
        manager: The pygame_gui UI manager
        window_size: Size of the main window (for positioning)
        message: The error message to display

    Returns:
        The message window (for event handling if needed)
    """
    dialog_width = 400
    dialog_height = 200
    x = (window_size[0] - dialog_width) // 2
    y = (window_size[1] - dialog_height) // 2

    return UIMessageWindow(
        rect=pygame.Rect((x, y), (dialog_width, dialog_height)),
        html_message=f"<b>Error:</b><br><br>{message}",
        manager=manager,
        window_title="FEN Error",
    )
