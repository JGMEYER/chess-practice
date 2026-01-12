from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .constants import Color, PieceType
from .pieces import King, Queen, Rook, Bishop, Knight, Pawn

if TYPE_CHECKING:
    from .board import Board
    from .game_state import GameState
    from .piece import Piece


class FENError(ValueError):
    """Raised when FEN parsing fails."""

    pass


@dataclass
class CastlingRights:
    """Represents castling availability for both sides."""

    white_kingside: bool = True
    white_queenside: bool = True
    black_kingside: bool = True
    black_queenside: bool = True


@dataclass
class FENData:
    """Parsed FEN string data."""

    pieces: dict[tuple[int, int], Piece] = field(default_factory=dict)
    active_color: Color = Color.WHITE
    castling_rights: CastlingRights = field(default_factory=CastlingRights)
    en_passant_target: tuple[int, int] | None = None
    halfmove_clock: int = 0
    fullmove_number: int = 1


class FENParser:
    """Parses FEN strings into FENData objects."""

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    PIECE_MAP: dict[str, tuple[type, Color]] = {
        "K": (King, Color.WHITE),
        "Q": (Queen, Color.WHITE),
        "R": (Rook, Color.WHITE),
        "B": (Bishop, Color.WHITE),
        "N": (Knight, Color.WHITE),
        "P": (Pawn, Color.WHITE),
        "k": (King, Color.BLACK),
        "q": (Queen, Color.BLACK),
        "r": (Rook, Color.BLACK),
        "b": (Bishop, Color.BLACK),
        "n": (Knight, Color.BLACK),
        "p": (Pawn, Color.BLACK),
    }

    @classmethod
    def parse(cls, fen_string: str) -> FENData:
        """
        Parse a FEN string into FENData.

        Args:
            fen_string: A valid FEN string with all 6 fields

        Returns:
            FENData containing the parsed position

        Raises:
            FENError: If the FEN string is invalid
        """
        parts = fen_string.strip().split()

        if len(parts) != 6:
            raise FENError(
                f"Invalid FEN: expected 6 fields, got {len(parts)}. "
                f"FEN must include: piece placement, active color, castling, "
                f"en passant, halfmove clock, fullmove number"
            )

        pieces = cls._parse_piece_placement(parts[0])
        active_color = cls._parse_active_color(parts[1])
        castling_rights = cls._parse_castling(parts[2])
        en_passant_target = cls._parse_en_passant(parts[3])
        halfmove_clock = cls._parse_halfmove(parts[4])
        fullmove_number = cls._parse_fullmove(parts[5])

        return FENData(
            pieces=pieces,
            active_color=active_color,
            castling_rights=castling_rights,
            en_passant_target=en_passant_target,
            halfmove_clock=halfmove_clock,
            fullmove_number=fullmove_number,
        )

    @classmethod
    def _parse_piece_placement(cls, placement: str) -> dict[tuple[int, int], Piece]:
        """Parse the piece placement field (field 1)."""
        pieces: dict[tuple[int, int], Piece] = {}
        ranks = placement.split("/")

        if len(ranks) != 8:
            raise FENError(
                f"Invalid piece placement: expected 8 ranks, got {len(ranks)}"
            )

        for fen_rank_idx, rank_str in enumerate(ranks):
            # FEN rank 8 (index 0) = internal rank 7
            internal_rank = 7 - fen_rank_idx
            file = 0

            for char in rank_str:
                if char.isdigit():
                    empty_squares = int(char)
                    if empty_squares < 1 or empty_squares > 8:
                        raise FENError(f"Invalid empty square count: {char}")
                    file += empty_squares
                elif char in cls.PIECE_MAP:
                    piece_class, color = cls.PIECE_MAP[char]
                    pieces[(file, internal_rank)] = piece_class(color)
                    file += 1
                else:
                    raise FENError(f"Invalid character in piece placement: '{char}'")

            if file != 8:
                raise FENError(
                    f"Invalid rank {8 - fen_rank_idx}: "
                    f"expected 8 files, got {file}"
                )

        return pieces

    @classmethod
    def _parse_active_color(cls, color: str) -> Color:
        """Parse the active color field (field 2)."""
        if color == "w":
            return Color.WHITE
        elif color == "b":
            return Color.BLACK
        else:
            raise FENError(f"Invalid active color: '{color}' (expected 'w' or 'b')")

    @classmethod
    def _parse_castling(cls, castling: str) -> CastlingRights:
        """Parse the castling availability field (field 3)."""
        if castling == "-":
            return CastlingRights(
                white_kingside=False,
                white_queenside=False,
                black_kingside=False,
                black_queenside=False,
            )

        rights = CastlingRights(
            white_kingside=False,
            white_queenside=False,
            black_kingside=False,
            black_queenside=False,
        )

        for char in castling:
            if char == "K":
                rights.white_kingside = True
            elif char == "Q":
                rights.white_queenside = True
            elif char == "k":
                rights.black_kingside = True
            elif char == "q":
                rights.black_queenside = True
            else:
                raise FENError(f"Invalid castling character: '{char}'")

        return rights

    @classmethod
    def _parse_en_passant(cls, en_passant: str) -> tuple[int, int] | None:
        """
        Parse the en passant target square field (field 4).

        Note: FEN specifies the landing square (e.g., e3), but we store
        the position of the pawn that can be captured (e.g., e4).
        """
        if en_passant == "-":
            return None

        if len(en_passant) != 2:
            raise FENError(f"Invalid en passant square: '{en_passant}'")

        file_char, rank_char = en_passant

        if file_char not in "abcdefgh":
            raise FENError(f"Invalid en passant file: '{file_char}'")
        if rank_char not in "36":
            raise FENError(
                f"Invalid en passant rank: '{rank_char}' (must be 3 or 6)"
            )

        file = ord(file_char) - ord("a")

        # Convert landing square to pawn position
        # If rank is 3 (white can capture), black pawn is on rank 4 (index 3)
        # If rank is 6 (black can capture), white pawn is on rank 5 (index 4)
        if rank_char == "3":
            pawn_rank = 3  # Black pawn on rank 4
        else:  # rank_char == "6"
            pawn_rank = 4  # White pawn on rank 5

        return (file, pawn_rank)

    @classmethod
    def _parse_halfmove(cls, halfmove: str) -> int:
        """Parse the halfmove clock field (field 5)."""
        try:
            value = int(halfmove)
            if value < 0:
                raise FENError(f"Halfmove clock cannot be negative: {value}")
            return value
        except ValueError:
            raise FENError(f"Invalid halfmove clock: '{halfmove}'")

    @classmethod
    def _parse_fullmove(cls, fullmove: str) -> int:
        """Parse the fullmove number field (field 6)."""
        try:
            value = int(fullmove)
            if value < 1:
                raise FENError(f"Fullmove number must be at least 1: {value}")
            return value
        except ValueError:
            raise FENError(f"Invalid fullmove number: '{fullmove}'")


