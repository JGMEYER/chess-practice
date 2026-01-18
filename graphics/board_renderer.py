from __future__ import annotations

import pygame

from chess.board import Board
from graphics.piece_renderer import PieceRenderer
from graphics.arrow_renderer import ArrowRenderer

from .constants import (
    LIGHT_SQUARE,
    DARK_SQUARE,
    BACKGROUND,
    LABEL_COLOR,
    SQUARE_SIZE,
    BOARD_SIZE,
    LABEL_MARGIN,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
    SELECTED_SQUARE,
    VALID_MOVE_DOT,
    LAST_MOVE_LIGHT,
    LAST_MOVE_DARK,
    CHECK_LIGHT,
    CHECK_DARK,
    CHECKMATE_LIGHT,
    CHECKMATE_DARK,
)


class BoardRenderer:
    """Renders the chess board squares, labels, pieces, arrows, and move indicators."""

    def __init__(self, piece_renderer: PieceRenderer):
        """Initialize the board renderer."""
        self._font: pygame.font.Font | None = None
        self._piece_renderer = piece_renderer
        self._arrow_renderer = ArrowRenderer()
        self._rotated = False

    @property
    def rotated(self) -> bool:
        """Whether the board is rotated 180 degrees (black at bottom)."""
        return self._rotated

    def toggle_rotation(self) -> None:
        """Toggle the board orientation (rotate 180 degrees)."""
        self._rotated = not self._rotated
        self._arrow_renderer.rotated = self._rotated

    def set_arrows(self, arrows: list[tuple[tuple[int, int], tuple[int, int]]]) -> None:
        """Set the arrows to display on the board.

        Args:
            arrows: List of (from_square, to_square) tuples
        """
        self._arrow_renderer.clear()
        for from_sq, to_sq in arrows:
            self._arrow_renderer.add_arrow(from_sq, to_sq)

    def _ensure_font(self) -> None:
        """Initialize the font if not already done."""
        if self._font is None:
            pygame.font.init()
            self._font = pygame.font.SysFont("Arial", 14, bold=True)

    def _square_to_pixel(self, file: int, rank: int) -> tuple[int, int]:
        """
        Convert board coordinates to pixel position.

        Args:
            file: File index (0-7)
            rank: Rank index (0-7)

        Returns:
            Pixel (x, y) of the top-left corner of the square
        """
        if self._rotated:
            x = BOARD_OFFSET_X + (BOARD_SIZE - 1 - file) * SQUARE_SIZE
            y = BOARD_OFFSET_Y + rank * SQUARE_SIZE
        else:
            x = BOARD_OFFSET_X + file * SQUARE_SIZE
            y = BOARD_OFFSET_Y + (BOARD_SIZE - 1 - rank) * SQUARE_SIZE
        return x, y

    def draw_board(
        self,
        surface: pygame.Surface,
        selected_square: tuple[int, int] | None = None,
        last_move_squares: tuple[tuple[int, int], tuple[int, int]] | None = None,
        check_square: tuple[int, int] | None = None,
        is_checkmate: bool = False,
    ) -> None:
        """
        Draw the chess board squares.

        Args:
            surface: The pygame surface to draw on
            selected_square: Optional (file, rank) of selected square to highlight
            last_move_squares: Optional (from_square, to_square) of last move to highlight
            check_square: Optional (file, rank) of king in check to highlight
            is_checkmate: Whether the game is in checkmate (uses red instead of amber)
        """
        for file in range(BOARD_SIZE):
            for rank in range(BOARD_SIZE):
                is_light = (file + rank) % 2 == 1
                square = (file, rank)

                # Determine square color (priority: selection > check/checkmate > last move > default)
                if selected_square and square == selected_square:
                    color = SELECTED_SQUARE
                elif check_square and square == check_square:
                    if is_checkmate:
                        color = CHECKMATE_LIGHT if is_light else CHECKMATE_DARK
                    else:
                        color = CHECK_LIGHT if is_light else CHECK_DARK
                elif last_move_squares and square in last_move_squares:
                    color = LAST_MOVE_LIGHT if is_light else LAST_MOVE_DARK
                elif is_light:
                    color = LIGHT_SQUARE
                else:
                    color = DARK_SQUARE

                x, y = self._square_to_pixel(file, rank)
                pygame.draw.rect(surface, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    def draw_labels(self, surface: pygame.Surface) -> None:
        """
        Draw rank and file labels in the margins.

        Args:
            surface: The pygame surface to draw on
        """
        self._ensure_font()

        # File labels (a-h) along the bottom
        for file in range(BOARD_SIZE):
            # When flipped, files go h-a from left to right
            display_file = (BOARD_SIZE - 1 - file) if self._rotated else file
            letter = chr(ord("a") + display_file)
            text = self._font.render(letter, True, LABEL_COLOR)
            x = BOARD_OFFSET_X + file * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
            y = BOARD_OFFSET_Y + BOARD_SIZE * SQUARE_SIZE + 4
            surface.blit(text, (x, y))

        # Rank labels (1-8) along the left
        for visual_row in range(BOARD_SIZE):
            # When flipped, ranks go 1-8 from top to bottom
            # When not flipped, ranks go 8-1 from top to bottom
            if self._rotated:
                rank = visual_row + 1
            else:
                rank = BOARD_SIZE - visual_row
            number = str(rank)
            text = self._font.render(number, True, LABEL_COLOR)
            x = (LABEL_MARGIN - text.get_width()) // 2
            y = BOARD_OFFSET_Y + visual_row * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
            surface.blit(text, (x, y))

    def draw_valid_moves(
        self,
        surface: pygame.Surface,
        valid_moves: list[tuple[int, int]],
    ) -> None:
        """
        Draw dots on valid move squares.

        Args:
            surface: The pygame surface to draw on
            valid_moves: List of (file, rank) tuples for valid destinations
        """
        dot_radius = SQUARE_SIZE // 6

        for file, rank in valid_moves:
            # Calculate center of square
            px, py = self._square_to_pixel(file, rank)
            x = px + SQUARE_SIZE // 2
            y = py + SQUARE_SIZE // 2

            # Draw semi-transparent dot
            dot_surface = pygame.Surface((dot_radius * 2, dot_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, VALID_MOVE_DOT, (dot_radius, dot_radius), dot_radius)
            surface.blit(dot_surface, (x - dot_radius, y - dot_radius))

    def draw(
        self,
        surface: pygame.Surface,
        board: Board,
        selected_square: tuple[int, int] | None = None,
        valid_moves: list[tuple[int, int]] | None = None,
        last_move_squares: tuple[tuple[int, int], tuple[int, int]] | None = None,
        check_square: tuple[int, int] | None = None,
        is_checkmate: bool = False,
    ) -> None:
        """
        Draw the complete board with all elements.

        Rendering order:
        1. Board squares and highlights
        2. Labels
        3. Pieces
        4. Arrows (from set_arrows)
        5. Valid move circles (on top of arrows)

        Args:
            surface: The pygame surface to draw on
            board: The board with piece positions
            selected_square: Optional (file, rank) of selected square
            valid_moves: Optional list of valid move squares to show as dots
            last_move_squares: Optional (from_square, to_square) of last move to highlight
            check_square: Optional (file, rank) of king in check to highlight
            is_checkmate: Whether the game is in checkmate (uses red instead of amber)
        """
        surface.fill(BACKGROUND)
        self.draw_board(surface, selected_square, last_move_squares, check_square, is_checkmate)
        self.draw_labels(surface)
        self._piece_renderer.draw_pieces(surface, board, self._rotated)
        self._arrow_renderer.draw(surface)
        if valid_moves:
            self.draw_valid_moves(surface, valid_moves)
