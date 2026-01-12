# Chess Practice

A chess game built with Pygame for practicing and experimenting with Python code.

## Requirements

- Python 3.12+
- Poetry 2.2+

## Setup

1. Install dependencies and create virtual environment:

   ```bash
   poetry install
   ```

2. The virtual environment is created in `.venv/` within the project directory.

## Running Scripts

Run Python scripts using Poetry:

```bash
poetry run python main.py
```

Or activate the virtual environment shell:

```bash
poetry shell
python main.py
```

## Managing Dependencies

Add a new dependency:

```bash
poetry add <package-name>
```

Add a development dependency:

```bash
poetry add --group dev <package-name>
```

Remove a dependency:

```bash
poetry remove <package-name>
```

Update all dependencies:

```bash
poetry update
```

## Chess Game

Run the chess game:

```bash
python -m poetry run python chess_game.py
```

## Running Tests

```bash
python -m poetry run pytest tests/ -v
```

## Project Structure

```
chess-practice/
├── .venv/              # Virtual environment (in-project)
├── assets/
│   └── sprites/        # Chess piece sprites (SVG)
├── chess/              # Chess game logic (pure Python)
│   ├── board.py        # Board state management
│   ├── constants.py    # PieceType and Color enums
│   ├── piece.py        # Base Piece class
│   └── pieces/         # Individual piece classes
├── graphics/           # Pygame rendering
│   ├── board_renderer.py
│   ├── constants.py    # Colors and dimensions
│   ├── piece_renderer.py
│   └── sprites.py      # SVG sprite loader
├── tests/              # Pytest test suite
├── chess_game.py       # Chess game entry point
├── main.py             # Main script
├── poetry.lock         # Locked dependency versions
├── pyproject.toml      # Project configuration
└── README.md
```

## Roadmap

- [x] King check logic
- [x] Castling
- [x] Undo/Redo UI
- [x] Flip board
- [x] Pawn promotion
- [x] AI move integration
- [ ] AI chat / analysis
- [ ] AI analysis bar
