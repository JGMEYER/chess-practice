from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from chess.constants import Color


@dataclass(frozen=True)
class Opening:
    name: str
    opening_type: str
    side: Color
    eco_code: str
    moves: str


class OpeningsRepository:
    """In-memory repository for chess openings."""

    def __init__(self) -> None:
        self._by_side: dict[Color, dict[str, Opening]] = {
            Color.WHITE: {},
            Color.BLACK: {},
        }

    def add(self, opening: Opening) -> None:
        self._by_side[opening.side][opening.moves] = opening

    def find_by_moves(self, moves: str) -> Opening | None:
        side = self._infer_side_from_moves(moves)
        return self._by_side[side].get(moves)

    def _infer_side_from_moves(self, moves: str) -> Color:
        """Infer which side the opening is for based on the last move notation.

        In PGN, move numbers only appear before White's moves:
        - "1.e4" = White's move (contains dot)
        - "e5" = Black's move (no dot, follows White)
        - "2...Nf6" = Black's move (explicit black notation)
        """
        last_token = moves.split()[-1]
        # White moves have format "N.move" (e.g., "1.e4", "2.Nf3")
        # Black moves are either plain (e.g., "e5") or explicit (e.g., "2...Nf6")
        if "..." in last_token:
            return Color.BLACK
        if "." in last_token:
            return Color.WHITE
        return Color.BLACK

    @classmethod
    def from_csv(cls, path: Path) -> OpeningsRepository:
        repo = cls()
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                side = Color.WHITE if row["side"] == "White" else Color.BLACK
                opening = Opening(
                    name=row["name"],
                    opening_type=row["type"],
                    side=side,
                    eco_code=row["eco_code"],
                    moves=row["moves"],
                )
                repo.add(opening)
        return repo


def load_openings() -> OpeningsRepository:
    """Load the famous openings repository."""
    data_path = Path(__file__).parent / "data" / "famous_openings.csv"
    return OpeningsRepository.from_csv(data_path)
