from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextBox


# HTML content for the credits
CREDITS_HTML = """<b>Icon Attributions:</b>
- "redo" by Gregor Cresnar (<a href="https://thenounproject.com/icon/redo-3557655/">link</a>)
- "undo" by Gregor Cresnar (<a href="https://thenounproject.com/icon/undo-3557660/">link</a>)
- "vertical flip" by Gregor Cresnar (<a href="https://thenounproject.com/icon/vertical-flip-3552560/">link</a>)
"""


class CreditsDialog(pygame_gui.elements.UIWindow):
    """Modal dialog for displaying credits and attributions."""

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        window_size: tuple[int, int],
    ):
        """
        Initialize the Credits dialog.

        Args:
            manager: The pygame_gui UI manager
            window_size: Size of the main window (for centering)
        """
        dialog_width = 600
        dialog_height = 400

        # Center the dialog
        x = (window_size[0] - dialog_width) // 2
        y = (window_size[1] - dialog_height) // 2

        super().__init__(
            rect=pygame.Rect((x, y), (dialog_width, dialog_height)),
            manager=manager,
            window_display_title="Credits",
            object_id="#credits_dialog",
        )

        # Disable dragging
        if hasattr(self, 'title_bar'):
            self.title_bar.disable()

        # Text box for scrollable credits content
        self.text_box = UITextBox(
            html_text=CREDITS_HTML,
            relative_rect=pygame.Rect((10, 10), (dialog_width - 40, dialog_height - 110)),
            manager=manager,
            container=self,
        )

        # Close button at the bottom with more spacing
        self.close_button = UIButton(
            relative_rect=pygame.Rect(
                ((dialog_width - 100) // 2, dialog_height - 80),
                (100, 40),
            ),
            text="Close",
            manager=manager,
            container=self,
        )
