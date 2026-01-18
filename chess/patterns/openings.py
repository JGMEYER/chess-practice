from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from chess.pgn import PGNParser

# Constant for positions where multiple openings pass through
BOOK_MOVE = "Book Move"


@dataclass(frozen=True)
class Opening:
    """Represents a chess opening."""

    opening_name: str  # e.g., "Sicilian Defense"
    variation_name: str | None = None  # e.g., "Dragon Variation" or None

    @property
    def display_name(self) -> str:
        """Format for display: 'Opening' or 'Opening: Variation'."""
        if self.variation_name:
            return f"{self.opening_name}: {self.variation_name}"
        return self.opening_name

    @property
    def is_book_move(self) -> bool:
        """Check if this is a generic book move (multiple openings)."""
        return self.opening_name == BOOK_MOVE


@dataclass
class TrieNode:
    """A node in the opening trie."""

    children: dict[str, TrieNode] = field(default_factory=dict)
    # Set of Opening objects that pass through this node
    openings: set[Opening] = field(default_factory=set)


class OpeningTrie:
    """Trie structure for efficient opening lookup by move sequence."""

    def __init__(self) -> None:
        self._root = TrieNode()

    @property
    def root(self) -> TrieNode:
        """Get the root node of the trie."""
        return self._root

    def insert(
        self, san_moves: list[str], opening_name: str, variation_name: str | None
    ) -> None:
        """
        Insert an opening line into the trie.

        Adds the Opening to every node along the path, tracking all openings
        that pass through each position.
        """
        opening = Opening(opening_name, variation_name)
        node = self._root

        for san in san_moves:
            if san not in node.children:
                node.children[san] = TrieNode()
            node = node.children[san]
            node.openings.add(opening)

    def lookup(self, san_moves: list[str]) -> Opening | None:
        """
        Look up the opening at the given move sequence.

        Returns an Opening object if found, None if not in trie.
        If multiple different opening names pass through this position,
        returns Opening(BOOK_MOVE, None).
        """
        node = self._root
        for san in san_moves:
            if san not in node.children:
                return None
            node = node.children[san]

        if not node.openings:
            return None

        # Get unique opening names
        unique_names = {o.opening_name for o in node.openings}

        if len(unique_names) > 1:
            # Multiple different openings pass through - return book move
            return Opening(BOOK_MOVE, None)

        # Single opening name - get the opening_name and check variations
        opening_name = unique_names.pop()
        variations = {o.variation_name for o in node.openings}

        if len(variations) == 1:
            # Single variation (or None)
            return Opening(opening_name, variations.pop())
        else:
            # Multiple variations - return just the opening name
            return Opening(opening_name, None)

    def get_continuations(
        self, san_moves: list[str]
    ) -> list[tuple[str, Opening | None]]:
        """
        Get available book moves from the given position.

        Returns list of (san, Opening) tuples where Opening may be None
        if the child node has no openings (shouldn't happen in practice).
        """
        node = self._root
        for san in san_moves:
            if san not in node.children:
                return []
            node = node.children[san]

        result = []
        for san, child in node.children.items():
            # Use the same logic as lookup to get Opening for each child
            if not child.openings:
                result.append((san, None))
                continue

            unique_names = {o.opening_name for o in child.openings}
            if len(unique_names) > 1:
                result.append((san, Opening(BOOK_MOVE, None)))
            else:
                opening_name = unique_names.pop()
                variations = {o.variation_name for o in child.openings}
                if len(variations) == 1:
                    result.append((san, Opening(opening_name, variations.pop())))
                else:
                    result.append((san, Opening(opening_name, None)))

        return result

    def get_all_openings(self) -> list[str]:
        """Get sorted list of unique opening names in the trie.

        Returns:
            Alphabetically sorted list of opening names (e.g., "Sicilian Defense").
        """
        openings: set[str] = set()
        self._collect_openings(self._root, openings)
        return sorted(openings)

    def _collect_openings(self, node: TrieNode, openings: set[str]) -> None:
        """Recursively collect opening names from all nodes."""
        for opening in node.openings:
            if not opening.is_book_move:
                openings.add(opening.opening_name)
        for child in node.children.values():
            self._collect_openings(child, openings)

    def get_variations_for_opening(self, opening_name: str) -> list[str]:
        """Get sorted list of variation names for a specific opening.

        Args:
            opening_name: The opening name to get variations for.

        Returns:
            Alphabetically sorted list of variation names (excluding None).
        """
        variations: set[str] = set()
        self._collect_variations(self._root, opening_name, variations)
        return sorted(variations)

    def _collect_variations(
        self, node: TrieNode, opening_name: str, variations: set[str]
    ) -> None:
        """Recursively collect variation names for a specific opening."""
        for opening in node.openings:
            if (
                opening.opening_name == opening_name
                and opening.variation_name is not None
            ):
                variations.add(opening.variation_name)
        for child in node.children.values():
            self._collect_variations(child, opening_name, variations)

    @classmethod
    def from_csv(cls, path: Path) -> OpeningTrie:
        """Load openings from CSV and build trie."""
        trie = cls()
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip "Mate" type entries - they're checkmate patterns, not openings
                if row.get("type") != "Opening":
                    continue

                opening_name = row["opening_name"]
                variation_name = row["variation_name"] or None
                movetext = row["moves"]

                # Parse movetext to SAN list
                san_moves = PGNParser._parse_movetext(movetext)

                if san_moves:
                    trie.insert(san_moves, opening_name, variation_name)

        return trie


def load_openings() -> OpeningTrie:
    """Load the famous openings trie."""
    data_path = Path(__file__).parent / "data" / "famous_openings.csv"
    return OpeningTrie.from_csv(data_path)