class FENGenerator:
    """Generates FEN strings from board and game state."""

    PIECE_CHARS = {
        (PieceType.KING, Color.WHITE): "K",
        (PieceType.QUEEN, Color.WHITE): "Q",
        (PieceType.ROOK, Color.WHITE): "R",
        (PieceType.BISHOP, Color.WHITE): "B",
        (PieceType.KNIGHT, Color.WHITE): "N",
        (PieceType.PAWN, Color.WHITE): "P",
        (PieceType.KING, Color.BLACK): "k",
        (PieceType.QUEEN, Color.BLACK): "q",
        (PieceType.ROOK, Color.BLACK): "r",
        (PieceType.BISHOP, Color.BLACK): "b",
        (PieceType.KNIGHT, Color.BLACK): "n",
        (PieceType.PAWN, Color.BLACK): "p",
    }

    @classmethod
    def generate(cls, board: Board, game_state: GameState) -> str:
        """
        Generate a FEN string from the current board and game state.

        Args:
            board: The current board position
            game_state: The current game state

        Returns:
            A valid FEN string representing the position
        """
        parts = [
            cls._generate_piece_placement(board),
            cls._generate_active_color(game_state),
            cls._generate_castling(game_state),
            cls._generate_en_passant(game_state),
            str(game_state.halfmove_clock),
            str(game_state.fullmove_number),
        ]
        return " ".join(parts)

    @classmethod
    def _generate_piece_placement(cls, board: Board) -> str:
        """Generate the piece placement field (field 1)."""
        ranks = []
        for rank in range(7, -1, -1):  # FEN starts from rank 8 (index 7)
            rank_str = ""
            empty_count = 0

            for file in range(8):
                piece = board.get_piece(file, rank)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    rank_str += cls.PIECE_CHARS[(piece.piece_type, piece.color)]

            if empty_count > 0:
                rank_str += str(empty_count)

            ranks.append(rank_str)

        return "/".join(ranks)

    @classmethod
    def _generate_active_color(cls, game_state: GameState) -> str:
        """Generate the active color field (field 2)."""
        return "w" if game_state.current_turn == Color.WHITE else "b"

    @classmethod
    def _generate_castling(cls, game_state: GameState) -> str:
        """Generate the castling availability field (field 3)."""
        rights = game_state.castling_rights
        castling = ""

        if rights.white_kingside:
            castling += "K"
        if rights.white_queenside:
            castling += "Q"
        if rights.black_kingside:
            castling += "k"
        if rights.black_queenside:
            castling += "q"

        return castling if castling else "-"

    @classmethod
    def _generate_en_passant(cls, game_state: GameState) -> str:
        """
        Generate the en passant target square field (field 4).

        Note: Our internal representation stores the pawn position,
        but FEN expects the landing square.
        """
        target = game_state.current_en_passant_target
        if target is None:
            return "-"

        file, pawn_rank = target
        file_char = chr(ord("a") + file)

        # Convert pawn position to landing square
        # If black pawn on rank 4 (index 3), landing square is rank 3
        # If white pawn on rank 5 (index 4), landing square is rank 6
        if pawn_rank == 3:
            rank_char = "3"
        else:  # pawn_rank == 4
            rank_char = "6"

        return file_char + rank_char
