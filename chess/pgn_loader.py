"""PGN loading - applies parsed PGN moves to Board and GameState."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .board import Board
from .constants import Color, PieceType
from .fen_loader import FENLoader
from .move_executor import MoveExecutor
from .move_generator import MoveGenerator
from .pgn import PGNData, PGNError, PGNParser

if TYPE_CHECKING:
    from .game_state import GameState
    from .piece import Piece


class PGNLoader:
    """Loads PGN games into Board and GameState."""

    # Regex for parsing SAN moves
    # Matches: piece letter, source file, source rank, capture, destination, promotion
    SAN_PATTERN = re.compile(
        r"^([KQRBN])?"  # Piece (optional for pawns)
        r"([a-h])?"  # Source file disambiguation
        r"([1-8])?"  # Source rank disambiguation
        r"(x)?"  # Capture
        r"([a-h][1-8])"  # Destination square
        r"(?:=([QRBN]))?"  # Promotion piece
        r"[+#]?$"  # Check/checkmate indicators (ignored)
    )

    PIECE_TYPE_MAP = {
        "K": PieceType.KING,
        "Q": PieceType.QUEEN,
        "R": PieceType.ROOK,
        "B": PieceType.BISHOP,
        "N": PieceType.KNIGHT,
    }

    def __init__(self, board: Board, game_state: GameState):
        """
        Initialize the PGN loader.

        Args:
            board: The board to load the game onto
            game_state: The game state to update
        """
        self.board = board
        self.game_state = game_state
        self.move_generator = MoveGenerator()
        self.move_executor = MoveExecutor(board, game_state)
        self.fen_loader = FENLoader(board, game_state)

    def load(self, pgn_string: str) -> list[str]:
        """
        Load a PGN game, applying all moves to the board.

        Args:
            pgn_string: Valid PGN string

        Returns:
            List of SAN notation strings for the moves played

        Raises:
            PGNError: If the PGN is invalid or contains illegal moves
        """
        pgn_data = PGNParser.parse(pgn_string)
        return self.load_from_data(pgn_data)

    def load_from_data(self, pgn_data: PGNData) -> list[str]:
        """
        Load a game from parsed PGN data.

        Args:
            pgn_data: Parsed PGN data

        Returns:
            List of SAN notation strings

        Raises:
            PGNError: If the PGN contains illegal moves
        """
        # Load starting position
        if pgn_data.fen:
            try:
                self.fen_loader.load(pgn_data.fen)
            except ValueError as e:
                raise PGNError(f"Invalid FEN in PGN: {e}") from e
        else:
            self.fen_loader.load_starting_position()

        # Execute each move
        for i, san in enumerate(pgn_data.san_moves):
            try:
                self._execute_san_move(san)
            except PGNError as e:
                raise PGNError(f"Error at move {i + 1} ({san}): {e}") from e

        return pgn_data.san_moves

    def _execute_san_move(self, san: str) -> None:
        """
        Parse and execute a SAN move.

        Args:
            san: SAN notation string

        Raises:
            PGNError: If the move is illegal or ambiguous
        """
        # Handle castling
        clean_san = san.rstrip("+#")
        if clean_san in ("O-O", "O-O-O", "0-0", "0-0-0"):
            self._execute_castling(clean_san)
            return

        # Parse SAN components
        parsed = self._parse_san(san)

        # Find source square using disambiguation
        from_square = self._find_source_square(parsed, san)
        to_square = parsed["to_square"]
        promotion = parsed.get("promotion")

        self.move_executor.execute_move(from_square, to_square, promotion)

    def _execute_castling(self, san: str) -> None:
        """
        Execute a castling move.

        Args:
            san: Castling notation (O-O, O-O-O, 0-0, or 0-0-0)

        Raises:
            PGNError: If castling is illegal
        """
        # Determine king's starting position
        rank = 0 if self.game_state.current_turn == Color.WHITE else 7
        from_square = (4, rank)  # King starts on e-file

        # Determine destination based on castling type
        is_kingside = san in ("O-O", "0-0")
        to_file = 6 if is_kingside else 2
        to_square = (to_file, rank)

        # Verify the king exists and castling is legal
        king = self.board.get_piece(*from_square)
        if king is None or king.piece_type != PieceType.KING:
            raise PGNError(f"No king at expected position for castling")

        legal_moves = self.move_generator.get_legal_moves(
            self.board, king, self.game_state
        )
        if to_square not in legal_moves:
            side = "kingside" if is_kingside else "queenside"
            raise PGNError(f"Illegal {side} castling")

        self.move_executor.execute_move(from_square, to_square)

    def _parse_san(self, san: str) -> dict:
        """
        Parse a SAN move into its components.

        Args:
            san: SAN notation string

        Returns:
            Dictionary with keys:
                - piece_type: PieceType
                - from_file: int | None (0-7 if specified)
                - from_rank: int | None (0-7 if specified)
                - is_capture: bool
                - to_square: tuple[int, int]
                - promotion: PieceType | None

        Raises:
            PGNError: If the SAN format is invalid
        """
        # Remove check/checkmate indicators
        clean_san = san.rstrip("+#")

        match = self.SAN_PATTERN.match(clean_san)
        if not match:
            raise PGNError(f"Invalid SAN format: {san}")

        piece_letter, from_file, from_rank, capture, dest, promo = match.groups()

        # Determine piece type
        if piece_letter:
            piece_type = self.PIECE_TYPE_MAP[piece_letter]
        else:
            piece_type = PieceType.PAWN

        # Parse disambiguation
        parsed_from_file = None
        parsed_from_rank = None
        if from_file:
            parsed_from_file = ord(from_file) - ord("a")
        if from_rank:
            parsed_from_rank = int(from_rank) - 1

        # Parse destination
        dest_file = ord(dest[0]) - ord("a")
        dest_rank = int(dest[1]) - 1
        to_square = (dest_file, dest_rank)

        # Parse promotion
        promotion = None
        if promo:
            promotion = self.PIECE_TYPE_MAP[promo]

        return {
            "piece_type": piece_type,
            "from_file": parsed_from_file,
            "from_rank": parsed_from_rank,
            "is_capture": capture is not None,
            "to_square": to_square,
            "promotion": promotion,
        }

    def _find_source_square(
        self, parsed: dict, original_san: str
    ) -> tuple[int, int]:
        """
        Find the source square for a move given SAN disambiguation.

        Args:
            parsed: Parsed SAN components
            original_san: Original SAN string (for error messages)

        Returns:
            Source square (file, rank)

        Raises:
            PGNError: If the move is illegal or ambiguous
        """
        piece_type = parsed["piece_type"]
        to_square = parsed["to_square"]
        from_file = parsed.get("from_file")
        from_rank = parsed.get("from_rank")

        # Find all pieces of the correct type that can reach the destination
        candidates: list[tuple[int, int]] = []

        for file, rank, piece in self.board:
            if piece is None:
                continue
            if piece.piece_type != piece_type:
                continue
            if piece.color != self.game_state.current_turn:
                continue

            # Apply disambiguation filters
            if from_file is not None and piece.file != from_file:
                continue
            if from_rank is not None and piece.rank != from_rank:
                continue

            # Check if this piece can legally move to target
            legal_moves = self.move_generator.get_legal_moves(
                self.board, piece, self.game_state
            )
            if to_square in legal_moves:
                candidates.append(piece.position)

        if len(candidates) == 0:
            raise PGNError(f"No legal piece found for move: {original_san}")
        if len(candidates) > 1:
            raise PGNError(
                f"Ambiguous move: {original_san} "
                f"(could be from {candidates[0]} or {candidates[1]})"
            )

        return candidates[0]
