from __future__ import annotations

import io

import cairosvg
import pygame


class IconLoader:
    """Loads SVG icons and converts them to pygame surfaces."""

    def __init__(self, icon_size: int = 40):
        """
        Initialize the icon loader.

        Args:
            icon_size: Size in pixels for square icons
        """
        self.icon_size = icon_size
        self._icons: dict[str, pygame.Surface] = {}

    def load_icon(self, name: str, path: str) -> pygame.Surface:
        """
        Load an SVG icon and convert to pygame surface.

        Args:
            name: Name to store the icon under
            path: Path to the SVG file

        Returns:
            The loaded pygame surface
        """
        # Read SVG file and modify viewBox to crop attribution text
        with open(path, 'r') as f:
            svg_content = f.read()

        # Replace viewBox to crop to just the icon (100x100 instead of 100x125)
        # This removes the "Created by..." text at the bottom
        svg_content = svg_content.replace('viewBox="0 0 100 125"', 'viewBox="0 0 100 100"')

        # Convert SVG to PNG in memory at the desired size
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=self.icon_size,
            output_height=self.icon_size,
        )
        surface = pygame.image.load(io.BytesIO(png_data))

        # Invert colors to make icons white (better visibility on dark background)
        surface = self._invert_surface(surface)

        self._icons[name] = surface
        return surface

    def _invert_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Recolor black icons to match UI label colors.

        Args:
            surface: The pygame surface to recolor

        Returns:
            The recolored surface
        """
        # White color for high contrast on dark button backgrounds
        target_color = (255, 255, 255)

        # Create a copy with per-pixel alpha
        recolored = surface.copy()
        width, height = recolored.get_size()

        # Lock surface for pixel access
        recolored.lock()
        for x in range(width):
            for y in range(height):
                r, g, b, a = recolored.get_at((x, y))
                if a > 0:  # Only recolor non-transparent pixels
                    # Calculate brightness (0-255)
                    brightness = (r + g + b) // 3
                    # Map black/dark pixels to target color, preserve relative brightness
                    factor = brightness / 255.0
                    new_r = int(target_color[0] * (0.5 + factor * 0.5))
                    new_g = int(target_color[1] * (0.5 + factor * 0.5))
                    new_b = int(target_color[2] * (0.5 + factor * 0.5))
                    recolored.set_at((x, y), (new_r, new_g, new_b, a))
        recolored.unlock()

        return recolored

    def get_icon(self, name: str) -> pygame.Surface:
        """
        Get a loaded icon surface.

        Args:
            name: Name of the icon to retrieve

        Returns:
            The pygame surface for the icon

        Raises:
            KeyError: If the icon hasn't been loaded
        """
        return self._icons[name]
