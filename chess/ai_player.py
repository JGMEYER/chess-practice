from __future__ import annotations

import random
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
            # Note: We don't use Stockfish's built-in UCI_Elo because its minimum
            # is 1320. Instead we handle skill levels in _select_move_by_skill()
            # using MultiPV + evaluation noise.
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

    # Skill system constants
    MIN_ELO = 300
    MAX_ELO = 2000
    # Noise sigma at MIN_ELO (in centipawns) - higher = more random
    MAX_SIGMA = 400
    # Number of top moves to consider for skill-adjusted selection
    NUM_CANDIDATE_MOVES = 5

    def get_move(
        self, fen: str, think_time_ms: int | None = None
    ) -> tuple[tuple[int, int], tuple[int, int], PieceType | None]:
        """
        Get a move for the given position, adjusted for skill level.

        At high Elo (2000), always returns the best move.
        At lower Elo, adds noise to move evaluations to simulate weaker play.

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

            # Get top N candidate moves with evaluations
            top_moves = self.engine.get_top_moves(self.NUM_CANDIDATE_MOVES)

            if not top_moves:
                raise AIPlayerError("Engine returned no moves (game may be over)")

            # Select move based on skill level
            uci_move = self._select_move_by_skill(top_moves)

        except StockfishException as e:
            raise AIPlayerError(f"Engine error: {e}")

        return self._parse_uci_move(uci_move)

    def _select_move_by_skill(self, top_moves: list[dict]) -> str:
        """
        Select a move from candidates based on skill level.

        At max Elo, always picks the best move.
        At lower Elo, adds Gaussian noise to evaluations and picks the
        move with the best noisy score.

        Args:
            top_moves: List of move dicts from stockfish.get_top_moves().
                       Each dict has 'Move', 'Centipawn', and 'Mate' keys.

        Returns:
            UCI move string of the selected move.
        """
        # At max skill, just return the best move
        if self.elo >= self.MAX_ELO:
            return top_moves[0]["Move"]

        # Calculate noise based on Elo
        sigma = self._elo_to_sigma(self.elo)

        # Score each move with noise
        candidates = []
        for move_info in top_moves:
            # Get centipawn score (handle mate scores)
            if move_info["Mate"] is not None:
                # Mate in N moves - use large value
                mate_moves = move_info["Mate"]
                # Positive mate = we're winning, negative = losing
                base_score = 10000 - abs(mate_moves) * 10
                if mate_moves < 0:
                    base_score = -base_score
            elif move_info["Centipawn"] is not None:
                base_score = move_info["Centipawn"]
            else:
                # No evaluation available, skip
                continue

            # Add Gaussian noise
            noisy_score = base_score + random.gauss(0, sigma)
            candidates.append((move_info["Move"], noisy_score))

        if not candidates:
            # Fallback to first move if scoring failed
            return top_moves[0]["Move"]

        # Pick move with best noisy score
        return max(candidates, key=lambda x: x[1])[0]

    def _elo_to_sigma(self, elo: int) -> float:
        """
        Convert Elo rating to noise standard deviation.

        Linear interpolation from MAX_SIGMA at MIN_ELO to 0 at MAX_ELO.

        Args:
            elo: Current Elo rating.

        Returns:
            Noise sigma in centipawns.
        """
        # Clamp elo to valid range
        elo = max(self.MIN_ELO, min(self.MAX_ELO, elo))
        # Linear interpolation
        return self.MAX_SIGMA * (self.MAX_ELO - elo) / (self.MAX_ELO - self.MIN_ELO)

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
        Set the AI's skill level (Elo rating).

        The skill level controls how much noise is added to move evaluations.
        At 2000 Elo, plays the best move. At lower Elo, increasingly likely
        to pick suboptimal moves.

        Args:
            elo: Target Elo rating (300-2000).
        """
        self.elo = max(self.MIN_ELO, min(self.MAX_ELO, elo))

    def quit(self) -> None:
        """Shut down the Stockfish engine."""
        try:
            self.engine.send_quit_command()
        except StockfishException:
            pass  # Ignore errors during shutdown
