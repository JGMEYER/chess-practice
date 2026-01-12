from __future__ import annotations

import io

import cairosvg
import pygame

from chess.constants import PieceType, Color
from .constants import SQUARE_SIZE


# Sprite sheet layout: each piece is 45x45 pixels
# Row 0 (y=0): White pieces
# Row 1 (y=45): Black pieces
# Columns: King, Queen, Bishop, Knight, Rook, Pawn (x = 0, 45, 90, 135, 180, 225)
SPRITE_SIZE = 45
PIECE_ORDER = [
    PieceType.KING,
    PieceType.QUEEN,
    PieceType.BISHOP,
    PieceType.KNIGHT,
    PieceType.ROOK,
    PieceType.PAWN,
]


class PieceSpriteLoader:
    """Loads and manages chess piece sprites from an SVG sprite sheet."""

    def __init__(self, sprite_path: str):
        """
        Load the sprite sheet and slice it into individual piece surfaces.

        Args:
            sprite_path: Path to the SVG sprite sheet file
        """
        self._sprite_path = sprite_path
        self._sprites: dict[tuple[Color, PieceType], pygame.Surface] = {}
        self._sized_sprites: dict[int, dict[tuple[Color, PieceType], pygame.Surface]] = {}
        self._load_sprites(sprite_path)

    def _load_sprites(self, sprite_path: str) -> None:
        """Load and slice the sprite sheet into individual pieces."""
        # Calculate the scaled sprite sheet size
        # Original: 270x90, we want pieces at SQUARE_SIZE
        scale_factor = SQUARE_SIZE / SPRITE_SIZE
        scaled_width = int(270 * scale_factor)
        scaled_height = int(90 * scale_factor)

        # Convert SVG to PNG in memory at the desired scale
        png_data = cairosvg.svg2png(
            url=sprite_path,
            output_width=scaled_width,
            output_height=scaled_height,
        )
        sprite_sheet = pygame.image.load(io.BytesIO(png_data))

        scaled_piece_size = SQUARE_SIZE

        # Slice out individual pieces
        for col, piece_type in enumerate(PIECE_ORDER):
            x = col * scaled_piece_size

            # White pieces (row 0)
            white_rect = pygame.Rect(x, 0, scaled_piece_size, scaled_piece_size)
            white_surface = pygame.Surface(
                (scaled_piece_size, scaled_piece_size), pygame.SRCALPHA
            )
            white_surface.blit(sprite_sheet, (0, 0), white_rect)
            self._sprites[(Color.WHITE, piece_type)] = white_surface

            # Black pieces (row 1)
            black_rect = pygame.Rect(
                x, scaled_piece_size, scaled_piece_size, scaled_piece_size
            )
            black_surface = pygame.Surface(
                (scaled_piece_size, scaled_piece_size), pygame.SRCALPHA
            )
            black_surface.blit(sprite_sheet, (0, 0), black_rect)
            self._sprites[(Color.BLACK, piece_type)] = black_surface

    def get_sprite(self, color: Color, piece_type: PieceType) -> pygame.Surface:
        """
        Get the sprite surface for a specific piece at the default size (SQUARE_SIZE).

        Args:
            color: The piece color
            piece_type: The type of piece

        Returns:
            A pygame Surface containing the piece sprite
        """
        return self._sprites[(color, piece_type)]

    def get_sprite_at_size(
        self, color: Color, piece_type: PieceType, size: int
    ) -> pygame.Surface:
        """
        Get the sprite surface for a specific piece at a custom size.

        Renders directly from SVG at the requested size for best quality.

        Args:
            color: The piece color
            piece_type: The type of piece
            size: The desired size in pixels

        Returns:
            A pygame Surface containing the piece sprite at the requested size
        """
        # Return cached if available
        if size in self._sized_sprites:
            return self._sized_sprites[size][(color, piece_type)]

        # Render SVG at the requested size
        scale_factor = size / SPRITE_SIZE
        scaled_width = int(270 * scale_factor)
        scaled_height = int(90 * scale_factor)

        png_data = cairosvg.svg2png(
            url=self._sprite_path,
            output_width=scaled_width,
            output_height=scaled_height,
        )
        sprite_sheet = pygame.image.load(io.BytesIO(png_data))

        # Slice out individual pieces and cache them
        self._sized_sprites[size] = {}
        for col, pt in enumerate(PIECE_ORDER):
            x = col * size

            # White pieces (row 0)
            white_rect = pygame.Rect(x, 0, size, size)
            white_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            white_surface.blit(sprite_sheet, (0, 0), white_rect)
            self._sized_sprites[size][(Color.WHITE, pt)] = white_surface

            # Black pieces (row 1)
            black_rect = pygame.Rect(x, size, size, size)
            black_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            black_surface.blit(sprite_sheet, (0, 0), black_rect)
            self._sized_sprites[size][(Color.BLACK, pt)] = black_surface

        return self._sized_sprites[size][(color, piece_type)]
