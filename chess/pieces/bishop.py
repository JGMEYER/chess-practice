from ..piece import Piece
from ..constants import PieceType


class Bishop(Piece):
    """The Bishop piece."""

    piece_type = PieceType.BISHOP
    move_offsets = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
    is_sliding = True
