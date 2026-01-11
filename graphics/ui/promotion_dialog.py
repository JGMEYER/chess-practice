from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from chess.constants import PieceType, Color

if TYPE_CHECKING:
    from graphics.sprites import SpriteLoader


# Pieces available for promotion (no pawn or king)
PROMOTION_PIECES = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]


class PromotionDialog(pygame_gui.elements.UIWindow):
    """Modal dialog for selecting pawn promotion piece."""

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        window_size: tuple[int, int],
        color: Color,
        sprite_loader: SpriteLoader,
    ):
        """
        Initialize the promotion dialog.

        Args:
            manager: The pygame_gui UI manager
            window_size: Size of the main window (for centering)
            color: The color of the promoting pawn
            sprite_loader: Sprite loader for piece images
        """
        self.color = color
        self.sprite_loader = sprite_loader
        self.selected_piece_type: PieceType | None = None

        # Dialog dimensions
        button_size = 70
        padding = 10
        dialog_width = len(PROMOTION_PIECES) * button_size + (len(PROMOTION_PIECES) + 1) * padding
        dialog_height = button_size + padding * 2 + 40  # Extra for title bar

        # Center the dialog
        x = (window_size[0] - dialog_width) // 2
        y = (window_size[1] - dialog_height) // 2

        super().__init__(
            rect=pygame.Rect((x, y), (dialog_width, dialog_height)),
            manager=manager,
            window_display_title="Choose Promotion",
            object_id="#promotion_dialog",
            draggable=False,
        )

        # Create buttons for each promotion piece
        self.piece_buttons: dict[UIButton, PieceType] = {}
        self._button_rects: list[tuple[pygame.Rect, PieceType]] = []

        for i, piece_type in enumerate(PROMOTION_PIECES):
            btn_x = padding + i * (button_size + padding)
            btn_y = padding

            button = UIButton(
                relative_rect=pygame.Rect((btn_x, btn_y), (button_size, button_size)),
                text="",
                manager=manager,
                container=self,
                object_id="#promotion_button",
            )
            self.piece_buttons[button] = piece_type

            # Store rect for drawing sprites
            # Account for window position and title bar
            abs_rect = pygame.Rect(
                self.rect.x + btn_x + 2,  # +2 for window border
                self.rect.y + btn_y + 28,  # +28 for title bar
                button_size,
                button_size,
            )
            self._button_rects.append((abs_rect, piece_type))

        self.button_size = button_size

    def draw_pieces(self, screen: pygame.Surface) -> None:
        """
        Draw piece sprites on top of buttons.

        Args:
            screen: The pygame surface to draw on
        """
        for rect, piece_type in self._button_rects:
            sprite = self.sprite_loader.get_sprite(self.color, piece_type)

            # Scale sprite to fit button (with some padding)
            scaled_size = self.button_size - 10
            scaled_sprite = pygame.transform.smoothscale(sprite, (scaled_size, scaled_size))

            # Center sprite in button
            sprite_x = rect.x + (self.button_size - scaled_size) // 2
            sprite_y = rect.y + (self.button_size - scaled_size) // 2

            screen.blit(scaled_sprite, (sprite_x, sprite_y))

    def process_event(self, event: pygame.event.Event) -> PieceType | None:
        """
        Process UI events.

        Args:
            event: A pygame event

        Returns:
            The selected PieceType, or None if no selection made
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.piece_buttons:
                return self.piece_buttons[event.ui_element]
        return None
