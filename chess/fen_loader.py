from __future__ import annotations

from .board import Board
from .fen import FENParser, FENError
from .game_state import GameState


class FENLoader:
    """Loads FEN positions into Board and GameState."""

    def __init__(self, board: Board, game_state: GameState):
        """
        Initialize the FEN loader.

        Args:
            board: The board to load positions into
            game_state: The game state to configure
        """
        self.board = board
        self.game_state = game_state

    def load(self, fen_string: str) -> None:
        """
        Load a FEN string, updating both board and game state.

        Args:
            fen_string: Valid FEN string

        Raises:
            FENError: If the FEN string is invalid
        """
        fen_data = FENParser.parse(fen_string)
        self.board.load_from_fen_data(fen_data)
        self.game_state.load_from_fen_data(fen_data)

    def load_starting_position(self) -> None:
        """Load the standard starting position."""
        self.load(FENParser.STARTING_FEN)
