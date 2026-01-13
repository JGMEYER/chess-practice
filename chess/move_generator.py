from __future__ import annotations

from chess.game_state import GameState

from .board import Board
from .piece import Piece
from .constants import Color, PieceType
from .pieces.knight import Knight
from .pieces.queen import Queen


class MoveGenerator:
    """Generates valid moves for chess pieces."""

    def get_possible_moves(self, board: Board, piece: Piece, game_state: GameState) -> list[tuple[int, int]]:
        """
        Get all possible moves for a piece based on its movement rules.

        These moves follow the piece's movement patterns but may leave the
        king in check. Use get_legal_moves() for fully legal moves that
        respect check rules.

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
            List of (file, rank) tuples representing pseudo-legal destination squares
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

    def get_legal_moves(
        self, board: Board, piece: Piece, game_state: GameState
    ) -> list[tuple[int, int]]:
        """
        Get all legal moves for a piece (filtering out moves that leave king in check).

        This is the main public method for move generation. It generates possible
        moves using get_possible_moves(), then filters out moves that would leave the
        player's king in check.

        Args:
            board: The current board state
            piece: The piece to get legal moves for
            game_state: The current game state

        Returns:
            List of (file, rank) tuples representing legal destination squares
        """
        # Get pseudo-legal moves
        pseudo_legal_moves = self.get_possible_moves(board, piece, game_state)

        # Filter out moves that would leave king in check
        legal_moves = []
        for to_square in pseudo_legal_moves:
            if not self._would_leave_king_in_check(board, piece, to_square, game_state):
                legal_moves.append(to_square)

        # Add castling moves for kings
        if piece.piece_type == PieceType.KING:
            castling_moves = self._get_castling_moves(board, piece, game_state)
            legal_moves.extend(castling_moves)

        return legal_moves

    def _get_castling_moves(
        self, board: Board, king: Piece, game_state: GameState
    ) -> list[tuple[int, int]]:
        """
        Get legal castling moves for the king.

        Castling is legal when:
        1. Neither the king nor the rook has previously moved (castling_rights)
        2. There are no pieces between the king and the rook
        3. The king is not currently in check
        4. The king does not pass through or finish on a square attacked by enemy

        Args:
            board: The current board state
            king: The king piece
            game_state: The current game state

        Returns:
            List of (file, rank) tuples for legal castling destinations

        Raises:
            ValueError: If castling rights indicate rook should exist but doesn't
        """
        castling_moves = []

        # Can't castle if king is in check (rule 3)
        if self.is_in_check(board, king.color):
            return castling_moves

        file, rank = king.position
        castling_rights = game_state.castling_rights

        # Determine which castling rights to check based on color
        if king.color == Color.WHITE:
            can_kingside = castling_rights.white_kingside
            can_queenside = castling_rights.white_queenside
            king_start_rank = 0  # Rank 1 in chess notation
        else:
            can_kingside = castling_rights.black_kingside
            can_queenside = castling_rights.black_queenside
            king_start_rank = 7  # Rank 8 in chess notation

        # King must be on starting square (e1 for white, e8 for black)
        if file != 4 or rank != king_start_rank:
            return castling_moves

        # Check kingside castling (O-O)
        if can_kingside:
            # Check squares between king and rook are empty (f1/f8 and g1/g8)
            if (board.get_piece(5, rank) is None and
                board.get_piece(6, rank) is None):
                # Check rook is in correct position (h1/h8)
                rook = board.get_piece(7, rank)
                if rook is None:
                    raise ValueError(
                        f"Invalid game state: castling rights indicate kingside castling "
                        f"is available for {king.color.name}, but rook is missing at "
                        f"{'h1' if king.color == Color.WHITE else 'h8'}"
                    )
                if (rook.piece_type != PieceType.ROOK or rook.color != king.color):
                    raise ValueError(
                        f"Invalid game state: expected {king.color.name} rook at "
                        f"{'h1' if king.color == Color.WHITE else 'h8'} for kingside castling"
                    )

                # Check king doesn't pass through or end in check (rule 4)
                # King moves from e to g, passing through f
                opponent_color = Color.BLACK if king.color == Color.WHITE else Color.WHITE
                f_square = (5, rank)  # f1/f8
                g_square = (6, rank)  # g1/g8

                if (not self.is_square_attacked(board, f_square, opponent_color) and
                    not self.is_square_attacked(board, g_square, opponent_color)):
                    castling_moves.append(g_square)

        # Check queenside castling (O-O-O)
        if can_queenside:
            # Check squares between king and rook are empty (d1/d8, c1/c8, b1/b8)
            if (board.get_piece(3, rank) is None and
                board.get_piece(2, rank) is None and
                board.get_piece(1, rank) is None):
                # Check rook is in correct position (a1/a8)
                rook = board.get_piece(0, rank)
                if rook is None:
                    raise ValueError(
                        f"Invalid game state: castling rights indicate queenside castling "
                        f"is available for {king.color.name}, but rook is missing at "
                        f"{'a1' if king.color == Color.WHITE else 'a8'}"
                    )
                if (rook.piece_type != PieceType.ROOK or rook.color != king.color):
                    raise ValueError(
                        f"Invalid game state: expected {king.color.name} rook at "
                        f"{'a1' if king.color == Color.WHITE else 'a8'} for queenside castling"
                    )

                # Check king doesn't pass through or end in check (rule 4)
                # King moves from e to c, passing through d
                opponent_color = Color.BLACK if king.color == Color.WHITE else Color.WHITE
                d_square = (3, rank)  # d1/d8
                c_square = (2, rank)  # c1/c8

                if (not self.is_square_attacked(board, d_square, opponent_color) and
                    not self.is_square_attacked(board, c_square, opponent_color)):
                    castling_moves.append(c_square)

        return castling_moves

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
            # But only if both the intermediate and destination squares are empty
            if ((piece.color == Color.WHITE and rank == 1)
                    or (piece.color == Color.BLACK and rank == 6)):
                if (board.get_piece(*one_move_forward) is None
                        and board.get_piece(*two_moves_forward) is None):
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

    def is_square_attacked(
        self, board: Board, square: tuple[int, int], attacking_color: Color
    ) -> bool:
        """
        Check if a square is under attack by pieces of the given color.

        Uses a generalized "reverse perspective" algorithm: checks from the target
        square outward in all possible directions. When a piece is found, checks if
        that piece's move_offsets would allow it to reach back to the target square.

        This approach works for any piece type without hardcoding specific piece logic.

        Args:
            board: The current board state
            square: The square to check (file, rank)
            attacking_color: The color of pieces that might attack the square

        Returns:
            True if the square is under attack, False otherwise
        """
        target_file, target_rank = square

        # Check all possible directions (8 sliding directions + knight moves)
        # For sliding pieces, we'll check along rays
        # For non-sliding pieces (knight, king), we check direct positions

        # All 8 sliding directions (orthogonal + diagonal)
        sliding_directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Orthogonal
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
        ]

        for direction in sliding_directions:
            check_file = target_file + direction[0]
            check_rank = target_rank + direction[1]

            # Slide in this direction until we hit a piece or edge
            while self._is_on_board(check_file, check_rank):
                piece = board.get_piece(check_file, check_rank)

                if piece is not None:
                    # Found a piece - check if it can attack back to our square
                    if piece.color == attacking_color:
                        # Check if this piece can attack in the reverse direction
                        reverse_direction = (-direction[0], -direction[1])

                        if reverse_direction in piece.move_offsets:
                            # For sliding pieces, they can attack from any distance
                            # For non-sliding pieces, check distance
                            if piece.is_sliding:
                                return True
                            else:
                                # Non-sliding piece - must be exactly one offset away
                                distance = max(abs(piece.position[0] - target_file),
                                             abs(piece.position[1] - target_rank))
                                if distance == 1:
                                    return True
                    break  # Either found attacker or piece blocks further checks

                # Continue sliding
                check_file += direction[0]
                check_rank += direction[1]

        # Check for knight attacks (knight is non-sliding with L-shaped offsets)
        for offset in Knight.move_offsets:
            check_file = target_file + offset[0]
            check_rank = target_rank + offset[1]

            if not self._is_on_board(check_file, check_rank):
                continue

            piece = board.get_piece(check_file, check_rank)
            if (piece is not None
                and piece.color == attacking_color
                and piece.piece_type == PieceType.KNIGHT):
                return True

        # Check for pawn attacks (special case - pawns attack differently than they move)
        # Pawns are the only piece where move_offsets don't represent attacks
        pawn_attack_rank_offset = -1 if attacking_color == Color.WHITE else 1
        pawn_attack_offsets = [(-1, pawn_attack_rank_offset), (1, pawn_attack_rank_offset)]

        for offset in pawn_attack_offsets:
            check_file = target_file + offset[0]
            check_rank = target_rank + offset[1]

            if not self._is_on_board(check_file, check_rank):
                continue

            piece = board.get_piece(check_file, check_rank)
            if (piece is not None
                and piece.color == attacking_color
                and piece.piece_type == PieceType.PAWN):
                return True

        return False

    def _get_capture_square(
        self, piece: Piece, to_square: tuple[int, int], game_state: GameState
    ) -> tuple[int, int]:
        """
        Get the square where a captured piece is located.

        For normal moves, this is the destination square. For en passant,
        it's the en passant target square (where the pawn actually sits).

        Args:
            piece: The piece being moved
            to_square: The destination square
            game_state: The current game state

        Returns:
            The square where the captured piece is located
        """
        # En passant: captured pawn is at a different square than destination
        if (piece.piece_type == PieceType.PAWN
            and to_square == game_state.current_en_passant_taking_square):
            return game_state.current_en_passant_target

        # Normal move: capture is at destination square
        return to_square

    def _would_leave_king_in_check(
        self, board: Board, piece: Piece, to_square: tuple[int, int], game_state: GameState
    ) -> bool:
        """
        Check if a move would leave the player's king in check.

        Simulates the move temporarily on the board, checks for check, then restores
        the board state. Handles both normal captures and en passant captures.

        Args:
            board: The current board state
            piece: The piece to move
            to_square: The destination square
            game_state: The current game state

        Returns:
            True if the move would leave the king in check, False otherwise
        """
        from_square = piece.position
        capture_square = self._get_capture_square(piece, to_square, game_state)

        # Save current board state (3 squares: from, to, and capture location)
        saved_from = board.get_piece(*from_square)
        saved_to = board.get_piece(*to_square)
        saved_capture = board.get_piece(*capture_square)

        # Apply the move
        board.set_piece(*from_square, None)
        board.set_piece(*to_square, piece)
        if capture_square != to_square:  # En passant case
            board.set_piece(*capture_square, None)

        # Check for check
        in_check = self.is_in_check(board, piece.color)

        # Restore board state
        board.set_piece(*from_square, saved_from)
        board.set_piece(*to_square, saved_to)
        if capture_square != to_square:  # En passant case
            board.set_piece(*capture_square, saved_capture)

        return in_check

    def is_in_check(self, board: Board, color: Color) -> bool:
        """
        Check if the king of the given color is currently in check.

        Args:
            board: The current board state
            color: The color of the king to check

        Returns:
            True if king is in check, False otherwise
        """
        # Find the king
        king_position = None
        for file, rank, piece in board:
            if (piece is not None
                and piece.color == color
                and piece.piece_type == PieceType.KING):
                king_position = (file, rank)
                break

        if king_position is None:
            # No king found - shouldn't happen in normal game
            return False

        # Check if king's square is attacked by opponent
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(board, king_position, opponent_color)

    def get_all_legal_moves(
        self, board: Board, color: Color, game_state: GameState
    ) -> dict[Piece, list[tuple[int, int]]]:
        """
        Get all legal moves for all pieces of a color.

        Returns only moves that don't leave the king in check.

        Args:
            board: The current board state
            color: The color to get moves for
            game_state: The current game state

        Returns:
            Dictionary mapping pieces to their legal moves
        """
        all_moves = {}

        for file, rank, piece in board:
            if piece is not None and piece.color == color:
                moves = self.get_legal_moves(board, piece, game_state)
                if moves:
                    all_moves[piece] = moves

        return all_moves
