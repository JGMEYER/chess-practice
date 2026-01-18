import pygame
import pygame_gui

from game_controller import GameController
from chess import AIPlayerError, PGNError
from chess.clipboard import copy_to_clipboard
from graphics import (
    BoardRenderer,
    PieceRenderer,
    PieceSpriteLoader,
    IconLoader,
    CapturedPiecesRenderer,
    MoveListRenderer,
    OpeningRenderer,
    ArrowRenderer,
)
from graphics.ui import (
    MenuBar,
    FENDialog,
    show_error_dialog,
    CreditsDialog,
    ControlPanel,
    PromotionDialog,
    PGNDialog,
    SidePanel,
    TriePanel,
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
    MOVE_LIST_TOP_Y,
    MOVE_LIST_BOTTOM_Y,
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
    sprite_loader = PieceSpriteLoader(SPRITE_PATH)
    icon_loader = IconLoader(CONTROL_ICON_SIZE)
    icon_loader.load_icon("undo", "assets/sprites/undo.svg")
    icon_loader.load_icon("redo", "assets/sprites/redo.svg")
    icon_loader.load_icon("rotate", "assets/sprites/rotate.svg")

    # Initialize renderers
    piece_renderer = PieceRenderer(sprite_loader)
    board_renderer = BoardRenderer(piece_renderer)
    arrow_renderer = ArrowRenderer()

    captured_renderer = CapturedPiecesRenderer(sprite_loader)
    move_list_renderer = MoveListRenderer()
    opening_renderer = OpeningRenderer(ui_manager)

    # Initialize UI components
    menu_bar = MenuBar(ui_manager, WINDOW_WIDTH)
    control_panel = ControlPanel(ui_manager, icon_loader)
    trie_panel = TriePanel(ui_manager)
    side_panel = SidePanel(content=trie_panel, expanded=False)

    # Expand side panel by default
    side_panel.set_expanded(True)
    screen = pygame.display.set_mode((side_panel.get_window_width(), WINDOW_HEIGHT))
    ui_manager.set_window_resolution((side_panel.get_window_width(), WINDOW_HEIGHT))

    # Dialog state
    fen_dialog: FENDialog | None = None
    pgn_dialog: PGNDialog | None = None
    credits_dialog: CreditsDialog | None = None
    promotion_dialog: PromotionDialog | None = None
    pending_promotion: tuple[int, int] | None = None  # Target square for promotion

    # Initialize game controller
    game = GameController()

    # Initialize trie visualization with the opening trie
    trie_panel.set_trie(game.opening_trie.root)

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
            elif action == "load_pgn":
                pgn_dialog = PGNDialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT))
            elif action == "copy_fen":
                copy_to_clipboard(game.get_fen())
            elif action == "copy_pgn":
                copy_to_clipboard(game.get_pgn())
            elif action == "reset_game":
                game.reset()
                move_list_renderer.reset_scroll()
            elif action == "show_credits":
                credits_dialog = CreditsDialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT))

            # Handle FEN dialog
            if fen_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == fen_dialog.ok_button:
                    try:
                        game.load_fen(fen_dialog.get_fen_string())
                        move_list_renderer.reset_scroll()
                    except ValueError as e:
                        show_error_dialog(
                            ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT), str(e)
                        )
                    fen_dialog.kill()
                    fen_dialog = None
                elif event.ui_element == fen_dialog.cancel_button:
                    fen_dialog.kill()
                    fen_dialog = None

            # Handle PGN dialog
            if pgn_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == pgn_dialog.ok_button:
                    try:
                        game.load_pgn(pgn_dialog.get_pgn_string())
                        move_list_renderer.reset_scroll()
                    except (ValueError, PGNError) as e:
                        show_error_dialog(
                            ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT), str(e)
                        )
                    pgn_dialog.kill()
                    pgn_dialog = None
                elif event.ui_element == pgn_dialog.cancel_button:
                    pgn_dialog.kill()
                    pgn_dialog = None

            # Handle credits dialog
            if credits_dialog is not None and event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == credits_dialog.close_button:
                    credits_dialog.kill()
                    credits_dialog = None

            # Handle window close events
            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if fen_dialog is not None and event.ui_element == fen_dialog:
                    fen_dialog = None
                if pgn_dialog is not None and event.ui_element == pgn_dialog:
                    pgn_dialog = None
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
                elif control_action == "toggle_ai":
                    game.toggle_ai_mode()

                # Handle keyboard shortcuts for undo/redo/focus
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        control_panel.trigger_button_press("undo")
                        game.undo()
                    elif event.key == pygame.K_d:
                        control_panel.trigger_button_press("redo")
                        game.redo()
                    elif event.key == pygame.K_f:
                        trie_panel.toggle_focus_mode()

            # Handle board clicks
            all_dialogs_closed = (
                fen_dialog is None
                and pgn_dialog is None
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

            # Handle side panel tab click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if side_panel.handle_click(event.pos):
                    screen = pygame.display.set_mode(
                        (side_panel.get_window_width(), WINDOW_HEIGHT)
                    )
                    ui_manager.set_window_resolution(
                        (side_panel.get_window_width(), WINDOW_HEIGHT)
                    )

            # Handle side panel events (trie visualization interactions)
            trie_action = side_panel.process_event(event)
            if trie_action is not None:
                if trie_action.startswith("trie_navigate:"):
                    # Navigate to the specified move index
                    target_index = int(trie_action.split(":")[1])
                    game.move_executor.jump_to_history_index(target_index)
                    game.clear_selection()
                    game._update_current_opening()
                elif trie_action.startswith("trie_play:"):
                    # Play the specified move (from available moves in trie)
                    san = trie_action.split(":", 1)[1]
                    game.execute_san_move(san)
                # "trie_center" and "trie_select" are handled internally

            # Handle mouse motion for side panel hover
            if event.type == pygame.MOUSEMOTION:
                side_panel.update_hover(event.pos)

            # Handle mouse wheel for move list scrolling
            if event.type == pygame.MOUSEWHEEL and all_dialogs_closed:
                # Check if mouse is over the sidebar area
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x >= SIDEBAR_X and mouse_y >= MOVE_LIST_TOP_Y and mouse_y <= MOVE_LIST_BOTTOM_Y:
                    move_list_renderer.handle_scroll(event.y, len(game.san_history))

        # Update AI
        try:
            game.update_ai()
        except AIPlayerError as e:
            show_error_dialog(ui_manager, (WINDOW_WIDTH, WINDOW_HEIGHT), f"AI error: {e}")

        # Update trie visualization with current game state
        trie_panel.update(game.san_history, game.current_move_count)

        # Update UI
        ui_manager.update(time_delta)
        control_panel.update(time_delta)
        control_panel.update_button_states(
            game.game_state.can_undo(), game.game_state.can_redo()
        )
        control_panel.update_ai_button_state(game.ai_mode_enabled, game.ai_available)

        # Get last move squares for highlighting
        last_move = game.game_state.last_move
        last_move_squares = None
        if last_move:
            last_move_squares = (last_move.from_square, last_move.to_square)

        # Draw
        board_renderer.draw(
            screen,
            game.board,
            game.selected_square,
            game.valid_moves,
            last_move_squares,
            game.check_square,
            game.is_checkmate,
        )

        # Draw arrows on top of board
        arrow_renderer.rotated = board_renderer.rotated
        arrow_renderer.draw(screen)

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

        # Draw opening name if detected (update handles tooltip hover)
        opening_renderer.update()
        opening_renderer.draw(screen, game.current_opening)

        # Draw move list (current position is last move index, or -1 if at start)
        current_move_index = len(game.game_state.move_history) - 1
        move_list_renderer.draw(
            screen,
            game.san_history,
            current_move_index if current_move_index >= 0 else None,
        )

        captured_renderer.draw(
            screen,
            game.game_state.captured_pieces,
            board_renderer.rotated,
        )

        side_panel.draw(screen)
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
