from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from chess.constants import PieceType, Color
from .constants import (
    CAPTURED_GROUP_GAP,
    CAPTURED_PIECE_SIZE,
    CAPTURED_ROW_Y_TOP,
    CAPTURED_ROW_Y_BOTTOM,
    CAPTURED_ROW_X,
    SIDEBAR_X,
    SIDEBAR_WIDTH,
)

if TYPE_CHECKING:
    from chess import Piece
    from .piece_sprites import PieceSpriteLoader


# Sort order for tiebreaks (knights before bishops)
PIECE_SORT_ORDER = {
    PieceType.PAWN: 0,
    PieceType.KNIGHT: 1,
    PieceType.BISHOP: 2,
    PieceType.ROOK: 3,
    PieceType.QUEEN: 4,
    PieceType.KING: 5,
}

# Visual width of each piece type (how much space it occupies)
# Pawns are narrow, knights/bishops medium, rooks/queens/kings wide
PIECE_VISUAL_WIDTH = {
    PieceType.PAWN: 12,
    PieceType.KNIGHT: 18,
    PieceType.BISHOP: 14,
    PieceType.ROOK: 16,
    PieceType.QUEEN: 18,
    PieceType.KING: 18,
}

# Per-piece-type overlap when same pieces are adjacent
# Pawns use less overlap for better countability
SAME_TYPE_OVERLAP = {
    PieceType.PAWN: 5,
    PieceType.KNIGHT: 7,
    PieceType.BISHOP: 7,
    PieceType.ROOK: 7,
    PieceType.QUEEN: 7,
    PieceType.KING: 7,
}

# Kerning adjustments for piece pairs (from_type, to_type) -> gap adjustment
# Positive = more space, Negative = less space (tighter)
# Accounts for optical density differences between piece silhouettes
PIECE_KERNING = {
    # Knight to bishop: bishop has open left side (mitre), reduce gap
    (PieceType.KNIGHT, PieceType.BISHOP): -2,
    # Knight to rook: knight has irregular right edge, tighten slightly
    (PieceType.KNIGHT, PieceType.ROOK): -1,
    # Knight to queen: tighten slightly
    (PieceType.KNIGHT, PieceType.QUEEN): -1,
    # Bishop to queen: queen is dense, bishop open on right
    (PieceType.BISHOP, PieceType.QUEEN): -1,
}


class CapturedPiecesRenderer:
    """Renders captured pieces in the sidebar."""

    def __init__(self, sprite_loader: PieceSpriteLoader):
        """
        Initialize the captured pieces renderer.

        Args:
            sprite_loader: The sprite loader with loaded piece sprites
        """
        self._sprite_loader = sprite_loader
        self._scaled_sprites: dict[tuple[Color, PieceType], pygame.Surface] = {}
        self._font = pygame.font.SysFont("Arial", 14, bold=True)
        self._load_scaled_sprites()

    def _load_scaled_sprites(self) -> None:
        """Load sprites at the captured piece size (rendered from SVG for clarity)."""
        for color in Color:
            for piece_type in PieceType:
                sprite = self._sprite_loader.get_sprite_at_size(
                    color, piece_type, CAPTURED_PIECE_SIZE
                )
                self._scaled_sprites[(color, piece_type)] = sprite

    def _sort_key(self, piece: Piece) -> tuple[int, int]:
        """Sort key for captured pieces: by point value, then by piece type order."""
        return (piece.point_value, PIECE_SORT_ORDER[piece.piece_type])

    def draw(
        self,
        surface: pygame.Surface,
        captured_pieces: list[Piece],
        rotated: bool,
    ) -> None:
        """
        Draw captured pieces in the sidebar.

        Args:
            surface: The pygame surface to draw on
            captured_pieces: List of captured Piece objects
            rotated: Whether the board is rotated (black at bottom)
        """
        # Separate pieces by the color of the captured piece
        # white_captures = black pieces that white captured
        # black_captures = white pieces that black captured
        white_captures = [p for p in captured_pieces if p.color == Color.BLACK]
        black_captures = [p for p in captured_pieces if p.color == Color.WHITE]

        # Sort by point value, with knights before bishops for tiebreak
        white_captures.sort(key=self._sort_key)
        black_captures.sort(key=self._sort_key)

        # Calculate point totals
        white_points = sum(p.point_value for p in white_captures)
        black_points = sum(p.point_value for p in black_captures)
        point_diff = white_points - black_points

        # Determine row order based on rotation
        # Each player sees their captures (opponent's pieces) on their side
        # Not rotated (white at bottom): white's captures on bottom, black's on top
        # Rotated (black at bottom): black's captures on bottom, white's on top
        if rotated:
            top_captures = white_captures
            bottom_captures = black_captures
            top_diff = point_diff if point_diff > 0 else 0
            bottom_diff = -point_diff if point_diff < 0 else 0
        else:
            top_captures = black_captures
            bottom_captures = white_captures
            top_diff = -point_diff if point_diff < 0 else 0
            bottom_diff = point_diff if point_diff > 0 else 0

        # Draw rows
        self._draw_row(surface, top_captures, CAPTURED_ROW_Y_TOP, top_diff)
        self._draw_row(surface, bottom_captures, CAPTURED_ROW_Y_BOTTOM, bottom_diff)

    def _draw_row(
        self,
        surface: pygame.Surface,
        pieces: list[Piece],
        y: int,
        point_diff: int,
    ) -> None:
        """
        Draw a single row of captured pieces.

        Args:
            surface: The pygame surface to draw on
            pieces: List of captured pieces to draw
            y: Y coordinate for this row
            point_diff: Point differential to show (0 means don't show)
        """
        group_gap = CAPTURED_GROUP_GAP

        # Calculate x positions first so we can draw left-to-right
        # (rightmost pieces drawn last, appearing on top)
        positions: list[tuple[int, Piece]] = []
        x = CAPTURED_ROW_X
        last_piece_type = None

        for piece in pieces:
            if last_piece_type is not None:
                # Use visual width of previous piece for spacing
                prev_width = PIECE_VISUAL_WIDTH[last_piece_type]
                if piece.piece_type == last_piece_type:
                    # Use per-type overlap for same pieces
                    overlap = SAME_TYPE_OVERLAP.get(piece.piece_type, 7)
                    x += prev_width - overlap
                else:
                    # Base gap + kerning adjustment for this pair
                    kerning = PIECE_KERNING.get(
                        (last_piece_type, piece.piece_type), 0
                    )
                    x += prev_width + group_gap + kerning

            positions.append((x, piece))
            last_piece_type = piece.piece_type

        # Draw pieces left-to-right (rightmost on top)
        for x, piece in positions:
            sprite = self._scaled_sprites[(piece.color, piece.piece_type)]
            surface.blit(sprite, (x, y))

        # Draw point differential if > 0
        if point_diff > 0:
            text = self._font.render(f"+{point_diff}", True, (200, 200, 200))
            text_x = SIDEBAR_X + SIDEBAR_WIDTH - text.get_width() - 10
            # +1px down to align with perceived piece visual center
            text_y = y + (CAPTURED_PIECE_SIZE - text.get_height()) // 2 + 1
            surface.blit(text, (text_x, text_y))
