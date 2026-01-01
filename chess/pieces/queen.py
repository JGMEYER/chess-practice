from ..piece import Piece
from ..constants import PieceType


class Queen(Piece):
    """The Queen piece."""

    piece_type = PieceType.QUEEN
    move_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1),   # orthogonal
                    (1,-1), (1, 1), (-1, -1), (-1, 1)]  # diagonal
    is_sliding = True
