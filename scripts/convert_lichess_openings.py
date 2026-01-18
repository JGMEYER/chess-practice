#!/usr/bin/env python3
"""
Convert Lichess chess-openings TSV files to our CSV format.

Reads the lichess_*.tsv files and produces a single famous_openings.csv
with the same structure as our existing file.

Usage:
    python scripts/convert_lichess_openings.py
"""

import csv
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent


def parse_opening_name(name: str) -> tuple[str, str]:
    """
    Parse Lichess opening name into opening_name and variation_name.

    Lichess format: "Opening: Variation, Subvariation"
    Our format: opening_name="Opening", variation_name="Variation, Subvariation"
    """
    if ": " in name:
        parts = name.split(": ", 1)
        return parts[0], parts[1]
    else:
        return name, ""


def determine_side(pgn: str) -> str:
    """
    Determine which side plays the last move (who "owns" the opening).

    Count moves to determine if it ends on White or Black.
    """
    # Count the moves by splitting on move numbers
    moves = pgn.split()
    # Filter out move numbers
    actual_moves = [m for m in moves if not m[0].isdigit() and m != "."]

    # If odd number of moves, last move was White; even means Black
    return "White" if len(actual_moves) % 2 == 1 else "Black"


def main():
    tsv_files = [
        project_root / "lichess_a.tsv",
        project_root / "lichess_b.tsv",
        project_root / "lichess_c.tsv",
        project_root / "lichess_d.tsv",
        project_root / "lichess_e.tsv",
    ]

    output_path = project_root / "chess" / "patterns" / "data" / "famous_openings_lichess.csv"

    openings = []

    for tsv_file in tsv_files:
        if not tsv_file.exists():
            print(f"Warning: {tsv_file} not found, skipping", file=sys.stderr)
            continue

        with open(tsv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                eco = row["eco"]
                name = row["name"]
                pgn = row["pgn"]

                opening_name, variation_name = parse_opening_name(name)
                side = determine_side(pgn)

                openings.append({
                    "opening_name": opening_name,
                    "variation_name": variation_name,
                    "type": "Opening",
                    "side": side,
                    "eco_code": eco,
                    "moves": pgn,
                })

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["opening_name", "variation_name", "type", "side", "eco_code", "moves"],
        )
        writer.writeheader()
        writer.writerows(openings)

    print(f"Converted {len(openings)} openings to {output_path}")


if __name__ == "__main__":
    main()
