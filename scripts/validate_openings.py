#!/usr/bin/env python3
"""
Validate opening data for illegal move sequences.

This script reads all entries from famous_openings.csv and attempts to play
through each move sequence to detect any illegal moves. It reports all
problematic entries with details about what went wrong.

Usage:
    python scripts/validate_openings.py
"""

import csv
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from chess.board import Board
from chess.fen import FENParser
from chess.game_state import GameState
from chess.pgn import PGNParser
from chess.pgn_loader import PGNLoader, PGNError


def validate_opening(
    line_number: int,
    opening_name: str,
    variation_name: str,
    eco_code: str,
    moves: str,
) -> dict | None:
    """
    Validate a single opening by playing through its moves.

    Returns None if valid, or a dict with error details if invalid.
    """
    # Parse moves from PGN-style notation
    san_moves = PGNParser._parse_movetext(moves)

    if not san_moves:
        return {
            "line": line_number,
            "opening": opening_name,
            "variation": variation_name,
            "eco": eco_code,
            "move_number": 0,
            "move": "(none)",
            "error": "No moves found in entry",
        }

    # Set up fresh board and game state
    board = Board()
    game_state = GameState()
    fen_data = FENParser.parse(FENParser.STARTING_FEN)
    board.load_from_fen_data(fen_data)
    game_state.load_from_fen_data(fen_data)

    # Create PGN loader to execute moves
    loader = PGNLoader(board, game_state)

    # Try to play through all moves
    for i, san in enumerate(san_moves):
        move_number = (i // 2) + 1
        try:
            loader._execute_san_move(san)
        except PGNError as e:
            return {
                "line": line_number,
                "opening": opening_name,
                "variation": variation_name,
                "eco": eco_code,
                "move_number": move_number,
                "ply": i + 1,
                "move": san,
                "error": str(e),
            }
        except Exception as e:
            return {
                "line": line_number,
                "opening": opening_name,
                "variation": variation_name,
                "eco": eco_code,
                "move_number": move_number,
                "ply": i + 1,
                "move": san,
                "error": f"Unexpected error: {e}",
            }

    return None  # Valid


def main():
    """Run validation on all openings."""
    # Check for command line argument to specify which file to validate
    if len(sys.argv) > 1:
        csv_path = project_root / sys.argv[1]
    else:
        csv_path = project_root / "chess" / "patterns" / "data" / "famous_openings.csv"

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    print(f"Validating openings from: {csv_path}")
    print()

    errors = []
    total_count = 0
    opening_count = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_number, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
            total_count += 1

            # Skip non-opening entries (like "Mate" type)
            if row.get("type") != "Opening":
                continue

            opening_count += 1

            result = validate_opening(
                line_number=line_number,
                opening_name=row["opening_name"],
                variation_name=row.get("variation_name", ""),
                eco_code=row.get("eco_code", ""),
                moves=row["moves"],
            )

            if result is not None:
                errors.append(result)

    # Print results
    print(f"Total entries in CSV: {total_count}")
    print(f"Opening entries validated: {opening_count}")
    print()

    if errors:
        print(f"FOUND {len(errors)} ILLEGAL ENTRY/ENTRIES:")
        print("=" * 70)
        for err in errors:
            print()
            print(f"Line {err['line']}: {err['opening']}")
            if err["variation"]:
                print(f"  Variation: {err['variation']}")
            print(f"  ECO: {err['eco']}")
            print(f"  Move {err['move_number']} (ply {err.get('ply', '?')}): {err['move']}")
            print(f"  Error: {err['error']}")
        print()
        print("=" * 70)
        print(f"Summary: {len(errors)} illegal entries found out of {opening_count} openings")
        sys.exit(1)
    else:
        print("All openings validated successfully!")
        print(f"Summary: 0 errors found in {opening_count} openings")
        sys.exit(0)


if __name__ == "__main__":
    main()
