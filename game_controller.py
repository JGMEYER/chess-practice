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
    NotationGenerator,
    PGNLoader,
    PGNError,
)
from chess.game_state import GameState

if TYPE_CHECKING:
    from chess import PieceType
    from chess.move import Move


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

        # Move notation history (SAN strings)
        self.san_history: list[str] = []

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
    def is_at_end_of_history(self) -> bool:
        """Check if we're at the latest position (no redo available)."""
        return not self.game_state.can_redo()

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

        # Generate SAN before executing the move (needs pre-move board state)
        san = self._generate_san_for_move(self.selected_square, to_square, promotion_piece)

        self.move_executor.execute_move(
            self.selected_square, to_square, promotion_piece
        )

        # Truncate redo history from san_history if we're in the middle of the game
        if len(self.san_history) > len(self.game_state.move_history) - 1:
            self.san_history = self.san_history[: len(self.game_state.move_history) - 1]

        self.san_history.append(san)
        self.clear_selection()
        self._cancel_ai_thinking()

    def _generate_san_for_move(
        self,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
        promotion_piece: PieceType | None = None,
    ) -> str:
        """Generate SAN notation for a move before it's executed."""
        from chess.move import Move

        piece = self.board.get_piece(*from_square)
        if piece is None:
            return "?"

        captured = self.board.get_piece(*to_square)

        # Check for en passant capture
        if (
            piece.piece_type.name == "PAWN"
            and to_square == self.game_state.current_en_passant_taking_square
        ):
            captured = self.board.get_piece(*self.game_state.current_en_passant_target)

        # Check for castling
        is_castling = (
            piece.piece_type.name == "KING"
            and abs(from_square[0] - to_square[0]) == 2
        )

        # Build a temporary Move object for notation generation
        promoted_to = None
        if promotion_piece is not None:
            from chess.pieces import Queen, Rook, Bishop, Knight
            piece_classes = {
                "QUEEN": Queen,
                "ROOK": Rook,
                "BISHOP": Bishop,
                "KNIGHT": Knight,
            }
            if promotion_piece.name in piece_classes:
                promoted_to = piece_classes[promotion_piece.name](piece.color)

        move = Move(
            from_square=from_square,
            to_square=to_square,
            piece=piece,
            captured_piece=captured,
            is_castling=is_castling,
            is_promotion=promotion_piece is not None,
            promoted_to=promoted_to,
        )

        return NotationGenerator.move_to_san(
            move, self.board, self.game_state, self.move_generator
        )

    def undo(self) -> None:
        """Undo the last move."""
        if not self.game_state.can_undo():
            return

        self.move_executor.undo_move()
        self.clear_selection()
        self._cancel_ai_thinking()

    def redo(self) -> None:
        """Redo the last undone move."""
        if not self.game_state.can_redo():
            return

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
        self.san_history.clear()
        self.clear_selection()
        self._cancel_ai_thinking()

    def load_pgn(self, pgn_string: str) -> list[str]:
        """
        Load a game from a PGN string.

        Args:
            pgn_string: Valid PGN string

        Returns:
            List of SAN notation strings for the moves

        Raises:
            PGNError: If the PGN is invalid or contains illegal moves
        """
        pgn_loader = PGNLoader(self.board, self.game_state)
        san_moves = pgn_loader.load(pgn_string)
        self.san_history = san_moves.copy()
        self.clear_selection()
        self._cancel_ai_thinking()
        return san_moves

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

        # Start AI thinking if it's AI's turn, at end of history, and not already thinking
        if is_ai_turn and self._ai_future is None and self.is_at_end_of_history:
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
                    # Generate SAN before executing the move
                    san = self._generate_san_for_move(from_sq, to_sq, promotion_piece)
                    self.move_executor.execute_move(from_sq, to_sq, promotion_piece)
                    self.san_history.append(san)
                    self.clear_selection()
            finally:
                self._ai_future = None
                self._ai_thinking_for_fen = None

    def cleanup(self) -> None:
        """Clean up resources. Should be called when shutting down."""
        self._executor.shutdown(wait=False)
        if self._ai_player is not None:
            self._ai_player.quit()
