"""PGN (Portable Game Notation) parsing for chess games."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


class PGNError(ValueError):
    """Raised when PGN parsing or loading fails."""

    pass


@dataclass
class PGNData:
    """Parsed PGN game data."""

    # Standard Seven Tag Roster (STR)
    event: str = "?"
    site: str = "?"
    date: str = "????.??.??"
    round: str = "?"
    white: str = "?"
    black: str = "?"
    result: str = "*"

    # Additional optional tags
    extra_tags: dict[str, str] = field(default_factory=dict)

    # Move list as SAN strings (e.g., ["e4", "e5", "Nf3", "Nc6"])
    moves: list[str] = field(default_factory=list)

    # Starting position FEN (if game doesn't start from standard position)
    fen: str | None = None


class PGNParser:
    """Parses PGN strings into PGNData objects."""

    # Regex patterns
    TAG_PATTERN = re.compile(r'\[(\w+)\s+"([^"]*)"\]')
    MOVE_NUMBER_PATTERN = re.compile(r"\d+\.+")
    RESULT_PATTERN = re.compile(r"(1-0|0-1|1/2-1/2|\*)")

    # Map of standard tag names to PGNData attributes
    TAG_MAP = {
        "Event": "event",
        "Site": "site",
        "Date": "date",
        "Round": "round",
        "White": "white",
        "Black": "black",
        "Result": "result",
        "FEN": "fen",
    }

    @classmethod
    def parse(cls, pgn_string: str) -> PGNData:
        """
        Parse a PGN string into a PGNData object.

        Args:
            pgn_string: A string containing PGN formatted game data

        Returns:
            PGNData object with parsed tags and moves

        Raises:
            PGNError: If the PGN string is malformed
        """
        if not pgn_string or not pgn_string.strip():
            raise PGNError("Empty PGN string")

        data = PGNData()
        lines = pgn_string.strip().split("\n")
        movetext_lines: list[str] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for tag pair
            tag_match = cls.TAG_PATTERN.match(line)
            if tag_match:
                cls._apply_tag(data, tag_match.group(1), tag_match.group(2))
            else:
                # Assume it's movetext
                movetext_lines.append(line)

        # Parse movetext if present
        if movetext_lines:
            movetext = " ".join(movetext_lines)
            data.moves = cls._parse_movetext(movetext)

            # Extract result from movetext if not in tags
            result_match = cls.RESULT_PATTERN.search(movetext)
            if result_match and data.result == "*":
                data.result = result_match.group(1)

        return data

    @classmethod
    def _apply_tag(cls, data: PGNData, tag_name: str, value: str) -> None:
        """
        Apply a parsed tag to PGNData.

        Args:
            data: The PGNData object to update
            tag_name: The tag name (e.g., "Event", "White")
            value: The tag value
        """
        if tag_name in cls.TAG_MAP:
            setattr(data, cls.TAG_MAP[tag_name], value)
        else:
            data.extra_tags[tag_name] = value

    @classmethod
    def _parse_movetext(cls, movetext: str) -> list[str]:
        """
        Parse the movetext section into a list of SAN moves.

        Removes comments, variations, move numbers, and result markers.

        Args:
            movetext: The movetext string

        Returns:
            List of SAN move strings
        """
        # Remove comments in braces {comment}
        movetext = re.sub(r"\{[^}]*\}", "", movetext)

        # Remove variations in parentheses (variation) - handle nested
        depth = 0
        result = []
        for char in movetext:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif depth == 0:
                result.append(char)
        movetext = "".join(result)

        # Remove annotations like !, ?, !!, ??, !?, ?!
        movetext = re.sub(r"[!?]+", "", movetext)

        # Remove Numeric Annotation Glyphs (NAGs) like $1, $2
        movetext = re.sub(r"\$\d+", "", movetext)

        # Remove move numbers (1. or 1... patterns)
        movetext = cls.MOVE_NUMBER_PATTERN.sub("", movetext)

        # Remove result marker
        movetext = cls.RESULT_PATTERN.sub("", movetext)

        # Split into tokens and filter for valid moves
        tokens = movetext.split()
        moves = []

        for token in tokens:
            token = token.strip(".")
            if token and cls._is_valid_san(token):
                # Normalize castling notation (0-0 to O-O)
                token = token.replace("0-0-0", "O-O-O").replace("0-0", "O-O")
                moves.append(token)

        return moves

    @classmethod
    def _is_valid_san(cls, token: str) -> bool:
        """
        Check if a token looks like a valid SAN move.

        This is a basic validation - full validation happens during loading.

        Args:
            token: The token to validate

        Returns:
            True if the token appears to be a valid SAN move
        """
        # Castling
        if token in ("O-O", "O-O-O", "0-0", "0-0-0"):
            return True

        # Remove check/checkmate indicators for validation
        token = token.rstrip("+#")

        # Empty after stripping
        if not token:
            return False

        # Must contain at least one destination square (letter + number)
        # e.g., e4, Nf3, Bxe5, Qh4xe1, e8=Q
        if not re.search(r"[a-h][1-8]", token):
            return False

        # Basic structure check - starts with piece letter or file letter
        first_char = token[0]
        if first_char not in "KQRBNabcdefgh":
            return False

        return True
