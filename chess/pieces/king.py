from ..piece import Piece
from ..constants import PieceType


class King(Piece):
    """The King piece."""

    piece_type = PieceType.KING
    move_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1),   # orthogonal
                    (1,-1), (1, 1), (-1, -1), (-1, 1)]  # diagonal
    is_sliding = False
    point_value = 0
