import pygame
import pygame_gui

from game_controller import GameController
from chess import AIPlayerError
from graphics import BoardRenderer, PieceRenderer, SpriteLoader, IconLoader
from graphics.ui import (
    MenuBar,
    FENDialog,
    show_error_dialog,
    CreditsDialog,
    ControlPanel,
    PromotionDialog,
)
from graphics.constants import (
    BOARD_PIXEL_SIZE,
    SQUARE_SIZE,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
    BOARD_SIZE,
    MENU_BUTTON_HEIGHT,
    MENU_BAR_BORDER,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SIDEBAR_X,
    SIDEBAR_Y,
    SIDEBAR_WIDTH,
    CONTROL_ICON_SIZE,
    SIDEBAR_BACKGROUND,
)

SPRITE_PATH = "assets/sprites/Chess_Pieces_Sprite.svg"


def pixel_to_square(x: int, y: int, rotated: bool = False) -> tuple[int, int] | None:
    """Convert pixel coordinates to board square (file, rank)."""
    if x < BOARD_OFFSET_X or x >= BOARD_OFFSET_X + BOARD_PIXEL_SIZE:
        return None
    if y < BOARD_OFFSET_Y or y >= BOARD_OFFSET_Y + BOARD_PIXEL_SIZE:
        return None

    if rotated:
        file = BOARD_SIZE - 1 - (x - BOARD_OFFSET_X) // SQUARE_SIZE
        rank = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
    else:
        file = (x - BOARD_OFFSET_X) // SQUARE_SIZE
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

    # Load sprites and icons
    sprite_loader = SpriteLoader(SPRITE_PATH)
    icon_loader = IconLoader(CONTROL_ICON_SIZE)
    icon_loader.load_icon("undo", "assets/sprites/undo.svg")
    icon_loader.load_icon("redo", "assets/sprites/redo.svg")
    icon_loader.load_icon("rotate", "assets/sprites/rotate.svg")

    # Initialize renderers
    piece_renderer = PieceRenderer(sprite_loader)
    board_renderer = BoardRenderer(piece_renderer)

    # Initialize UI components
    menu_bar = MenuBar(ui_manager, WINDOW_WIDTH)
    control_panel = ControlPanel(ui_manager, icon_loader)

    # Dialog state
    fen_dialog: FENDialog | None = None
    credits_dialog: CreditsDialog | None = None
    promotion_dialog: PromotionDialog | None = None
    pending_promotion: tuple[int, int] | None = None  # Target square for promotion

    # Initialize game controller
    game = GameController()

    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui_manager.process_events(event)

            # Handle menu bar
            action = menu_bar.process_event(event)
            if action == "load_fen":
                fen_dialog = FENDialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT))
            elif action == "show_credits":
                credits_dialog = CreditsDialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT))

            # Handle FEN dialog
            if fen_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == fen_dialog.ok_button:
                    try:
                        game.load_fen(fen_dialog.get_fen_string())
                    except ValueError as e:
                        show_error_dialog(
                            ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT), str(e)
                        )
                    fen_dialog.kill()
                    fen_dialog = None
                elif event.ui_element == fen_dialog.cancel_button:
                    fen_dialog.kill()
                    fen_dialog = None

            # Handle credits dialog
            if credits_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == credits_dialog.close_button:
                    credits_dialog.kill()
                    credits_dialog = None

            # Handle window close events
            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if fen_dialog is not None and event.ui_element == fen_dialog:
                    fen_dialog = None
                if credits_dialog is not None and event.ui_element == credits_dialog:
                    credits_dialog = None
                if promotion_dialog is not None and event.ui_element == promotion_dialog:
                    promotion_dialog = None
                    pending_promotion = None

            # Handle promotion dialog
            if promotion_dialog is not None:
                selected_piece_type = promotion_dialog.process_event(event)
                if selected_piece_type is not None and pending_promotion is not None:
                    game.execute_move(pending_promotion, selected_piece_type)
                    promotion_dialog.kill()
                    promotion_dialog = None
                    pending_promotion = None

            # Handle control panel (only when no dialogs and AI not thinking)
            if promotion_dialog is None and not game.ai_is_thinking:
                control_action = control_panel.process_event(event)
                if control_action == "undo":
                    game.undo()
                elif control_action == "redo":
                    game.redo()
                elif control_action == "rotate":
                    board_renderer.toggle_rotation()
                    game.clear_selection()

            # Handle board clicks
            all_dialogs_closed = (
                fen_dialog is None
                and credits_dialog is None
                and promotion_dialog is None
            )
            if (
                all_dialogs_closed
                and game.is_human_turn
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                clicked_square = pixel_to_square(*event.pos, board_renderer.rotated)

                if clicked_square is not None:
                    if game.is_valid_move(clicked_square):
                        # Execute move (check for promotion first)
                        if game.is_promotion_move(clicked_square):
                            promoting_piece = game.board.get_piece(*game.selected_square)
                            promotion_dialog = PromotionDialog(
                                ui_manager,
                                (WINDOW_WIDTH, WINDOW_HEIGHT),
                                promoting_piece.color,
                                sprite_loader,
                            )
                            pending_promotion = clicked_square
                        else:
                            game.execute_move(clicked_square)
                    else:
                        game.select_square(*clicked_square)
                else:
                    game.clear_selection()

        # Update AI
        try:
            game.update_ai()
        except AIPlayerError as e:
            show_error_dialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT), f"AI error: {e}")

        # Update UI
        ui_manager.update(time_delta)
        control_panel.update_button_states(
            game.game_state.can_undo(), game.game_state.can_redo()
        )

        # Draw
        board_renderer.draw(
            screen, game.board, game.selected_square, game.valid_moves
        )

        # Draw sidebar
        sidebar_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, BOARD_PIXEL_SIZE)
        pygame.draw.rect(screen, SIDEBAR_BACKGROUND, sidebar_rect)

        # Draw menu bar border
        pygame.draw.line(
            screen,
            MENU_BAR_BORDER,
            (0, MENU_BUTTON_HEIGHT),
            (WINDOW_WIDTH, MENU_BUTTON_HEIGHT),
        )

        ui_manager.draw_ui(screen)
        control_panel.draw(screen)

        if promotion_dialog is not None:
            promotion_dialog.draw_pieces(screen)

        pygame.display.flip()

    # Cleanup
    game.cleanup()
    pygame.quit()


if __name__ == "__main__":
    main()
