from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, Future
from typing import TYPE_CHECKING

from chess import (
    Board,
    MoveGenerator,
    MoveExecutor,
    FENLoader,
    FENGenerator,
    PlayerType,
    load_config,
    AIPlayer,
    AIPlayerError,
)
from chess.game_state import GameState

if TYPE_CHECKING:
    from chess import PieceType


class GameController:
    """Manages game logic, AI, and move history navigation."""

    def __init__(self):
        # Core game components
        self.board = Board()
        self.game_state = GameState()
        self.fen_loader = FENLoader(self.board, self.game_state)
        self.move_generator = MoveGenerator()
        self.move_executor = MoveExecutor(self.board, self.game_state)

        # Selection state
        self.selected_square: tuple[int, int] | None = None
        self.valid_moves: list[tuple[int, int]] = []

        # AI components
        self._config = load_config()
        self._ai_player: AIPlayer | None = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._ai_future: Future | None = None
        self._ai_thinking_for_fen: str | None = None

        self._init_ai()
        self.fen_loader.load_starting_position()

    def _init_ai(self) -> None:
        """Initialize AI player if possible."""
        try:
            self._ai_player = AIPlayer(self._config)
        except AIPlayerError as e:
            print(f"AI player disabled: {e}")

    @property
    def ai_is_thinking(self) -> bool:
        """Check if AI is currently computing a move."""
        return self._ai_future is not None

    @property
    def is_human_turn(self) -> bool:
        """Check if it's a human player's turn."""
        return self.game_state.players[self.game_state.current_turn] == PlayerType.HUMAN

    @property
    def is_vs_ai(self) -> bool:
        """Check if this is a Human vs AI game."""
        players = self.game_state.players.values()
        return PlayerType.AI in players and PlayerType.HUMAN in players

    def clear_selection(self) -> None:
        """Clear the current piece selection."""
        self.selected_square = None
        self.valid_moves = []

    def select_square(self, file: int, rank: int) -> None:
        """
        Handle a square selection (click).

        Args:
            file: File index (0-7)
            rank: Rank index (0-7)
        """
        clicked_square = (file, rank)

        if clicked_square in self.valid_moves:
            # Valid move - will be handled by try_move or promotion flow
            return

        if self.selected_square == clicked_square:
            # Clicked same square - deselect
            self.clear_selection()
            return

        # Check if there's a moveable piece on the clicked square
        piece = self.board.get_piece(file, rank)
        if piece is not None and piece.color == self.game_state.current_turn:
            # Select this piece
            self.selected_square = clicked_square
            self.valid_moves = self.move_generator.get_legal_moves(
                self.board, piece, self.game_state
            )
        else:
            # Clicked empty square or opponent's piece - deselect
            self.clear_selection()

    def is_valid_move(self, to_square: tuple[int, int]) -> bool:
        """Check if moving to the given square is valid."""
        return to_square in self.valid_moves

    def is_promotion_move(self, to_square: tuple[int, int]) -> bool:
        """Check if the current move would be a pawn promotion."""
        if self.selected_square is None:
            return False
        return self.move_executor.is_promotion_move(self.selected_square, to_square)

    def execute_move(
        self, to_square: tuple[int, int], promotion_piece: PieceType | None = None
    ) -> None:
        """
        Execute a move from the selected square to the target square.

        Args:
            to_square: Destination square (file, rank)
            promotion_piece: Piece type for pawn promotion (if applicable)
        """
        if self.selected_square is None:
            return

        self.move_executor.execute_move(
            self.selected_square, to_square, promotion_piece
        )
        self.clear_selection()
        self._cancel_ai_thinking()

    def undo(self) -> None:
        """
        Undo the last move(s).

        In Human vs AI games, undoes moves until it's a human's turn.
        """
        if not self.game_state.can_undo():
            return

        self.move_executor.undo_move()

        # In Human vs AI, undo again if it's now AI's turn
        if self.is_vs_ai and not self.is_human_turn:
            if self.game_state.can_undo():
                self.move_executor.undo_move()

        self.clear_selection()
        self._cancel_ai_thinking()

    def redo(self) -> None:
        """
        Redo the last undone move(s).

        In Human vs AI games, redoes moves until it's a human's turn.
        """
        if not self.game_state.can_redo():
            return

        self.move_executor.redo_move()

        # In Human vs AI, redo again if it's now AI's turn
        if self.is_vs_ai and not self.is_human_turn:
            if self.game_state.can_redo():
                self.move_executor.redo_move()

        self.clear_selection()
        self._cancel_ai_thinking()

    def load_fen(self, fen_string: str) -> None:
        """
        Load a position from a FEN string.

        Args:
            fen_string: Valid FEN string

        Raises:
            ValueError: If the FEN string is invalid
        """
        self.fen_loader.load(fen_string)
        self.clear_selection()
        self._cancel_ai_thinking()

    def _cancel_ai_thinking(self) -> None:
        """Cancel any pending AI computation."""
        self._ai_future = None
        self._ai_thinking_for_fen = None

    def update_ai(self) -> None:
        """
        Update AI state. Should be called each frame.

        Raises:
            AIPlayerError: If the AI encounters an error computing a move.
        """
        if self._ai_player is None:
            return

        is_ai_turn = not self.is_human_turn

        # Start AI thinking if it's AI's turn and not already thinking
        if is_ai_turn and self._ai_future is None:
            self._ai_thinking_for_fen = FENGenerator.generate(
                self.board, self.game_state
            )
            self._ai_future = self._executor.submit(
                self._ai_player.get_move, self._ai_thinking_for_fen
            )

        # Check if AI has finished thinking
        if self._ai_future is not None and self._ai_future.done():
            try:
                from_sq, to_sq, promotion_piece = self._ai_future.result()
                # Only apply move if board position hasn't changed
                current_fen = FENGenerator.generate(self.board, self.game_state)
                if current_fen == self._ai_thinking_for_fen:
                    self.move_executor.execute_move(from_sq, to_sq, promotion_piece)
                    self.clear_selection()
            finally:
                self._ai_future = None
                self._ai_thinking_for_fen = None

    def cleanup(self) -> None:
        """Clean up resources. Should be called when shutting down."""
        self._executor.shutdown(wait=False)
        if self._ai_player is not None:
            self._ai_player.quit()
