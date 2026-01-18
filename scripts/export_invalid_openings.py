#!/usr/bin/env python3
"""
Export invalid openings with full details for research.

Outputs a CSV file with:
- Line number
- Opening name
- Variation name
- ECO code
- Full move sequence
- Move number where error occurred
- The problematic move
- Error description

Usage:
    python scripts/export_invalid_openings.py > invalid_openings.csv
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


def validate_opening(row: dict, line_number: int) -> dict | None:
    """
    Validate a single opening and return error details if invalid.
    """
    moves = row["moves"]
    san_moves = PGNParser._parse_movetext(moves)

    if not san_moves:
        return {
            "line": line_number,
            "opening": row["opening_name"],
            "variation": row.get("variation_name", ""),
            "eco": row.get("eco_code", ""),
            "moves": moves,
            "error_ply": 0,
            "error_move": "(none)",
            "error": "No moves found in entry",
        }

    # Set up fresh board and game state
    board = Board()
    game_state = GameState()
    fen_data = FENParser.parse(FENParser.STARTING_FEN)
    board.load_from_fen_data(fen_data)
    game_state.load_from_fen_data(fen_data)

    loader = PGNLoader(board, game_state)

    for i, san in enumerate(san_moves):
        try:
            loader._execute_san_move(san)
        except PGNError as e:
            return {
                "line": line_number,
                "opening": row["opening_name"],
                "variation": row.get("variation_name", ""),
                "eco": row.get("eco_code", ""),
                "moves": moves,
                "error_ply": i + 1,
                "error_move": san,
                "error": str(e),
            }
        except Exception as e:
            return {
                "line": line_number,
                "opening": row["opening_name"],
                "variation": row.get("variation_name", ""),
                "eco": row.get("eco_code", ""),
                "moves": moves,
                "error_ply": i + 1,
                "error_move": san,
                "error": f"Unexpected: {e}",
            }

    return None


def main():
    csv_path = project_root / "chess" / "patterns" / "data" / "famous_openings.csv"

    # Output header
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=["line", "opening", "variation", "eco", "moves", "error_ply", "error_move", "error"],
    )
    writer.writeheader()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_number, row in enumerate(reader, start=2):
            if row.get("type") != "Opening":
                continue

            result = validate_opening(row, line_number)
            if result is not None:
                writer.writerow(result)


if __name__ == "__main__":
    main()
