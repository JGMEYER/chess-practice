import pygame

from chess import Board, MoveGenerator, MoveExecutor, FENLoader
from chess.game_state import GameState
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
    game_state = GameState()
    fen_loader = FENLoader(board, game_state)
    fen_loader.load_starting_position()

    sprite_loader = SpriteLoader(SPRITE_PATH)
    piece_renderer = PieceRenderer(sprite_loader)
    board_renderer = BoardRenderer(piece_renderer)
    move_generator = MoveGenerator()
    move_executor = MoveExecutor(board, game_state)

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

                    if clicked_square in valid_moves:
                        move_executor.execute_move(selected_square, clicked_square)
                        selected_square = None
                        valid_moves = []
                    elif clicked_square is None:
                        # Clicked outside board - deselect
                        selected_square = None
                        valid_moves = []
                    elif selected_square == clicked_square:
                        # Clicked same square - deselect
                        selected_square = None
                        valid_moves = []
                    else:
                        # Check if there's a moveable piece on the clicked square
                        piece = board.get_piece(*clicked_square)
                        if (
                            piece is not None
                            and piece.color == game_state.current_turn
                        ):
                            # Select this piece
                            selected_square = clicked_square
                            valid_moves = move_generator.get_valid_moves(
                                board, piece, game_state
                            )
                        else:
                            # Clicked empty square - deselect
                            selected_square = None
                            valid_moves = []

        # Draw
        board_renderer.draw(screen, board, selected_square, valid_moves)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
