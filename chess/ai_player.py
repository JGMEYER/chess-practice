from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from stockfish import Stockfish, StockfishException

from .constants import PieceType

if TYPE_CHECKING:
    from .config import Config


class AIPlayerError(Exception):
    """Raised when AI player encounters an error."""

    pass


class AIPlayer:
    """AI chess player powered by Stockfish engine."""

    PROMOTION_MAP = {
        "q": PieceType.QUEEN,
        "r": PieceType.ROOK,
        "b": PieceType.BISHOP,
        "n": PieceType.KNIGHT,
    }

    def __init__(self, config: Config):
        """
        Initialize the AI player with Stockfish engine.

        Args:
            config: Application configuration with stockfish path and AI settings.

        Raises:
            AIPlayerError: If Stockfish engine cannot be initialized.
        """
        self.config = config
        self.elo = config.ai.elo
        self.think_time_ms = config.ai.think_time_ms

        stockfish_path = self._find_stockfish_path()
        if stockfish_path is None:
            raise AIPlayerError(
                "Stockfish engine not found. Please install Stockfish and configure "
                "the path in config.json. See config.example.json for reference."
            )

        try:
            self.engine = Stockfish(path=stockfish_path)
            self.engine.set_elo_rating(self.elo)
        except StockfishException as e:
            raise AIPlayerError(f"Failed to initialize Stockfish: {e}")

    def _find_stockfish_path(self) -> str | None:
        """
        Find the Stockfish executable path.

        Returns:
            Path to Stockfish executable, or None if not found.
        """
        # First check config
        if self.config.stockfish_path:
            return self.config.stockfish_path

        # Try to find in PATH
        path = shutil.which("stockfish")
        if path:
            return path

        return None

    def get_move(
        self, fen: str, think_time_ms: int | None = None
    ) -> tuple[tuple[int, int], tuple[int, int], PieceType | None]:
        """
        Get the best move for the given position.

        Args:
            fen: FEN string representing the current position.
            think_time_ms: Time to think in milliseconds. Defaults to config value.

        Returns:
            Tuple of (from_square, to_square, promotion_piece).
            Squares are (file, rank) tuples with 0-indexed values.
            promotion_piece is None for non-promotion moves.

        Raises:
            AIPlayerError: If engine fails to find a move.
        """
        if think_time_ms is None:
            think_time_ms = self.think_time_ms

        try:
            self.engine.set_fen_position(fen)
            uci_move = self.engine.get_best_move_time(think_time_ms)
        except StockfishException as e:
            raise AIPlayerError(f"Engine error: {e}")

        if uci_move is None:
            raise AIPlayerError("Engine returned no move (game may be over)")

        return self._parse_uci_move(uci_move)

    def _parse_uci_move(
        self, uci: str
    ) -> tuple[tuple[int, int], tuple[int, int], PieceType | None]:
        """
        Parse a UCI move string into coordinates.

        Args:
            uci: UCI move string like "e2e4" or "e7e8q" (promotion).

        Returns:
            Tuple of (from_square, to_square, promotion_piece).
        """
        from_file = ord(uci[0]) - ord("a")
        from_rank = int(uci[1]) - 1
        to_file = ord(uci[2]) - ord("a")
        to_rank = int(uci[3]) - 1

        promotion_piece = None
        if len(uci) == 5:
            promotion_piece = self.PROMOTION_MAP.get(uci[4].lower())

        return ((from_file, from_rank), (to_file, to_rank), promotion_piece)

    def set_elo(self, elo: int) -> None:
        """
        Set the engine's ELO rating.

        Args:
            elo: Target ELO rating.
        """
        self.elo = elo
        self.engine.set_elo_rating(elo)

    def quit(self) -> None:
        """Shut down the Stockfish engine."""
        try:
            self.engine.send_quit_command()
        except StockfishException:
            pass  # Ignore errors during shutdown
