from enum import Enum, auto


class PieceType(Enum):
    KING = auto()
    QUEEN = auto()
    BISHOP = auto()
    KNIGHT = auto()
    ROOK = auto()
    PAWN = auto()


class Color(Enum):
    WHITE = auto()
    BLACK = auto()


class PlayerType(Enum):
    HUMAN = auto()
    AI = auto()
