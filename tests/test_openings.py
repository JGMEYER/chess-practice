from pathlib import Path

import pytest

from chess.patterns import Opening, OpeningsRepository
from chess.constants import Color


@pytest.fixture
def repo() -> OpeningsRepository:
    fixtures_path = Path(__file__).parent / "fixtures" / "test_openings.csv"
    return OpeningsRepository.from_csv(fixtures_path)


class TestOpeningsRepository:
    def test_find_white_opening_by_moves(self, repo: OpeningsRepository) -> None:
        result = repo.find_by_moves("1.e4 e5 2.Nf3 Nc6 3.Bc4")
        assert result is not None
        assert result.name == "Italian Game"
        assert result.side == Color.WHITE

    def test_find_black_opening_by_moves(self, repo: OpeningsRepository) -> None:
        result = repo.find_by_moves("1.e4 c5")
        assert result is not None
        assert result.name == "Sicilian Defense"
        assert result.side == Color.BLACK

    def test_find_nonexistent_opening_returns_none(
        self, repo: OpeningsRepository
    ) -> None:
        result = repo.find_by_moves("1.e4 e5 2.Ke2")
        assert result is None

    def test_opening_has_all_fields(self, repo: OpeningsRepository) -> None:
        result = repo.find_by_moves("1.e4 e6")
        assert result is not None
        assert result.name == "French Defense"
        assert result.opening_type == "Opening"
        assert result.side == Color.BLACK
        assert result.eco_code == "C00"
        assert result.moves == "1.e4 e6"


class TestSideInference:
    def test_infers_white_from_white_last_move(self) -> None:
        repo = OpeningsRepository()
        assert repo._infer_side_from_moves("1.e4 e5 2.Nf3") == Color.WHITE

    def test_infers_black_from_black_last_move(self) -> None:
        repo = OpeningsRepository()
        assert repo._infer_side_from_moves("1.e4 c5") == Color.BLACK

    def test_infers_black_from_explicit_black_notation(self) -> None:
        repo = OpeningsRepository()
        assert repo._infer_side_from_moves("1.e4 e5 2...Nc6") == Color.BLACK
