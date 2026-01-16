from __future__ import annotations

from typing import TYPE_CHECKING

from .board import Board
from .constants import PieceType, Color
from .game_state import GameState
from .move import Move
from .pieces import Queen, Rook, Bishop, Knight

if TYPE_CHECKING:
    from .piece import Piece


class MoveExecutor:
    """Executes chess moves and handles special move types."""

    def __init__(self, board: Board, game_state: GameState):
        """
        Initialize the move executor.

        Args:
            board: The board to execute moves on
            game_state: The game state to update
        """
        self.board = board
        self.game_state = game_state

    def execute_move(
        self,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
        promotion_piece_type: PieceType | None = None,
    ) -> Move:
        """
        Execute a move and return the Move object.

        Handles normal moves, captures, en passant, castling, and promotion.

        Args:
            from_square: The starting square (file, rank)
            to_square: The destination square (file, rank)
            promotion_piece_type: The piece type to promote to (for pawn promotion)

        Returns:
            The executed Move object with all fields populated
        """
        piece = self.board.get_piece(*from_square)

        # Detect move type and prepare move data
        if self._is_castling_move(piece, from_square, to_square):
            move_data = self._prepare_castling_move(piece, from_square, to_square)
        elif self._is_en_passant_move(piece, to_square):
            move_data = self._prepare_en_passant_move(piece, from_square, to_square)
        else:
            move_data = self._prepare_normal_move(piece, from_square, to_square)

        # Handle promotion
        if promotion_piece_type is not None:
            promoted_piece = self._create_promoted_piece(
                promotion_piece_type, piece.color, to_square
            )
            move_data["is_promotion"] = True
            move_data["promoted_to"] = promoted_piece

        # Execute the move on the board
        self._apply_move_to_board(move_data)

        # Update game state
        self._update_castling_rights(piece, from_square, to_square)

        # Clear redo history when making a new move
        self.game_state.redo_history.clear()

        # Create and record move
        move = Move(**move_data)
        self.game_state.record_move(move)
        return move

    def _create_promoted_piece(
        self, piece_type: PieceType, color: Color, position: tuple[int, int]
    ) -> Piece:
        """Create a new piece for promotion."""
        piece_classes = {
            PieceType.QUEEN: Queen,
            PieceType.ROOK: Rook,
            PieceType.BISHOP: Bishop,
            PieceType.KNIGHT: Knight,
        }
        piece_class = piece_classes[piece_type]
        return piece_class(color, position)

    def _is_castling_move(
        self, piece: Piece, from_square: tuple[int, int], to_square: tuple[int, int]
    ) -> bool:
        """Check if this is a castling move."""
        if piece.piece_type != PieceType.KING:
            return False
        file_diff = abs(to_square[0] - from_square[0])
        return file_diff == 2

    def _is_en_passant_move(self, piece: Piece, to_square: tuple[int, int]) -> bool:
        """Check if this is an en passant move."""
        if piece.piece_type != PieceType.PAWN:
            return False
        en_passant_taking_square = self.game_state.current_en_passant_taking_square
        return en_passant_taking_square is not None and to_square == en_passant_taking_square

    def is_promotion_move(
        self, from_square: tuple[int, int], to_square: tuple[int, int]
    ) -> bool:
        """
        Check if a move would result in pawn promotion.

        Args:
            from_square: The starting square (file, rank)
            to_square: The destination square (file, rank)

        Returns:
            True if this move is a pawn reaching the back rank
        """
        piece = self.board.get_piece(*from_square)
        if piece is None or piece.piece_type != PieceType.PAWN:
            return False

        # White promotes on rank 7, black promotes on rank 0
        promotion_rank = 7 if piece.color == Color.WHITE else 0
        return to_square[1] == promotion_rank

    def _prepare_castling_move(
        self, piece: Piece, from_square: tuple[int, int], to_square: tuple[int, int]
    ) -> dict:
        """Prepare move data for a castling move."""
        file_diff = to_square[0] - from_square[0]
        rank = from_square[1]

        if file_diff == 2:  # Kingside castling
            castling_rook_from = (7, rank)
            castling_rook_to = (5, rank)
        else:  # Queenside castling
            castling_rook_from = (0, rank)
            castling_rook_to = (3, rank)

        return {
            "from_square": from_square,
            "to_square": to_square,
            "piece": piece,
            "captured_piece": None,
            "current_en_passant_target": None,
            "is_en_passant": False,
            "is_castling": True,
            "castling_rook_from": castling_rook_from,
            "castling_rook_to": castling_rook_to,
        }

    def _prepare_en_passant_move(
        self, piece: Piece, from_square: tuple[int, int], to_square: tuple[int, int]
    ) -> dict:
        """Prepare move data for an en passant move."""
        en_passant_target = self.game_state.current_en_passant_target
        captured_piece = self.board.get_piece(*en_passant_target)

        return {
            "from_square": from_square,
            "to_square": to_square,
            "piece": piece,
            "captured_piece": captured_piece,
            "current_en_passant_target": None,
            "is_en_passant": True,
            "is_castling": False,
            "castling_rook_from": None,
            "castling_rook_to": None,
        }

    def _prepare_normal_move(
        self, piece: Piece, from_square: tuple[int, int], to_square: tuple[int, int]
    ) -> dict:
        """Prepare move data for a normal move."""
        captured_piece = self.board.get_piece(*to_square)
        new_en_passant_target = self._calculate_en_passant_target(
            piece, from_square, to_square
        )

        return {
            "from_square": from_square,
            "to_square": to_square,
            "piece": piece,
            "captured_piece": captured_piece,
            "current_en_passant_target": new_en_passant_target,
            "is_en_passant": False,
            "is_castling": False,
            "castling_rook_from": None,
            "castling_rook_to": None,
        }

    def _apply_move_to_board(self, move_data: dict) -> None:
        """Apply the move to the board based on move type."""
        # Move the main piece (or promoted piece if promotion)
        self.board.set_piece(*move_data["from_square"], None)

        # Place either the promoted piece or the original piece
        if move_data.get("is_promotion") and move_data.get("promoted_to"):
            self.board.set_piece(*move_data["to_square"], move_data["promoted_to"])
        else:
            self.board.set_piece(*move_data["to_square"], move_data["piece"])

        # Handle special move types
        if move_data.get("is_castling"):
            # Move the rook
            rook = self.board.get_piece(*move_data["castling_rook_from"])
            self.board.set_piece(*move_data["castling_rook_from"], None)
            self.board.set_piece(*move_data["castling_rook_to"], rook)

        elif move_data.get("is_en_passant"):
            # Remove the captured pawn
            en_passant_target = self.game_state.current_en_passant_target
            self.board.set_piece(*en_passant_target, None)

    def _calculate_en_passant_target(
        self,
        piece: Piece,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
    ) -> tuple[int, int] | None:
        """
        Calculate the en passant target square if pawn moved two squares.

        Args:
            piece: The piece that moved
            from_square: Starting position
            to_square: Ending position

        Returns:
            The en passant target square, or None if not applicable
        """
        if piece.piece_type != PieceType.PAWN:
            return None

        rank_diff = abs(to_square[1] - from_square[1])
        if rank_diff != 2:
            return None

        return to_square

    def _update_castling_rights(
        self,
        piece: Piece,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
    ) -> None:
        """
        Update castling rights based on the move.

        Castling rights are lost when:
        - The king moves (both sides lost for that color)
        - A rook moves from its starting position (that side lost for that color)
        - A rook is captured on its starting position (that side lost for that color)

        Args:
            piece: The piece that moved
            from_square: The starting square
            to_square: The destination square
        """
        from .constants import Color

        castling_rights = self.game_state.castling_rights

        # If king moves, lose both castling rights for that color
        if piece.piece_type == PieceType.KING:
            if piece.color == Color.WHITE:
                castling_rights.white_kingside = False
                castling_rights.white_queenside = False
            else:
                castling_rights.black_kingside = False
                castling_rights.black_queenside = False

        # If rook moves from starting position, lose castling right for that side
        if piece.piece_type == PieceType.ROOK:
            file, rank = from_square

            if piece.color == Color.WHITE and rank == 0:  # White back rank
                if file == 7:  # h1 - kingside rook
                    castling_rights.white_kingside = False
                elif file == 0:  # a1 - queenside rook
                    castling_rights.white_queenside = False

            elif piece.color == Color.BLACK and rank == 7:  # Black back rank
                if file == 7:  # h8 - kingside rook
                    castling_rights.black_kingside = False
                elif file == 0:  # a8 - queenside rook
                    castling_rights.black_queenside = False

        # If a rook is captured on its starting position, opponent loses castling right
        captured_piece = self.board.get_piece(*to_square)
        if captured_piece and captured_piece.piece_type == PieceType.ROOK:
            file, rank = to_square

            if captured_piece.color == Color.WHITE and rank == 0:
                if file == 7:
                    castling_rights.white_kingside = False
                elif file == 0:
                    castling_rights.white_queenside = False

            elif captured_piece.color == Color.BLACK and rank == 7:
                if file == 7:
                    castling_rights.black_kingside = False
                elif file == 0:
                    castling_rights.black_queenside = False

    def undo_move(self) -> Move | None:
        """
        Undo the last move.

        Handles undoing normal moves, captures, en passant, and castling.

        Returns:
            The undone Move, or None if no moves to undo
        """
        if not self.game_state.move_history:
            return None

        move = self.game_state.move_history.pop()
        self.game_state.redo_history.append(move)

        # Restore pieces based on move type
        self._restore_main_piece(move)
        self._restore_special_move_pieces(move)
        self._restore_captured_piece(move)

        # Revert turn
        self.game_state.current_turn = move.piece.color

        return move

    def _restore_main_piece(self, move: Move) -> None:
        """Restore the main piece to its original position."""
        # Remove the piece at destination (could be promoted piece)
        self.board.set_piece(*move.to_square, None)
        # Restore the original piece (pawn in case of promotion)
        self.board.set_piece(*move.from_square, move.piece)

    def _restore_special_move_pieces(self, move: Move) -> None:
        """Restore pieces involved in special moves (castling rook)."""
        if move.is_castling:
            rook = self.board.get_piece(*move.castling_rook_to)
            self.board.set_piece(*move.castling_rook_to, None)
            self.board.set_piece(*move.castling_rook_from, rook)

    def _restore_captured_piece(self, move: Move) -> None:
        """Restore captured piece to its original position."""
        if not move.captured_piece:
            return

        if move.is_en_passant:
            # En passant: restore pawn to calculated square
            # Same file as to_square, same rank as from_square
            captured_pawn_square = (move.to_square[0], move.from_square[1])
            self.board.set_piece(*captured_pawn_square, move.captured_piece)
        else:
            # Normal capture: restore to to_square
            self.board.set_piece(*move.to_square, move.captured_piece)

    def redo_move(self) -> Move | None:
        """
        Redo a previously undone move.

        Returns:
            The redone Move, or None if no moves to redo
        """
        if not self.game_state.redo_history:
            return None

        move = self.game_state.redo_history.pop()

        # Re-apply the move to the board
        move_data = {
            "from_square": move.from_square,
            "to_square": move.to_square,
            "piece": move.piece,
            "is_castling": move.is_castling,
            "castling_rook_from": move.castling_rook_from,
            "castling_rook_to": move.castling_rook_to,
            "is_en_passant": move.is_en_passant,
            "is_promotion": move.is_promotion,
            "promoted_to": move.promoted_to,
        }
        self._apply_move_to_board(move_data)

        # Handle en passant capture removal
        if move.is_en_passant and move.captured_piece:
            captured_square = (move.to_square[0], move.from_square[1])
            self.board.set_piece(*captured_square, None)

        # Record move back to history and switch turn
        self.game_state.move_history.append(move)
        self.game_state.current_turn = (
            Color.BLACK if move.piece.color == Color.WHITE else Color.WHITE
        )

        return move

    def jump_to_history_index(self, target_index: int) -> None:
        """
        Jump to a specific point in the move history via undo/redo.

        Args:
            target_index: Target index in history (0 = starting position,
                          1 = after first move, etc.)

        Raises:
            ValueError: If target_index is out of valid range
        """
        current = len(self.game_state.move_history)
        max_index = current + len(self.game_state.redo_history)

        if target_index < 0:
            raise ValueError(f"Invalid history index: {target_index} (cannot be negative)")
        if target_index > max_index:
            raise ValueError(
                f"Invalid history index: {target_index} (max reachable: {max_index})"
            )

        if target_index < current:
            # Undo moves
            for _ in range(current - target_index):
                self.undo_move()
        elif target_index > current:
            # Redo moves
            for _ in range(target_index - current):
                self.redo_move()
