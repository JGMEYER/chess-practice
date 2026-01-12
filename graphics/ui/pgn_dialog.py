"""PGN input dialog."""

from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryBox


class PGNDialog(pygame_gui.elements.UIWindow):
    """Modal dialog for entering PGN strings."""

    # Example PGN for the placeholder
    EXAMPLE_PGN = """[Event "Example Game"]
[White "Player1"]
[Black "Player2"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5"""

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        window_size: tuple[int, int],
    ):
        """
        Initialize the PGN dialog.

        Args:
            manager: The pygame_gui UI manager
            window_size: Size of the main window (for centering)
        """
        dialog_width = 550
        dialog_height = 350

        # Center the dialog
        x = (window_size[0] - dialog_width) // 2
        y = (window_size[1] - dialog_height) // 2

        super().__init__(
            rect=pygame.Rect((x, y), (dialog_width, dialog_height)),
            manager=manager,
            window_display_title="Load PGN Game",
            object_id="#pgn_dialog",
            draggable=False,
        )

        # Label
        self.label = UILabel(
            relative_rect=pygame.Rect((10, 10), (dialog_width - 40, 25)),
            text="Paste PGN:",
            manager=manager,
            container=self,
        )

        # Multi-line text box for PGN input
        self.text_box = UITextEntryBox(
            relative_rect=pygame.Rect((10, 40), (dialog_width - 40, 220)),
            manager=manager,
            container=self,
        )
        # Set example PGN as default
        self.text_box.set_text(self.EXAMPLE_PGN)

        # OK button
        self.ok_button = UIButton(
            relative_rect=pygame.Rect((dialog_width - 180, 270), (75, 30)),
            text="OK",
            manager=manager,
            container=self,
        )

        # Cancel button
        self.cancel_button = UIButton(
            relative_rect=pygame.Rect((dialog_width - 95, 270), (75, 30)),
            text="Cancel",
            manager=manager,
            container=self,
        )

    def get_pgn_string(self) -> str:
        """Get the entered PGN string."""
        return self.text_box.get_text()
