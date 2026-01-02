from __future__ import annotations

from chess.game_state import GameState

from .board import Board
from .piece import Piece
from .constants import Color, PieceType


class MoveGenerator:
    """Generates valid moves for chess pieces."""

    def get_valid_moves(self, board: Board, piece: Piece, game_state: GameState) -> list[tuple[int, int]]:
        """
        Get all valid moves for a piece.

        For sliding pieces (is_sliding=True):
          - Repeat each offset direction until hitting board edge or piece
          - Can capture enemy, stops before friendly

        For non-sliding pieces (is_sliding=False):
          - Apply each offset once
          - Can land on empty or enemy square, not friendly

        Args:
            board: The current board state
            piece: The piece to get moves for
            game_state: The current game state

        Returns:
            List of (file, rank) tuples representing valid destination squares
        """
        if piece.position is None:
            return []

        if piece.piece_type == PieceType.PAWN:
            return self._get_pawn_moves(board, piece, game_state)

        moves = []

        for offset in piece.move_offsets:
            if piece.is_sliding:
                moves.extend(self._get_sliding_moves(board, piece, offset))
            else:
                move = self._get_single_move(board, piece, offset)
                if move is not None:
                    moves.append(move)

        return moves
    
    def _get_pawn_moves(
        self, board: Board, piece: Piece, game_state: GameState
    ) -> list[tuple[int, int]]:
        moves = []
        file, rank = piece.position
        forward_offset = 1 if piece.color == Color.WHITE else -1

        one_move_forward = (file, rank+forward_offset)
        two_moves_forward = (file, rank+forward_offset*2)
        diagonal_moves = [(file-1, rank+forward_offset), (file+1, rank+forward_offset)]

        if self._is_on_board(*one_move_forward):
            # Standard move
            if board.get_piece(*one_move_forward) is None:
                moves.append(one_move_forward)

        if (self._is_on_board(*two_moves_forward)):
            # Pawn has not moved from starting square - can move 2 spaces
            if ((piece.color == Color.WHITE and rank == 1)
                    or (piece.color == Color.BLACK and rank == 6)):
                if board.get_piece(*two_moves_forward) is None:
                    moves.append(two_moves_forward)
        
        for possible_diagonal in diagonal_moves:
            if not self._is_on_board(*possible_diagonal):
                continue

            target_piece = board.get_piece(*possible_diagonal)

            if (target_piece is not None and target_piece.color != piece.color):
                # Pawn can take piece diagonally
                moves.append(possible_diagonal)
            else:
                # Pawn can en passant
                taking_square = game_state.current_en_passant_taking_square
                if possible_diagonal == taking_square:
                    moves.append(possible_diagonal)
        
        # (TODO) Promotion logic
        return moves

    def _get_sliding_moves(
        self, board: Board, piece: Piece, direction: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Get all moves in a sliding direction until blocked."""
        moves = []
        file, rank = piece.position
        d_file, d_rank = direction

        while True:
            file += d_file
            rank += d_rank

            if not self._is_on_board(file, rank):
                break

            target_piece = board.get_piece(file, rank)

            if target_piece is None:
                moves.append((file, rank))
            elif target_piece.color != piece.color:
                moves.append((file, rank))  # Can capture
                break
            else:
                break  # Blocked by friendly piece

        return moves

    def _get_single_move(
        self, board: Board, piece: Piece, offset: tuple[int, int]
    ) -> tuple[int, int] | None:
        """Get a single move if valid (for non-sliding pieces)."""
        file = piece.file + offset[0]
        rank = piece.rank + offset[1]

        if not self._is_on_board(file, rank):
            return None

        target_piece = board.get_piece(file, rank)

        if target_piece is None or target_piece.color != piece.color:
            return (file, rank)

        return None  # Blocked by friendly piece

    def _is_on_board(self, file: int, rank: int) -> bool:
        """Check if position is within board bounds."""
        return 0 <= file < 8 and 0 <= rank < 8

    def get_all_moves(
        self, board: Board, color: Color
    ) -> dict[Piece, list[tuple[int, int]]]:
        """
        Get all valid moves for all pieces of a color.

        Args:
            board: The current board state
            color: The color to get moves for

        Returns:
            Dictionary mapping pieces to their valid moves
        """
        all_moves = {}

        for file, rank, piece in board:
            if piece is not None and piece.color == color:
                moves = self.get_valid_moves(board, piece)
                if moves:
                    all_moves[piece] = moves

        return all_moves
