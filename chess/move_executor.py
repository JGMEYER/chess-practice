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

        Handles normal moves, captures, en passant, and castling.

        Args:
            from_square: The starting square (file, rank)
            to_square: The destination square (file, rank)

        Returns:
            The executed Move object with all fields populated
        """
        piece = self.board.get_piece(*from_square)
        captured_piece = self.board.get_piece(*to_square)

        # Check for castling
        is_castling = False
        castling_rook_from = None
        castling_rook_to = None

        if piece.piece_type == PieceType.KING:
            file_diff = to_square[0] - from_square[0]
            # Castling if king moves 2 squares horizontally
            if abs(file_diff) == 2:
                is_castling = True
                rank = from_square[1]

                if file_diff == 2:  # Kingside castling (king moves to g-file)
                    castling_rook_from = (7, rank)  # h-file
                    castling_rook_to = (5, rank)    # f-file
                else:  # Queenside castling (king moves to c-file)
                    castling_rook_from = (0, rank)  # a-file
                    castling_rook_to = (3, rank)    # d-file

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

        # Execute castling rook move if applicable
        if is_castling:
            rook = self.board.get_piece(*castling_rook_from)
            self.board.set_piece(*castling_rook_from, None)
            self.board.set_piece(*castling_rook_to, rook)

        # Determine new en passant target
        new_en_passant_target = self._calculate_en_passant_target(
            piece, from_square, to_square
        )

        # Update castling rights
        self._update_castling_rights(piece, from_square, to_square)

        # Create and record move
        move = Move(
            from_square=from_square,
            to_square=to_square,
            piece=piece,
            captured_piece=captured_piece,
            current_en_passant_target=new_en_passant_target,
            is_en_passant=is_en_passant,
            is_castling=is_castling,
            castling_rook_from=castling_rook_from,
            castling_rook_to=castling_rook_to,
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

        # Restore piece to original position
        self.board.set_piece(*move.to_square, None)
        self.board.set_piece(*move.from_square, move.piece)

        # Undo castling rook move if applicable
        if move.is_castling:
            rook = self.board.get_piece(*move.castling_rook_to)
            self.board.set_piece(*move.castling_rook_to, None)
            self.board.set_piece(*move.castling_rook_from, rook)

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
