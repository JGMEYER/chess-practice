from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from graphics.constants import (
    SIDEBAR_X,
    SIDEBAR_Y,
    SIDEBAR_WIDTH,
    CONTROL_BUTTON_SIZE,
    CONTROL_ICON_SIZE,
    CONTROL_BUTTON_SPACING,
)

if TYPE_CHECKING:
    from graphics.icon_loader import IconLoader


class ControlPanel:
    """Right sidebar control panel with undo/redo/rotate buttons."""

    def __init__(self, manager: pygame_gui.UIManager, icon_loader: IconLoader):
        """
        Initialize the control panel.

        Args:
            manager: The pygame_gui UI manager
            icon_loader: Icon loader with loaded control icons
        """
        self.manager = manager

        # Calculate button positions (centered in sidebar)
        # 4 buttons (40px each) + 3 gaps (10px each) = 190px total
        # Center in SIDEBAR_WIDTH (216px): (216 - 190) / 2 = 13px margin
        total_width = 4 * CONTROL_BUTTON_SIZE + 3 * CONTROL_BUTTON_SPACING
        start_x = SIDEBAR_X + (SIDEBAR_WIDTH - total_width) // 2
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

        # Create rotate button (rotates board 180 degrees)
        rotate_x = start_x + 2 * (CONTROL_BUTTON_SIZE + CONTROL_BUTTON_SPACING)
        self.rotate_button = UIButton(
            relative_rect=pygame.Rect(
                (rotate_x, button_y),
                (CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE)
            ),
            text="",
            manager=manager,
            object_id="#control_button",
        )

        # Create AI toggle button
        ai_x = start_x + 3 * (CONTROL_BUTTON_SIZE + CONTROL_BUTTON_SPACING)
        self.ai_button = UIButton(
            relative_rect=pygame.Rect(
                (ai_x, button_y),
                (CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE)
            ),
            text="",
            manager=manager,
            object_id="#control_button",
        )

        # Store icons and buttons for custom rendering
        self.undo_icon = icon_loader.get_icon("undo")
        self.redo_icon = icon_loader.get_icon("redo")
        self.rotate_icon = self._create_rotate_icon(icon_loader.get_icon("rotate"))
        self.ai_icon = self._create_ai_text_icon()

        # Calculate padding to center icons within buttons
        self.icon_padding = (CONTROL_BUTTON_SIZE - CONTROL_ICON_SIZE) // 2

        # Create disabled (dimmed) versions of icons for unavailable actions
        self.undo_icon_disabled = self._create_disabled_icon(self.undo_icon)
        self.redo_icon_disabled = self._create_disabled_icon(self.redo_icon)
        self.ai_icon_disabled = self._create_disabled_icon(self.ai_icon)
        # Active (green) version for when AI mode is ON
        self.ai_icon_active = self._create_active_icon(self.ai_icon)

        # Track action button states (whether action is available)
        self._undo_available = False
        self._redo_available = False
        # Track AI toggle state (whether AI mode is on/off)
        self._ai_mode_active = True
        self._ai_available = True
        self.undo_button.disable()
        self.redo_button.disable()

    def _create_disabled_icon(self, icon: pygame.Surface) -> pygame.Surface:
        """Create a dimmed version of an icon for disabled state."""
        disabled = icon.copy()
        disabled.set_alpha(80)
        return disabled

    def _create_active_icon(self, icon: pygame.Surface) -> pygame.Surface:
        """Create a green-tinted version of an icon for active toggle state."""
        active = icon.copy()
        active.fill((100, 255, 100), special_flags=pygame.BLEND_MULT)
        return active

    def _create_rotate_icon(self, base_icon: pygame.Surface) -> pygame.Surface:
        """Create rotate icon with '180' text overlay."""
        icon = base_icon.copy()

        # Create small font for "180" text
        font = pygame.font.SysFont("Arial", 10, bold=True)
        text = font.render("180", True, (255, 255, 255))

        # Position text in bottom-right area of icon
        text_x = icon.get_width() - text.get_width() - 1
        text_y = icon.get_height() - text.get_height() - 1
        icon.blit(text, (text_x, text_y))

        return icon

    def _create_ai_text_icon(self) -> pygame.Surface:
        """Create an 'AI' text icon matching the control icon size."""
        icon = pygame.Surface((CONTROL_ICON_SIZE, CONTROL_ICON_SIZE), pygame.SRCALPHA)

        # Use a bold font for "AI" text
        font = pygame.font.SysFont("Arial", 20, bold=True)
        text = font.render("AI", True, (255, 255, 255))

        # Center the text in the icon
        text_x = (CONTROL_ICON_SIZE - text.get_width()) // 2
        text_y = (CONTROL_ICON_SIZE - text.get_height()) // 2
        icon.blit(text, (text_x, text_y))

        return icon

    def update_button_states(self, can_undo: bool, can_redo: bool) -> None:
        """
        Update the enabled/disabled state of undo and redo buttons.

        Args:
            can_undo: Whether undo action is available
            can_redo: Whether redo action is available
        """
        if can_undo != self._undo_available:
            self._undo_available = can_undo
            if can_undo:
                self.undo_button.enable()
            else:
                self.undo_button.disable()

        if can_redo != self._redo_available:
            self._redo_available = can_redo
            if can_redo:
                self.redo_button.enable()
            else:
                self.redo_button.disable()

    def update_ai_button_state(self, ai_active: bool, ai_available: bool) -> None:
        """
        Update the AI toggle button visual state.

        Args:
            ai_active: Whether AI mode is currently ON (active)
            ai_available: Whether AI (Stockfish) is available at all
        """
        self._ai_mode_active = ai_active
        self._ai_available = ai_available

        # Button is disabled only when Stockfish is unavailable
        if not ai_available:
            self.ai_button.disable()
        else:
            self.ai_button.enable()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw icons centered on top of buttons.

        Args:
            screen: The pygame surface to draw on
        """
        padding = self.icon_padding

        # Draw undo icon (dimmed when action unavailable)
        undo_rect = self.undo_button.rect
        undo_icon = self.undo_icon if self._undo_available else self.undo_icon_disabled
        screen.blit(undo_icon, (undo_rect.x + padding, undo_rect.y + padding))

        # Draw redo icon (dimmed when action unavailable)
        redo_rect = self.redo_button.rect
        redo_icon = self.redo_icon if self._redo_available else self.redo_icon_disabled
        screen.blit(redo_icon, (redo_rect.x + padding, redo_rect.y + padding))

        # Draw rotate icon (always available)
        rotate_rect = self.rotate_button.rect
        screen.blit(self.rotate_icon, (rotate_rect.x + padding, rotate_rect.y + padding))

        # Draw AI toggle icon:
        # - Dimmed: Stockfish unavailable (button disabled)
        # - Normal: AI mode OFF (click to turn on)
        # - Green/Active: AI mode ON (click to turn off)
        ai_rect = self.ai_button.rect
        if not self._ai_available:
            ai_icon = self.ai_icon_disabled
        elif self._ai_mode_active:
            ai_icon = self.ai_icon_active
        else:
            ai_icon = self.ai_icon  # Normal icon when AI is off but available
        screen.blit(ai_icon, (ai_rect.x + padding, ai_rect.y + padding))

    def process_event(self, event: pygame.event.Event) -> str | None:
        """
        Process UI events.

        Args:
            event: A pygame event

        Returns:
            Action string: "undo", "redo", "rotate", "toggle_ai", or None
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.undo_button:
                return "undo"
            elif event.ui_element == self.redo_button:
                return "redo"
            elif event.ui_element == self.rotate_button:
                return "rotate"
            elif event.ui_element == self.ai_button:
                return "toggle_ai"
        return None
