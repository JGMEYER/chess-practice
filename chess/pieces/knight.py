from ..piece import Piece
from ..constants import PieceType


class Knight(Piece):
    """The Knight piece."""

    piece_type = PieceType.KNIGHT
    move_offsets = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2),
    ]
    is_sliding = False
    point_value = 3
