"""Standard Algebraic Notation (SAN) generation for chess moves."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .board import Board
from .constants import PieceType, Color

if TYPE_CHECKING:
    from .game_state import GameState
    from .move import Move
    from .move_generator import MoveGenerator
    from .piece import Piece


class NotationGenerator:
    """Generates Standard Algebraic Notation (SAN) from Move objects."""

    PIECE_LETTERS = {
        PieceType.KING: "K",
        PieceType.QUEEN: "Q",
        PieceType.ROOK: "R",
        PieceType.BISHOP: "B",
        PieceType.KNIGHT: "N",
        PieceType.PAWN: "",
    }

    @classmethod
    def move_to_san(
        cls,
        move: Move,
        board: Board,
        game_state: GameState,
        move_generator: MoveGenerator,
        include_check: bool = True,
    ) -> str:
        """
        Convert a Move to Standard Algebraic Notation.

        Args:
            move: The move to convert
            board: Board state BEFORE the move is executed
            game_state: Game state BEFORE the move
            move_generator: For computing legal moves (disambiguation)
            include_check: Whether to append + or # for check/checkmate

        Returns:
            SAN string (e.g., "Nf3", "exd5", "O-O", "e8=Q", "Qh4xe1+")
        """
        # Handle castling
        if move.is_castling:
            return cls._get_castling_notation(move)

        # Build notation piece by piece
        piece_letter = cls.PIECE_LETTERS[move.piece.piece_type]
        disambiguation = cls._get_disambiguation(
            move, board, game_state, move_generator
        )
        capture_notation = cls._get_capture_notation(move)
        destination = cls._square_to_algebraic(move.to_square)
        promotion = cls._get_promotion_notation(move)

        # Assemble the notation
        if move.piece.piece_type == PieceType.PAWN:
            if move.captured_piece is not None:
                # Pawn captures include source file: exd5
                san = Board.file_to_letter(move.from_square[0]) + capture_notation + destination
            else:
                # Simple pawn move: e4
                san = destination
            san += promotion
        else:
            # Non-pawn: Piece + disambiguation + capture + destination
            san = piece_letter + disambiguation + capture_notation + destination

        # Add check/checkmate indicator
        if include_check:
            check_indicator = cls._get_check_indicator(
                move, board, game_state, move_generator
            )
            san += check_indicator

        return san

    @classmethod
    def _get_castling_notation(cls, move: Move) -> str:
        """Return O-O or O-O-O based on castling direction."""
        to_file = move.to_square[0]
        return "O-O" if to_file == 6 else "O-O-O"

    @classmethod
    def _get_disambiguation(
        cls,
        move: Move,
        board: Board,
        game_state: GameState,
        move_generator: MoveGenerator,
    ) -> str:
        """
        Get disambiguation string for moves where multiple pieces could reach same square.

        Returns:
            Empty string if no disambiguation needed,
            file letter (e.g., "b") if file is unique,
            rank number (e.g., "1") if rank is unique,
            both (e.g., "b1") if neither is unique alone.
        """
        # Pawns don't need disambiguation (handled separately via source file on captures)
        if move.piece.piece_type == PieceType.PAWN:
            return ""

        # Find all same-type, same-color pieces that can reach the same destination
        ambiguous_pieces: list[Piece] = []

        for file, rank, piece in board:
            if piece is None:
                continue
            if piece.piece_type != move.piece.piece_type:
                continue
            if piece.color != move.piece.color:
                continue
            if (file, rank) == move.from_square:
                continue

            # Check if this piece can legally move to the same square
            legal_moves = move_generator.get_legal_moves(board, piece, game_state)
            if move.to_square in legal_moves:
                ambiguous_pieces.append(piece)

        if not ambiguous_pieces:
            return ""

        from_file, from_rank = move.from_square

        # Check if file alone is sufficient for disambiguation
        if not any(p.file == from_file for p in ambiguous_pieces):
            return Board.file_to_letter(from_file)

        # Check if rank alone is sufficient
        if not any(p.rank == from_rank for p in ambiguous_pieces):
            return Board.rank_to_number(from_rank)

        # Need both file and rank
        return Board.file_to_letter(from_file) + Board.rank_to_number(from_rank)

    @classmethod
    def _get_capture_notation(cls, move: Move) -> str:
        """Return 'x' if this is a capture, empty string otherwise."""
        return "x" if move.captured_piece is not None else ""

    @classmethod
    def _square_to_algebraic(cls, square: tuple[int, int]) -> str:
        """Convert (file, rank) tuple to algebraic notation (e.g., 'e4')."""
        file, rank = square
        return Board.file_to_letter(file) + Board.rank_to_number(rank)

    @classmethod
    def _get_promotion_notation(cls, move: Move) -> str:
        """Return promotion notation (e.g., '=Q') if this is a promotion."""
        if not move.is_promotion or move.promoted_to is None:
            return ""
        return "=" + cls.PIECE_LETTERS[move.promoted_to.piece_type]

    @classmethod
    def _get_check_indicator(
        cls,
        move: Move,
        board: Board,
        game_state: GameState,
        move_generator: MoveGenerator,
    ) -> str:
        """
        Determine if the move results in check or checkmate.

        Returns '+' for check, '#' for checkmate, or empty string.
        """
        from .move_executor import MoveExecutor

        # Create a copy of board and game state to simulate the move
        # We need to actually execute the move to check the resulting position
        test_board = Board()
        for file, rank, piece in board:
            if piece is not None:
                # Create a new piece instance
                new_piece = piece.__class__(piece.color)
                test_board.set_piece(file, rank, new_piece)

        # Create test game state
        from .game_state import GameState
        test_state = GameState()
        test_state.current_turn = game_state.current_turn
        test_state._castling_rights = game_state._castling_rights

        # Execute the move on test board
        test_executor = MoveExecutor(test_board, test_state)

        # Determine promotion piece type
        promotion_type = None
        if move.is_promotion and move.promoted_to is not None:
            promotion_type = move.promoted_to.piece_type

        test_executor.execute_move(move.from_square, move.to_square, promotion_type)

        # Check if opponent is in check
        opponent_color = Color.BLACK if move.piece.color == Color.WHITE else Color.WHITE
        is_in_check = move_generator.is_in_check(test_board, opponent_color)

        if not is_in_check:
            return ""

        # Check if it's checkmate (no legal moves for opponent)
        all_moves = move_generator.get_all_legal_moves(
            test_board, opponent_color, test_state
        )
        has_legal_moves = len(all_moves) > 0

        return "#" if not has_legal_moves else "+"
