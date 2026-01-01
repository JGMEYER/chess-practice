import pygame

from chess import Board
from graphics import BoardRenderer, PieceRenderer, SpriteLoader
from graphics.constants import WINDOW_SIZE, LABEL_MARGIN, BOARD_PIXEL_SIZE

# Window dimensions: board + margins for labels
WINDOW_WIDTH = BOARD_PIXEL_SIZE + LABEL_MARGIN
WINDOW_HEIGHT = BOARD_PIXEL_SIZE + LABEL_MARGIN

SPRITE_PATH = "assets/sprites/Chess_Pieces_Sprite.svg"


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

    clock = pygame.time.Clock()

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw
        board_renderer.draw(screen)
        piece_renderer.draw_pieces(screen, board)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
