import pygame
import pygame_gui

from chess import Board, MoveGenerator, MoveExecutor, FENLoader
from chess.game_state import GameState
from graphics import BoardRenderer, PieceRenderer, SpriteLoader, IconLoader
from graphics.ui import MenuBar, FENDialog, show_error_dialog, CreditsDialog, ControlPanel
from graphics.constants import (
    LABEL_MARGIN,
    BOARD_PIXEL_SIZE,
    SQUARE_SIZE,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
    BOARD_SIZE,
    MENU_BAR_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SIDEBAR_X,
    SIDEBAR_Y,
    SIDEBAR_WIDTH,
    CONTROL_BUTTON_SIZE,
    BACKGROUND,
    SIDEBAR_BACKGROUND,
)

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

    # Initialize pygame_gui
    ui_manager = pygame_gui.UIManager(
        (WINDOW_WIDTH, WINDOW_HEIGHT), "assets/theme.json"
    )

    # Load control icons
    icon_loader = IconLoader(CONTROL_BUTTON_SIZE)
    icon_loader.load_icon("undo", "assets/sprites/undo.svg")
    icon_loader.load_icon("redo", "assets/sprites/redo.svg")
    icon_loader.load_icon("flip", "assets/sprites/flip.svg")

    # Initialize UI components
    menu_bar = MenuBar(ui_manager, WINDOW_WIDTH)
    control_panel = ControlPanel(ui_manager, icon_loader)
    fen_dialog: FENDialog | None = None
    credits_dialog: CreditsDialog | None = None

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
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Process UI events
            ui_manager.process_events(event)

            # Handle menu bar actions
            action = menu_bar.process_event(event)
            if action == "load_fen":
                fen_dialog = FENDialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT))
            elif action == "show_credits":
                credits_dialog = CreditsDialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT))

            # Handle FEN dialog events
            if fen_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == fen_dialog.ok_button:
                    fen_string = fen_dialog.get_fen_string()
                    try:
                        fen_loader.load(fen_string)
                        selected_square = None
                        valid_moves = []
                    except ValueError as e:
                        show_error_dialog(
                            ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT), str(e)
                        )
                    fen_dialog.kill()
                    fen_dialog = None
                elif event.ui_element == fen_dialog.cancel_button:
                    fen_dialog.kill()
                    fen_dialog = None

            # Handle credits dialog events
            if credits_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == credits_dialog.close_button:
                    credits_dialog.kill()
                    credits_dialog = None

            # Handle window close events (for dialogs)
            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if fen_dialog is not None and event.ui_element == fen_dialog:
                    fen_dialog = None
                if credits_dialog is not None and event.ui_element == credits_dialog:
                    credits_dialog = None

            # Handle control panel actions
            control_action = control_panel.process_event(event)
            if control_action == "undo":
                print("Undo clicked (not yet implemented)")
            elif control_action == "redo":
                print("Redo clicked (not yet implemented)")
            elif control_action == "flip":
                print("Flip clicked (not yet implemented)")

            # Handle board clicks (only when no dialog is open)
            if fen_dialog is None and credits_dialog is None and event.type == pygame.MOUSEBUTTONDOWN:
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
                            valid_moves = move_generator.get_legal_moves(
                                board, piece, game_state
                            )
                        else:
                            # Clicked empty square - deselect
                            selected_square = None
                            valid_moves = []

        # Update UI
        ui_manager.update(time_delta)

        # Draw
        board_renderer.draw(screen, board, selected_square, valid_moves)

        # Draw sidebar background
        sidebar_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, BOARD_PIXEL_SIZE)
        pygame.draw.rect(screen, SIDEBAR_BACKGROUND, sidebar_rect)

        ui_manager.draw_ui(screen)

        # Draw control panel icons on top of buttons
        control_panel.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
