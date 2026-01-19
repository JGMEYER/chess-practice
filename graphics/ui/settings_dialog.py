"""Settings dialog for configuring AI difficulty and other options."""

from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIHorizontalSlider, UILabel


class SettingsDialog(pygame_gui.elements.UIWindow):
    """Modal dialog for adjusting game settings including AI difficulty."""

    # Elo range for the slider
    MIN_ELO = 300
    MAX_ELO = 2000
    ELO_STEP = 100  # Snap to nearest 100

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        window_size: tuple[int, int],
        current_elo: int,
    ):
        """
        Initialize the settings dialog.

        Args:
            manager: The pygame_gui UI manager
            window_size: Size of the main window (for centering)
            current_elo: Current AI Elo rating
        """
        dialog_width = 400
        dialog_height = 180

        # Center the dialog
        x = (window_size[0] - dialog_width) // 2
        y = (window_size[1] - dialog_height) // 2

        super().__init__(
            rect=pygame.Rect((x, y), (dialog_width, dialog_height)),
            manager=manager,
            window_display_title="Settings",
            object_id="#settings_dialog",
            draggable=False,
        )

        self._manager = manager
        self._current_elo = current_elo

        # AI Difficulty section
        self.difficulty_label = UILabel(
            relative_rect=pygame.Rect((15, 10), (dialog_width - 50, 25)),
            text="AI Difficulty (Elo Rating)",
            manager=manager,
            container=self,
        )

        # Elo slider
        self.elo_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect((15, 40), (dialog_width - 130, 30)),
            start_value=float(current_elo),
            value_range=(float(self.MIN_ELO), float(self.MAX_ELO)),
            manager=manager,
            container=self,
            object_id="#elo_slider",
        )

        # Elo value display
        self.elo_value_label = UILabel(
            relative_rect=pygame.Rect((dialog_width - 110, 40), (90, 30)),
            text=str(current_elo),
            manager=manager,
            container=self,
            object_id="#elo_value_label",
        )

        # Difficulty description
        self.description_label = UILabel(
            relative_rect=pygame.Rect((15, 75), (dialog_width - 50, 25)),
            text=self._get_difficulty_description(current_elo),
            manager=manager,
            container=self,
            object_id="#difficulty_description",
        )

        # OK button
        self.ok_button = UIButton(
            relative_rect=pygame.Rect((dialog_width - 180, 115), (75, 30)),
            text="OK",
            manager=manager,
            container=self,
        )

        # Cancel button
        self.cancel_button = UIButton(
            relative_rect=pygame.Rect((dialog_width - 95, 115), (75, 30)),
            text="Cancel",
            manager=manager,
            container=self,
        )

    def _get_difficulty_description(self, elo: int) -> str:
        """Get a human-readable description for the Elo level."""
        if elo < 500:
            return "Very Easy - Makes many mistakes"
        elif elo < 800:
            return "Easy - Beginner level play"
        elif elo < 1100:
            return "Casual - Occasional blunders"
        elif elo < 1400:
            return "Medium - Club player level"
        elif elo < 1700:
            return "Hard - Strong amateur"
        elif elo < 1900:
            return "Very Hard - Expert level"
        else:
            return "Maximum - Best moves always"

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process UI events.

        Args:
            event: The pygame event to process

        Returns:
            True if the event was consumed
        """
        consumed = super().process_event(event)

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.elo_slider:
                # Snap to nearest ELO_STEP
                raw_value = self.elo_slider.get_current_value()
                snapped_value = round(raw_value / self.ELO_STEP) * self.ELO_STEP
                snapped_value = max(self.MIN_ELO, min(self.MAX_ELO, snapped_value))
                self._current_elo = int(snapped_value)

                # Update display
                self.elo_value_label.set_text(str(self._current_elo))
                self.description_label.set_text(
                    self._get_difficulty_description(self._current_elo)
                )
                consumed = True

        return consumed

    def get_elo(self) -> int:
        """Get the currently selected Elo value."""
        return self._current_elo
