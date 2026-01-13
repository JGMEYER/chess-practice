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
        # Key by move sequence - side in CSV indicates theoretical "owner" of the
        # opening (e.g., Sicilian = Black's system), not whose turn it is
        self._by_moves: dict[str, Opening] = {}

    def add(self, opening: Opening) -> None:
        self._by_moves[opening.moves] = opening

    def find_by_moves(self, moves: str) -> Opening | None:
        return self._by_moves.get(moves)

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
