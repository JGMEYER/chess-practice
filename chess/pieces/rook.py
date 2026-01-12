from ..piece import Piece
from ..constants import PieceType


class Rook(Piece):
    """The Rook piece."""

    piece_type = PieceType.ROOK
    move_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    is_sliding = True
    point_value = 5
