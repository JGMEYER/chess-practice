from __future__ import annotations

from typing import TYPE_CHECKING

from .board import Board
from .constants import PieceType
from .game_state import GameState
from .move import Move

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
    ) -> Move:
        """
        Execute a move and return the Move object.

        Handles normal moves, normal captures, and en passant captures.

        Args:
            from_square: The starting square (file, rank)
            to_square: The destination square (file, rank)

        Returns:
            The executed Move object with all fields populated
        """
        piece = self.board.get_piece(*from_square)
        captured_piece = self.board.get_piece(*to_square)

        # Check for en passant
        is_en_passant = False
        en_passant_taking_square = self.game_state.current_en_passant_taking_square

        if (
            piece.piece_type == PieceType.PAWN
            and en_passant_taking_square is not None
            and to_square == en_passant_taking_square
        ):
            is_en_passant = True
            en_passant_target = self.game_state.current_en_passant_target
            captured_piece = self.board.get_piece(*en_passant_target)

        # Execute the move on the board
        self.board.set_piece(*from_square, None)
        self.board.set_piece(*to_square, piece)

        # Remove en passant captured pawn if applicable
        if is_en_passant:
            self.board.set_piece(*self.game_state.current_en_passant_target, None)

        # Determine new en passant target
        new_en_passant_target = self._calculate_en_passant_target(
            piece, from_square, to_square
        )

        # Create and record move
        move = Move(
            from_square=from_square,
            to_square=to_square,
            piece=piece,
            captured_piece=captured_piece,
            current_en_passant_target=new_en_passant_target,
            is_en_passant=is_en_passant,
        )

        self.game_state.record_move(move)
        return move

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

    def undo_move(self) -> Move | None:
        """
        Undo the last move.

        Returns:
            The undone Move, or None if no moves to undo
        """
        if not self.game_state.move_history:
            return None

        move = self.game_state.move_history.pop()

        # Restore piece to original position
        self.board.set_piece(*move.to_square, None)
        self.board.set_piece(*move.from_square, move.piece)

        # Restore captured piece
        if move.captured_piece:
            if move.is_en_passant:
                # En passant: restore pawn to calculated square
                # Same file as to_square, same rank as from_square
                captured_pawn_square = (move.to_square[0], move.from_square[1])
                self.board.set_piece(*captured_pawn_square, move.captured_piece)
            else:
                # Normal capture: restore to to_square
                self.board.set_piece(*move.to_square, move.captured_piece)

        # Revert turn
        self.game_state.current_turn = move.piece.color

        return move
