from ..piece import Piece
from ..constants import PieceType


class Pawn(Piece):
    """The Pawn piece."""

    piece_type = PieceType.PAWN
    move_offsets = []  # Pawn has its own logic
    is_sliding = False
