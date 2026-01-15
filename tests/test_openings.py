from pathlib import Path

import pytest

from chess.patterns import BOOK_MOVE, Opening, OpeningTrie


@pytest.fixture
def trie() -> OpeningTrie:
    fixtures_path = Path(__file__).parent / "fixtures" / "test_openings.csv"
    return OpeningTrie.from_csv(fixtures_path)


class TestOpening:
    def test_display_name_without_variation(self) -> None:
        """Test display_name with no variation."""
        opening = Opening("Sicilian Defense", None)
        assert opening.display_name == "Sicilian Defense"

    def test_display_name_with_variation(self) -> None:
        """Test display_name with variation."""
        opening = Opening("Sicilian Defense", "Dragon Variation")
        assert opening.display_name == "Sicilian Defense: Dragon Variation"

    def test_is_book_move_false(self) -> None:
        """Test is_book_move returns False for normal openings."""
        opening = Opening("Sicilian Defense", None)
        assert opening.is_book_move is False

    def test_is_book_move_true(self) -> None:
        """Test is_book_move returns True for book move."""
        opening = Opening(BOOK_MOVE, None)
        assert opening.is_book_move is True


class TestOpeningTrie:
    def test_lookup_base_opening(self, trie: OpeningTrie) -> None:
        """Test looking up a base opening without variation."""
        result = trie.lookup(["e4", "c5"])
        assert result is not None
        assert result.opening_name == "Sicilian Defense"
        assert result.variation_name is None

    def test_lookup_opening_with_variation(self, trie: OpeningTrie) -> None:
        """Test looking up an opening with a variation name."""
        result = trie.lookup(["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "g6"])
        assert result is not None
        assert result.opening_name == "Sicilian Defense"
        assert result.variation_name == "Dragon Variation"

    def test_lookup_intermediate_position(self, trie: OpeningTrie) -> None:
        """Test looking up an intermediate position (not end of a line)."""
        # 1.e4 e5 is on the path to Italian Game but not a named line itself
        result = trie.lookup(["e4", "e5"])
        assert result is not None
        assert result.opening_name == "Italian Game"
        assert result.variation_name is None  # Intermediate position, no variation

    def test_lookup_complete_line(self, trie: OpeningTrie) -> None:
        """Test looking up a complete opening line."""
        result = trie.lookup(["e4", "e5", "Nf3", "Nc6", "Bc4"])
        assert result is not None
        assert result.opening_name == "Italian Game"

    def test_lookup_nonexistent_returns_none(self, trie: OpeningTrie) -> None:
        """Test that unknown move sequences return None."""
        result = trie.lookup(["e4", "e5", "Ke2"])
        assert result is None

    def test_lookup_empty_sequence(self, trie: OpeningTrie) -> None:
        """Test looking up empty move sequence."""
        result = trie.lookup([])
        assert result is None

    def test_get_continuations(self, trie: OpeningTrie) -> None:
        """Test getting available book moves from a position."""
        # From starting position, we should see e4 as a continuation
        continuations = trie.get_continuations([])
        san_moves = [c[0] for c in continuations]
        assert "e4" in san_moves
        # d4 might also be there if we add more openings

    def test_get_continuations_after_e4(self, trie: OpeningTrie) -> None:
        """Test continuations after 1.e4."""
        continuations = trie.get_continuations(["e4"])
        san_moves = [c[0] for c in continuations]
        # Our test fixture has Sicilian (c5), French (e6), and Italian (e5)
        assert "c5" in san_moves
        assert "e5" in san_moves
        assert "e6" in san_moves

    def test_continuations_include_opening_info(self, trie: OpeningTrie) -> None:
        """Test that continuations include opening information."""
        continuations = trie.get_continuations(["e4"])
        # Find the c5 continuation (Sicilian)
        sicilian_cont = [c for c in continuations if c[0] == "c5"]
        assert len(sicilian_cont) == 1
        san, opening = sicilian_cont[0]
        assert opening is not None
        assert opening.opening_name == "Sicilian Defense"

    def test_variation_with_separator(self, trie: OpeningTrie) -> None:
        """Test opening with variation name containing separator."""
        # Albin Countergambit: Lasker Trap
        result = trie.lookup(["d4", "d5", "c4", "e5", "dxe5", "d4", "e3", "Bb4+", "Bd2", "dxe3"])
        assert result is not None
        assert result.opening_name == "Albin Countergambit"
        assert result.variation_name == "Lasker Trap"

    def test_book_move_for_multiple_openings(self) -> None:
        """Test that positions with multiple openings return Book Move."""
        # Create a trie with multiple openings sharing early moves
        trie = OpeningTrie()
        trie.insert(["e4", "e5"], "Italian Game", None)
        trie.insert(["e4", "c5"], "Sicilian Defense", None)
        trie.insert(["e4", "e6"], "French Defense", None)

        # After 1.e4, multiple openings pass through - should be Book Move
        result = trie.lookup(["e4"])
        assert result is not None
        assert result.is_book_move is True
        assert result.opening_name == BOOK_MOVE

    def test_single_opening_not_book_move(self) -> None:
        """Test that positions with single opening don't return Book Move."""
        trie = OpeningTrie()
        trie.insert(["e4", "c5", "Nf3"], "Sicilian Defense", None)

        # After 1.e4 c5 Nf3, only Sicilian passes through
        result = trie.lookup(["e4", "c5", "Nf3"])
        assert result is not None
        assert result.is_book_move is False
        assert result.opening_name == "Sicilian Defense"
