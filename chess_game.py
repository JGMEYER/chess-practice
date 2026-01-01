import pygame

from chess import Board, MoveGenerator
from graphics import BoardRenderer, PieceRenderer, SpriteLoader
from graphics.constants import (
    LABEL_MARGIN,
    BOARD_PIXEL_SIZE,
    SQUARE_SIZE,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
    BOARD_SIZE,
)

# Window dimensions: board + margins for labels
WINDOW_WIDTH = BOARD_PIXEL_SIZE + LABEL_MARGIN
WINDOW_HEIGHT = BOARD_PIXEL_SIZE + LABEL_MARGIN

SPRITE_PATH = "assets/sprites/Chess_Pieces_Sprite.svg"


def pixel_to_square(x: int, y: int) -> tuple[int, int] | None:
    """Convert pixel coordinates to board square (file, rank)."""
    # Check if click is within board bounds
    if x < BOARD_OFFSET_X or x >= BOARD_OFFSET_X + BOARD_PIXEL_SIZE:
        return None
    if y < BOARD_OFFSET_Y or y >= BOARD_OFFSET_Y + BOARD_PIXEL_SIZE:
        return None

    file = (x - BOARD_OFFSET_X) // SQUARE_SIZE
    # Flip y to get rank (rank 0 is at bottom)
    rank = BOARD_SIZE - 1 - (y - BOARD_OFFSET_Y) // SQUARE_SIZE

    return (file, rank)


def main():
    pygame.init()

    # Window setup
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess")

    # Initialize game components
    board = Board()
    board.setup_initial_position()

    sprite_loader = SpriteLoader(SPRITE_PATH)
    board_renderer = BoardRenderer()
    piece_renderer = PieceRenderer(sprite_loader)
    move_generator = MoveGenerator()

    clock = pygame.time.Clock()

    # Selection state
    selected_square: tuple[int, int] | None = None
    valid_moves: list[tuple[int, int]] = []

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    clicked_square = pixel_to_square(*event.pos)

                    if clicked_square is None:
                        # Clicked outside board
                        selected_square = None
                        valid_moves = []
                    elif selected_square == clicked_square:
                        # Clicked same square - deselect
                        selected_square = None
                        valid_moves = []
                    else:
                        # Check if there's a piece on the clicked square
                        piece = board.get_piece(*clicked_square)
                        if piece is not None:
                            # Select this piece
                            selected_square = clicked_square
                            valid_moves = move_generator.get_valid_moves(board, piece)
                        else:
                            # Clicked empty square - deselect
                            selected_square = None
                            valid_moves = []

        # Draw
        board_renderer.draw(screen, selected_square, valid_moves)
        piece_renderer.draw_pieces(screen, board)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
